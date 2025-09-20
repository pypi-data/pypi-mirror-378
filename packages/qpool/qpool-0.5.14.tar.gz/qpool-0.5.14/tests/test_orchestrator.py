import asyncio
import os
import signal
import sys

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    pinned,
    task,
)
from wombat.multiprocessing.errors import WorkerCrashError
from wombat.multiprocessing.systems import PinnedSystem
from wombat.multiprocessing.worker import Worker


# Test Actions
@task
def simple_sync_task(_worker: Worker, x: int, y: int) -> int:
    return x + y


@task
async def simple_async_task(_worker: Worker, x: int, y: int) -> int:
    await asyncio.sleep(0.01)
    return x * y


@task
def worker_name_task(worker: Worker) -> str:
    return worker.identity.name


@task
def crash_worker_task(_worker: Worker):
    os.kill(os.getpid(), signal.SIGKILL)


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    """Fixture to provide a started orchestrator and ensure it's shut down."""
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions(
            [
                simple_sync_task,
                simple_async_task,
                worker_name_task,
                crash_worker_task,
            ]
        )
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_e2e_lifecycle(orchestrator: Orchestrator):
    """Tests the basic end-to-end lifecycle of submitting tasks and getting results."""
    tasks = [simple_sync_task(1, 2), simple_async_task(3, 4)]
    await orchestrator.add_tasks(tasks)
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 2, "Should have two results.")

    sync_result = next(r for r in results if r.action == simple_sync_task.action_name)
    async_result = next(r for r in results if r.action == simple_async_task.action_name)

    sync_state_trait = next(
        (t for t in sync_result.traits if isinstance(t, StateTrait)), None
    )
    check.is_not_none(sync_state_trait, "StateTrait should be present on sync result.")
    check.equal(
        sync_state_trait.outcome, TaskOutcome.SUCCESS, "Sync task should succeed."
    )
    check.equal(sync_result.result, 3, "Sync task result should be correct.")
    async_state_trait = next(
        (t for t in async_result.traits if isinstance(t, StateTrait)), None
    )
    check.is_not_none(async_state_trait, "StateTrait should be present on async result.")
    check.equal(
        async_state_trait.outcome, TaskOutcome.SUCCESS, "Async task should succeed."
    )
    check.equal(async_result.result, 12, "Async task result should be correct.")


