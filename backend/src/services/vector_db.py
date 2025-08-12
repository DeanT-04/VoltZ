"""
Vector database service using ChromaDB for component search and retrieval.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import uuid

from .embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for managing vector database operations with ChromaDB."""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """
        Initialize the vector database service.
        
        Args:
            persist_directory: Directory to persist the ChromaDB data
        """
        self.persist_directory = persist_directory
        self._client: Optional[chromadb.Client] = None
        self._collection: Optional[chromadb.Collection] = None
        self.collection_name = "component_datasheets"
        
        # Ensure the persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
    def _get_client(self) -> chromadb.Client:
        """Get or create the ChromaDB client."""
        if self._client is None:
            logger.info(f"Initializing ChromaDB client with persist directory: {self.persist_directory}")
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        return self._client
    
    def _get_collection(self) -> chromadb.Collection:
        """Get or create the component datasheets collection."""
        if self._collection is None:
            client = self._get_client()
            
            # Use our custom embedding service
            embedding_service = get_embedding_service()
            
            # Create a custom embedding function that uses our service
            class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction):
                def __init__(self):
                    pass
                    
                def __call__(self, input: List[str]) -> List[List[float]]:
                    return embedding_service.generate_embeddings(input)
            
            try:
                self._collection = client.get_collection(
                    name=self.collection_name,
                    embedding_function=CustomEmbeddingFunction()
                )
                logger.info(f"Retrieved existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self._collection = client.create_collection(
                    name=self.collection_name,
                    embedding_function=CustomEmbeddingFunction(),
                    metadata={"description": "Component datasheet chunks with embeddings"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        return self._collection
    
    def add_document_chunks(
        self, 
        chunks: List[str], 
        metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add document chunks to the vector database.
        
        Args:
            chunks: List of text chunks to add
            metadata_list: List of metadata dictionaries for each chunk
            
        Returns:
            List of document IDs that were added
        """
        if len(chunks) != len(metadata_list):
            raise ValueError("Number of chunks must match number of metadata entries")
            
        collection = self._get_collection()
        
        # Generate unique IDs for each chunk
        doc_ids = [str(uuid.uuid4()) for _ in chunks]
        
        try:
            collection.add(
                documents=chunks,
                metadatas=metadata_list,
                ids=doc_ids
            )
            logger.info(f"Added {len(chunks)} document chunks to vector database")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add document chunks: {e}")
            raise
    
    def search_similar(
        self, 
        query: str, 
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """
        Search for similar document chunks.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            where: Optional metadata filter conditions
            
        Returns:
            Tuple of (documents, metadata, distances)
        """
        collection = self._get_collection()
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Extract results
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            logger.info(f"Found {len(documents)} similar documents for query")
            return documents, metadatas, distances
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            raise
    
    def search_by_category(
        self, 
        query: str, 
        category: str, 
        n_results: int = 5
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """
        Search for components in a specific category.
        
        Args:
            query: Search query text
            category: Component category (e.g., "microcontroller", "sensor")
            n_results: Number of results to return
            
        Returns:
            Tuple of (documents, metadata, distances)
        """
        where_filter = {"category": category}
        return self.search_similar(query, n_results, where_filter)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection."""
        collection = self._get_collection()
        
        try:
            count = collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def delete_collection(self) -> None:
        """Delete the entire collection (use with caution)."""
        client = self._get_client()
        try:
            client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise


# Global vector database service instance
_vector_db_service: Optional[VectorDBService] = None


def get_vector_db_service() -> VectorDBService:
    """Get the global vector database service instance."""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service