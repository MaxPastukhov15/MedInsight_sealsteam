"""Text embeddings for RAG."""

from typing import List

import numpy as np
from monitoring.logging_config import logger

# TODO: Install sentence-transformers
# from sentence_transformers import SentenceTransformer



class EmbeddingModel:
    """Embedding model for text vectorization."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize embedding model.

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        # TODO: Uncomment when sentence-transformers is installed
        # self.model = SentenceTransformer(model_name)
        logger.info("embedding_model_initialized", model=model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings.

        Args:
            texts: List of texts to encode

        Returns:
            Array of embeddings
        """
        # TODO: Uncomment when sentence-transformers is installed
        # return self.model.encode(texts)
        logger.warning("using_mock_embeddings")
        return np.random.rand(len(texts), 384)  # Mock embeddings


# Global embedding model
embedding_model = EmbeddingModel()
