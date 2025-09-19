from __future__ import annotations

import asyncio
import hashlib
import inspect
import logging
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    List,
    Type,
    Union,
)

import atomics
import msgpack

from wombat.multiprocessing.errors import EvaluationFailureError
from wombat.multiprocessing.ipc.utilities import default_encoder
from wombat.multiprocessing.traits.accounting import (
    AccountingTrait,
    GeneratedTrait,
    UncountedTrait,
)
from wombat.multiprocessing.traits.breaker import BreakerTrait, CircuitBreakerState
from wombat.multiprocessing.traits.consumes import ConsumesTrait
from wombat.multiprocessing.traits.debounce import DebounceTrait
from wombat.multiprocessing.traits.delayed import DelayedTrait
from wombat.multiprocessing.traits.evaluatable import EvaluatableTrait
from wombat.multiprocessing.traits.expirable import ExpirableTrait
from wombat.multiprocessing.traits.lifecycle import QueuedTrait
from wombat.multiprocessing.traits.loggable import LogCarrierTrait
from wombat.multiprocessing.traits.pinned import PinnedTrait
from wombat.multiprocessing.traits.produces import ProducesTrait
from wombat.multiprocessing.traits.rate_limit import RateLimitTrait
from wombat.multiprocessing.traits.requires_props import RequiresPropsTrait
from wombat.multiprocessing.traits.retryable import RetryableTrait
from wombat.multiprocessing.traits.state import StateTrait, TaskOutcome, TaskState
from wombat.multiprocessing.traits.tagged import TaggedTrait
from wombat.multiprocessing.traits.timeout import TimeoutTrait
from wombat.multiprocessing.traits.models import Task


def priority(level: int):
    """A decorator to assign a priority level to a system hook."""

    def wrapper(func):
        setattr(func, "_hook_priority", level)
        return func

    return wrapper


if TYPE_CHECKING:
    from wombat.multiprocessing.orchestrator import Orchestrator, OrchestratorBuilder
    from wombat.multiprocessing.traits.models import BaseTrait
    from wombat.multiprocessing.worker import Worker
    from wombat.multiprocessing.ipc.shared_memory_hash_map import SharedMemoryHashMap


async def _atomic_op(
    entity: Union["Orchestrator", "Worker"], op_name: str, value: int
):
    """Helper to run an atomic operation in an executor to avoid blocking the event loop."""
    loop = getattr(entity, "loop", None)
    if not loop and hasattr(entity, "runtime_state"):
        loop = getattr(entity.runtime_state, "loop", None)

    if not loop:
        return

    counter_prop = entity.props.get("in_flight_task_counter")
    if not counter_prop or not counter_prop.instance:
        return

    atomic_view = counter_prop.instance
    op = getattr(atomic_view, op_name)
    await loop.run_in_executor(None, op, value)


def _atomic_prop_initializer(shm_name: str):
    """
    Initializes an atomic view from a shared memory name. This function is
    designed to be pickled and sent to worker processes.
    """
    from multiprocessing import shared_memory

    attached_shm = shared_memory.SharedMemory(name=shm_name)
    # The prop system will manage this context manager.
    atomic_cm = atomics.atomicview(buffer=attached_shm.buf, atype=atomics.INT)
    # Keep a reference to the SharedMemory object on the context manager to
    # prevent it from being garbage-collected prematurely, which would cause
    # a BufferError on shutdown.
    atomic_cm._shm_obj_ref = attached_shm
    return atomic_cm


class BaseSystem:
    """Base class for all systems."""

    # A system declares the data components it operates on.
    required_traits: ClassVar[List[Type[BaseTrait]]] = []


def _sync_increment_raw_count(
    accounting_store: "SharedMemoryHashMap", worker_key: str, key: str, value: int
):
    """Synchronous helper to increment worker and total counts under a single lock."""
    with accounting_store.lock:
        worker_counts = accounting_store.get(worker_key, {})
        worker_counts[key] = worker_counts.get(key, 0) + value
        accounting_store[worker_key] = worker_counts

        total_counts = accounting_store.get("Total", {})
        total_counts[key] = total_counts.get(key, 0) + value
        accounting_store["Total"] = total_counts


def _sync_increment_worker_raw_count(
    accounting_store: "SharedMemoryHashMap", worker_key: str, key: str, value: int
):
    """Synchronous helper to increment only worker counts under a single lock."""
    with accounting_store.lock:
        worker_counts = accounting_store.get(worker_key, {})
        worker_counts[key] = worker_counts.get(key, 0) + value
        accounting_store[worker_key] = worker_counts


