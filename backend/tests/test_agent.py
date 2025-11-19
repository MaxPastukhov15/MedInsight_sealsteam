"""Tests for AI agent.

Тесты для LangGraph агента и инструментов.
"""

import pytest
from agent.tools import agent_tools


@pytest.mark.asyncio
async def test_agent_tools_initialization() -> None:
    """Test agent tools initialization."""
    assert agent_tools is not None
    assert hasattr(agent_tools, "analyze_disease")
    assert hasattr(agent_tools, "get_trends")
    assert hasattr(agent_tools, "forecast_disease")
    assert hasattr(agent_tools, "get_recommendations")
    assert hasattr(agent_tools, "detect_patterns")


@pytest.mark.asyncio
async def test_analyze_disease_tool() -> None:
    """Test analyze_disease tool."""
    result = await agent_tools.analyze_disease(
        disease_name="грипп",
        region="Санкт-Петербург",
        days=7,
    )
    
    assert result is not None
    assert "current_cases" in result


@pytest.mark.asyncio
async def test_get_trends_tool() -> None:
    """Test get_trends tool."""
    result = await agent_tools.get_trends(
        disease_name="грипп",
        days=14,
    )
    
    assert result is not None
    assert "trend_direction" in result


# TODO: Add more comprehensive agent tests when agent.py is implemented
