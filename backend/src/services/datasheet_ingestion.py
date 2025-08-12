"""
Datasheet ingestion service for processing PDF datasheets and extracting text chunks.
"""

import logging
import os
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

from pdfminer.high_level import extract_text
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

from .vector_db import get_vector_db_service

logger = logging.getLogger(__name__)


class DatasheetIngestionService:
    """Service for ingesting PDF datasheets and creating searchable text chunks."""
    
    def __init__(self, datasheet_directory: str = "./data/datasheets"):
        """
        Initialize the datasheet ingestion service.
        
        Args:
            datasheet_directory: Directory to store cached datasheets
        """
        self.datasheet_directory = Path(datasheet_directory)
        self.datasheet_directory.mkdir(parents=True, exist_ok=True)
        
        # Text chunking parameters
        self.min_chunk_size = 1000  # Minimum characters per chunk
        self.max_chunk_size = 2000  # Maximum characters per chunk
        self.overlap_size = 200     # Overlap between chunks for context
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Use pdfminer.six for robust text extraction
            text = extract_text(pdf_path)
            
            if not text.strip():
                logger.warning(f"No text extracted from PDF: {pdf_path}")
                return ""
                
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers (common patterns)
        text = re.sub(r'Page \d+.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'www\.[^\s]+', '', text)  # Remove URLs
        
        # Remove excessive punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\/\+\=\<\>\@\#\$\%\^\&\*]', ' ', text)
        
        # Normalize whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def create_text_chunks(
        self, 
        text: str, 
        source_metadata: Dict[str, Any]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split text into overlapping chunks with provenance tracking.
        
        Args:
            text: Input text to chunk
            source_metadata: Metadata about the source document
            
        Returns:
            List of (chunk_text, chunk_metadata) tuples
        """
        if not text.strip():
            return []
            
        chunks = []
        start_pos = 0
        chunk_index = 0
        
        while start_pos < len(text):
            # Calculate end position for this chunk
            end_pos = min(start_pos + self.max_chunk_size, len(text))
            
            # If we're not at the end, try to break at a sentence boundary
            if end_pos < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start_pos + self.min_chunk_size, end_pos - 200)
                sentence_end = -1
                
                for pattern in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
                    pos = text.rfind(pattern, search_start, end_pos)
                    if pos > sentence_end:
                        sentence_end = pos + len(pattern)
                
                if sentence_end > 0:
                    end_pos = sentence_end
            
            # Extract the chunk
            chunk_text = text[start_pos:end_pos].strip()
            
            if len(chunk_text) >= self.min_chunk_size or start_pos + len(chunk_text) >= len(text):
                # Create metadata for this chunk
                chunk_metadata = {
                    **source_metadata,
                    "chunk_index": chunk_index,
                    "chunk_start": start_pos,
                    "chunk_end": end_pos,
                    "chunk_length": len(chunk_text),
                    "total_text_length": len(text)
                }
                
                chunks.append((chunk_text, chunk_metadata))
                chunk_index += 1
            
            # Move to next chunk with overlap
            next_start = max(start_pos + self.min_chunk_size, end_pos - self.overlap_size)
            
            # Prevent infinite loop - ensure we're making progress
            if next_start <= start_pos:
                next_start = start_pos + self.min_chunk_size
            
            start_pos = next_start
            
            # Break if we've processed all text
            if start_pos >= len(text):
                break
        
        logger.info(f"Created {len(chunks)} text chunks from {len(text)} characters")
        return chunks
    
    def ingest_datasheet(
        self, 
        pdf_path: str, 
        component_info: Dict[str, Any]
    ) -> List[str]:
        """
        Ingest a datasheet PDF and add chunks to the vector database.
        
        Args:
            pdf_path: Path to the PDF datasheet
            component_info: Information about the component (mpn, manufacturer, category, etc.)
            
        Returns:
            List of document IDs that were added to the vector database
        """
        try:
            # Extract text from PDF
            raw_text = self.extract_text_from_pdf(pdf_path)
            if not raw_text:
                logger.warning(f"No text extracted from {pdf_path}")
                return []
            
            # Clean the text
            cleaned_text = self.clean_text(raw_text)
            
            # Create source metadata
            source_metadata = {
                "source_file": os.path.basename(pdf_path),
                "source_path": pdf_path,
                "mpn": component_info.get("mpn", "unknown"),
                "manufacturer": component_info.get("manufacturer", "unknown"),
                "category": component_info.get("category", "unknown"),
                "description": component_info.get("description", ""),
                "datasheet_url": component_info.get("datasheet_url", ""),
                "ingestion_timestamp": component_info.get("timestamp", ""),
                "file_hash": self._calculate_file_hash(pdf_path)
            }
            
            # Create text chunks
            chunks_with_metadata = self.create_text_chunks(cleaned_text, source_metadata)
            
            if not chunks_with_metadata:
                logger.warning(f"No chunks created from {pdf_path}")
                return []
            
            # Extract chunks and metadata for vector database
            chunks = [chunk for chunk, _ in chunks_with_metadata]
            metadata_list = [metadata for _, metadata in chunks_with_metadata]
            
            # Add to vector database
            vector_db = get_vector_db_service()
            doc_ids = vector_db.add_document_chunks(chunks, metadata_list)
            
            logger.info(f"Successfully ingested datasheet {pdf_path} with {len(doc_ids)} chunks")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to ingest datasheet {pdf_path}: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file for deduplication."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return "unknown"
    
    def batch_ingest_datasheets(
        self, 
        datasheet_configs: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Batch ingest multiple datasheets.
        
        Args:
            datasheet_configs: List of dictionaries containing pdf_path and component_info
            
        Returns:
            Dictionary mapping file paths to lists of document IDs
        """
        results = {}
        
        for config in datasheet_configs:
            pdf_path = config.get("pdf_path")
            component_info = config.get("component_info", {})
            
            if not pdf_path or not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                results[pdf_path] = []
                continue
            
            try:
                doc_ids = self.ingest_datasheet(pdf_path, component_info)
                results[pdf_path] = doc_ids
            except Exception as e:
                logger.error(f"Failed to ingest {pdf_path}: {e}")
                results[pdf_path] = []
        
        return results


# Global datasheet ingestion service instance
_datasheet_service: Optional[DatasheetIngestionService] = None


def get_datasheet_ingestion_service() -> DatasheetIngestionService:
    """Get the global datasheet ingestion service instance."""
    global _datasheet_service
    if _datasheet_service is None:
        _datasheet_service = DatasheetIngestionService()
    return _datasheet_service