"""
Unit tests for the datasheet ingestion service.
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from backend.src.services.datasheet_ingestion import DatasheetIngestionService, get_datasheet_ingestion_service


class TestDatasheetIngestionService:
    """Unit tests for DatasheetIngestionService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def ingestion_service(self, temp_dir):
        """Create a datasheet ingestion service for testing."""
        return DatasheetIngestionService(datasheet_directory=temp_dir)
    
    def test_initialization(self, temp_dir):
        """Test service initialization."""
        service = DatasheetIngestionService(datasheet_directory=temp_dir)
        assert service.datasheet_directory == Path(temp_dir)
        assert service.min_chunk_size == 1000
        assert service.max_chunk_size == 2000
        assert service.overlap_size == 200
        
        # Check that directory was created
        assert os.path.exists(temp_dir)
    
    def test_initialization_creates_directory(self):
        """Test that initialization creates datasheet directory."""
        temp_dir = tempfile.mkdtemp()
        test_dir = os.path.join(temp_dir, "new_dir")
        
        try:
            service = DatasheetIngestionService(datasheet_directory=test_dir)
            assert os.path.exists(test_dir)
        finally:
            shutil.rmtree(temp_dir)
    
    @patch('backend.src.services.datasheet_ingestion.extract_text')
    def test_extract_text_from_pdf_success(self, mock_extract_text, ingestion_service):
        """Test successful PDF text extraction."""
        mock_extract_text.return_value = "This is extracted text from PDF."
        
        result = ingestion_service.extract_text_from_pdf("test.pdf")
        
        assert result == "This is extracted text from PDF."
        mock_extract_text.assert_called_once_with("test.pdf")
    
    @patch('backend.src.services.datasheet_ingestion.extract_text')
    def test_extract_text_from_pdf_empty(self, mock_extract_text, ingestion_service):
        """Test PDF text extraction with empty result."""
        mock_extract_text.return_value = "   "  # Only whitespace
        
        result = ingestion_service.extract_text_from_pdf("test.pdf")
        
        assert result == ""
    
    @patch('backend.src.services.datasheet_ingestion.extract_text')
    def test_extract_text_from_pdf_error(self, mock_extract_text, ingestion_service):
        """Test PDF text extraction with error."""
        mock_extract_text.side_effect = Exception("PDF parsing error")
        
        with pytest.raises(Exception, match="PDF parsing error"):
            ingestion_service.extract_text_from_pdf("test.pdf")
    
    def test_clean_text(self, ingestion_service):
        """Test text cleaning functionality."""
        dirty_text = """
        Page 1 of 50
        
        This    is   a    test    document.
        
        Visit www.example.com for more info.
        
        Some special characters: @@@ ### $$$ %%%
        
        Normal text continues here.
        """
        
        cleaned = ingestion_service.clean_text(dirty_text)
        
        # Check that excessive whitespace is normalized
        assert "    " not in cleaned
        assert cleaned.count("  ") == 0  # No double spaces
        
        # Check that URLs are removed
        assert "www.example.com" not in cleaned
        
        # Check that normal text is preserved
        assert "This is a test document" in cleaned
        assert "Normal text continues here" in cleaned
        
        # Check that text starts and ends cleanly
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")
    
    def test_create_text_chunks_empty_text(self, ingestion_service):
        """Test chunking with empty text."""
        result = ingestion_service.create_text_chunks("", {"test": "metadata"})
        assert result == []
        
        result = ingestion_service.create_text_chunks("   ", {"test": "metadata"})
        assert result == []
    
    def test_create_text_chunks_short_text(self, ingestion_service):
        """Test chunking with text shorter than min_chunk_size."""
        short_text = "This is a short text."
        metadata = {"mpn": "TEST123", "manufacturer": "Test Corp"}
        
        result = ingestion_service.create_text_chunks(short_text, metadata)
        
        assert len(result) == 1
        chunk_text, chunk_metadata = result[0]
        assert chunk_text == short_text
        assert chunk_metadata["mpn"] == "TEST123"
        assert chunk_metadata["chunk_index"] == 0
        assert chunk_metadata["chunk_start"] == 0
        assert chunk_metadata["chunk_end"] == len(short_text)
    
    def test_create_text_chunks_long_text(self, ingestion_service):
        """Test chunking with text longer than max_chunk_size."""
        # Create text longer than max_chunk_size (2000 chars)
        # Use a longer text to ensure multiple chunks
        long_text = "This is a test sentence. " * 150  # ~3750 characters
        metadata = {"mpn": "TEST123", "manufacturer": "Test Corp"}
        
        result = ingestion_service.create_text_chunks(long_text, metadata)
        
        assert len(result) > 1  # Should create multiple chunks
        
        # Check each chunk
        for i, (chunk_text, chunk_metadata) in enumerate(result):
            # Check chunk size constraints
            if i < len(result) - 1:  # Not the last chunk
                assert len(chunk_text) >= ingestion_service.min_chunk_size
            assert len(chunk_text) <= ingestion_service.max_chunk_size
            
            # Check metadata
            assert chunk_metadata["mpn"] == "TEST123"
            assert chunk_metadata["manufacturer"] == "Test Corp"
            assert chunk_metadata["chunk_index"] == i
            assert "chunk_start" in chunk_metadata
            assert "chunk_end" in chunk_metadata
            assert "chunk_length" in chunk_metadata
            assert chunk_metadata["chunk_length"] == len(chunk_text)
    
    def test_create_text_chunks_sentence_boundaries(self, ingestion_service):
        """Test that chunking respects sentence boundaries."""
        # Create text with clear sentence boundaries
        sentences = [f"This is sentence number {i}." for i in range(100)]
        long_text = " ".join(sentences)
        metadata = {"test": "metadata"}
        
        result = ingestion_service.create_text_chunks(long_text, metadata)
        
        # Check that chunks end at sentence boundaries when possible
        for chunk_text, _ in result[:-1]:  # Exclude last chunk
            # Should end with sentence-ending punctuation
            assert chunk_text.rstrip().endswith(('.', '!', '?'))
    
    def test_create_text_chunks_overlap(self, ingestion_service):
        """Test that chunks have proper overlap."""
        # Create predictable text
        long_text = "Word " * 1000  # 5000 characters
        metadata = {"test": "metadata"}
        
        result = ingestion_service.create_text_chunks(long_text, metadata)
        
        if len(result) > 1:
            # Check that there's overlap between consecutive chunks
            for i in range(len(result) - 1):
                chunk1_end = result[i][1]["chunk_end"]
                chunk2_start = result[i + 1][1]["chunk_start"]
                
                # There should be overlap (chunk2_start < chunk1_end)
                overlap = chunk1_end - chunk2_start
                assert overlap > 0, f"No overlap between chunks {i} and {i+1}"
                assert overlap <= ingestion_service.overlap_size + 100  # Allow some flexibility
    
    @patch('backend.src.services.datasheet_ingestion.get_vector_db_service')
    @patch.object(DatasheetIngestionService, 'extract_text_from_pdf')
    @patch.object(DatasheetIngestionService, '_calculate_file_hash')
    def test_ingest_datasheet_success(self, mock_hash, mock_extract, mock_get_vector_db, ingestion_service):
        """Test successful datasheet ingestion."""
        # Setup mocks
        mock_extract.return_value = "This is extracted text from the datasheet. " * 50  # ~2000 chars
        mock_hash.return_value = "abc123hash"
        mock_vector_db = Mock()
        mock_vector_db.add_document_chunks.return_value = ["doc1", "doc2"]
        mock_get_vector_db.return_value = mock_vector_db
        
        component_info = {
            "mpn": "ESP32-WROOM-32",
            "manufacturer": "Espressif",
            "category": "microcontroller",
            "description": "WiFi + Bluetooth MCU",
            "datasheet_url": "https://example.com/datasheet.pdf",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = ingestion_service.ingest_datasheet("test.pdf", component_info)
        
        assert result == ["doc1", "doc2"]
        mock_extract.assert_called_once_with("test.pdf")
        mock_vector_db.add_document_chunks.assert_called_once()
        
        # Check that chunks and metadata were passed correctly
        call_args = mock_vector_db.add_document_chunks.call_args
        chunks = call_args[0][0]
        metadata_list = call_args[0][1]
        
        assert len(chunks) > 0
        assert len(chunks) == len(metadata_list)
        
        # Check metadata structure
        for metadata in metadata_list:
            assert metadata["mpn"] == "ESP32-WROOM-32"
            assert metadata["manufacturer"] == "Espressif"
            assert metadata["category"] == "microcontroller"
            assert metadata["source_file"] == "test.pdf"
            assert metadata["file_hash"] == "abc123hash"
    
    @patch.object(DatasheetIngestionService, 'extract_text_from_pdf')
    def test_ingest_datasheet_no_text(self, mock_extract, ingestion_service):
        """Test datasheet ingestion with no extracted text."""
        mock_extract.return_value = ""
        
        result = ingestion_service.ingest_datasheet("test.pdf", {"mpn": "TEST"})
        
        assert result == []
    
    @patch.object(DatasheetIngestionService, 'extract_text_from_pdf')
    def test_ingest_datasheet_error(self, mock_extract, ingestion_service):
        """Test datasheet ingestion with extraction error."""
        mock_extract.side_effect = Exception("Extraction failed")
        
        with pytest.raises(Exception, match="Extraction failed"):
            ingestion_service.ingest_datasheet("test.pdf", {"mpn": "TEST"})
    
    def test_calculate_file_hash(self, ingestion_service, temp_dir):
        """Test file hash calculation."""
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        hash1 = ingestion_service._calculate_file_hash(test_file)
        hash2 = ingestion_service._calculate_file_hash(test_file)
        
        # Same file should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
        assert hash1 != "unknown"
    
    def test_calculate_file_hash_nonexistent(self, ingestion_service):
        """Test file hash calculation with nonexistent file."""
        result = ingestion_service._calculate_file_hash("nonexistent.pdf")
        assert result == "unknown"
    
    @patch('os.path.exists')
    @patch.object(DatasheetIngestionService, 'ingest_datasheet')
    def test_batch_ingest_datasheets(self, mock_ingest, mock_exists, ingestion_service):
        """Test batch ingestion of multiple datasheets."""
        mock_exists.return_value = True  # All files exist
        mock_ingest.side_effect = [["doc1", "doc2"], ["doc3"], []]
        
        configs = [
            {"pdf_path": "file1.pdf", "component_info": {"mpn": "COMP1"}},
            {"pdf_path": "file2.pdf", "component_info": {"mpn": "COMP2"}},
            {"pdf_path": "file3.pdf", "component_info": {"mpn": "COMP3"}},
        ]
        
        result = ingestion_service.batch_ingest_datasheets(configs)
        
        expected = {
            "file1.pdf": ["doc1", "doc2"],
            "file2.pdf": ["doc3"],
            "file3.pdf": []
        }
        assert result == expected
        assert mock_ingest.call_count == 3
    
    @patch('os.path.exists')
    def test_batch_ingest_datasheets_missing_file(self, mock_exists, ingestion_service):
        """Test batch ingestion with missing file."""
        mock_exists.return_value = False
        
        configs = [
            {"pdf_path": "missing.pdf", "component_info": {"mpn": "COMP1"}},
        ]
        
        result = ingestion_service.batch_ingest_datasheets(configs)
        
        assert result == {"missing.pdf": []}


class TestDatasheetIngestionServiceGlobal:
    """Test global datasheet ingestion service instance."""
    
    def test_get_datasheet_ingestion_service_singleton(self):
        """Test that get_datasheet_ingestion_service returns singleton."""
        service1 = get_datasheet_ingestion_service()
        service2 = get_datasheet_ingestion_service()
        
        assert service1 is service2
        assert isinstance(service1, DatasheetIngestionService)
    
    @patch('backend.src.services.datasheet_ingestion._datasheet_service', None)
    def test_get_datasheet_ingestion_service_creates_new_instance(self):
        """Test that get_datasheet_ingestion_service creates new instance when needed."""
        service = get_datasheet_ingestion_service()
        assert isinstance(service, DatasheetIngestionService)
        assert service.min_chunk_size == 1000
        assert service.max_chunk_size == 2000