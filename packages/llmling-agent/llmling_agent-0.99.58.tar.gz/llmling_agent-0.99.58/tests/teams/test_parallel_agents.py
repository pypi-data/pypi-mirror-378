"""Tests for parallel agent execution."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
import pytest

from llmling_agent import AgentPool, AgentsManifest, Team, TeamRun


class _TestOutput(BaseModel):
    """Expected output format."""

    message: str


def make_test_response(prompt: str) -> _TestOutput:
    """Callback for test agent responses."""
    return _TestOutput(message=f"Response to: {prompt}")


TEST_CONFIG = f"""\
responses:
  _TestOutput:
    response_schema:
        type: inline
        description: Simple test output
        fields:
            message:
                type: str
                description: Message from agent

agents:
  agent_1:
    name: First Agent
    description: First test agent
    provider:
      type: callback
      callback: {__name__}.make_test_response
    model: test
    result_type: _TestOutput
    system_prompts:
      - You are the first agent

  agent_2:
    name: Second Agent
    description: Second test agent
    provider:
      type: callback
      callback: {__name__}.make_test_response
    model: test
    result_type: _TestOutput
    system_prompts:
      - You are the second agent
"""


@pytest.mark.asyncio
async def test_parallel_execution():
    """Test parallel execution of multiple agents."""
    manifest = AgentsManifest.from_yaml(TEST_CONFIG)

    async with AgentPool[None](manifest) as pool:
        group: Team[Any] = pool.create_team(["agent_1", "agent_2"])

        prompt = "Test input"
        responses = await group.execute(prompt)
        # Verify execution
        assert len(responses) == 2  # noqa: PLR2004
        assert all(r.success for r in responses)
        assert all(r.message.data.message == f"Response to: {prompt}" for r in responses)  # type: ignore

        # Verify agent names
        agent_names = {r.message.name for r in responses}  # type: ignore
        assert agent_names == {"agent_1", "agent_2"}


@pytest.mark.asyncio
async def test_sequential_execution():
    """Test sequential execution through agent chain."""
    manifest: AgentsManifest = AgentsManifest.from_yaml(TEST_CONFIG)

    async with AgentPool[None](manifest) as pool:
        group: TeamRun[Any, Any] = pool.create_team_run(["agent_1", "agent_2"])

        prompt = "Test input"
        responses = await group.execute(prompt)

        # Verify execution order
        assert len(responses) == 2  # noqa: PLR2004
        assert all(r.success for r in responses)
        agent_order = [r.message.name for r in responses]  # type: ignore
        assert agent_order == ["agent_1", "agent_2"]

        # Verify message chain
        first_response = responses[0].message.data.message  # type: ignore
        assert first_response == f"Response to: {prompt}"

        second_response = responses[1].message.data.message  # type: ignore
        expected_input = "Response to: Test input"  # Just care about the content
        assert expected_input in second_response


# @pytest.mark.asyncio
# async def test_shared_context():
#     """Test that AgentGroup properly sets shared context."""
#     manifest = AgentsManifest.from_yaml(TEST_CONFIG)
#     shared_data = {"key": "shared_value"}

#     async with AgentPool[None](manifest) as pool:
#         # Get agents before group creation
#         agent1 = pool.get_agent("agent_1")
#         agent2 = pool.get_agent("agent_2")

#         # Verify no shared context before group
#         assert agent1.context.data is None
#         assert agent2.context.data is None

#         # Create team with shared context
#         _group = pool.create_team([agent1, agent2], shared_deps=shared_data)

#         # Verify shared context was set for both agents
#         assert agent1.context.data == shared_data
#         assert agent2.context.data == shared_data
