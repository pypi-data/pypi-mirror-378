from datetime import timedelta

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    delayed,
    expirable,
    task,
)
from wombat.multiprocessing.systems import DelayedSystem, ExpirableSystem
from wombat.multiprocessing.worker import Worker

# --- Test Actions ---

@task
def simple_action(_worker: Worker) -> str:
    return "executed"


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_action])
        .with_systems([ExpirableSystem, DelayedSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_expirable_task_is_skipped(orchestrator: Orchestrator):
    """Tests that an expired task is skipped and marked with the Expired trait."""
    # This task expires in 0.1s but is delayed for 0.3s, so it should expire.
    expirable_action = delayed(delay=0.3)(expirable(expires_after=timedelta(seconds=0.1))(simple_action))

    await orchestrator.add_task(expirable_action())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1, "Should be one result for the expired task.")
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(
        state_trait.outcome, TaskOutcome.EXPIRED, "The task should have an outcome of EXPIRED."
    )


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_expirable_task_succeeds(orchestrator: Orchestrator):
    """Tests that a non-expired task executes successfully."""
    # This task expires in 0.3s and is delayed for 0.1s, so it should run.
    expirable_action = delayed(delay=0.1)(expirable(expires_after=timedelta(seconds=0.3))(simple_action))

    await orchestrator.add_task(expirable_action())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1, "Should be one result for the successful task.")
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(
        state_trait.outcome,
        TaskOutcome.SUCCESS,
        "The non-expired task should succeed.",
    )
