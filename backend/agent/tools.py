"""Agent tools for LangGraph.

5 инструментов для AI-агента:
1. analyze_disease - анализ текущей заболеваемости
2. get_trends - анализ трендов
3. forecast_disease - прогнозирование
4. get_recommendations - рекомендации
5. detect_patterns - поиск паттернов

Использование:
    from agent.tools import agent_tools
    result = await agent_tools.analyze_disease("грипп")
"""

from typing import Any, Dict, List

from monitoring.logging_config import logger
from scenarios.scenario_1_disease_analysis import DiseaseAnalysisScenario
from scenarios.scenario_2_trend_analysis import TrendAnalysisScenario
from scenarios.scenario_3_forecast import ForecastScenario
from scenarios.scenario_4_recommendations import RecommendationsScenario
from scenarios.scenario_5_pattern_detection import PatternDetectionScenario


class AgentTools:
    """Tools available to the agent."""

    def __init__(self) -> None:
        """Initialize all 5 scenario tools."""
        self.disease_analysis = DiseaseAnalysisScenario()
        self.trend_analysis = TrendAnalysisScenario()
        self.forecast = ForecastScenario()
        self.recommendations = RecommendationsScenario()
        self.pattern_detection = PatternDetectionScenario()
        logger.info("agent_tools_initialized", tools_count=5)

    async def analyze_disease(
        self,
        disease_name: str,
        region: str = None,
        age_group: str = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Tool 1: Analyze disease statistics."""
        params = {
            "disease_name": disease_name,
            "region": region,
            "age_group": age_group,
            "days": days,
        }
        return await self.disease_analysis.run(params)

    async def get_trends(
        self,
        disease_name: str,
        region: str = None,
        days: int = 14,
    ) -> Dict[str, Any]:
        """Tool 2: Get disease trends."""
        params = {
            "disease_name": disease_name,
            "region": region,
            "days": days,
        }
        return await self.trend_analysis.run(params)

    async def forecast_disease(
        self,
        disease_name: str,
        region: str = None,
        forecast_days: int = 14,
    ) -> Dict[str, Any]:
        """Tool 3: Forecast disease cases."""
        params = {
            "disease_name": disease_name,
            "region": region,
            "forecast_days": forecast_days,
        }
        return await self.forecast.run(params)

    async def get_recommendations(
        self,
        disease_name: str = None,
        query: str = None,
        context: str = None,
    ) -> Dict[str, Any]:
        """Tool 4: Get medical recommendations."""
        params = {
            "disease_name": disease_name,
            "query": query,
            "context": context,
        }
        return await self.recommendations.run(params)

    async def detect_patterns(
        self,
        disease_name: str,
        pattern_type: str,
        region: str = None,
    ) -> Dict[str, Any]:
        """Tool 5: Detect patterns in disease data."""
        params = {
            "disease_name": disease_name,
            "pattern_type": pattern_type,
            "region": region,
        }
        return await self.pattern_detection.run(params)


agent_tools = AgentTools()
