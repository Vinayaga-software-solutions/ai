"""
Text Extraction Module
Extracts text from various file formats (TXT, PDF, JSON, etc.)
Currently supports TXT with extensibility for future formats.
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Handles text extraction from various file formats.
    Implements the Data Ingestion step from DESIGN_KNOWLEDGE.md
    """
    
    SUPPORTED_FORMATS = {
        '.txt': 'text',
        '.md': 'text',
        '.pdf': 'pdf',
        # '.json': 'json',
        # '.csv': 'csv',
    }
    
    def __init__(self):
        self.extractors = {
            'text': self._extract_text,
            'pdf': self._extract_pdf,
            # 'json': self._extract_json,
        }
    
    def extract(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Extract text from a file.
        
        Args:
            file_path: Path to the file
            encoding: Text encoding (default: utf-8)
            
        Returns:
            Dictionary with extracted text and metadata
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = path.suffix.lower()
        
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )
        
        format_type = self.SUPPORTED_FORMATS[file_extension]
        extractor = self.extractors.get(format_type)
        
        if not extractor:
            raise ValueError(f"No extractor available for format: {format_type}")
        
        try:
            text = extractor(path, encoding)
            
            # Get file metadata
            metadata = self._get_file_metadata(path)
            
            return {
                "text": text,
                "metadata": metadata,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return {
                "text": "",
                "metadata": {},
                "success": False,
                "error": str(e)
            }
    
    def _extract_text(self, path: Path, encoding: str) -> str:
        """Extract text from plain text files (.txt, .md)."""
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    
    def _get_file_metadata(self, path: Path) -> Dict[str, Any]:
        """Extract metadata from file."""
        stat = path.stat()
        
        return {
            "filename": path.name,
            "file_path": str(path.absolute()),
            "file_extension": path.suffix,
            "file_size_bytes": stat.st_size,
            "created_timestamp": stat.st_ctime,
            "modified_timestamp": stat.st_mtime,
        }
    
    def _extract_pdf(self, path: Path, encoding: str = None) -> str:
        """Extract text from PDF files."""
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError(
                "pypdf is required for PDF ingestion. Install it with: pip install pypdf"
            ) from exc

        with open(path, 'rb') as f:
            reader = PdfReader(f)
            if reader.is_encrypted:
                raise ValueError("Encrypted PDFs are not supported.")

            extracted_pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                extracted_pages.append(page_text)

        combined_text = "\n".join(extracted_pages).strip()
        if not combined_text:
            raise ValueError("PDF contains no extractable text (possible scanned images).")

        return combined_text
    
    # Future JSON support
    # def _extract_json(self, path: Path, encoding: str) -> str:
    #     """Extract text from JSON files."""
    #     import json
    #     with open(path, 'r', encoding=encoding) as f:
    #         data = json.load(f)
    #     # Convert JSON to text representation
    #     return json.dumps(data, indent=2)
