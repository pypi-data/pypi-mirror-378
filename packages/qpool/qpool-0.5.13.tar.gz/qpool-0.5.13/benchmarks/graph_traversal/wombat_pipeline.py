import logging
import time
from typing import Optional

from benchmarks.graph_traversal import tasks
from wombat.multiprocessing import (
    OrchestratorBuilder,
)
from wombat.multiprocessing.ipc.buffer import BufferConfig
from wombat.multiprocessing.systems import ProducesSystem

logger = logging.getLogger(__name__)


async def run_wombat_graph_pipeline(
    num_trees: int,
    num_workers: int,
    depth: int,
    fanout: int,
    benchmark_name: Optional[str] = None,
) -> float:
    """
    Runs a graph traversal benchmark using Wombat.

    This benchmark creates a high volume of short-lived, dynamically generated
    tasks to stress the orchestration capabilities of the framework.
    """
    logger.info("--- Running Wombat Graph Traversal Benchmark ---")
    logger.info(
        f"Trees: {num_trees}, Workers: {num_workers}, Depth: {depth}, Fanout: {fanout}"
    )

    start_time = time.monotonic()

    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=num_workers)
        .with_actions(
            [
                tasks.traverse_task,
                tasks.final_node_task,
            ]
        )
        .with_systems([ProducesSystem])
        .without_logging()
        .with_progress_bar(False)
        .with_batch_config(BufferConfig(size=1.28e8))
    )

    async with builder.build() as orchestrator:
        initial_tasks = [
            tasks.traverse_task(
                path=[i], current_depth=1, max_depth=depth, fanout=fanout
            )
            for i in range(num_trees)
        ]
        await orchestrator.add_tasks(initial_tasks)
        await orchestrator.finish_tasks()
        # Consume results to ensure they are processed.
        _ = list(orchestrator.get_results())

    end_time = time.monotonic()
    duration = end_time - start_time
    logger.info(f"[Graph Traversal] Total time: {duration:.2f} seconds")
    return duration
