"""
Unit tests for the vector database service.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import os

from backend.src.services.vector_db import VectorDBService, get_vector_db_service


class TestVectorDBService:
    """Unit tests for VectorDBService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def vector_db_service(self, temp_dir):
        """Create a vector database service for testing."""
        return VectorDBService(persist_directory=temp_dir)
    
    def test_initialization(self, temp_dir):
        """Test service initialization."""
        service = VectorDBService(persist_directory=temp_dir)
        assert service.persist_directory == temp_dir
        assert service.collection_name == "component_datasheets"
        assert service._client is None
        assert service._collection is None
        
        # Check that directory was created
        assert os.path.exists(temp_dir)
    
    def test_initialization_creates_directory(self):
        """Test that initialization creates persist directory."""
        temp_dir = tempfile.mkdtemp()
        test_dir = os.path.join(temp_dir, "new_dir")
        
        try:
            service = VectorDBService(persist_directory=test_dir)
            assert os.path.exists(test_dir)
        finally:
            shutil.rmtree(temp_dir)
    
    @patch('backend.src.services.vector_db.chromadb.PersistentClient')
    def test_get_client_creation(self, mock_client_class, vector_db_service):
        """Test ChromaDB client creation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = vector_db_service._get_client()
        
        assert client == mock_client
        assert vector_db_service._client == mock_client
        mock_client_class.assert_called_once()
    
    @patch('backend.src.services.vector_db.chromadb.PersistentClient')
    def test_get_client_singleton(self, mock_client_class, vector_db_service):
        """Test that client is created only once."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client1 = vector_db_service._get_client()
        client2 = vector_db_service._get_client()
        
        assert client1 == client2 == mock_client
        mock_client_class.assert_called_once()
    
    @patch('backend.src.services.vector_db.get_embedding_service')
    @patch('backend.src.services.vector_db.chromadb.PersistentClient')
    def test_get_collection_existing(self, mock_client_class, mock_get_embedding_service, vector_db_service):
        """Test getting existing collection."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_embedding_service = Mock()
        
        mock_client_class.return_value = mock_client
        mock_client.get_collection.return_value = mock_collection
        mock_get_embedding_service.return_value = mock_embedding_service
        
        collection = vector_db_service._get_collection()
        
        assert collection == mock_collection
        assert vector_db_service._collection == mock_collection
        mock_client.get_collection.assert_called_once()
        mock_client.create_collection.assert_not_called()
    
    @patch('backend.src.services.vector_db.get_embedding_service')
    @patch('backend.src.services.vector_db.chromadb.PersistentClient')
    def test_get_collection_create_new(self, mock_client_class, mock_get_embedding_service, vector_db_service):
        """Test creating new collection when it doesn't exist."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_embedding_service = Mock()
        
        mock_client_class.return_value = mock_client
        mock_client.get_collection.side_effect = ValueError("Collection not found")
        mock_client.create_collection.return_value = mock_collection
        mock_get_embedding_service.return_value = mock_embedding_service
        
        collection = vector_db_service._get_collection()
        
        assert collection == mock_collection
        assert vector_db_service._collection == mock_collection
        mock_client.get_collection.assert_called_once()
        mock_client.create_collection.assert_called_once()
    
    @patch.object(VectorDBService, '_get_collection')
    def test_add_document_chunks(self, mock_get_collection, vector_db_service):
        """Test adding document chunks."""
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection
        
        chunks = ["chunk1", "chunk2", "chunk3"]
        metadata_list = [{"key": "value1"}, {"key": "value2"}, {"key": "value3"}]
        
        doc_ids = vector_db_service.add_document_chunks(chunks, metadata_list)
        
        assert len(doc_ids) == 3
        assert all(isinstance(doc_id, str) for doc_id in doc_ids)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args[1]["documents"] == chunks
        assert call_args[1]["metadatas"] == metadata_list
        assert len(call_args[1]["ids"]) == 3
    
    def test_add_document_chunks_mismatched_lengths(self, vector_db_service):
        """Test that mismatched chunk and metadata lengths raise ValueError."""
        chunks = ["chunk1", "chunk2"]
        metadata_list = [{"key": "value1"}]  # Different length
        
        with pytest.raises(ValueError, match="Number of chunks must match"):
            vector_db_service.add_document_chunks(chunks, metadata_list)
    
    @patch.object(VectorDBService, '_get_collection')
    def test_search_similar(self, mock_get_collection, vector_db_service):
        """Test searching for similar documents."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['doc1', 'doc2']],
            'metadatas': [[{'key': 'value1'}, {'key': 'value2'}]],
            'distances': [[0.1, 0.2]]
        }
        mock_get_collection.return_value = mock_collection
        
        documents, metadata, distances = vector_db_service.search_similar("test query", n_results=2)
        
        assert documents == ['doc1', 'doc2']
        assert metadata == [{'key': 'value1'}, {'key': 'value2'}]
        assert distances == [0.1, 0.2]
        
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=2,
            where=None
        )
    
    @patch.object(VectorDBService, '_get_collection')
    def test_search_similar_with_filter(self, mock_get_collection, vector_db_service):
        """Test searching with metadata filter."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['doc1']],
            'metadatas': [[{'category': 'sensor'}]],
            'distances': [[0.1]]
        }
        mock_get_collection.return_value = mock_collection
        
        where_filter = {"category": "sensor"}
        documents, metadata, distances = vector_db_service.search_similar(
            "test query", n_results=1, where=where_filter
        )
        
        assert len(documents) == 1
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=1,
            where=where_filter
        )
    
    @patch.object(VectorDBService, 'search_similar')
    def test_search_by_category(self, mock_search_similar, vector_db_service):
        """Test category-specific search."""
        mock_search_similar.return_value = (['doc1'], [{'category': 'sensor'}], [0.1])
        
        documents, metadata, distances = vector_db_service.search_by_category(
            "temperature", "sensor", n_results=1
        )
        
        assert documents == ['doc1']
        mock_search_similar.assert_called_once_with(
            "temperature", 1, {"category": "sensor"}
        )
    
    @patch.object(VectorDBService, '_get_collection')
    def test_get_collection_stats(self, mock_get_collection, vector_db_service):
        """Test getting collection statistics."""
        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_get_collection.return_value = mock_collection
        
        stats = vector_db_service.get_collection_stats()
        
        expected_stats = {
            "total_documents": 42,
            "collection_name": "component_datasheets",
            "persist_directory": vector_db_service.persist_directory
        }
        assert stats == expected_stats
    
    @patch.object(VectorDBService, '_get_collection')
    def test_get_collection_stats_error(self, mock_get_collection, vector_db_service):
        """Test collection stats with error."""
        mock_collection = Mock()
        mock_collection.count.side_effect = Exception("Database error")
        mock_get_collection.return_value = mock_collection
        
        stats = vector_db_service.get_collection_stats()
        
        assert "error" in stats
        assert stats["error"] == "Database error"
    
    @patch.object(VectorDBService, '_get_client')
    def test_delete_collection(self, mock_get_client, vector_db_service):
        """Test deleting collection."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        vector_db_service.delete_collection()
        
        mock_client.delete_collection.assert_called_once_with(name="component_datasheets")
        assert vector_db_service._collection is None


class TestVectorDBServiceGlobal:
    """Test global vector database service instance."""
    
    def test_get_vector_db_service_singleton(self):
        """Test that get_vector_db_service returns singleton."""
        service1 = get_vector_db_service()
        service2 = get_vector_db_service()
        
        assert service1 is service2
        assert isinstance(service1, VectorDBService)
    
    @patch('backend.src.services.vector_db._vector_db_service', None)
    def test_get_vector_db_service_creates_new_instance(self):
        """Test that get_vector_db_service creates new instance when needed."""
        service = get_vector_db_service()
        assert isinstance(service, VectorDBService)
        assert service.collection_name == "component_datasheets"