async def _increment_worker_raw_count(worker: "Worker", key: str, value: int = 1):
    """
    A raw, non-idempotent counter increment for worker-only accounting, run in
    an executor to prevent deadlocks.
    """
    await worker.runtime_state.loop.run_in_executor(
        None,
        _sync_increment_worker_raw_count,
        worker.props["accounting_store"].instance,
        worker.identity.name,
        key,
        value,
    )


async def _increment_raw_count(worker: "Worker", key: str, value: int = 1):
    """
    A raw, non-idempotent counter increment for accounting, run in an executor
    to prevent deadlocks.
    """
    await worker.runtime_state.loop.run_in_executor(
        None,
        _sync_increment_raw_count,
        worker.props["accounting_store"].instance,
        worker.identity.name,
        key,
        value,
    )


class AccountingSystem(BaseSystem):
    """System that handles the accounting logic for tasks."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [
        AccountingTrait,
        UncountedTrait,
        GeneratedTrait,
        StateTrait,
    ]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        """
        Auto-provisions a `SharedMemoryHashMap` for accounting if not already present.

        This build hook ensures that the necessary shared memory resource for
        storing task counts is created and managed by the orchestrator.
        """
        if "accounting_store" not in builder.props:
            from wombat.multiprocessing.ipc.shared_memory_hash_map import (
                SharedMemoryHashMap,
            )
            from wombat.multiprocessing.traits.models import Prop

            context = builder.context
            # Use a reasonably large capacity and slot size for accounting data.
            shm_map = SharedMemoryHashMap.create(
                context=context, capacity=4096, slot_size=1024, purpose="accounting"
            )
            builder.register_resource_for_cleanup(shm_map)
            builder.props["accounting_store"] = Prop(
                initializer=shm_map,
                use_context_manager=False,
            )

        if "in_flight_task_counter" not in builder.props:
            from multiprocessing import shared_memory

            from wombat.multiprocessing.traits.models import Prop

            # Create the shared memory block in the parent.
            shm_counter = shared_memory.SharedMemory(create=True, size=8)
            builder.register_resource_for_cleanup(shm_counter)

            builder.props["in_flight_task_counter"] = Prop(
                initializer=partial(_atomic_prop_initializer, shm_counter.name),
                use_context_manager=True,
            )

    @staticmethod
    async def _increment_worker_count(
        worker: "Worker", accounting_trait: "AccountingTrait", key: str, value: int = 1
    ):
        """Idempotent counter increment that only affects the worker's counts."""
        # Retries are cumulative and not idempotent, so they bypass the `counted` check.
        if key != "retries":
            if accounting_trait.counted.get(key):
                return

        await _increment_worker_raw_count(worker, key, value)

        if key != "retries":
            accounting_trait.counted[key] = True

    @staticmethod
    async def _increment_count(
        worker: "Worker", accounting_trait: "AccountingTrait", key: str, value: int = 1
    ):
        # Retries are cumulative and not idempotent, so they bypass the `counted` check.
        if key != "retries":
            if accounting_trait.counted.get(key):
                return

        await _increment_raw_count(worker, key, value)

        if key != "retries":
            accounting_trait.counted[key] = True

    @staticmethod
    async def on_batch_received(batch: list[Task], worker: "Worker"):
        """
        Initial task counting is handled by the `on_task_received` hook to
        prevent race conditions. This hook is a no-op.
        """
        pass

    @staticmethod
    @priority(500)
    async def on_task_received(task: "Task", worker: "Worker") -> None:
        """
        Processes 'received' counting rules from other traits.

        This hook is responsible for the 'initial' and 'generated' counts. After
        counting, it removes the `Uncounted` or `Generated` marker traits to
        prevent re-counting on retries.
        """
        accounting_trait = next(
            (t for t in task.traits if isinstance(t, AccountingTrait)), None
        )
        if not accounting_trait:
            return

        processed_a_received_event = False
        # Iterate over a copy, as we may modify the list.
        for trait in task.traits[:]:
            if trait.counting_rules:
                for rule in trait.counting_rules:
                    if rule.on_event == "received":
                        # This handles 'generated' and 'logs'. The orchestrator now
                        # handles the 'Total' count, and the worker handles its own count.
                        await AccountingSystem._increment_worker_count(
                            worker, accounting_trait, rule.counter_name
                        )
                        processed_a_received_event = True

        # Any task that does not have a 'received' event counter is considered
        # an initial task from the worker's perspective. This handles both
        # truly initial tasks and emitted consumers.
        if not processed_a_received_event:
            await AccountingSystem._increment_worker_count(
                worker, accounting_trait, "initial"
            )

        # Remove the marker trait(s) after counting to prevent re-counting on retries.
        task.remove_traits_by_type(UncountedTrait, GeneratedTrait)

    @staticmethod
    @priority(850)
    async def on_terminal_state(task: "Task", worker: "Worker"):
        """
        On any terminal state, increment the appropriate counter based on the
        final outcome.
        """
        accounting_trait = next(
            (t for t in task.traits if isinstance(t, AccountingTrait)), None
        )
        if not accounting_trait:
            return

        state_trait = next((t for t in task.traits if isinstance(t, StateTrait)), None)
        if not state_trait or state_trait.outcome is None:
            return

        outcome_map = {
            TaskOutcome.SUCCESS: "completed",
            TaskOutcome.FAILURE: "failures",
            TaskOutcome.CANCELLED: "cancelled",
            TaskOutcome.SKIPPED: "skipped",
            TaskOutcome.EXPIRED: "expired",
        }
        counter_name = outcome_map.get(state_trait.outcome)
        if counter_name:
            await AccountingSystem._increment_count(
                worker, accounting_trait, counter_name
            )
            await _atomic_op(worker, "sub", 1)

        # Process 'success' or 'failure' rules from other traits.
        if state_trait.outcome == TaskOutcome.SUCCESS:
            rule_event = "success"
        elif state_trait.outcome == TaskOutcome.FAILURE:
            rule_event = "failure"
        else:
            return  # No other outcomes trigger these rules.

        for trait in task.traits:
            if trait.counting_rules:
                for rule in trait.counting_rules:
                    if rule.on_event == rule_event:
                        await AccountingSystem._increment_count(
                            worker, accounting_trait, rule.counter_name
                        )

    @staticmethod
    @priority(500)
    async def on_tasks_sent(tasks: list[Task], orchestrator: "Orchestrator"):
        """
        Handles accounting for tasks that have been successfully sent to a worker.
        """
        initial_task_count = sum(
            1
            for task in tasks
            if any(isinstance(t, UncountedTrait) for t in task.traits)
        )
        await orchestrator._increment_total_count("initial", initial_task_count)
        if initial_task_count > 0:
            await _atomic_op(orchestrator, "add", initial_task_count)

    @staticmethod
    @priority(500)
    async def on_task_requeued(task: "Task", orchestrator: "Orchestrator") -> bool:
        """
        Handles accounting for tasks that re-enter the orchestrator via the
        requeue mechanism (e.g., produced tasks, log tasks).
        """
        # The orchestrator is responsible for incrementing the total 'generated'
        # and 'logs' counts to prevent race conditions with `finish_tasks`.
        is_generated = any(isinstance(t, GeneratedTrait) for t in task.traits)
        is_log = any(isinstance(t, LogCarrierTrait) for t in task.traits)

        if is_generated:
            await orchestrator._increment_total_count("generated", 1)
            await _atomic_op(orchestrator, "add", 1)
        if is_log:
            await orchestrator._increment_total_count("logs", 1)
            await _atomic_op(orchestrator, "add", 1)

        # This hook is only for accounting side-effects; it does not "handle"
        # the task, so the task should proceed to normal dispatch.
        return False


