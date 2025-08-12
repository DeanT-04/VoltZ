"""
Unit tests for the embedding service.
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from backend.src.services.embeddings import EmbeddingService, get_embedding_service


class TestEmbeddingService:
    """Unit tests for EmbeddingService."""
    
    @pytest.fixture
    def embedding_service(self):
        """Create an embedding service for testing."""
        return EmbeddingService()
    
    def test_initialization(self):
        """Test service initialization."""
        service = EmbeddingService()
        assert service.model_name == "all-MiniLM-L6-v2"
        assert service._model is None
    
    def test_initialization_with_custom_model(self):
        """Test service initialization with custom model."""
        service = EmbeddingService(model_name="custom-model")
        assert service.model_name == "custom-model"
    
    @patch('backend.src.services.embeddings.SentenceTransformer')
    def test_lazy_model_loading(self, mock_sentence_transformer, embedding_service):
        """Test that model is loaded lazily."""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        # Model should not be loaded initially
        assert embedding_service._model is None
        
        # Access model should trigger loading
        model = embedding_service._get_model()
        
        assert model == mock_model
        assert embedding_service._model == mock_model
        mock_sentence_transformer.assert_called_once_with("all-MiniLM-L6-v2")
    
    @patch('backend.src.services.embeddings.SentenceTransformer')
    def test_model_loading_thread_safety(self, mock_sentence_transformer, embedding_service):
        """Test that model loading is thread-safe."""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        # Multiple calls should only create one model instance
        model1 = embedding_service._get_model()
        model2 = embedding_service._get_model()
        
        assert model1 == model2 == mock_model
        mock_sentence_transformer.assert_called_once()
    
    @patch('backend.src.services.embeddings.SentenceTransformer')
    def test_generate_embedding_single_text(self, mock_sentence_transformer, embedding_service):
        """Test generating embedding for single text."""
        mock_model = Mock()
        mock_embedding = np.array([0.1, 0.2, 0.3])
        mock_model.encode.return_value = np.array([mock_embedding])
        mock_sentence_transformer.return_value = mock_model
        
        result = embedding_service.generate_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]
        mock_model.encode.assert_called_once_with(["test text"], convert_to_numpy=True)
    
    def test_generate_embedding_empty_text(self, embedding_service):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            embedding_service.generate_embedding("")
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            embedding_service.generate_embedding("   ")
    
    @patch('backend.src.services.embeddings.SentenceTransformer')
    def test_generate_embeddings_multiple_texts(self, mock_sentence_transformer, embedding_service):
        """Test generating embeddings for multiple texts."""
        mock_model = Mock()
        mock_embeddings = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
        mock_model.encode.return_value = mock_embeddings
        mock_sentence_transformer.return_value = mock_model
        
        texts = ["text1", "text2", "text3"]
        result = embedding_service.generate_embeddings(texts)
        
        expected = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        assert result == expected
        mock_model.encode.assert_called_once_with(texts, convert_to_numpy=True)
    
    def test_generate_embeddings_empty_list(self, embedding_service):
        """Test that empty list returns empty list."""
        result = embedding_service.generate_embeddings([])
        assert result == []
    
    def test_generate_embeddings_all_empty_texts(self, embedding_service):
        """Test that all empty texts raises ValueError."""
        with pytest.raises(ValueError, match="All texts are empty"):
            embedding_service.generate_embeddings(["", "   ", "\n"])
    
    @patch('backend.src.services.embeddings.SentenceTransformer')
    def test_generate_embeddings_filters_empty_texts(self, mock_sentence_transformer, embedding_service):
        """Test that empty texts are filtered out."""
        mock_model = Mock()
        mock_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_model.encode.return_value = mock_embeddings
        mock_sentence_transformer.return_value = mock_model
        
        texts = ["text1", "", "text2", "   "]
        result = embedding_service.generate_embeddings(texts)
        
        expected = [[0.1, 0.2], [0.3, 0.4]]
        assert result == expected
        mock_model.encode.assert_called_once_with(["text1", "text2"], convert_to_numpy=True)
    
    @patch('backend.src.services.embeddings.SentenceTransformer')
    def test_get_embedding_dimension(self, mock_sentence_transformer, embedding_service):
        """Test getting embedding dimension."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model
        
        dimension = embedding_service.get_embedding_dimension()
        
        assert dimension == 384
        mock_model.get_sentence_embedding_dimension.assert_called_once()


class TestEmbeddingServiceGlobal:
    """Test global embedding service instance."""
    
    def test_get_embedding_service_singleton(self):
        """Test that get_embedding_service returns singleton."""
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        
        assert service1 is service2
        assert isinstance(service1, EmbeddingService)
    
    @patch('backend.src.services.embeddings._embedding_service', None)
    def test_get_embedding_service_creates_new_instance(self):
        """Test that get_embedding_service creates new instance when needed."""
        service = get_embedding_service()
        assert isinstance(service, EmbeddingService)
        assert service.model_name == "all-MiniLM-L6-v2"