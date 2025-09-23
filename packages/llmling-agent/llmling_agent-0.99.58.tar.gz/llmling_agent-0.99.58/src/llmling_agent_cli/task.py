"""Task execution command."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import typer as t

from llmling_agent_cli import resolve_agent_config


if TYPE_CHECKING:
    from llmling_agent import AgentsManifest


TASK_HELP = """
Execute a defined task with the specified agent.

Example:
    llmling-agent task docs write_api_docs --prompt "Include code examples"
    llmling-agent task docs write_api_docs --log-level DEBUG
"""


async def execute_job(
    agent_name: str,
    task_name: str,
    config: AgentsManifest,
    *,
    prompt: str | None = None,
):
    """Execute task with agent."""
    from llmling_agent import AgentPool

    async with AgentPool[None](config) as pool:
        # Get both agent and task
        agent = pool.get_agent(agent_name)
        task = pool.get_job(task_name)

        # Create final prompt from task and additional input
        task_prompt = task.prompt
        if prompt:
            task_prompt = f"{task_prompt}\n\nAdditional instructions:\n{prompt}"

        result = await agent.run(task_prompt)
        return result.data


def task_command(
    agent_name: str = t.Argument(help="Name of agent to run task with"),
    task_name: str = t.Argument(help="Name of task to execute"),
    config: str | None = t.Option(
        None, "--config", "-c", help="Agent configuration file"
    ),
    prompt: str | None = t.Option(None, "--prompt", "-p", help="Additional prompt"),
    log_level: str = t.Option(
        "WARNING",
        "--log-level",
        "-l",
        help="Log level (DEBUG, INFO, WARNING, ERROR)",
        case_sensitive=False,
    ),
):
    """Execute a task with the specified agent."""
    try:
        # Set up logging
        level = getattr(logging, log_level.upper())
        logging.basicConfig(level=level)
        logger = logging.getLogger("llmling_agent.task")
        logger.debug("Starting task execution: %s", task_name)

        # Resolve configuration path
        try:
            config_path = resolve_agent_config(config)
            logger.debug("Using config from: %s", config_path)
        except ValueError as e:
            msg = str(e)
            raise t.BadParameter(msg) from e

        # Load manifest
        from llmling_agent import AgentsManifest

        manifest = AgentsManifest.from_file(config_path)

        # Execute task
        result = asyncio.run(execute_job(agent_name, task_name, manifest, prompt=prompt))
        print(result)

    except Exception as e:
        t.echo(f"Error: {e}", err=True)
        if level <= logging.DEBUG:
            import traceback

            t.echo(traceback.format_exc(), err=True)
        raise t.Exit(1) from e


if __name__ == "__main__":
    task_command()