class BreakerSystem(BaseSystem):
    """System that implements the Circuit Breaker pattern."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [BreakerTrait, StateTrait]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        """
        Auto-provisions the necessary lock and shared dictionary for circuit breakers.

        This build hook ensures that the `breaker_lock` and `breaker_states`
        props are available for all workers if any task uses the `Breaker` trait.
        """
        from wombat.multiprocessing.ipc.shared_memory_hash_map import (
            SharedMemoryHashMap,
        )
        from wombat.multiprocessing.traits.models import Prop

        context = builder.context

        if "breaker_lock" not in builder.props:
            lock = context.Lock()
            builder.props["breaker_lock"] = Prop(
                initializer=lock, use_context_manager=False
            )

        if "breaker_states" not in builder.props:
            shm_map = SharedMemoryHashMap.create(context=context, purpose="breaker")
            builder.register_resource_for_cleanup(shm_map)
            builder.props["breaker_states"] = Prop(
                initializer=shm_map,
                use_context_manager=False,
            )

    @staticmethod
    def _get_circuit_key(task: "Task", breaker_trait: "BreakerTrait") -> str:
        """The key is based on the group, as the circuit protects a shared resource."""
        return breaker_trait.group or task.action

    @staticmethod
    @priority(100)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """
        Checks the state of the circuit before executing the task.

        If the circuit is OPEN, it prevents execution. If it has been OPEN for
        longer than the `recovery_timeout`, it transitions to HALF_OPEN to allow
        a single task to test the downstream service.
        """
        breaker_trait = next((t for t in task.traits if isinstance(t, BreakerTrait)), None)
        if not breaker_trait:
            return True, task

        lock = worker.props["breaker_lock"].instance
        states_dict = worker.props["breaker_states"].instance
        key = BreakerSystem._get_circuit_key(task, breaker_trait)
        now = worker.get_time()

        await worker.runtime_state.loop.run_in_executor(None, lock.acquire)
        try:
            shared_state = states_dict.get(key)
            if not shared_state:
                # Lazily initialize the state for this circuit.
                shared_state = {
                    "state": CircuitBreakerState.CLOSED.value,
                    "failures": 0,
                    "opened_at": 0.0,
                }
                states_dict[key] = shared_state
                return True, task

            current_state = CircuitBreakerState(shared_state["state"])
            if current_state == CircuitBreakerState.OPEN:
                if now - shared_state["opened_at"] > breaker_trait.recovery_timeout:
                    shared_state["state"] = CircuitBreakerState.HALF_OPEN.value
                    states_dict[key] = shared_state
                    worker.log(
                        f"Circuit breaker for {key} is now HALF_OPEN.", logging.INFO
                    )
                    return True, task  # Allow one test task
                else:
                    state_trait = next(
                        (t for t in task.traits if isinstance(t, StateTrait)), None
                    )
                    if state_trait:
                        state_trait.outcome = TaskOutcome.FAILURE
                        state_trait.reason = "Circuit breaker is open."
                    return False, task  # Block execution
            return True, task
        finally:
            await worker.runtime_state.loop.run_in_executor(None, lock.release)

    @staticmethod
    @priority(300)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """
        Resets the circuit breaker to CLOSED on a successful execution.

        If the circuit was in the HALF_OPEN state, a successful task execution
        is taken as a sign that the downstream service has recovered, so the
        circuit is closed and the failure count is reset. A successful task also
        resets the failure count if the circuit is currently CLOSED.
        """
        breaker_trait = next((t for t in task.traits if isinstance(t, BreakerTrait)), None)
        if not breaker_trait:
            return None

        lock = worker.props["breaker_lock"].instance
        states_dict = worker.props["breaker_states"].instance
        key = BreakerSystem._get_circuit_key(task, breaker_trait)

        await worker.runtime_state.loop.run_in_executor(None, lock.acquire)
        try:
            shared_state = states_dict.get(key)
            if not shared_state:
                return None

            current_state = CircuitBreakerState(shared_state["state"])
            if current_state == CircuitBreakerState.HALF_OPEN:
                worker.log(f"Circuit breaker for {key} has CLOSED.", logging.INFO)
                shared_state["state"] = CircuitBreakerState.CLOSED.value
                shared_state["failures"] = 0
                states_dict[key] = shared_state
            elif (
                current_state == CircuitBreakerState.CLOSED
                and shared_state["failures"] > 0
            ):
                worker.log(
                    f"Resetting failure count for {key} after success.", logging.DEBUG
                )
                shared_state["failures"] = 0
                states_dict[key] = shared_state
        finally:
            await worker.runtime_state.loop.run_in_executor(None, lock.release)
        return None

    @staticmethod
    @priority(200)
    async def on_action_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """
        Increments the failure count and potentially opens the circuit.

        If a task fails while the circuit is CLOSED, the failure count is
        incremented. If the count exceeds the `failure_threshold`, the circuit
        transitions to the OPEN state. If a task fails while HALF_OPEN, the
        circuit transitions back to OPEN.
        """
        breaker_trait = next((t for t in task.traits if isinstance(t, BreakerTrait)), None)
        if not breaker_trait:
            return

        lock = worker.props["breaker_lock"].instance
        states_dict = worker.props["breaker_states"].instance
        key = BreakerSystem._get_circuit_key(task, breaker_trait)
        now = worker.get_time()

        await worker.runtime_state.loop.run_in_executor(None, lock.acquire)
        try:
            shared_state = states_dict.get(key)
            if not shared_state:
                return

            current_state = CircuitBreakerState(shared_state["state"])
            if current_state == CircuitBreakerState.HALF_OPEN:
                shared_state["state"] = CircuitBreakerState.OPEN.value
                shared_state["opened_at"] = now
                worker.log(
                    f"Circuit for {key} failed in HALF_OPEN, re-opening.",
                    logging.WARNING,
                )
            elif current_state == CircuitBreakerState.OPEN:
                # The circuit is already open, do nothing.
                pass
            elif current_state == CircuitBreakerState.CLOSED:
                shared_state["failures"] += 1
                if shared_state["failures"] >= breaker_trait.failure_threshold:
                    shared_state["state"] = CircuitBreakerState.OPEN.value
                    shared_state["opened_at"] = now
                    worker.log(
                        f"Circuit for {key} has OPENED due to {shared_state['failures']} failures.",
                        logging.WARNING,
                    )
            states_dict[key] = shared_state
        finally:
            await worker.runtime_state.loop.run_in_executor(None, lock.release)


class DebounceSystem(BaseSystem):
    """System to prevent duplicate task execution."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [DebounceTrait, StateTrait]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        """
        Auto-provisions a `SharedMemoryHashMap` for deduplication if not present.

        This build hook ensures that the necessary shared memory resource for
        storing task execution timestamps is created and managed by the
        orchestrator.
        """
        if "deduplication_cache" not in builder.props:
            from wombat.multiprocessing.ipc.shared_memory_hash_map import (
                SharedMemoryHashMap,
            )
            from wombat.multiprocessing.traits.models import Prop

            context = builder.context
            shm_map = SharedMemoryHashMap.create(context=context, purpose="debounce")
            builder.register_resource_for_cleanup(shm_map)
            builder.props["deduplication_cache"] = Prop(
                initializer=shm_map,
                use_context_manager=False,
            )

    @staticmethod
    def _get_task_key(task: "Task", debounce_trait: "DebounceTrait") -> str:
        """
        Creates a stable, unique key for deduplication.

        If a `group` is provided, all tasks in that group are considered
        duplicates of each other, regardless of their action or arguments. The
        key will be the group name itself.

        If no `group` is provided, the key is generated from the task's action
        name and a hash of its arguments, ensuring only identical tasks are
        deduplicated.
        """
        if debounce_trait.group:
            return debounce_trait.group

        # Create a stable representation of the task's arguments.
        args_bytes = msgpack.packb(
            (task.args, task.kwargs), default=default_encoder, use_bin_type=True
        )
        # Use a stable hash algorithm to ensure the key is consistent across processes.
        hasher = hashlib.sha256()
        hasher.update(args_bytes)
        return f"{task.action}:{hasher.hexdigest()}"

    @staticmethod
    @priority(110)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """
        Checks if a similar task has run recently and skips execution if so.

        This hook calculates a unique key for the task based on its action and
        arguments. It then checks a shared cache to see if a task with the
        same key has executed within the configured `window`. If it has, the
        task is marked as `skipped`. Otherwise, the current time is recorded
        and execution proceeds.
        """
        debounce_trait = next((t for t in task.traits if isinstance(t, DebounceTrait)), None)
        if not debounce_trait:
            return True, task

        key = DebounceSystem._get_task_key(task, debounce_trait)
        dedupe_cache = worker.props["deduplication_cache"].instance

        def _check_and_set_sync():
            """Performs the check and set operation atomically under a lock."""
            with dedupe_cache.lock:
                now = worker.get_time()
                last_seen = dedupe_cache.get(key)
                if (
                    last_seen is not None
                    and (now - last_seen) <= debounce_trait.window.total_seconds()
                ):
                    return False
                dedupe_cache[key] = now
                return True

        should_run = await worker.runtime_state.loop.run_in_executor(
            None, _check_and_set_sync
        )

        if not should_run:
            worker.log(
                f"Task {task.id} (key: {key}) is a duplicate within the {debounce_trait.window} window. Skipping.",
                logging.INFO,
            )
            state_trait = next((t for t in task.traits if isinstance(t, StateTrait)), None)
            if state_trait:
                state_trait.outcome = TaskOutcome.SKIPPED
            return False, task

        return True, task


class DelayedSystem(BaseSystem):
    """System to delay task execution."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [DelayedTrait]

    @staticmethod
    @priority(140)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """Waits for the specified delay before proceeding with execution."""
        delayed_trait = next((t for t in task.traits if isinstance(t, DelayedTrait)), None)
        if not delayed_trait:
            return True, task

        await asyncio.sleep(delayed_trait.delay)
        return True, task


