from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import Field

from .models import BaseTrait, CountingRule


def _log_carrier_rules_factory():
    return [CountingRule(counter_name="logs", on_event="received")]


class LogCarrierTrait(BaseTrait):
    """This indicates a task that MUST NEVER generate log messages during it's execution.
    i.e. For when you make a logging task for a failure, and the logging task fails thus causing a logging cycle. This prevents that cycle."""

    trait_name: Literal["log_carrier"] = "log_carrier"
    forbids_traits: list[str] = ["uncounted"]
    requires_traits: list[str] = ["accounting"]
    counting_rules: Optional[List[CountingRule]] = Field(
        default_factory=_log_carrier_rules_factory
    )
