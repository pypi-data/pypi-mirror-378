import logging
import os

import pytest
import pytest_check as check

from wombat.multiprocessing import (
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
)
from wombat.multiprocessing.logging import setup_logging
from wombat.multiprocessing.systems import LoggableSystem
from wombat.multiprocessing.traits.models import TaskDefinition
from wombat.multiprocessing.worker import Worker

# --- Test setup_logging ---


@pytest.mark.timeout(5)
def test_setup_logging_defaults():
    """Tests that setup_logging works with default arguments."""
    # Use a unique name to avoid conflicts with other tests
    logger = setup_logging(name="test_default")
    check.equal(logger.level, logging.ERROR, "Default log level should be ERROR.")
    check.is_true(
        any(isinstance(h, logging.FileHandler) for h in logger.handlers),
        "A file handler should be configured by default.",
    )
    # Cleanup handlers to not affect other tests
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


@pytest.mark.timeout(5)
def test_setup_logging_with_args():
    """Tests that setup_logging respects passed arguments."""
    log_dir = "test_logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "test_setup_logging_args.log")
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    try:
        logger = setup_logging(
            name="test_args",
            level=logging.DEBUG,
            log_file=log_file_path,
            to_console=True,
            max_bytes=100,
            backups=1,
        )
        check.equal(logger.level, logging.DEBUG, "Log level should be set to DEBUG.")
        check.is_true(
            any(isinstance(h, logging.StreamHandler) for h in logger.handlers),
            "A stream handler should be configured for console output.",
        )
        file_handler = next(
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        )
        check.equal(
            file_handler.baseFilename,
            os.path.abspath(log_file_path),
            "Log file path should match the argument.",
        )
        check.equal(file_handler.maxBytes, 100, "maxBytes should be set correctly.")
        check.equal(file_handler.backupCount, 1, "backupCount should be set correctly.")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
    finally:
        if os.path.exists(log_file_path):
            os.remove(log_file_path)


@pytest.mark.timeout(5)
def test_setup_logging_env_overrides():
    """Tests that environment variables correctly override defaults."""
    old_env = os.environ.copy()
    os.environ["WOMBAT_LOG_LEVEL"] = "INFO"
    os.environ["WOMBAT_LOG_STDOUT"] = "true"
    os.environ["WOMBAT_LOG_MAX"] = "200"
    os.environ["WOMBAT_LOG_BACKUPS"] = "3"

    try:
        logger = setup_logging(name="test_env")
        check.equal(
            logger.level, logging.INFO, "Log level should be INFO from environment variable."
        )
        check.is_true(
            any(isinstance(h, logging.StreamHandler) for h in logger.handlers),
            "Console logging should be enabled by environment variable.",
        )
        file_handler = next(
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        )
        check.equal(
            file_handler.maxBytes, 200, "maxBytes should be set by environment variable."
        )
        check.equal(
            file_handler.backupCount, 3, "backupCount should be set by environment variable."
        )
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
    finally:
        os.environ.clear()
        os.environ.update(old_env)


@pytest.mark.timeout(5)
def test_setup_logging_idempotency():
    """Tests that calling setup_logging multiple times doesn't add duplicate handlers."""
    logger = setup_logging(name="test_idempotent", to_console=True)
    initial_handler_count = len(logger.handlers)
    setup_logging(name="test_idempotent", to_console=True)
    check.equal(
        len(logger.handlers),
        initial_handler_count,
        "Calling setup_logging multiple times should not add duplicate handlers.",
    )
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


# --- E2E Test ---


def log_action(worker: Worker, message: str, level: int):
    """A task that uses the worker's log method."""
    worker.log(message, level)


log_message_task = TaskDefinition(
    action=log_action,
    action_name=f"{log_action.__module__}.{log_action.__name__}",
)


@pytest.mark.asyncio
@pytest.mark.timeout(10)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_e2e_logging(progress_bar_enabled: bool):
    """
    Tests the full end-to-end logging pipeline:
    1. A task worker calls `worker.log()`.
    2. This creates a `log_task` and sends it to the orchestrator's requeue.
    3. The orchestrator routes the `log_task` to the dedicated log worker.
    4. The log worker executes the task, writing the message to a file.
    5. The test verifies the file content after the orchestrator shuts down.
    6. It also verifies that the internal `log_task` does not appear in results.
    """
    log_dir = "test_logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "test_e2e_logging.log")
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    try:
        logging_config = {
            "log_file": log_file_path,
            "level": logging.INFO,
            "to_console": False,
        }

        builder = (
            OrchestratorBuilder()
            .with_workers(num_workers=1)
            .with_actions([log_message_task])
            .with_logging(logging_config)
            .with_systems([LoggableSystem])
            .with_progress_bar(progress_bar_enabled)
        )

        test_message = "This is an end-to-end test log message."
        async with builder.build() as orchestrator:
            task_instance = log_message_task(message=test_message, level=logging.INFO)
            await orchestrator.add_task(task_instance)
            # We must wait for the main task to finish, which is what triggers the log task.
            await orchestrator.finish_tasks()

            # Check that the results only contain the original task, not the log task.
            results = list(orchestrator.get_results())
            check.equal(len(results), 1, "Only the original task should be in the results.")
            result = results[0]
            check.equal(
                result.id, task_instance.id, "Result ID should match the submitted task ID."
            )
            state_trait = next(
                (t for t in result.traits if isinstance(t, StateTrait)), None
            )
            check.is_not_none(state_trait, "StateTrait should be present on the result.")
            check.equal(
                state_trait.outcome,
                TaskOutcome.SUCCESS,
                "The original task should have succeeded.",
            )

            # With the new accounting changes, finish_tasks() now correctly waits for
            # the log_task to complete, ensuring no logs are lost. The manual sleep
            # is no longer needed. The graceful shutdown (`__aexit__`) also ensures
            # the log worker has processed all tasks.

        with open(log_file_path) as f:
            log_content = f.read()

        check.is_in(
            test_message, log_content, "The log message should be in the log file."
        )
        check.is_in(
            "worker=worker-0",
            log_content,
            "The worker name should be in the log message.",
        )
        check.is_in("INFO", log_content, "The log level should be in the log message.")

    finally:
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