class EvaluatableSystem(BaseSystem):
    """System for post-execution result evaluation."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [EvaluatableTrait]

    @staticmethod
    async def _evaluate(evaluatable_trait: "EvaluatableTrait", data: Any) -> bool:
        """
        Runs the provided evaluator function against the task result.

        This method supports both synchronous and asynchronous evaluator functions.

        Args:
            data: The result of the task's action.

        Returns:
            `True` if the evaluation passes or if no evaluator is configured,
            `False` otherwise.
        """
        if not evaluatable_trait.evaluator:
            return True

        evaluation = evaluatable_trait.evaluator(data)
        if inspect.isawaitable(evaluation):
            return await evaluation
        return evaluation

    @staticmethod
    @priority(100)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """
        On success, evaluates the result. If the evaluation fails, it raises
        an `EvaluationFailureError` to trigger the standard failure-handling
        path in the worker.
        """
        evaluatable_trait = next(
            (t for t in task.traits if isinstance(t, EvaluatableTrait)), None
        )
        if not evaluatable_trait:
            return None

        if not await EvaluatableSystem._evaluate(evaluatable_trait, result):
            # Raise an exception to trigger the on_task_failure lifecycle.
            raise EvaluationFailureError(f"Evaluation failed for result: {result!r}")

        # If the evaluation is successful, do nothing.
        return None


class ExpirableSystem(BaseSystem):
    """System to handle task expiration."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [ExpirableTrait, StateTrait]

    @staticmethod
    def _is_expired(expirable_trait: "ExpirableTrait") -> bool:
        if not expirable_trait.expires_at:
            return False
        # utc_datetime is defined in wombat.multiprocessing.traits.models
        from wombat.multiprocessing.traits.models import utc_datetime

        return utc_datetime() >= expirable_trait.expires_at

    @staticmethod
    @priority(120)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """Hook to check for expiration before execution."""
        expirable_trait = next(
            (t for t in task.traits if isinstance(t, ExpirableTrait)), None
        )
        if not expirable_trait:
            return True, task

        if ExpirableSystem._is_expired(expirable_trait):
            worker.log(
                f"Task {getattr(task, 'id', 'N/A')} expired and was skipped.",
                logging.INFO,
            )
            state_trait = next((t for t in task.traits if isinstance(t, StateTrait)), None)
            if state_trait:
                state_trait.outcome = TaskOutcome.EXPIRED
            return False, task  # Prevent execution
        return True, task



