import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    consumes,
    produces,
    task,
)
from wombat.multiprocessing.systems import ConsumesSystem, ProducesSystem
from wombat.multiprocessing.traits.models import Task
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---


@task
def child_task(_worker: Worker, value: int) -> int:
    """A simple child task that returns a value."""
    return value * 2


@produces(tags=["batch1"])
@task
def producer_task(_worker: Worker, num_children: int) -> list[Task]:
    """Produces a batch of child tasks."""
    return [child_task(value=i) for i in range(num_children)]


@consumes(tags=["batch1"], batch_size=5)
@task
def consumer_task(_worker: Worker, consumed_results: list[int] | None = None) -> int:
    """Consumes the results of the child tasks and sums them."""
    if consumed_results is None:
        return -1  # Should not happen
    return sum(consumed_results)


# --- Fixture ---


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([producer_task, child_task, consumer_task])
        .with_systems([ProducesSystem, ConsumesSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


# --- Test ---


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_produces_consumes_workflow(orchestrator: Orchestrator):
    """
    Tests the full fan-out/fan-in workflow:
    1. A producer creates a batch of child tasks with a tag.
    2. A consumer is submitted to wait for results with the same tag.
    3. The orchestrator runs the child tasks.
    4. Once the batch is complete, the orchestrator emits the consumer.
    5. The consumer receives the collected results and produces a final result.
    """
    # Add the consumer first. It will be held by the orchestrator until its
    # dependencies are met. Then, add the producer which will generate the work.
    await orchestrator.add_tasks([consumer_task(), producer_task(num_children=5)])

    # This waits for all initial tasks *and* all dynamically generated tasks
    # (including the emitted consumer) to complete.
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())

    # We should only get the final result from the `consumer_task`. The producer's
    # result is suppressed, and the children's results are consumed.
    check.equal(
        len(results), 1, "Should only get the final result from the consumer task."
    )

    result = results[0]
    state_trait = next((t for t in result.traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait, "StateTrait should be present on the result.")
    check.equal(state_trait.outcome, TaskOutcome.SUCCESS, "The consumer task should have succeeded.")
    check.equal(
        result.action,
        consumer_task.action_name,
        "The result should be from the consumer task.",
    )

    # Expected results from children: [0*2, 1*2, 2*2, 3*2, 4*2] -> [0, 2, 4, 6, 8]
    # The consumer sums them: 0 + 2 + 4 + 6 + 8 = 20
    check.equal(result.result, 20, "The consumer task should have the correct summed result.")


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_unsatisfied_consumer_is_not_run(orchestrator: Orchestrator):
    """
    Tests that if not enough results are produced to satisfy a consumer's
    batch_size, the consumer task is never run and `finish_tasks` completes.
    """
    # The consumer expects 5 results, but the producer will only create 3.
    await orchestrator.add_tasks([consumer_task(), producer_task(num_children=3)])
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())

    # No results should be yielded. The producer and child results are suppressed,
    # and the consumer is never run because its dependency is not met.
    check.equal(
        len(results),
        0,
        "No results should be yielded when the consumer is not satisfied.",
    )


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_multiple_consumers_for_same_tag(orchestrator: Orchestrator):
    """
    Tests that multiple consumers waiting for the same tag are correctly
    processed in order as results become available.
    """
    # Two consumers, each needing 5 results. The producer will create 10.
    tasks_to_add = [
        consumer_task(),
        consumer_task(),
        producer_task(num_children=10),
    ]
    await orchestrator.add_tasks(tasks_to_add)
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())

    # We should get two results, one from each consumer.
    check.equal(len(results), 2, "Should get two results, one from each consumer.")
    for r in results:
        state_trait = next((t for t in r.traits if isinstance(t, StateTrait)), None)
        check.is_not_none(
            state_trait, "StateTrait should be present on each consumer result."
        )
        check.equal(
            state_trait.outcome, TaskOutcome.SUCCESS, "Each consumer task should have succeeded."
        )

    # The results from the 10 child tasks are summed by the two consumers.
    # With multiple workers, the order of completion is not guaranteed, so we
    # check that the total sum is correct, rather than the sum of each batch.
    # Expected child results: [0, 2, 4, ..., 18]. Sum = 90.
    total_sum = sum(r.result for r in results)
    expected_total = sum(i * 2 for i in range(10))
    check.equal(
        total_sum,
        expected_total,
        "The sum of consumed results should match the total of all produced results.",
    )
