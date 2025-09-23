"""Integration tests for process management with AgentPool."""

from __future__ import annotations

import platform

import pytest

from llmling_agent.config.capabilities import Capabilities
from llmling_agent.delegation.pool import AgentPool
from llmling_agent.models.agents import AgentConfig
from llmling_agent.models.manifest import AgentsManifest


def get_echo_command(message: str) -> tuple[str, list[str]]:
    """Get platform-appropriate echo command."""
    if platform.system() == "Windows":
        return "cmd", ["/c", "echo", message]
    return "echo", [message]


def get_sleep_command(seconds: str) -> tuple[str, list[str]]:
    """Get platform-appropriate sleep command."""
    if platform.system() == "Windows":
        return "cmd", ["/c", "timeout", seconds]
    return "sleep", [seconds]


def get_python_command() -> str:
    """Get platform-appropriate python command."""
    if platform.system() == "Windows":
        return "python"
    return "python3"


def get_temp_dir() -> str:
    """Get platform-appropriate temporary directory."""
    if platform.system() == "Windows":
        return "C:\\Windows\\Temp"
    return "/tmp"


@pytest.fixture
def process_manifest():
    """Create manifest with process management capabilities."""
    agent_config = AgentConfig(
        name="ProcessAgent",
        model="test",
        capabilities=Capabilities(
            can_manage_processes=True,
            can_read_files=True,
        ),
    )
    return AgentsManifest(agents={"process_agent": agent_config})


@pytest.mark.asyncio
async def test_process_manager_pool_integration(process_manifest):
    """Test ProcessManager is properly integrated with AgentPool."""
    async with AgentPool[None](process_manifest) as pool:
        # Verify process manager exists in pool
        assert hasattr(pool, "process_manager")

        # Verify agents can access process manager
        agent = pool.agents["process_agent"]
        assert hasattr(agent.context, "process_manager")
        assert agent.context.process_manager is pool.process_manager


