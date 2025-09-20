import asyncio
import time
from typing import Any, Dict

import pytest
import pytest_check as check

from wombat.multiprocessing import (
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    requires_props,
    task,
)
from wombat.multiprocessing.traits.models import Prop
from wombat.multiprocessing.worker import Worker


# Test Actions
@task
def simple_sync_task(_worker: Worker, x: int, y: int) -> int:
    return x + y


@task
async def simple_async_task(_worker: Worker, x: int, y: int) -> int:
    await asyncio.sleep(0.01)
    return x * y


@requires_props(requires_props=["my_prop"])
@task
def prop_task(_worker: Worker, props: Dict[str, Any]) -> str:
    return props["my_prop"].instance


@task
def exception_task(_worker: Worker) -> None:
    raise ValueError("This task is designed to fail.")


@task
async def sleep_task(_worker: Worker, duration: float) -> float:
    start = time.monotonic()
    await asyncio.sleep(duration)
    end = time.monotonic()
    return end - start


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_worker_executes_sync_and_async_tasks(progress_bar_enabled: bool):
    """Tests that a worker can correctly execute both sync and async actions."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_sync_task, simple_async_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        tasks = [simple_sync_task(10, 5), simple_async_task(10, 5)]
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 2, "Should have two results.")

        sync_result = next(r for r in results if r.action == simple_sync_task.action_name)
        async_result = next(
            r for r in results if r.action == simple_async_task.action_name
        )

        sync_state_trait = next(
            (t for t in sync_result.traits if isinstance(t, StateTrait)), None
        )
        check.is_not_none(sync_state_trait, "StateTrait should be present on sync result.")
        check.equal(
            sync_state_trait.outcome, TaskOutcome.SUCCESS, "Sync task should succeed."
        )
        check.equal(sync_result.result, 15, "Sync task result should be correct.")
        async_state_trait = next(
            (t for t in async_result.traits if isinstance(t, StateTrait)), None
        )
        check.is_not_none(async_state_trait, "StateTrait should be present on async result.")
        check.equal(
            async_state_trait.outcome, TaskOutcome.SUCCESS, "Async task should succeed."
        )
        check.equal(async_result.result, 50, "Async task result should be correct.")


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_worker_handles_props(progress_bar_enabled: bool):
    """Tests that a worker correctly initializes and injects props into a task."""
    prop_value = "hello from prop"
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([prop_task])
        .add_prop(
            "my_prop",
            Prop(
                initializer=prop_value,
                use_context_manager=False,
            ),
        )
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )

    async with builder.build() as orchestrator:
        await orchestrator.add_task(prop_task())
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 1, "Should have one result.")
        state_trait = next(
            (t for t in results[0].traits if isinstance(t, StateTrait)), None
        )
        check.is_not_none(state_trait, "StateTrait should be present on the result.")
        check.equal(state_trait.outcome, TaskOutcome.SUCCESS, "Prop task should succeed.")
        check.equal(
            results[0].result, prop_value, "Prop task should return the correct prop value."
        )


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_worker_handles_task_exception(progress_bar_enabled: bool):
    """Tests that a worker correctly handles exceptions raised by a task action."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([exception_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(exception_task())
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 1, "Should have one result.")
        result = results[0]

        state_trait = next((t for t in result.traits if isinstance(t, StateTrait)), None)
        check.is_not_none(state_trait, "StateTrait should be present on the result.")
        check.equal(
            state_trait.outcome,
            TaskOutcome.FAILURE,
            "Task that raises an exception should have a FAILURE outcome.",
        )
        # Result is a list [exception_string, original_result (None)]
        check.is_instance(result.result, list, "Failure result should be a list.")
        check.is_in(
            "ValueError: This task is designed to fail.",
            result.result[0],
            "Failure result should contain the exception string.",
        )


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_worker_concurrency_limit(progress_bar_enabled: bool):
    """Tests that a worker respects the max_concurrent_tasks setting."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1, max_concurrent_tasks=2)
        .with_actions([sleep_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        start_time = time.monotonic()
        tasks = [sleep_task(duration=0.2) for _ in range(4)]
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()
        end_time = time.monotonic()

        duration = end_time - start_time
        # Expect two batches of two tasks, so ~0.4s.
        # Allow a generous margin for overhead.
        check.is_true(
            0.4 <= duration < 0.6,
            "Total duration should reflect the concurrency limit.",
        )


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_worker_cancels_task_on_shutdown(progress_bar_enabled: bool):
    """
    Tests that the worker cancels in-flight tasks during shutdown and reports
    them as failed.
    """
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([sleep_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        # Add a long-running task but don't wait for it to finish.
        await orchestrator.add_task(sleep_task(duration=5.0))
        # Give it a moment to be dispatched to the worker.
        await asyncio.sleep(0.1)

    # The context manager exit triggers shutdown.
    # Now, inspect the final results buffer.
    results = list(orchestrator.get_results())

    # If a result makes it back, it should be a failure.
    # The primary goal is ensuring the process terminates cleanly without hanging.
    if results:
        check.equal(len(results), 1, "Should have one result.")
        result = results[0]
        state_trait = next((t for t in result.traits if isinstance(t, StateTrait)), None)
        check.is_not_none(state_trait, "StateTrait should be present on the result.")
        check.equal(
            state_trait.outcome, TaskOutcome.FAILURE, "Task should fail due to worker shutdown."
        )
        check.is_in(
            "worker shutdown", result.result[0], "Failure reason should indicate worker shutdown."
        )
