# File: src/wombat/multiprocessing/worker.py
"""
Worker process for wombat.
"""

from __future__ import annotations

import asyncio
import functools
import heapq
import importlib
import inspect
import logging
import os
import sys
import time
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import AsyncExitStack
from enum import Enum
from traceback import format_exc
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import cloudpickle as pickle
import msgpack
from pydantic import UUID4, BaseModel, ConfigDict, Field

from wombat.multiprocessing.errors import (
    ExecutionSkippedError,
)
from wombat.multiprocessing.ipc.buffer import _HEADER, BufferState
from wombat.multiprocessing.ipc.utilities import (
    default_encoder,
    is_async_context_manager,
    is_sync_context_manager,
    queue_get_async,
)
from wombat.multiprocessing.logging import log_task
from wombat.multiprocessing.traits.state import StateTrait, TaskOutcome, TaskState
from wombat.multiprocessing.traits.models import (
    Prop,
    PropConfig,
    Task,
    TaskResult,
)

if TYPE_CHECKING:
    from multiprocessing.sharedctypes import Synchronized

    from .queues import TraitQueue


class ProfilingConfig(BaseModel):
    """Configuration for profiling workers."""

    enabled: bool = False
    dir: Optional[str] = None
    to_console: bool = True


class WorkerIdentityConfig(BaseModel):
    name: Optional[str] = None
    id: Optional[UUID4] = None
    progress_bar_id: Optional[int] = None


class WorkerPerformanceConfig(BaseModel):
    max_concurrent_tasks: Optional[int] = None
    thread_pool_size: Optional[int] = None
    loop_timeout: float = 0.1


class WorkerIPCConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    context: Optional[Any] = None
    control_queues: Optional[Dict[str, "TraitQueue"]] = None
    queues: Optional[Dict[str, "TraitQueue"]] = None
    batch_buffer: Any | None = None
    status: Optional["Synchronized"] = None


class WorkerLoggingConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    enabled: bool = True
    shutdown_event: Optional[Any] = None


class WorkerConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
    )

    # Declarative fields
    actions: dict[str, Any] = Field(default_factory=dict)
    props: dict[str, Union[Prop, PropConfig]] = Field(default_factory=dict)
    trait_registry: dict[str, Any] = Field(default_factory=dict)
    system_registry: dict[str, Any] = Field(default_factory=dict)

    # Grouped configurations
    identity: WorkerIdentityConfig = Field(default_factory=WorkerIdentityConfig)
    performance: WorkerPerformanceConfig = Field(
        default_factory=WorkerPerformanceConfig
    )
    ipc: WorkerIPCConfig = Field(default_factory=WorkerIPCConfig)
    logging: WorkerLoggingConfig = Field(default_factory=WorkerLoggingConfig)
    profiling: ProfilingConfig = Field(default_factory=ProfilingConfig)


