import asyncio
import functools
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import Optional

from benchmarks.graph_traversal.tasks import (
    final_node_task_cf,
    traverse_task_cf,
)

logger = logging.getLogger(__name__)

CF_ACTION_REGISTRY = {
    "traverse_task_cf": traverse_task_cf,
    "final_node_task_cf": final_node_task_cf,
}


async def run_concurrent_futures_graph_pipeline(
    num_trees: int,
    num_workers: int,
    depth: int,
    fanout: int,
    benchmark_name: Optional[str] = None,
) -> float:
    """Runs the graph traversal benchmark using concurrent.futures."""
    logger.info("--- Running concurrent.futures Graph Traversal Benchmark ---")
    logger.info(
        f"Trees: {num_trees}, Workers: {num_workers}, Depth: {depth}, Fanout: {fanout}"
    )

    loop = asyncio.get_running_loop()
    start_time = time.monotonic()

    with ProcessPoolExecutor(
        max_workers=num_workers, mp_context=get_context("spawn")
    ) as executor:
        futures = set()
        for i in range(num_trees):
            p_func = functools.partial(
                traverse_task_cf,
                path=[i],
                current_depth=1,
                max_depth=depth,
                fanout=fanout,
            )
            future = loop.run_in_executor(executor, p_func)
            futures.add(future)

        tasks_in_flight = num_trees

        while tasks_in_flight > 0:
            done, futures = await asyncio.wait(
                futures, return_when=asyncio.FIRST_COMPLETED
            )

            for future in done:
                result = await future
                tasks_in_flight -= 1

                if result is None:
                    continue

                next_actions = []
                if isinstance(result, list):
                    next_actions.extend(result)
                elif isinstance(result, tuple):
                    next_actions.append(result)
                else:
                    # It's a final result, do nothing.
                    continue

                for action_name, kwargs in next_actions:
                    next_func = CF_ACTION_REGISTRY[action_name]
                    p_func = functools.partial(next_func, **kwargs)
                    new_future = loop.run_in_executor(executor, p_func)
                    futures.add(new_future)
                    tasks_in_flight += 1

    end_time = time.monotonic()
    duration = end_time - start_time
    logger.info(
        f"[concurrent.futures Graph Traversal] Total time: {duration:.2f} seconds"
    )
    return duration
