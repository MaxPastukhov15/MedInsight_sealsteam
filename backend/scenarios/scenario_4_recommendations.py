"""Scenario 4: Recommendations using RAG."""

from typing import Any, Dict

from monitoring.logging_config import logger
from rag.rag_pipeline import rag_pipeline
from scenarios.base import Scenario


class RecommendationsScenario(Scenario):
    """Generate medical recommendations using RAG."""

    def __init__(self) -> None:
        """Initialize recommendations scenario."""
        super().__init__("recommendations")

    def validate(self, params: Dict[str, Any]) -> bool:
        """Validate parameters.

        Args:
            params: Must contain disease_name or query

        Returns:
            True if valid
        """
        return "disease_name" in params or "query" in params

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recommendations generation.

        Args:
            params: {
                disease_name: Optional[str],
                query: Optional[str],
                context: Optional[str]
            }

        Returns:
            {
                recommendations: str,
                sources: List[str],
                confidence: float
            }
        """
        disease_name = params.get("disease_name")
        query = params.get("query", "")
        context = params.get("context", "")

        # Build search query
        if disease_name:
            search_query = f"Рекомендации по лечению: {disease_name}"
        else:
            search_query = query

        if context:
            search_query += f" {context}"

        logger.info(
            "generating_recommendations",
            disease=disease_name,
            query=search_query,
        )

        # TODO: Use RAG pipeline to retrieve and generate
        # 1. Retrieve relevant protocols
        # 2. Format context
        # 3. Generate recommendations with LLM
        # 4. Extract sources

        # Mock implementation
        prompt = await rag_pipeline.generate_prompt(
            query=search_query,
            system_prompt="Ты медицинский эксперт. Предоставь рекомендации.",
        )

        return {
            "recommendations": "Рекомендации будут сгенерированы с LLM",
            "sources": [],
            "confidence": 0.85,
            "prompt_preview": prompt[:200] + "...",
        }
