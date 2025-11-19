"""RAG (Retrieval Augmented Generation) pipeline."""

from typing import Any, Dict, List

from monitoring.logging_config import logger
from rag.knowledge_base import knowledge_base


class RAGPipeline:
    """RAG pipeline for generating recommendations."""

    def __init__(self, top_k: int = 5) -> None:
        """Initialize RAG pipeline.

        Args:
            top_k: Number of documents to retrieve
        """
        self.top_k = top_k
        logger.info("rag_pipeline_initialized", top_k=top_k)

    async def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents.

        Args:
            query: Search query

        Returns:
            List of relevant documents
        """
        return await knowledge_base.search(query, n_results=self.top_k)

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context.

        Args:
            documents: Retrieved documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "Контекст не найден."

        context_parts = []
        for idx, doc in enumerate(documents, 1):
            context_parts.append(f"Документ {idx}:\n{doc['content']}\n")

        return "\n".join(context_parts)

    async def generate_prompt(
        self,
        query: str,
        system_prompt: str = "",
    ) -> str:
        """Generate prompt with retrieved context.

        Args:
            query: User query
            system_prompt: System prompt template

        Returns:
            Complete prompt with context
        """
        # Retrieve relevant documents
        documents = await self.retrieve(query)

        # Format context
        context = self.format_context(documents)

        # Generate prompt
        prompt = f"""{system_prompt}

Контекст из базы знаний:
{context}

Вопрос пользователя:
{query}

Ответ:"""

        logger.info(
            "rag_prompt_generated",
            query_length=len(query),
            context_length=len(context),
            documents_count=len(documents),
        )

        return prompt


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()
