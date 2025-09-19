from typing import Literal

import pytest
import pytest_check as check

from wombat.multiprocessing.traits.models import BaseTrait, Task


class ForbiddenTrait(BaseTrait):
    """A trait that can be forbidden by another."""

    trait_name: Literal["forbidden"] = "forbidden"


class ForbiddingTrait(BaseTrait):
    """A trait that forbids the ForbiddenTrait."""

    trait_name: Literal["forbidding"] = "forbidding"
    forbids_traits: list[str] = ["forbidden"]


def test_forbids_traits_rule():
    """
    Tests that the `forbids_traits` rule correctly removes a forbidden
    trait during task instantiation.
    """
    task = Task(
        action="test_action",
        traits=[ForbiddingTrait(), ForbiddenTrait()],
    )

    trait_names = {getattr(t, "trait_name", None) for t in task.traits}

    check.is_in("forbidding", trait_names, "ForbiddingTrait should be present.")
    check.is_not_in(
        "forbidden", trait_names, "ForbiddenTrait should have been removed."
    )


def test_depends_on_cyclic_dependency_raises_error():
    """
    Tests that a cyclic dependency in `depends_on` raises a ValueError during
    task instantiation.
    """

    class DependsOnCycleA(BaseTrait):
        """Trait with a dependency."""

        trait_name: Literal["depends_on_cycle_a"] = "depends_on_cycle_a"
        depends_on: list[str] = ["depends_on_cycle_b"]

    class DependsOnCycleB(BaseTrait):
        """Trait that creates a dependency cycle."""

        trait_name: Literal["depends_on_cycle_b"] = "depends_on_cycle_b"
        depends_on: list[str] = ["depends_on_cycle_a"]

    with pytest.raises(ValueError, match="Cycle detected in trait dependencies"):
        Task(
            action="test_action",
            traits=[DependsOnCycleA(), DependsOnCycleB()],
        )