class LoggableSystem(BaseSystem):
    """System to handle logging for tasks."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [LogCarrierTrait]

    # --- From LogCarrier ---
    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """Suppresses the result of this task from being yielded by the orchestrator."""
        return any(isinstance(t, LogCarrierTrait) for t in task.traits)

    @staticmethod
    @priority(500)
    def should_log_failure(task: "Task", worker: "Worker") -> bool:
        """Prevents logging a failure for this task to avoid logging cycles."""
        return not any(isinstance(t, LogCarrierTrait) for t in task.traits)

    @staticmethod
    @priority(500)
    def should_log_requeue(task: "Task") -> bool:
        """Prevents logging about requeued log tasks to avoid log noise."""
        return not any(isinstance(t, LogCarrierTrait) for t in task.traits)


class PinnedSystem(BaseSystem):
    """System to handle task pinning."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [PinnedTrait]

    @staticmethod
    @priority(500)
    def on_task_routed(task: "Task", workers: list["Worker"]) -> list["Worker"] | None:
        """Filters the list of workers to only the one matching the pinned name."""
        pinned_trait = next((t for t in task.traits if isinstance(t, PinnedTrait)), None)
        if not pinned_trait:
            return None  # No change to routing
        return [w for w in workers if w.identity.name == pinned_trait.worker_name]


