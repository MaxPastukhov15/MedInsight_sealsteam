"""Tests for analytical scenarios.

Тесты для всех 5 сценариев.
"""

import pytest
from scenarios.scenario_1_disease_analysis import DiseaseAnalysisScenario
from scenarios.scenario_2_trend_analysis import TrendAnalysisScenario
from scenarios.scenario_3_forecast import ForecastScenario
from scenarios.scenario_4_recommendations import RecommendationsScenario
from scenarios.scenario_5_pattern_detection import PatternDetectionScenario


@pytest.mark.asyncio
async def test_disease_analysis_scenario() -> None:
    """Test disease analysis scenario."""
    scenario = DiseaseAnalysisScenario()
    params = {"disease_name": "грипп", "region": "Санкт-Петербург", "days": 7}

    result = await scenario.run(params)

    assert "current_cases" in result
    assert "deaths" in result
    assert "mortality_rate" in result
    assert "status" in result
    assert result["status"] in ["RISING", "FALLING", "STABLE"]


@pytest.mark.asyncio
async def test_trend_analysis_scenario() -> None:
    """Test trend analysis scenario."""
    scenario = TrendAnalysisScenario()
    params = {"disease_name": "грипп", "days": 14}

    result = await scenario.run(params)

    assert "trend_direction" in result
    assert "slope" in result
    assert "r_squared" in result
    assert result["trend_direction"] in ["RISING", "FALLING", "STABLE"]


@pytest.mark.asyncio
async def test_forecast_scenario() -> None:
    """Test forecast scenario."""
    scenario = ForecastScenario()
    params = {"disease_name": "грипп", "forecast_days": 14}

    result = await scenario.run(params)

    assert "predictions" in result
    assert "confidence_lower" in result
    assert "confidence_upper" in result
    assert "dates" in result
    assert len(result["predictions"]) == 14


@pytest.mark.asyncio
async def test_recommendations_scenario() -> None:
    """Test recommendations scenario."""
    scenario = RecommendationsScenario()
    params = {"disease_name": "грипп", "query": "лечение"}

    result = await scenario.run(params)

    assert "recommendations" in result


@pytest.mark.asyncio
async def test_pattern_detection_scenario() -> None:
    """Test pattern detection scenario."""
    scenario = PatternDetectionScenario()
    params = {
        "disease_name": "грипп",
        "pattern_type": "anomalies",
    }

    result = await scenario.run(params)

    assert "pattern_type" in result
    assert result["pattern_type"] == "anomalies"
