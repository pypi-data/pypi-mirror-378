import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from multiprocessing import cpu_count
from typing import TYPE_CHECKING, Literal, Optional

import numpy as np
from pydantic import BaseModel, Field, conint

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmarks.graph_traversal.concurrent_futures_pipeline import (
    run_concurrent_futures_graph_pipeline,
)
from benchmarks.graph_traversal.wombat_pipeline import run_wombat_graph_pipeline

if TYPE_CHECKING:
    pass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BenchmarkConfig(BaseModel):
    name: Optional[str] = None
    benchmark: Literal["graph-traversal", "graph-traversal-cf"]
    workers: Optional[conint(ge=1)] = Field(default_factory=cpu_count)
    num_trees: conint(ge=1) = 10
    depth: conint(ge=1) = 6
    fanout: conint(ge=1) = 3
    runs: conint(ge=1) = 1


def run_single_scenario(config: BenchmarkConfig):
    if config.benchmark == "graph-traversal":
        durations = []
        for i in range(config.runs):
            if config.runs > 1:
                logger.info(f"--- Run {i + 1}/{config.runs} ---")
            duration = asyncio.run(
                run_wombat_graph_pipeline(
                    num_trees=config.num_trees,
                    num_workers=config.workers or cpu_count() or 1,
                    depth=config.depth,
                    fanout=config.fanout,
                    benchmark_name=config.name,
                )
            )
            durations.append(duration)
        logger.info("--- Summary ---")
        logger.info(f"Graph Traversal Avg Duration: {np.mean(durations):.2f} seconds")
    elif config.benchmark == "graph-traversal-cf":
        durations = []
        for i in range(config.runs):
            if config.runs > 1:
                logger.info(f"--- Run {i + 1}/{config.runs} ---")
            duration = asyncio.run(
                run_concurrent_futures_graph_pipeline(
                    num_trees=config.num_trees,
                    num_workers=config.workers or cpu_count() or 1,
                    depth=config.depth,
                    fanout=config.fanout,
                    benchmark_name=config.name,
                )
            )
            durations.append(duration)
        logger.info("--- Summary ---")
        logger.info(
            f"concurrent.futures Graph Traversal Avg Duration: {np.mean(durations):.2f} seconds"
        )
    else:
        logger.error(f"Unknown benchmark type: {config.benchmark}")
        return


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark scenarios for Wombat."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="benchmarks/config.json",
        help="Path to the JSON configuration file.",
    )
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            scenarios_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {args.config}")
        return

    # Filter for graph traversal benchmarks
    scenarios = [
        BenchmarkConfig(**data)
        for data in scenarios_data
        if "graph" in data.get("benchmark", "")
    ]

    for scenario in scenarios:
        if scenario.name:
            banner = f" Running Benchmark: {scenario.name} "
            logger.info(
                f"\n{'=' * ((80 - len(banner)) // 2)}{banner}{'=' * ((80 - len(banner)) // 2)}"
            )
        run_single_scenario(scenario)


if __name__ == "__main__":
    main()
