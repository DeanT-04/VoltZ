"""
Embedding service for generating and managing text embeddings using sentence-transformers.
"""

import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import threading

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._lock = threading.Lock()
        
    def _get_model(self) -> SentenceTransformer:
        """Lazy load the embedding model (thread-safe)."""
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info(f"Loading embedding model: {self.model_name}")
                    self._model = SentenceTransformer(self.model_name)
                    logger.info("Embedding model loaded successfully")
        return self._model
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
            
        model = self._get_model()
        embedding = model.encode([text], convert_to_numpy=True)[0]
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embeddings, each as a list of float values
        """
        if not texts:
            return []
            
        # Filter out empty texts
        valid_texts = [text for text in texts if text.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")
            
        model = self._get_model()
        embeddings = model.encode(valid_texts, convert_to_numpy=True)
        return [embedding.tolist() for embedding in embeddings]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        model = self._get_model()
        return model.get_sentence_embedding_dimension()


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service