@pytest.mark.asyncio
async def test_process_tools_registration(process_manifest):
    """Test that process management tools are properly registered."""
    async with AgentPool[None](process_manifest) as pool:
        agent = pool.agents["process_agent"]

        # Get available tools
        tools = await agent.tools.get_tools()
        tool_names = [tool.name for tool in tools]

        # Verify process management tools are available
        expected_tools = [
            "start_process",
            "get_process_output",
            "wait_for_process",
            "kill_process",
            "release_process",
            "list_processes",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not found"


@pytest.mark.asyncio
async def test_basic_process_workflow(process_manifest):
    """Test a complete process management workflow."""
    async with AgentPool[None](process_manifest) as pool:
        pm = pool.process_manager

        # Start a simple process (platform-aware)
        command, args = get_echo_command("Hello, World!")
        process_id = await pm.start_process(command, args)
        assert process_id.startswith("proc_")

        # Wait for completion
        exit_code = await pm.wait_for_exit(process_id)
        assert exit_code == 0

        # Check output
        output = await pm.get_output(process_id)
        assert "Hello, World!" in output.stdout

        # Clean up
        await pm.release_process(process_id)

        # Verify it's gone
        processes = pm.list_processes()
        assert process_id not in processes


@pytest.mark.asyncio
async def test_pool_cleanup_kills_processes(process_manifest):
    """Test that pool cleanup properly kills all processes."""
    async with AgentPool[None](process_manifest) as pool:
        pm = pool.process_manager

        # Start a long-running process (platform-aware)
        command, args = get_sleep_command("60")
        process_id = await pm.start_process(command, args)

        # Verify it's running
        processes = pm.list_processes()
        assert process_id in processes

        # Pool cleanup should happen automatically when exiting context

    # After context exit, we can't easily verify cleanup happened
    # but the test passes if no exceptions were raised during cleanup


@pytest.mark.asyncio
async def test_capability_requirement_enforcement():
    """Test that tools are not available without proper capabilities."""
    # Create agent without process management capability
    agent_config = AgentConfig(
        name="LimitedAgent",
        model="test",
        capabilities=Capabilities(can_manage_processes=False),
    )
    manifest = AgentsManifest(agents={"limited_agent": agent_config})

    async with AgentPool[None](manifest) as pool:
        agent = pool.agents["limited_agent"]
        tools = await agent.tools.get_tools()
        tool_names = [tool.name for tool in tools]

        # Verify process tools are NOT available
        process_tools = [
            "start_process",
            "get_process_output",
            "wait_for_process",
            "kill_process",
            "release_process",
            "list_processes",
        ]

        for process_tool in process_tools:
            assert process_tool not in tool_names, (
                f"Tool {process_tool} should not be available"
            )


@pytest.mark.asyncio
async def test_multiple_processes_management(process_manifest):
    """Test managing multiple processes simultaneously."""
    async with AgentPool[None](process_manifest) as pool:
        pm = pool.process_manager

        # Start multiple processes (platform-aware)
        cmd1, args1 = get_echo_command("Process 1")
        cmd2, args2 = get_echo_command("Process 2")
        cmd3, args3 = get_echo_command("Process 3")

        proc1 = await pm.start_process(cmd1, args1)
        proc2 = await pm.start_process(cmd2, args2)
        proc3 = await pm.start_process(cmd3, args3)

        # Verify all are tracked
        processes = pm.list_processes()
        assert len(processes) == 3  # noqa: PLR2004
        assert all(p in processes for p in [proc1, proc2, proc3])

        # Wait for all to complete
        for proc_id in [proc1, proc2, proc3]:
            exit_code = await pm.wait_for_exit(proc_id)
            assert exit_code == 0

        # Clean up all
        for proc_id in [proc1, proc2, proc3]:
            await pm.release_process(proc_id)

        # Verify all cleaned up
        processes = pm.list_processes()
        assert len(processes) == 0


@pytest.mark.skip(reason="Output limit test needs refinement")
@pytest.mark.asyncio
async def test_process_output_limit(process_manifest):
    """Test process output limiting functionality."""
    async with AgentPool[None](process_manifest) as pool:
        pm = pool.process_manager

        # Start process with small output limit
        # Use a command that generates more output than the limit (platform-aware)
        python_cmd = get_python_command()
        process_id = await pm.start_process(
            python_cmd, ["-c", "print('x' * 500)"], output_limit=50
        )

        # Wait for completion
        exit_code = await pm.wait_for_exit(process_id)
        assert exit_code == 0

        # Check that output was truncated
        output = await pm.get_output(process_id)
        assert output.truncated
        assert len(output.combined.encode()) < 500  # noqa: PLR2004

        await pm.release_process(process_id)


@pytest.mark.asyncio
async def test_error_handling_invalid_command(process_manifest):
    """Test error handling for invalid commands."""
    async with AgentPool[None](process_manifest) as pool:
        pm = pool.process_manager

        # Try to start non-existent command
        with pytest.raises(OSError, match="Failed to start process"):
            await pm.start_process("nonexistent_command_12345")


@pytest.mark.asyncio
async def test_process_info_retrieval(process_manifest):
    """Test getting detailed process information."""
    async with AgentPool[None](process_manifest) as pool:
        pm = pool.process_manager

        # Use platform-appropriate commands and working directory
        cwd = get_temp_dir()
        command, args = get_echo_command("test")

        process_id = await pm.start_process(
            command, args, cwd=cwd, env={"TEST_VAR": "test_value"}
        )

        info = await pm.get_process_info(process_id)

        assert info["process_id"] == process_id
        assert info["command"] == command
        assert info["args"] == args
        assert info["cwd"] == cwd
        assert "created_at" in info
        assert "is_running" in info

        await pm.wait_for_exit(process_id)
        await pm.release_process(process_id)
