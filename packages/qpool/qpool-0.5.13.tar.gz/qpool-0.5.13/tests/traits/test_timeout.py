import asyncio

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    task,
    timeout,
)
from wombat.multiprocessing.systems import TimeoutSystem
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---

@task
async def sleep_task(_worker: Worker, duration: float):
    await asyncio.sleep(duration)
    return "done"


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([sleep_task])
        .with_systems([TimeoutSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_timeout_cancels_long_task(orchestrator: Orchestrator):
    """Tests that a task is cancelled if it exceeds its timeout."""
    timed_out_task = timeout(timeout=0.1)(sleep_task)
    
    await orchestrator.add_task(timed_out_task(duration=0.5))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1, "Should be one result for the timed-out task.")
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(
        state_trait.outcome, TaskOutcome.CANCELLED, "The task outcome should be CANCELLED."
    )


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_timeout_allows_short_task(orchestrator: Orchestrator):
    """Tests that a task succeeds if it finishes before its timeout."""
    successful_task = timeout(timeout=0.5)(sleep_task)
    
    await orchestrator.add_task(successful_task(duration=0.1))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1, "Should be one result for the successful task.")
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(
        state_trait.outcome,
        TaskOutcome.SUCCESS,
        "The task that finishes within its timeout should succeed.",
    )
