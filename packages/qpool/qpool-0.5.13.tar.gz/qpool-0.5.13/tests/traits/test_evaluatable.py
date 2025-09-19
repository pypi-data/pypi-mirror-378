import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    EvaluatableTrait,
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    create_trait_decorator,
    task,
)
from wombat.multiprocessing.systems import EvaluatableSystem
from wombat.multiprocessing.worker import Worker

# --- Test Setup ---

evaluatable = create_trait_decorator(EvaluatableTrait)


def is_greater_than_5(x: int) -> bool:
    """A simple evaluator function for testing."""
    return x > 5


@task
def task_to_evaluate(_worker: Worker, value: int) -> int:
    return value


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([task_to_evaluate])
        .with_systems([EvaluatableSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_evaluatable_succeeds_on_true(orchestrator: Orchestrator):
    """Tests that the task is marked as Succeeded when the evaluator returns True."""
    passing_task = evaluatable(evaluator=is_greater_than_5)(task_to_evaluate)

    await orchestrator.add_task(passing_task(value=10))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1, "Should have one result.")
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(
        state_trait.outcome,
        TaskOutcome.SUCCESS,
        "The task should be marked as Succeeded when the evaluator returns True.",
    )


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_evaluatable_fails_on_false(orchestrator: Orchestrator):
    """Tests that the task is marked as Failed when the evaluator returns False."""
    failing_task = evaluatable(evaluator=is_greater_than_5)(task_to_evaluate)

    await orchestrator.add_task(failing_task(value=3))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1, "Should have one result.")
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(
        state_trait.outcome,
        TaskOutcome.FAILURE,
        "The task is marked as Failed when the evaluator returns False.",
    )
