from typing import TYPE_CHECKING, Any, List, Union

from wombat.multiprocessing import (
    produces,
    task,
)
from wombat.multiprocessing.traits.models import Task

if TYPE_CHECKING:
    from wombat.multiprocessing.worker import Worker


# --- Wombat Task Actions ---


@task
def final_node_task(_worker: "Worker", path: list[int]) -> int:
    """A terminal task that does minimal work."""
    # A simple calculation to simulate work.
    return sum(path)


@produces()
@task
def traverse_task(
    _worker: "Worker",
    path: list[int],
    current_depth: int,
    max_depth: int,
    fanout: int,
) -> Union[Task, List[Task]]:
    """A recursive task that fans out to traverse a tree."""
    if current_depth >= max_depth:
        return final_node_task(path=path)

    new_tasks = []
    for i in range(fanout):
        new_path = path + [i]
        new_tasks.append(
            traverse_task(
                path=new_path,
                current_depth=current_depth + 1,
                max_depth=max_depth,
                fanout=fanout,
            )
        )
    return new_tasks


# --- concurrent.futures compatible task functions ---


def final_node_task_cf(path: list[int]) -> int:
    """concurrent.futures version of the final_node_task."""
    return sum(path)


def traverse_task_cf(
    path: list[int],
    current_depth: int,
    max_depth: int,
    fanout: int,
) -> Any:
    """concurrent.futures version of the traverse_task."""
    if current_depth >= max_depth:
        return "final_node_task_cf", {"path": path}

    next_actions = []
    for i in range(fanout):
        new_path = path + [i]
        next_actions.append(
            (
                "traverse_task_cf",
                {
                    "path": new_path,
                    "current_depth": current_depth + 1,
                    "max_depth": max_depth,
                    "fanout": fanout,
                },
            )
        )
    return next_actions
