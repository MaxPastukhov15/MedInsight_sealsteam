"""ChromaDB integration for vector storage."""

from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

from monitoring.logging_config import logger


class VectorDatabase:
    """ChromaDB wrapper for vector storage and retrieval."""

    def __init__(self, persist_directory: str = "./chroma_data") -> None:
        """Initialize ChromaDB client.

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )
        logger.info("chromadb_initialized", directory=persist_directory)

    def get_or_create_collection(self, name: str) -> Any:
        """Get or create a collection.

        Args:
            name: Collection name

        Returns:
            ChromaDB collection
        """
        return self.client.get_or_create_collection(name=name)

    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to collection.

        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents
        """
        collection = self.get_or_create_collection(collection_name)

        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        collection.add(
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids,
        )
        logger.info(
            "documents_added",
            collection=collection_name,
            count=len(documents),
        )

    async def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """Query similar documents.

        Args:
            collection_name: Name of the collection
            query_texts: Query texts
            n_results: Number of results to return

        Returns:
            Query results with documents and distances
        """
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_texts=query_texts,
            n_results=n_results,
        )
        logger.info(
            "vector_query_executed",
            collection=collection_name,
            n_results=n_results,
        )
        return results


# Global vector database instance
vector_db = VectorDatabase()