@pytest.mark.parametrize("start_method", ["spawn", "fork", "forkserver"])
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_e2e_with_start_methods(start_method, progress_bar_enabled: bool):
    """Tests the e2e lifecycle with different multiprocessing start methods."""
    if start_method == "fork" and sys.platform == "win32":
        pytest.skip("Fork is not available on Windows")

    builder = (
        OrchestratorBuilder()
        .with_start_method(start_method)
        .with_workers(num_workers=2)
        .with_actions([simple_sync_task, simple_async_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        tasks = [simple_sync_task(1, 2), simple_async_task(3, 4)]
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 2, "Should have two results.")

        sync_result = next(
            r for r in results if r.action == simple_sync_task.action_name
        )
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
        check.equal(sync_result.result, 3, "Sync task result should be correct.")
        async_state_trait = next(
            (t for t in async_result.traits if isinstance(t, StateTrait)), None
        )
        check.is_not_none(async_state_trait, "StateTrait should be present on async result.")
        check.equal(
            async_state_trait.outcome, TaskOutcome.SUCCESS, "Async task should succeed."
        )
        check.equal(async_result.result, 12, "Async task result should be correct.")


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_orchestrator_task_distribution_with_pinning(progress_bar_enabled: bool):
    """Tests that the Pinned trait correctly routes tasks to a specific worker."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([worker_name_task])
        .with_systems([PinnedSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        pinned_task_def_0 = pinned(worker_name="worker-0")(worker_name_task)
        pinned_task_def_1 = pinned(worker_name="worker-1")(worker_name_task)
        pinned_task_0 = pinned_task_def_0()
        pinned_task_1 = pinned_task_def_1()

        await orchestrator.add_tasks([pinned_task_0, pinned_task_1])
        await orchestrator.finish_tasks()

        results = {r.id: r for r in orchestrator.get_results()}
        check.equal(len(results), 2, "Should have two results for pinned tasks.")
        check.equal(
            results[pinned_task_0.id].result,
            "worker-0",
            "Task should be pinned to worker-0.",
        )
        check.equal(
            results[pinned_task_1.id].result,
            "worker-1",
            "Task should be pinned to worker-1.",
        )


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_get_results_clears_buffer(orchestrator: Orchestrator):
    """Tests that get_results is a one-time operation that clears the internal buffer."""
    await orchestrator.add_task(simple_sync_task(5, 5))
    await orchestrator.finish_tasks()

    results1 = list(orchestrator.get_results())
    check.equal(len(results1), 1, "First get_results call should return one result.")
    check.equal(results1[0].result, 10, "Result value should be correct.")

    results2 = list(orchestrator.get_results())
    check.equal(len(results2), 0, "Second get_results call should return zero results.")


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_orchestrator_handles_worker_crash(progress_bar_enabled: bool):
    """Tests that the orchestrator raises WorkerCrashError when a worker dies."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([crash_worker_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(crash_worker_task())

        with pytest.raises(WorkerCrashError):
            await orchestrator.finish_tasks()


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_orchestrator_shutdown_with_context_manager(progress_bar_enabled: bool):
    """Tests that the async context manager correctly shuts down the orchestrator."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_sync_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(simple_sync_task(1, 1))
        # No call to finish_tasks, __aexit__ should handle shutdown

    # The test passes if no errors are raised and it doesn't hang.
    check.is_true(
        orchestrator.stopped,
        "Orchestrator should be marked as stopped after context exit.",
    )


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_add_task_and_add_tasks(orchestrator: Orchestrator):
    """Tests both single and batch task submission methods."""
    # Single task
    task1 = simple_sync_task(1, 1)
    await orchestrator.add_task(task1)

    # Batch of tasks
    tasks2 = [simple_sync_task(2, 2), simple_sync_task(3, 3)]
    await orchestrator.add_tasks(tasks2)

    await orchestrator.finish_tasks()

    results = sorted([r.result for r in orchestrator.get_results()])
    check.equal(results, [2, 4, 6], "All submitted tasks should have correct results.")


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_orchestrator_with_zero_workers(progress_bar_enabled: bool):
    """Tests that the orchestrator can run and shut down with zero workers."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=0)
        .with_actions([simple_sync_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(simple_sync_task(1, 1))
        # With no workers, this should return immediately.
        await orchestrator.finish_tasks()
        results = list(orchestrator.get_results())
        # No tasks should have executed.
        check.equal(len(results), 0, "No tasks should have executed with zero workers.")

    # The test passes if it completes without hanging.


@pytest.mark.asyncio
@pytest.mark.timeout(20)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_add_tasks_with_unserializable_arg(progress_bar_enabled: bool):
    """
    Tests that add_tasks handles unserializable arguments gracefully by returning
    them in the `enqueue_failures` list.
    """
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_sync_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        # Lambda functions are not serializable by the custom encoder.
        task_with_bad_arg = simple_sync_task(x=1, y=lambda: 2)

        failures = await orchestrator.add_tasks([task_with_bad_arg])

        check.equal(
            len(failures),
            1,
            "One task with an unserializable argument should fail to enqueue.",
        )
        check.equal(
            failures[0].id,
            task_with_bad_arg.id,
            "The failed task should be the one with the bad argument.",
        )

        # Verify no tasks were actually run.
        await orchestrator.finish_tasks()
        results = list(orchestrator.get_results())
        check.equal(len(results), 0, "No tasks should have been executed.")


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_handles_large_number_of_tasks(orchestrator: Orchestrator):
    """Tests the orchestrator's ability to handle a large volume of tasks."""
    num_tasks = 1000
    tasks = [simple_sync_task(i, i) for i in range(num_tasks)]
    await orchestrator.add_tasks(tasks)
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(
        len(results), num_tasks, "Should have a result for every submitted task."
    )

    # Verify a few results to be sure
    results.sort(key=lambda r: r.result)
    expected_results = sorted([i + i for i in range(num_tasks)])
    check.equal(
        [r.result for r in results],
        expected_results,
        "All task results should be correct.",
    )