class ProducesSystem(BaseSystem):
    """System that allows a task to dynamically produce new tasks from its result."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [ProducesTrait]

    @staticmethod
    def get_dependent_traits() -> list[Type[BaseTrait]]:
        """Declares that this system can add `GeneratedTrait`, `QueuedTrait`, and `TaggedTrait`."""
        return [GeneratedTrait, QueuedTrait, TaggedTrait]

    @staticmethod
    @priority(200)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """
        After the producer task succeeds, this hook checks if the result is one
        or more `Task` objects. If so, it requeues them for execution by the
        orchestrator.
        """
        produces_trait = next(
            (t for t in task.traits if isinstance(t, ProducesTrait)), None
        )
        if not produces_trait:
            return None

        tasks_to_requeue = []
        if isinstance(result, Task):
            tasks_to_requeue.append(result)
        elif isinstance(result, list) and all(isinstance(t, Task) for t in result):
            tasks_to_requeue.extend(result)

        if tasks_to_requeue:
            # Mark these tasks as generated and queued so they are counted correctly
            # and handled by the orchestrator's requeue listener.
            for new_task in tasks_to_requeue:
                new_task.add_trait(GeneratedTrait())
                new_task.add_trait(QueuedTrait())
                if produces_trait.tags:
                    new_task.add_trait(TaggedTrait(tags=produces_trait.tags))

            # Use asyncio.gather to requeue them concurrently.
            await asyncio.gather(
                *(
                    worker.requeue_task_locally(new_task)
                    for new_task in tasks_to_requeue
                )
            )

        return None

    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """
        Suppresses the result of the producer task from being yielded by the
        orchestrator, as its "result" is the creation of new tasks.
        """
        return any(isinstance(t, ProducesTrait) for t in task.traits)


class ConsumesSystem(BaseSystem):
    """System to handle the consumer side of a producer-consumer pattern."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [ConsumesTrait]

    @staticmethod
    async def _check_and_emit_consumers(
        orchestrator: "Orchestrator", triggered_by_tags: set[str]
    ):
        """Checks if any waiting consumers can be satisfied and emits them."""
        tasks_to_add = []
        for tag in triggered_by_tags:
            while True:
                if not orchestrator._waiting_consumers[tag]:
                    break

                consumer_task = orchestrator._waiting_consumers[tag][0]
                consumes_trait = next(
                    (t for t in consumer_task.traits if isinstance(t, ConsumesTrait)),
                    None,
                )

                if not consumes_trait:
                    orchestrator._waiting_consumers[tag].pop(0)
                    continue

                if len(orchestrator._tagged_results[tag]) >= consumes_trait.batch_size:
                    orchestrator._waiting_consumers[tag].pop(0)
                    results_batch = orchestrator._tagged_results[tag][
                        : consumes_trait.batch_size
                    ]
                    orchestrator._tagged_results[tag] = orchestrator._tagged_results[
                        tag
                    ][consumes_trait.batch_size :]
                    consumer_task.kwargs["consumed_results"] = results_batch
                    tasks_to_add.append(consumer_task)
                else:
                    break

        if tasks_to_add:
            # Re-submit the consumers for execution now that they have their results.
            await orchestrator.add_tasks(tasks_to_add)

    @staticmethod
    @priority(500)
    async def on_task_submitted(task: "Task", orchestrator: "Orchestrator") -> bool:
        """
        Intercepts consumer tasks, holding them until their results are ready.
        Returns True if the task was handled, False otherwise.
        """
        consumes_trait = next(
            (t for t in task.traits if isinstance(t, ConsumesTrait)), None
        )
        # A consumer task is only a "waiting" consumer if it has not yet received
        # its consumed results. Once results are injected, it's a normal task.
        if consumes_trait and "consumed_results" not in task.kwargs:
            primary_tag = consumes_trait.tags[0]
            orchestrator._waiting_consumers[primary_tag].append(task)

            # Check if this new consumer can already be satisfied.
            await ConsumesSystem._check_and_emit_consumers(
                orchestrator, {primary_tag}
            )
            return True  # The task is handled (held) by this system.
        return False

    @staticmethod
    @priority(500)
    async def on_result_received(task: "Task", orchestrator: "Orchestrator"):
        """
        Checks if a result has a tag and, if so, adds it to the collected
        results and checks if any consumers can be emitted.
        """
        tagged_trait = next(
            (t for t in task.traits if isinstance(t, TaggedTrait)), None
        )
        if tagged_trait and tagged_trait.tags:
            affected_tags = set()
            for tag in tagged_trait.tags:
                orchestrator._tagged_results[tag].append(task.result)
                affected_tags.add(tag)

            if affected_tags:
                await ConsumesSystem._check_and_emit_consumers(
                    orchestrator, affected_tags
                )

    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """
        Suppresses the result of any tagged task, as its result is intended
        to be collected by a consumer, not yielded to the end user.
        """
        return any(isinstance(t, TaggedTrait) for t in task.traits)


