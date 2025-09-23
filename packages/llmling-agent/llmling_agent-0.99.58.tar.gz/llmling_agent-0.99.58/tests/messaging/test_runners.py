"""Tests for AgentPool functionality."""

from __future__ import annotations

from pydantic import BaseModel
import pytest

from llmling_agent import Agent, AgentPool, AgentsManifest


class ConversationOutput(BaseModel):
    """Test output for conversation flow."""

    message: str
    conversation_index: int


def make_response(prompt: str) -> ConversationOutput:
    """Callback that tracks conversation order."""
    # Track what message we're on in the conversation
    make_response.count = getattr(make_response, "count", 0) + 1  # type: ignore
    return ConversationOutput(
        message=f"Response to: {prompt}",
        conversation_index=make_response.count,  # type: ignore
    )


TEST_CONFIG = f"""\
responses:
  ConversationOutput:
    response_schema:
        type: inline
        description: Output with conversation tracking
        fields:
            message:
                type: str
                description: Response message
            conversation_index:
                type: int
                description: Position in conversation

agents:
  test_agent:
    name: Test Agent
    description: Agent for testing conversation flow
    provider:
      type: callback
      callback: {__name__}.make_response
    model: test
    result_type: ConversationOutput
    system_prompts:
      - You are a test agent

  error_agent:
    name: Error Agent
    description: Agent that always raises errors
    model: test
    system_prompts:
      - You are an error agent
"""


@pytest.mark.asyncio
async def test_agent_pool_conversation_flow():
    """Test conversation flow maintaining history between messages."""
    manifest = AgentsManifest.from_yaml(TEST_CONFIG)

    async with AgentPool[None](manifest) as pool:
        # Get agent directly for conversation
        agent = pool.get_agent("test_agent")

        # Run multiple prompts in sequence
        responses = []
        prompts = ["Hello!", "How are you?"]

        for prompt in prompts:
            result = await agent.run(prompt)
            responses.append(result)

        # Verify correct number of responses
        assert len(responses) == 2  # noqa: PLR2004

        # Verify conversation order was maintained
        assert responses[0].data.conversation_index == 1  # type: ignore
        assert responses[1].data.conversation_index == 2  # type: ignore # noqa: PLR2004

        # Verify message content
        assert responses[0].data.message == "Response to: Hello!"  # type: ignore
        assert responses[1].data.message == "Response to: How are you?"  # type: ignore

        # Verify agent name
        assert all(r.name == "test_agent" for r in responses)


@pytest.mark.asyncio
async def test_agent_pool_validation():
    """Test AgentPool validation and error handling."""
    manifest = AgentsManifest.from_yaml(TEST_CONFIG)

    # Test getting non-existent agent
    async with AgentPool[None](manifest) as pool:
        with pytest.raises(KeyError, match="nonexistent"):
            pool.get_agent("nonexistent")


@pytest.mark.asyncio
async def test_agent_pool_team_errors():
    """Test error handling in team tasks."""
    manifest = AgentsManifest.from_yaml(TEST_CONFIG)

    async with AgentPool[None](manifest) as pool:
        # Test with non-existent team member
        with pytest.raises(KeyError, match="nonexistent"):
            pool.create_team(["test_agent", "nonexistent"])


@pytest.mark.asyncio
async def test_agent_pool_cleanup():
    """Test proper cleanup of agent resources."""
    manifest = AgentsManifest.from_yaml(TEST_CONFIG)

    # Use context manager to ensure proper cleanup
    async with AgentPool[None](manifest) as pool:
        # Add some agents
        agent: Agent[None] = pool.get_agent("test_agent")
        assert "test_agent" in pool.agents

        # Get runtime reference to check cleanup
        runtime = agent.runtime
        assert runtime is not None

        # Test manual cleanup
        await pool.cleanup()
        assert not pool.agents  # Should be empty after cleanup


@pytest.mark.asyncio
async def test_agent_pool_context_cleanup():
    """Test cleanup through context manager."""
    manifest = AgentsManifest.from_yaml(TEST_CONFIG)
    runtime_ref = None

    async with AgentPool[None](manifest) as pool:
        agent: Agent[None] = pool.get_agent("test_agent")
        runtime_ref = agent.runtime
        assert "test_agent" in pool.agents
        assert runtime_ref is not None

    # After context exit
    assert not pool.agents
