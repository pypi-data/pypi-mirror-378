import asyncio
import logging
import os
import random
from collections import deque
from multiprocessing import cpu_count

import pytest
import pytest_check as check

from wombat.multiprocessing import (
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    task,
)
from wombat.multiprocessing.worker import Worker


# --- Test Actions for Mixed Workload ---


@task
def fast_cpu_task(worker: Worker, x: int) -> int:
    """A very fast, CPU-bound task."""
    worker.log(f"Running fast_cpu_task with {x}", logging.DEBUG)
    return x * x


@task
def slow_cpu_task(worker: Worker, n: int = 1000) -> int:
    """A slightly slower, CPU-bound task."""
    worker.log(f"Running slow_cpu_task with n={n}", logging.DEBUG)
    return sum(i * i for i in range(n))


@task
async def io_bound_task(worker: Worker, duration: float = 0.01) -> None:
    """A task that simulates I/O by sleeping."""
    worker.log(f"Running io_bound_task with duration={duration}", logging.DEBUG)
    await asyncio.sleep(duration)


def print_last_log_lines(log_file_path: str, n: int = 1000):
    """Prints the last N lines of a file."""
    if not os.path.exists(log_file_path):
        print(f"\n--- Log file not found: {log_file_path} ---")
        return
    try:
        with open(log_file_path, "r") as f:
            # Use deque for an efficient sliding window over the file
            last_lines = deque(f, n)
        print(f"\n--- Last {len(last_lines)} lines of {log_file_path} ---")
        for line in last_lines:
            print(line, end="")
        print("\n--- End of log ---")
    except Exception as e:
        print(f"\n--- Error reading log file {log_file_path}: {e} ---")


@pytest.mark.asyncio
@pytest.mark.timeout(660)
async def test_high_volume_mixed_workload_e2e():
    """
    A stress test that runs a high volume of mixed-workload tasks with logging
    and progress bar enabled to test system stability and performance under load.
    """
    num_tasks = 100_000
    num_workers = cpu_count() or 2

    log_dir = "test_logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "test_stress.log")
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    logging_config = {
        "to_console": False,
        "level": logging.INFO,
        "log_file": log_file_path,
    }

    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=num_workers)
        .with_actions([fast_cpu_task, slow_cpu_task, io_bound_task])
        .with_logging(logging_config)
        .with_progress_bar(True)
    )

    async def run_orchestration():
        async with builder.build() as orchestrator:
            tasks_to_add = []
            for i in range(num_tasks):
                task_type = random.choice([0, 1, 2])
                if task_type == 0:
                    tasks_to_add.append(fast_cpu_task(x=i))
                elif task_type == 1:
                    tasks_to_add.append(slow_cpu_task(n=random.randint(500, 1500)))
                else:
                    tasks_to_add.append(
                        io_bound_task(duration=random.uniform(0.005, 0.015))
                    )

            await orchestrator.add_tasks(tasks_to_add)
            await orchestrator.finish_tasks()

            results = list(orchestrator.get_results())

            check.equal(
                len(results), num_tasks, f"Should have received {num_tasks} results."
            )

            success_count = 0
            for r in results:
                state_trait = next(
                    (t for t in r.traits if isinstance(t, StateTrait)), None
                )
                if state_trait and state_trait.outcome == TaskOutcome.SUCCESS:
                    success_count += 1

            check.equal(
                success_count, num_tasks, f"All {num_tasks} tasks should have succeeded."
            )

            # Check if log file was created and is not empty
            check.is_true(os.path.exists(log_file_path), "Log file should be created.")
            check.is_true(
                os.path.getsize(log_file_path) > 0, "Log file should not be empty."
            )

    try:
        # Wrap the core logic in a timeout. 600s should be enough for 100k tasks
        # if the system is not hanging.
        await asyncio.wait_for(run_orchestration(), timeout=600)
    except asyncio.TimeoutError:
        print("\n--- Test timed out. ---")
        print_last_log_lines(log_file_path)
        pytest.fail("Stress test timed out after 600 seconds.")
    finally:
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