class RateLimitSystem(BaseSystem):
    """System that limits the execution frequency of tasks within a group."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [RateLimitTrait]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        if "rate_limit_cache" not in builder.props:
            from wombat.multiprocessing.ipc.shared_memory_hash_map import (
                SharedMemoryHashMap,
            )
            from wombat.multiprocessing.traits.models import Prop

            context = builder.context
            shm_map = SharedMemoryHashMap.create(context=context, purpose="rate_limit")
            builder.register_resource_for_cleanup(shm_map)
            builder.props["rate_limit_cache"] = Prop(
                initializer=shm_map,
                use_context_manager=False,
            )

    @staticmethod
    @priority(130)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        rate_limit_trait = next(
            (t for t in task.traits if isinstance(t, RateLimitTrait)), None
        )
        if not rate_limit_trait:
            return True, task

        rate_limit_cache = worker.props["rate_limit_cache"].instance

        def _check_rate_limit_sync() -> float:
            """
            Checks the rate limit and updates timestamps atomically under a lock.
            Returns the required wait time in seconds.
            """
            with rate_limit_cache.lock:
                now = worker.get_time()
                group_timestamps = rate_limit_cache.get(rate_limit_trait.group, [])

                # Prune old timestamps
                period_seconds = rate_limit_trait.period.total_seconds()
                valid_timestamps = [
                    ts for ts in group_timestamps if now - ts < period_seconds
                ]

                if len(valid_timestamps) < rate_limit_trait.limit:
                    # We are within the limit, add our timestamp and proceed.
                    valid_timestamps.append(now)
                    rate_limit_cache[rate_limit_trait.group] = valid_timestamps
                    return 0.0  # No wait time needed.

                # We are at the limit, calculate wait time.
                oldest_ts = valid_timestamps[0]
                return (oldest_ts + period_seconds) - now

        while True:
            wait_time = await worker.runtime_state.loop.run_in_executor(
                None, _check_rate_limit_sync
            )

            if wait_time <= 0:
                return True, task

            worker.log(
                f"Rate limit for group '{rate_limit_trait.group}' reached. Waiting for {wait_time:.2f}s.",
                logging.DEBUG,
            )
            await asyncio.sleep(wait_time)


class RequiresPropsSystem(BaseSystem):
    """System to inject props required by traits into task kwargs."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [RequiresPropsTrait]

    @staticmethod
    @priority(500)
    def before_prepare_arguments(
        task: "Task", worker: "Worker", kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Injects props into task kwargs based on trait requirements."""
        for trait in task.traits:
            props_to_add = {}
            if getattr(trait, "include_all_props", False):
                props_to_add = worker.props
            elif getattr(trait, "requires_props", None):
                props_to_add = {
                    k: v for k, v in worker.props.items() if k in trait.requires_props
                }

            if props_to_add:
                if "props" not in kwargs:
                    kwargs["props"] = {}
                # Do not overwrite existing props if they are already present.
                for key, value in props_to_add.items():
                    if key not in kwargs["props"]:
                        kwargs["props"][key] = value
        return kwargs


def linear_backoff(trait: "RetryableTrait") -> float:
    """Linear backoff function. Delay increases linearly with each retry."""
    return min(trait.max_delay, trait.initial_delay * trait.tries)


def exponential_backoff(trait: "RetryableTrait") -> float:
    """Exponential backoff function. Delay increases exponentially with each retry until max_delay is reached."""
    # The number of retries will be 1 for the first retry, 2 for the second, etc.
    # The exponent should be `retries - 1` to get a multiplier of 1x for the first retry.
    return min(
        trait.max_delay,
        trait.initial_delay * (trait.backoff_multiplier ** (trait.tries - 1)),
    )


class RetryableSystem(BaseSystem):
    """System that handles retry logic for tasks."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [RetryableTrait, StateTrait]

    @staticmethod
    def _backoff(retry_trait: "RetryableTrait") -> float:
        """Calculates the backoff delay for the next retry attempt."""
        if retry_trait.backoff_strategy == "linear":
            return linear_backoff(retry_trait)
        elif retry_trait.backoff_strategy == "custom" and retry_trait.backoff_function:
            return retry_trait.backoff_function(retry_trait)

        return exponential_backoff(retry_trait)

    @staticmethod
    @priority(100)
    async def on_action_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """Schedules a retry if the task has the RetryableTrait and tries remain."""
        retry_trait = next((t for t in task.traits if isinstance(t, RetryableTrait)), None)
        if not retry_trait:
            return

        state_trait = next((t for t in task.traits if isinstance(t, StateTrait)), None)
        # A task that was cancelled (e.g., by timeout) does not trigger this hook,
        # so we don't need to check for it.

        if retry_trait.tries < retry_trait.max_tries:
            retry_trait.tries += 1

            # Manually increment the retries counter.
            accounting_trait = next(
                (t for t in task.traits if isinstance(t, AccountingTrait)), None
            )
            if accounting_trait:
                await AccountingSystem._increment_count(
                    worker, accounting_trait, "retries"
                )

            # Update traits for the new attempt.
            task.replace_trait(retry_trait)
            if state_trait:
                state_trait.state = TaskState.RETRYING

            backoff_delay = float(RetryableSystem._backoff(retry_trait))
            worker.log(
                f"Task {task.id} failed, scheduling retry {retry_trait.tries}/{retry_trait.max_tries} in {backoff_delay:.2f}s.",
                logging.INFO,
            )
            retry_at = worker.get_time() + backoff_delay
            await worker.add_task_for_retry(retry_at, task)
        else:
            # All retries have been exhausted. Do nothing. The worker's execute_task
            # loop will mark the task as Failed.
            worker.log(
                f"Task {task.id} failed after exhausting all {retry_trait.max_tries} retries.",
                logging.WARNING,
            )


class TimeoutSystem(BaseSystem):
    """System that adds a timeout to a task's execution."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [TimeoutTrait]

    @staticmethod
    @priority(500)
    async def around_task_execution(
        task: "Task",
        worker: "Worker",
        execution_callable: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Wraps the task execution with asyncio.wait_for."""
        timeout_trait = next((t for t in task.traits if isinstance(t, TimeoutTrait)), None)
        if not timeout_trait:
            return await execution_callable()

        try:
            return await asyncio.wait_for(execution_callable(), timeout_trait.timeout)
        except asyncio.TimeoutError:
            # Re-raise as CancelledError to ensure the worker's cancellation
            # logic is triggered, which correctly sets the task outcome to
            # CANCELLED.
            raise asyncio.CancelledError
