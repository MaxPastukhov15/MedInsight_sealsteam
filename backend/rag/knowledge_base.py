"""Knowledge base management for medical protocols."""

from typing import List, Dict, Any
from pathlib import Path

from rag.vector_db import vector_db
from monitoring.logging_config import logger


class KnowledgeBase:
    """Manage medical protocols knowledge base."""

    def __init__(self, collection_name: str = "medical_protocols") -> None:
        """Initialize knowledge base.

        Args:
            collection_name: ChromaDB collection name
        """
        self.collection_name = collection_name
        logger.info("knowledge_base_initialized", collection=collection_name)

    async def load_protocols(self, protocols_dir: str) -> None:
        """Load medical protocols from directory.

        Args:
            protocols_dir: Directory with protocol documents
        """
        protocols_path = Path(protocols_dir)
        if not protocols_path.exists():
            logger.warning(
                "protocols_directory_not_found",
                path=protocols_dir,
            )
            return

        documents = []
        metadatas = []
        ids = []

        for idx, file_path in enumerate(protocols_path.glob("*.txt")):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(content)
                metadatas.append({
                    "filename": file_path.name,
                    "type": "protocol",
                })
                ids.append(f"protocol_{idx}")

        if documents:
            await vector_db.add_documents(
                collection_name=self.collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(
                "protocols_loaded",
                count=len(documents),
                collection=self.collection_name,
            )

    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant protocols.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        results = await vector_db.query(
            collection_name=self.collection_name,
            query_texts=[query],
            n_results=n_results,
        )

        # Format results
        formatted_results = []
        if results.get("documents"):
            for idx, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][idx] if results.get("metadatas") else {},
                    "distance": results["distances"][0][idx] if results.get("distances") else 0,
                })

        logger.info(
            "knowledge_base_search",
            query=query,
            results_count=len(formatted_results),
        )

        return formatted_results


# Global knowledge base instance
knowledge_base = KnowledgeBase()