class WorkerCaches(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    filtered_props: dict = Field(default_factory=dict)
    actions: dict[str, tuple[Callable, bool] | None] = Field(default_factory=dict)
    task_capabilities: dict = Field(default_factory=dict)
    action_props: dict = Field(default_factory=dict)
    channel_queues: dict[str, "TraitQueue"] = Field(default_factory=dict)


class WorkerRuntimeState(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    retry_heap: list[tuple[float, "Task"]] = Field(default_factory=list)
    retry_event: Optional[asyncio.Event] = None
    semaphore: Optional[asyncio.Semaphore] = None
    loop: Optional[asyncio.AbstractEventLoop] = None
    running_tasks: set[asyncio.Task] = Field(default_factory=set)
    background_tasks: set[asyncio.Task] = Field(default_factory=set)
    profiler: Optional[Any] = None
    pending_account_updates: dict = Field(default_factory=lambda: defaultdict(int))
    pending_account_updates_lock: Optional[asyncio.Lock] = None


class WorkerStatus(Enum):
    CREATED = 0
    RUNNING = 1
    SLEEPING = 2
    STOPPED = 3
    PAUSED = 4


class Worker:
    def __getstate__(self):
        state = self.__dict__.copy()
        # The process object is not serializable and should not be transferred
        # to the worker process. It's only managed by the Orchestrator.
        state["_process"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __init__(
        self,
        config: WorkerConfig,
        get_time: Callable[[], float] = time.monotonic,
    ) -> None:
        # Store config sub-models directly.
        self.identity = config.identity
        self.performance = config.performance
        self.ipc = config.ipc
        self.logging = config.logging
        self.profiling = config.profiling
        self.props = config.props
        self.system_registry = config.system_registry

        self.get_time = get_time
        self.start_time = get_time()
        self.log(f"Worker {config.identity.name} __init__ in pid={os.getpid()}", logging.DEBUG)

        # Caches and runtime state
        self.caches = WorkerCaches()
        self.runtime_state = WorkerRuntimeState()

        # Pack the configuration here, just before creating the process.
        self.packed_actions = msgpack.packb(
            {k: v.action for k, v in config.actions.items()},
            default=default_encoder,
            use_bin_type=True,
        )
        self.packed_trait_registry = msgpack.packb(
            config.trait_registry, default=default_encoder, use_bin_type=True
        )

        try:
            self._process = self.ipc.context.Process(
                target=self.start_event_loop,
                name=self.identity.name,
            )
            if not self._process.is_alive():
                self.log(
                    f"Worker {self.identity.name} prepared for start", logging.DEBUG
                )
        except Exception:
            self.log(
                f"Worker {self.identity.name} failed to initialize: \n{format_exc()}",
                logging.ERROR,
            )

    def add_background_task(self, coro: asyncio.Coroutine) -> None:
        """
        Creates and tracks a background task on the worker's event loop.

        These tasks are managed in a separate set and are automatically cleaned
        up when they complete. They are all cancelled during worker shutdown.
        """
        task = self.runtime_state.loop.create_task(coro)
        self.runtime_state.background_tasks.add(task)
        task.add_done_callback(self.runtime_state.background_tasks.discard)

    async def _send_task_result(self, task: "Task") -> None:
        """
        Creates a `TaskResult` and puts it on the result queue.

        This runs the blocking `put` operation in a thread pool executor to avoid
        stalling the worker's event loop.
        """
        result_queue = self.ipc.queues.get("result")
        if not result_queue:
            return

        task_result = TaskResult(
            task_id=task.id,
            action=task.action,
            result=task.result,
            metadata=task.metadata,
            traits=[t.model_dump(mode="python") for t in task.traits],
        )

        if self.runtime_state.loop and self.runtime_state.loop.is_running():
            await self.runtime_state.loop.run_in_executor(
                None, result_queue.put_blocking, task_result
            )

    async def add_task_for_retry(self, retry_at: float, task: Task) -> None:
        """
        Adds a task to the in-memory retry heap and signals the scheduler.

        The retry scheduler is a background task that sleeps until the next
        scheduled retry time. This method ensures the scheduler wakes up if a
        new task is added that is scheduled to run sooner than the current
        next task.
        """
        heapq.heappush(self.runtime_state.retry_heap, (retry_at, task))
        if self.runtime_state.retry_event:
            self.runtime_state.retry_event.set()

    async def increment_local_account_count(self, key: str, value: int = 1):
        """Adds a count to a temporary local dictionary, to be flushed periodically."""
        async with self.runtime_state.pending_account_updates_lock:
            self.runtime_state.pending_account_updates[key] += value

    # ---------------------------
    # Logging helpers
    # ---------------------------

    def log(self, message: str, level: int) -> None:
        """
        Sends a log message to the orchestrator via a dedicated logging task.

        This method creates a `log_task` and puts it on the central requeue
        queue. The orchestrator will then dispatch this task to a dedicated
        log worker, ensuring that logging I/O does not block task workers.
        """
        if (
            not self.logging.enabled
            or (self.logging.shutdown_event and self.logging.shutdown_event.is_set())
        ):
            return

        try:
            logging_config_store_prop = self.props.get("logging_config_store")
            if logging_config_store_prop and logging_config_store_prop.instance:
                # Default to 0 (log everything) if the key isn't in the map.
                min_level = logging_config_store_prop.instance.get("level", 0)
                if level < min_level:
                    return  # Filter on the sender side
        except Exception:
            # Fallback to sending the log if any error occurs reading shared state.
            pass

        requeue_queue = self.ipc.queues.get("requeue")
        if requeue_queue:
            # Log tasks are sent to the central requeue queue to be discovered
            # and accounted for by the orchestrator. This is a blocking call
            # to prevent log loss if the queue is full.
            requeue_queue.put_blocking(
                log_task(
                    message=f"worker={self.identity.name} | {message}",
                    level=level,
                )
            )

    async def _retry_scheduler_loop(self):
        """A background task that manages and requeues retrying tasks from a min-heap."""
        self.log("Retry scheduler started.", logging.DEBUG)
        while True:
            try:
                if not self.runtime_state.retry_heap:
                    if self.runtime_state.retry_event:
                        self.runtime_state.retry_event.clear()
                        await self.runtime_state.retry_event.wait()
                    else:  # Event not initialized, wait briefly and retry
                        await asyncio.sleep(0.1)
                        continue

                # Now we have items, or the event was set
                if not self.runtime_state.retry_heap:
                    continue

                next_retry_time = self.runtime_state.retry_heap[0][0]
                now = self.get_time()
                sleep_duration = max(0, next_retry_time - now)

                # Wait for the sleep duration OR for a new item to be added.
                try:
                    if self.runtime_state.retry_event:
                        self.runtime_state.retry_event.clear()
                        await asyncio.wait_for(
                            self.runtime_state.retry_event.wait(),
                            timeout=sleep_duration,
                        )
                        # If we get here, a new item was added, so we loop to re-evaluate sleep time
                        continue
                except asyncio.TimeoutError:
                    # Sleep finished, time to process the task
                    pass

                # Process all tasks that are due
                while (
                    self.runtime_state.retry_heap
                    and self.runtime_state.retry_heap[0][0] <= self.get_time()
                ):
                    _retry_at, task = heapq.heappop(self.runtime_state.retry_heap)
                    await self.requeue_task_locally(task)

            except asyncio.CancelledError:
                self.log("Retry scheduler cancelled.", logging.INFO)
                break
            except IndexError:
                # Heap became empty, loop will wait on event
                continue
            except Exception as e:
                self.log(
                    f"Error in retry scheduler: {e}\n{format_exc()}", logging.ERROR
                )
                # Avoid busy-looping on persistent errors
                await asyncio.sleep(1)

    async def _flush_accounting_updates_loop(self):
        """A background task that periodically flushes batched accounting updates."""

        def _sync_bulk_update(accounting_store, worker_name, updates):
            """Synchronous helper to perform a bulk update under a single lock."""
            if not updates:
                return
            with accounting_store.lock:
                # Update worker counts
                worker_counts = accounting_store.get(worker_name, {})
                for key, value in updates.items():
                    worker_counts[key] = worker_counts.get(key, 0) + value
                accounting_store[worker_name] = worker_counts

                # Update total counts
                total_counts = accounting_store.get("Total", {})
                for key, value in updates.items():
                    total_counts[key] = total_counts.get(key, 0) + value
                accounting_store["Total"] = total_counts

        while True:
            try:
                await asyncio.sleep(0.05)  # Flush every 50ms

                async with self.runtime_state.pending_account_updates_lock:
                    if not self.runtime_state.pending_account_updates:
                        continue
                    updates_to_flush = self.runtime_state.pending_account_updates
                    self.runtime_state.pending_account_updates = defaultdict(int)

                if updates_to_flush:
                    await self.runtime_state.loop.run_in_executor(
                        None,
                        _sync_bulk_update,
                        self.props["accounting_store"].instance,
                        self.identity.name,
                        updates_to_flush,
                    )
            except asyncio.CancelledError:
                self.log("Accounting flush loop cancelled.", logging.INFO)
                break
            except Exception as e:
                self.log(
                    f"Error in accounting flush loop: {e}\n{format_exc()}",
                    logging.ERROR,
                )
                await asyncio.sleep(1)

    # ---------------
    # Process control
    # ---------------

    def start(self) -> None:
        """Starts the worker's underlying multiprocessing.Process."""
        if not self._process.is_alive():
            self.log(
                f"Orchestrator is starting worker process in pid={os.getpid()}",
                logging.DEBUG,
            )
            self.log(f"Starting process for {self.identity.name}", logging.DEBUG)
            self._process.start()
            with self.ipc.status.get_lock():
                self.ipc.status.value = WorkerStatus.RUNNING.value

    # -------------
    # Task execution
    # -------------

    async def requeue_task_locally(self, task: Task) -> None:
        """
        Puts a task on the central requeue queue for the orchestrator to process.

        This method is blocking and will wait if the queue is full, ensuring
        that dynamically produced tasks or retries are never lost. It is used
        for tasks that need to be retried or for dynamically produced tasks.
        The orchestrator's requeue listener will pick up the task and
        redistribute it according to its traits.
        """
        requeue_queue = self.ipc.queues.get("requeue")
        if requeue_queue:
            # Use the new blocking put method. This ensures that if the requeue
            # queue is full, the worker will wait for space instead of silently
            # dropping the task. This correctly uses the thread pool for a
            # potentially blocking operation.
            await self.runtime_state.loop.run_in_executor(
                None, requeue_queue.put_blocking, task
            )

    async def _run_task_action(self, func, is_async, args, kwargs) -> Any:
        """
        A helper to invoke the task action, handling async/sync and profiling.

        Synchronous functions are run in a `ThreadPoolExecutor` to avoid
        blocking the worker's main event loop.
        """
        if is_async:
            if self.runtime_state.profiler:
                self.runtime_state.profiler.enable_by_count()
                try:
                    return await func(self, *args, **kwargs)
                finally:
                    self.runtime_state.profiler.disable_by_count()
            return await func(self, *args, **kwargs)

        # For all sync functions, run in an executor to avoid blocking the event loop.
        def action_callable():
            return func(self, *args, **kwargs)

        if self.runtime_state.profiler:
            return await self.runtime_state.loop.run_in_executor(
                None, self.runtime_state.profiler(action_callable)
            )
        return await self.runtime_state.loop.run_in_executor(None, action_callable)

    async def _execute_with_hooks(
        self, *, task: Task, func: Callable, props: dict[str, Prop], is_async: bool
    ) -> Any:
        # 1. Run pre-flight hooks from registered systems.
        if "before_task_execution" in self.system_registry:
            for system_func in self.system_registry["before_task_execution"]:
                should_run, task = await system_func(task, self)
                if not should_run:
                    raise ExecutionSkippedError()

        # 2. Prepare kwargs by letting systems modify them.
        args = task.args.copy() if hasattr(task, "args") else []
        kwargs = task.kwargs.copy() if hasattr(task, "kwargs") else {}
        if "before_prepare_arguments" in self.system_registry:
            for system_func in self.system_registry["before_prepare_arguments"]:
                kwargs = system_func(task, self, kwargs)

        # 3. Run the actual task action.
        result = await self._run_task_action(func, is_async, args, kwargs)
        return result

    async def execute_task(
        self,
        *,
        task: Task,
        func: Callable,
        props: dict[str, Prop],
        is_async: bool,
    ) -> None:
        """
        Executes a single task, running it through an explicit state machine.
        """
        self.log(f"Executing task {task.id} ({task.action})", logging.DEBUG)

        state_trait = next((t for t in task.traits if isinstance(t, StateTrait)), None)
        if not state_trait:
            self.log(f"StateTrait not found on task {task.id}", logging.ERROR)
            return

        result_data = None
        last_exception = None

        try:
            state_trait.state = TaskState.RUNNING

            execution_callable = functools.partial(
                self._execute_with_hooks,
                task=task,
                func=func,
                props=props,
                is_async=is_async,
            )
            if "around_task_execution" in self.system_registry:
                for system_func in reversed(
                    self.system_registry["around_task_execution"]
                ):
                    execution_callable = functools.partial(
                        system_func, task, self, execution_callable
                    )

            result_data = await execution_callable()

            # A task is only successful if all `on_task_success` hooks also succeed.
            if "on_task_success" in self.system_registry:
                for system_func in self.system_registry["on_task_success"]:
                    await system_func(task, self, result_data)

            state_trait.outcome = TaskOutcome.SUCCESS
            task.result = result_data

        except ExecutionSkippedError as e:
            # A pre-flight hook has decided to skip this task. The hook is
            # responsible for setting the final outcome on the StateTrait in a
            # future commit. For now, we just record the reason.
            state_trait.reason = str(e) or "Execution skipped by a pre-flight hook"

        except asyncio.CancelledError:
            state_trait.outcome = TaskOutcome.CANCELLED
            state_trait.reason = "Task was cancelled."
            self.log(f"Task {task.id}: {state_trait.reason}", logging.WARNING)

        except Exception as e:
            last_exception = format_exc()

            # New hook for recoverable failures. Systems like RetryableSystem will
            # hook here in a future commit.
            if "on_action_failure" in self.system_registry:
                for system_func in self.system_registry["on_action_failure"]:
                    await system_func(task, self, e)

            # In a future commit, a system could set the state to RETRYING.
            # If not, the failure is terminal for this attempt.
            if state_trait.state != TaskState.RETRYING:
                state_trait.outcome = TaskOutcome.FAILURE
                state_trait.reason = last_exception

                should_log = True
                if "should_log_failure" in self.system_registry:
                    results = [
                        system_func(task, self)
                        for system_func in self.system_registry["should_log_failure"]
                    ]
                    if False in results:
                        should_log = False
                if should_log:
                    self.log(
                        message=f"Error executing task {task.id}: {last_exception}",
                        level=logging.ERROR,
                    )
        finally:
            self.log(f"Finished task {task.id} ({task.action})", logging.DEBUG)
            # If the state is not RETRYING, it's a terminal state for this execution.
            if state_trait.state != TaskState.RETRYING:
                state_trait.state = TaskState.COMPLETE

                if state_trait.outcome in (
                    TaskOutcome.FAILURE,
                    TaskOutcome.CANCELLED,
                ):
                    self._prepare_failure_result(task, state_trait.reason, result_data)
                elif state_trait.outcome == TaskOutcome.SUCCESS:
                    # `task.result` was already set.
                    pass
                else:
                    # This case covers when a pre-flight hook skips a task without
                    # setting an explicit outcome (e.g., Debounce, Breaker).
                    # We will treat it as a failure for result formatting.
                    self._prepare_failure_result(task, state_trait.reason, result_data)

                # New hook for actions on any terminal state (e.g., accounting).
                if "on_terminal_state" in self.system_registry:
                    for system_func in self.system_registry["on_terminal_state"]:
                        await system_func(task, self)

                await self._send_task_result(task)

    def _prepare_failure_result(
        self, task: Task, exc_info: Any, result_data: Any = None
    ):
        """Sets failure result and increments counter."""
        # Truncate large exception messages to avoid oversized TaskResult payloads.
        exc_str = str(exc_info)
        if len(exc_str) > 4096:
            exc_info = exc_str[:4096] + "... (truncated)"
        task.result = [exc_info, result_data]

    async def _fail_task_on_shutdown(self, task: Task):
        """Marks a task as failed due to shutdown and sends a terminal result."""
        self.log(f"Task {task.id} failed due to worker shutdown.", logging.WARNING)
        exception_str = "Task failed due to worker shutdown."

        state_trait = next((t for t in task.traits if isinstance(t, StateTrait)), None)
        if state_trait:
            state_trait.state = TaskState.COMPLETE
            state_trait.outcome = TaskOutcome.FAILURE
            state_trait.reason = exception_str

        self._prepare_failure_result(task, exception_str)

        if "on_terminal_state" in self.system_registry:
            for system_func in self.system_registry["on_terminal_state"]:
                await system_func(task, self)

        await self._send_task_result(task)

    async def _process_and_execute_task(self, task: Task, actions: dict[str, Callable]):
        """Helper coroutine to wrap the execution of a single task."""
        try:
            # Run `on_task_received` systems.
            if "on_task_received" in self.system_registry:
                for system_func in self.system_registry["on_task_received"]:
                    await system_func(task, self)

            if task.action not in self.caches.actions:
                action_obj = actions.get(task.action)
                if action_obj:
                    func = getattr(action_obj, "action", action_obj)
                    is_async = inspect.iscoroutinefunction(func)
                    self.caches.actions[task.action] = (func, is_async)
                else:
                    self.caches.actions[task.action] = None

            cached_action = self.caches.actions[task.action]
            if cached_action:
                func, is_async = cached_action
                await self.execute_task(
                    task=task,
                    func=func,
                    props=self.props,
                    is_async=is_async,
                )
            else:
                self.log(
                    f"No action '{task.action}' found for task {task.id}",
                    logging.ERROR,
                )
        except asyncio.CancelledError:
            self.log(f"Task {task.id} was cancelled during shutdown.", logging.INFO)
            # The `finally` block in `execute_task` is now solely responsible for
            # sending the result for a cancelled task. Do not send another one here.
            raise  # Re-raise to signal cancellation
        except Exception as e:
            self.log(
                f"Unhandled exception processing task {task.id}: {e}", logging.ERROR
            )
            await self._fail_task_on_shutdown(task)
        finally:
            pass

    def _run_with_profiling(self, actions: dict[str, Callable], props: dict[str, Any]):
        """Runs the worker's main loop with line-profiler enabled."""
        import line_profiler

        self.runtime_state.profiler = line_profiler.LineProfiler()

        # Profile the main run method and all task actions.
        self.runtime_state.profiler.add_function(self.run)
        self.runtime_state.profiler.add_function(self._batch_processing_loop)
        self.runtime_state.profiler.add_function(self._process_and_execute_task)
        for action_obj in actions.values():
            func = getattr(action_obj, "action", action_obj)
            self.runtime_state.profiler.add_function(func)

        try:
            self.runtime_state.profiler.enable_by_count()
            try:
                self.runtime_state.loop.run_until_complete(
                    self.run(actions=actions, props=props)
                )
            finally:
                self.runtime_state.profiler.disable_by_count()
        finally:
            if self.profiling.to_console:
                self.runtime_state.profiler.print_stats()

            if self.profiling.dir:
                # Dump full stats for the worker
                worker_profile_path = os.path.join(
                    self.profiling.dir, f"{self.identity.name}.prof"
                )
                with open(worker_profile_path, "w") as f:
                    self.runtime_state.profiler.print_stats(stream=f)

                # Dump stats for each profiled function (task actions)
                stats = self.runtime_state.profiler.get_stats()
                for (filename, lineno, func_name), timings in stats.timings.items():
                    if func_name != "run":  # Exclude the worker's own run loop
                        task_profile_path = os.path.join(
                            self.profiling.dir, f"{func_name}.prof"
                        )
                        with open(task_profile_path, "w") as f:
                            line_profiler.show_func(
                                filename,
                                lineno,
                                func_name,
                                stats.timings,
                                stats.unit,
                                stream=f,
                            )
            self.runtime_state.profiler.disable()
            self.runtime_state.profiler = None

    # ----------------------
    # Event loop & run logic
    # ----------------------

    def start_event_loop(self) -> None:
        """
        The main entry point for the worker process.

        This method sets up the asyncio event loop (uvloop), deserializes the
        actions and trait registry, initializes the retry scheduler, and starts
        the main `run` coroutine.
        """
        self.log(f"{self.identity.name} starting event loop.", logging.DEBUG)
        import uvloop  # noqa: PLC0415, want to retain the ability to support custom loops

        self.trait_registry = {}
        if self.packed_trait_registry:
            unpacked_map = msgpack.unpackb(self.packed_trait_registry, raw=False)
            for name, val in unpacked_map.items():
                if isinstance(val, dict) and val.get("__pickle__"):
                    self.trait_registry[name] = pickle.loads(val["data"])

        if self.profiling.enabled:
            # Suppress intermittent "Exception ignored" errors from line-profiler during shutdown
            # by redirecting the stderr file descriptor to /dev/null. This is more robust
            # than replacing sys.stderr, as it captures low-level writes.
            try:
                devnull_fd = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull_fd, sys.stderr.fileno())
                os.close(devnull_fd)
            except (OSError, AttributeError):
                # In some test environments (like pytest-forked), sys.stderr may not have a fileno.
                # In such cases, the redirection can be skipped.
                pass

        unpacked_actions = msgpack.unpackb(self.packed_actions, raw=False)
        actions = {}
        for k, v in unpacked_actions.items():
            if isinstance(v, str):
                try:
                    module_name, func_name = v.rsplit(".", 1)
                    module = importlib.import_module(module_name)
                    actions[k] = getattr(module, func_name)
                except (ValueError, ImportError, AttributeError):
                    actions[k] = (
                        v  # Not a function string, or can't import, leave as is
                    )
            elif isinstance(v, dict) and v.get("__pickle__"):
                actions[k] = pickle.loads(v["data"])
            else:
                actions[k] = v
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.runtime_state.loop = asyncio.new_event_loop()
        self.runtime_state.loop.set_default_executor(
            ThreadPoolExecutor(max_workers=self.performance.thread_pool_size)
        )
        self.runtime_state.retry_event = asyncio.Event()
        self.runtime_state.pending_account_updates_lock = asyncio.Lock()
        if (
            self.performance.max_concurrent_tasks is not None
            and self.performance.max_concurrent_tasks > 0
        ):
            self.runtime_state.semaphore = asyncio.Semaphore(
                self.performance.max_concurrent_tasks
            )
        asyncio.set_event_loop(self.runtime_state.loop)
        try:
            self.log(f"Entering start_event_loop in pid={os.getpid()}", logging.DEBUG)
            self.log(
                f"Starting event loop for {self.identity.name}:{os.getpid()}",
                logging.CRITICAL,
            )
            self.add_background_task(self._retry_scheduler_loop())
            self.add_background_task(self._flush_accounting_updates_loop())
            if self.profiling.enabled:
                self._run_with_profiling(actions, self.props)
            else:
                self.runtime_state.loop.run_until_complete(
                    self.run(actions=actions, props=self.props)
                )
        finally:
            self.log(f"Event loop shutting down in pid={os.getpid()}", logging.DEBUG)
            self.runtime_state.loop.run_until_complete(
                self.runtime_state.loop.shutdown_asyncgens()
            )
            self.runtime_state.loop.close()
            self.log(f"{self.identity.name} event loop closed.", logging.DEBUG)
            logging.shutdown()

    async def initialize_prop(
        self, *, props: dict[str, Prop], prop_name: str, reinitialize: bool = False
    ) -> Exception | None:
        """
        Initializes a single prop by calling its initializer.

        Handles both sync and async initializers and context managers. The
        resolved prop instance is stored back on the `Prop` object for the
        lifetime of the worker.

        Returns:
            An exception if initialization fails, otherwise None.
        """
        try:
            prop = props[prop_name]
            initializer = prop.initializer
            resolved_value = prop.instance if not reinitialize else None
            exit_stack = prop.exit_stack if not reinitialize else AsyncExitStack()
            if exit_stack is None and prop.use_context_manager:
                exit_stack = AsyncExitStack()
            if resolved_value is None:
                # Differentiate between a callable proxy object and a true initializer function.
                # A true initializer is a function, method, or partial that should be executed.
                # A proxy object should be used as-is, even if it's callable.
                is_proxy = hasattr(initializer, "__class__") and "Proxy" in getattr(
                    initializer.__class__, "__name__", ""
                )
                is_initializer_callable = callable(initializer) and not is_proxy

                if asyncio.iscoroutinefunction(initializer):
                    resolved_value = await initializer(**prop.init_kwargs)
                elif is_initializer_callable:
                    # Run sync initializer in the event loop's default executor.
                    resolved_value = await self.runtime_state.loop.run_in_executor(
                        None, functools.partial(initializer, **prop.init_kwargs)
                    )
                else:
                    resolved_value = initializer

            if prop.use_context_manager and resolved_value:
                prop_is_async_cm = is_async_context_manager(resolved_value)
                prop_is_sync_cm = (
                    is_sync_context_manager(resolved_value)
                    if not prop_is_async_cm
                    else False
                )
                if prop_is_async_cm:
                    resolved_value = await exit_stack.enter_async_context(resolved_value)
                elif prop_is_sync_cm:
                    resolved_value = exit_stack.enter_context(resolved_value)
            # Modify the existing Prop object in-place to ensure the change is persistent
            # for the lifetime of the worker, instead of creating a new object.
            prop.instance = resolved_value
            prop.exit_stack = exit_stack
        except Exception as e:
            self.log(
                f"Worker {self.identity.name} failed to initialize prop {prop_name}: {e}\n{format_exc()}",
                logging.ERROR,
            )
            return e

    async def _initialize_all_props(
        self, initialization_complete: asyncio.Event, actions: dict[str, Callable]
    ):
        """Initializes all props and sets an event upon completion."""
        self.log("Initializing all props.", logging.DEBUG)
        try:
            to_gather = [
                self.initialize_prop(props=self.props, prop_name=prop_name)
                for prop_name in self.props
            ]
            results = await asyncio.gather(*to_gather)
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                # Re-raise the first exception to terminate the worker initialization.
                raise exceptions[0]

            self.log("Props initialized.", logging.DEBUG)
            if "on_worker_startup" in self.system_registry:
                for system_func in self.system_registry["on_worker_startup"]:
                    await system_func(self)
            self.log(
                f"Worker {self.identity.name} initialization complete.", logging.INFO
            )
            initialization_complete.set()
        except asyncio.CancelledError:
            self.log(
                f"Worker {self.identity.name} initialization cancelled.", logging.INFO
            )
            raise
        except Exception as e:
            self.log(
                f"Worker {self.identity.name} failed during prop initialization: {e}",
                logging.CRITICAL,
            )
            # Re-raise to ensure the init_task reflects the failure.
            raise

    def _set_sleeping_if_idle_sync(self):
        if not self.runtime_state.running_tasks:
            with self.ipc.status.get_lock():
                current_status = self.ipc.status.value
                if current_status != WorkerStatus.SLEEPING.value:
                    self.ipc.status.value = WorkerStatus.SLEEPING.value

    def _task_done_callback(self, fut: asyncio.Task):
        """Callback to manage running tasks and worker status."""
        self.runtime_state.running_tasks.discard(fut)

        # Run the blocking sync call in an executor to not block the event loop.
        if self.runtime_state.loop and self.runtime_state.loop.is_running():
            self.runtime_state.loop.run_in_executor(
                None, self._set_sleeping_if_idle_sync
            )

    def _set_running_status_sync(self):
        with self.ipc.status.get_lock():
            if self.ipc.status.value != WorkerStatus.RUNNING.value:
                self.ipc.status.value = WorkerStatus.RUNNING.value

    async def _handle_control_queue_batch_mode(
        self, control_queue: "TraitQueue", init_task: asyncio.Task
    ):
        """Dedicated coroutine to handle control signals (like 'exit')."""
        while True:
            try:
                task_data = await queue_get_async(control_queue)
                task = (
                    Task.create_with_traits(task_data, self.trait_registry)
                    if isinstance(task_data, dict)
                    else task_data
                )
                if task.action == "exit":
                    self.log(f"{self.identity.name} received exit signal.", logging.DEBUG)
                    if not init_task.done():
                        init_task.cancel()
                    control_queue.task_done()
                    return
                control_queue.task_done()
            except (asyncio.CancelledError, EOFError, OSError, ValueError):
                return

    def _set_sleeping_status_sync(self):
        """Sets worker status to SLEEPING."""
        with self.ipc.status.get_lock():
            current_status = self.ipc.status.value
            if current_status != WorkerStatus.SLEEPING.value:
                self.ipc.status.value = WorkerStatus.SLEEPING.value

    def _consume_batch_sync(self):
        """Blocking function to read a batch from shared memory."""
        with self.ipc.batch_buffer.lock:
            if self.ipc.batch_buffer.state.value == BufferState.READY_FOR_WORKER.value:
                self.ipc.batch_buffer.state.value = BufferState.WORKER_PROCESSING.value
                data_len = self.ipc.batch_buffer.data_length.value
                packed = self.ipc.batch_buffer.buf[
                    _HEADER.size : _HEADER.size + data_len
                ]
                tasks_data = msgpack.unpackb(bytes(packed), raw=False)
                self.ipc.batch_buffer.state.value = BufferState.EMPTY.value
                return [
                    Task.create_with_traits(td, self.trait_registry)
                    for td in tasks_data
                ]
        return None

    async def run(
        self, *, actions: dict[str, Callable], props: dict[str, Prop]
    ) -> None:
        """
        The main async method that drives the worker's lifecycle.

        This method is responsible for:
        - Initializing all props.
        - Starting the main task processing loop (`_run_batch_mode`).
        - Handling graceful shutdown and resource cleanup.
        """
        self.log(f"Worker run method started in pid={os.getpid()}.", logging.DEBUG)
        self.props = props if props is not None else {}
        initialization_complete = asyncio.Event()

        init_task = self.runtime_state.loop.create_task(
            self._initialize_all_props(initialization_complete, actions)
        )

        try:
            self.log("Main worker loop starting.", logging.DEBUG)
            self.log(f"Worker {self.identity.name} is running", logging.INFO)

            await self.runtime_state.loop.run_in_executor(
                None, self._set_running_status_sync
            )

            # Wait for initialization to complete, but also monitor the init_task for exceptions.
            init_event_waiter = self.runtime_state.loop.create_task(
                initialization_complete.wait()
            )
            done, pending = await asyncio.wait(
                {init_task, init_event_waiter},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if init_task in done and init_task.exception():
                # Prop initialization failed. The exception is on the task.
                # The worker cannot continue. Re-raise to terminate.
                raise init_task.exception()

            # Clean up pending tasks
            for p in pending:
                p.cancel()

            if self.ipc.batch_buffer:
                await self._batch_processing_loop(
                    init_task, actions, self._task_done_callback
                )

        finally:
            self.log("Main run loop finally block.", logging.DEBUG)

            # Wait for all running tasks to complete, but cancel background tasks.
            running_tasks = list(self.runtime_state.running_tasks)
            if running_tasks:
                self.log(
                    f"Shutdown initiated, waiting for {len(running_tasks)} in-flight tasks...",
                    logging.INFO,
                )
                await asyncio.gather(*running_tasks, return_exceptions=True)

            background_tasks = list(self.runtime_state.background_tasks)
            if background_tasks:
                self.log(
                    f"Cancelling {len(background_tasks)} background tasks.", logging.INFO
                )
                for task in background_tasks:
                    task.cancel()
                await asyncio.gather(*background_tasks, return_exceptions=True)

            if not init_task.done():
                init_task.cancel()
            await asyncio.gather(init_task, return_exceptions=True)

            with self.ipc.status.get_lock():
                self.ipc.status.value = WorkerStatus.STOPPED.value
            for prop in self.props.values():
                if prop.use_context_manager and prop.exit_stack:
                    await prop.exit_stack.aclose()
                elif hasattr(prop.instance, "close"):
                    # For non-context-manager props that have a close method (like SharedMemoryHashMap)
                    prop.instance.close()
            # EOQ is no longer used for shutdown signaling. The orchestrator's
            # result collector now exits based on the shutdown event.
            self.log("Worker run finished.", logging.DEBUG)

    async def _batch_processing_loop(self, init_task, actions, done_callback):
        """Main worker loop for batch processing from shared memory."""
        control_queue = next(iter(self.ipc.control_queues.values()), None)

        control_task = self.runtime_state.loop.create_task(
            self._handle_control_queue_batch_mode(control_queue, init_task)
        )

        await self.runtime_state.loop.run_in_executor(
            None, self._set_sleeping_status_sync
        )

        while not control_task.done():
            tasks_to_run = []

            tasks_data = await self.runtime_state.loop.run_in_executor(
                None, self._consume_batch_sync
            )

            if tasks_data:
                if "on_batch_received" in self.system_registry:
                    for system_func in self.system_registry["on_batch_received"]:
                        await system_func(tasks_data, self)

            if tasks_data:
                tasks_to_run.extend(tasks_data)
                # Release the semaphore to signal that the buffer is free and the
                # orchestrator can send more work.
                await self.runtime_state.loop.run_in_executor(
                    None, self.ipc.batch_buffer.producer_semaphore.release
                )

            # If no tasks, wait on the wakeup pipe with a timeout. This is more
            # efficient than polling with asyncio.sleep() and avoids race conditions
            # during shutdown, as it doesn't block a thread.
            if not tasks_to_run:
                # Asynchronously wait for a signal on the pipe without blocking a thread.
                future = self.runtime_state.loop.create_future()
                pipe_fd = self.ipc.batch_buffer.wakeup_rx.fileno()

                def wakeup_callback():
                    if not future.done():
                        future.set_result(True)

                self.runtime_state.loop.add_reader(pipe_fd, wakeup_callback)

                try:
                    await asyncio.wait_for(future, self.performance.loop_timeout)
                    # If we woke up, drain the pipe to clear the signal.
                    while self.ipc.batch_buffer.wakeup_rx.poll():
                        self.ipc.batch_buffer.wakeup_rx.recv_bytes()
                except asyncio.TimeoutError:
                    # Timeout is not an error; we just continue the loop.
                    pass
                finally:
                    self.runtime_state.loop.remove_reader(pipe_fd)
                continue

            # Now, if we have any tasks, process them.
            if tasks_to_run and not self.runtime_state.running_tasks:
                await self.runtime_state.loop.run_in_executor(
                    None, self._set_running_status_sync
                )

            for task in tasks_to_run:
                created_task = self.runtime_state.loop.create_task(
                    self._process_and_execute_task(task, actions)
                )
                created_task.add_done_callback(done_callback)
                self.runtime_state.running_tasks.add(created_task)
            # Yield control to the event loop to allow created tasks to start.
            await asyncio.sleep(0)

        if not control_task.done():
            control_task.cancel()
        if self.runtime_state.running_tasks:
            for t in self.runtime_state.running_tasks:
                t.cancel()
            await asyncio.gather(
                *self.runtime_state.running_tasks, return_exceptions=True
            )


# Late imports to resolve forward references in Pydantic models
from multiprocessing.sharedctypes import Synchronized  # noqa: E402

from .ipc.queues.trait_queue import TraitQueue  # noqa: E402

WorkerConfig.model_rebuild()
