import logging
import os
import re
import subprocess
import time
from typing import Callable, Dict, List, Optional

from obvyr_agent.schemas import (
    CommandExecutionConfig,
    OutputMode,
    RunCommandResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_ci_environment() -> bool:
    """
    Detect CI environment via standard environment variables.

    Returns:
        True if running in a CI environment, False otherwise.
    """
    ci_indicators = [
        "CI",
        "CONTINUOUS_INTEGRATION",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "JENKINS_URL",
        "BUILDKITE",
        "CIRCLECI",
    ]
    return any(os.getenv(var) for var in ci_indicators)


def determine_execution_mode(config: CommandExecutionConfig) -> OutputMode:
    """
    Determine the execution mode based on configuration and environment.

    Args:
        config: Command execution configuration.

    Returns:
        The resolved output mode.
    """
    if config.output_mode == OutputMode.AUTO:
        return OutputMode.BATCH if is_ci_environment() else OutputMode.STREAM
    return config.output_mode


def build_environment_variables(
    config: CommandExecutionConfig,
) -> Dict[str, str]:
    """
    Build environment variables for command execution.

    Args:
        config: Command execution configuration.

    Returns:
        Dictionary of environment variables.
    """
    env = os.environ.copy()

    if config.force_color:
        env["FORCE_COLOR"] = "1"

    return env


class AnsiSequenceBuffer:
    """Buffer for handling incomplete ANSI escape sequences."""

    def __init__(self) -> None:
        """Initialise ANSI sequence buffer."""
        self._buffer = ""
        # Pattern to match incomplete ANSI escape sequences (missing final character)
        self._incomplete_pattern = re.compile(r"\x1b\[[0-9;]*$")

    def process_line(self, line: str) -> Optional[str]:
        """
        Process a line of output, buffering incomplete ANSI sequences.

        Args:
            line: Line of output to process.

        Returns:
            Complete line with ANSI sequences, or None if buffering.
        """
        # Strip newline for processing
        clean_line = line.rstrip("\n\r")

        # Combine with any buffered content
        full_line = self._buffer + clean_line

        # Check if line ends with incomplete ANSI sequence
        if self._incomplete_pattern.search(clean_line):
            # Buffer the entire line
            self._buffer = full_line
            return None

        # If we have buffered content, return the combined result
        if self._buffer:
            result = full_line
            self._buffer = ""
            return result

        # No buffering needed, return as-is
        return clean_line

    def flush(self) -> str:
        """
        Flush any remaining buffered content.

        Returns:
            Buffered content, if any.
        """
        result = self._buffer
        self._buffer = ""
        return result


def get_obvyr_agent_user() -> str:
    """
    Retrieves the user running the agent based on the OBVYR_AGENT_USER environment variable.
    This allows for maximum configurability and control by the customer.
    """
    user = os.getenv("OBVYR_AGENT_USER")
    if user:
        logger.info(f"Using user specified by OBVYR_AGENT_USER: {user}")
        return user

    # Default if the user hasn't specified anything
    logger.warning("OBVYR_AGENT_USER not set. Using default: 'unknown_user'")
    return "unknown_user"


def run_command(
    command: List[str],
    stream_callback: Optional[Callable[[str], None]] = None,
    config: Optional[CommandExecutionConfig] = None,
) -> RunCommandResponse:
    """
    Executes a system command with configurable output handling.

    Args:
        command: List of command arguments.
        stream_callback: Optional callback for real-time output streaming.
        config: Configuration for execution behaviour.

    Returns:
        RunCommandResponse object.
    """
    # Use default config if none provided
    if config is None:
        config = CommandExecutionConfig()

    user = get_obvyr_agent_user()
    start_time = time.time()

    # Determine execution mode
    execution_mode = determine_execution_mode(config)

    try:
        # Build environment variables
        env = build_environment_variables(config)

        # Use bytes mode to preserve ANSI color codes
        process = subprocess.Popen(  # noqa: S603
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        logger.info(f"Executed command: {' '.join(command)}")

        # Both modes use progressive output consumption to prevent pipe buffer overflow
        output_lines = []
        ansi_buffer = (
            AnsiSequenceBuffer()
            if execution_mode == OutputMode.STREAM
            else None
        )

        # Process stdout - guaranteed to exist with stdout=subprocess.PIPE
        assert process.stdout is not None  # Type assertion for mypy
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break

            if line:
                # Decode bytes to string, preserving ANSI codes
                decoded_line = line.decode("utf-8", errors="replace")
                output_lines.append(decoded_line)

                # Only stream in STREAM mode, collect silently in BATCH mode
                if execution_mode == OutputMode.STREAM and stream_callback:
                    # Process through ANSI buffer for smart streaming
                    if (
                        ansi_buffer
                    ):  # pragma: no cover - ansi_buffer is None in BATCH mode, difficult to test
                        processed_line = ansi_buffer.process_line(decoded_line)
                        if processed_line is not None:
                            stream_callback(processed_line)

        # Flush any remaining buffered content (only in STREAM mode)
        if (
            execution_mode == OutputMode.STREAM
            and stream_callback
            and ansi_buffer
        ):
            remaining = ansi_buffer.flush()
            if remaining:
                stream_callback(remaining)

        returncode = process.returncode
        output = "".join(output_lines).rstrip()

    except Exception as e:
        exception_type = e.__class__.__name__
        exception_string = f"{exception_type}: {e}"
        logger.error(
            f"Failed to execute command: {command}. {exception_string}"
        )
        output = exception_string
        returncode = -1

    end_time = time.time()
    execution_time = end_time - start_time

    return RunCommandResponse(
        command=command,
        output=output,
        returncode=returncode,
        user=user,
        execution_time=execution_time,
    )
