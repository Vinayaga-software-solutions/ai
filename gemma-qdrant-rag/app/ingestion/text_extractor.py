"""
Text Extraction Module
Extracts text from various file formats (TXT, PDF, JSON, CSV, DOCX, XLSX, etc.)
Currently supports TXT, PDF, JSON, CSV/TSV, DOC/DOCX, XLS/XLSX.
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
        '.json': 'json',
        '.csv': 'csv',
        '.tsv': 'tsv',
        '.docx': 'docx',
        '.doc': 'doc',
        '.xlsx': 'xlsx',
        '.xls': 'xls',
    }
    
    def __init__(self):
        self.extractors = {
            'text': self._extract_text,
            'pdf': self._extract_pdf,
            'json': self._extract_json,
            'csv': self._extract_csv,
            'tsv': self._extract_tsv,
            'docx': self._extract_docx,
            'doc': self._extract_doc,
            'xlsx': self._extract_xlsx,
            'xls': self._extract_xls,
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
        import importlib
        import importlib.util

        reader_module = None
        if importlib.util.find_spec("pypdf") is not None:
            reader_module = importlib.import_module("pypdf")
        elif importlib.util.find_spec("PyPDF2") is not None:
            reader_module = importlib.import_module("PyPDF2")
        else:
            raise ImportError(
                "PDF ingestion requires pypdf. Install it with: pip install pypdf"
            )

        PdfReader = reader_module.PdfReader

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

    def _extract_json(self, path: Path, encoding: str) -> str:
        """Extract text from JSON files."""
        import json
        with open(path, 'r', encoding=encoding) as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _extract_csv(self, path: Path, encoding: str) -> str:
        """Extract text from CSV files."""
        return self._extract_delimited_text(path, encoding, delimiter=None)

    def _extract_tsv(self, path: Path, encoding: str) -> str:
        """Extract text from TSV files."""
        return self._extract_delimited_text(path, encoding, delimiter="\t")

    def _extract_delimited_text(self, path: Path, encoding: str, delimiter: Optional[str]) -> str:
        import csv
        with open(path, 'r', encoding=encoding, newline='') as f:
            if delimiter is None:
                sample = f.read(4096)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ','

            reader = csv.reader(f, delimiter=delimiter)
            rows = []
            for row in reader:
                rows.append("\t".join(row))
            return "\n".join(rows)

    def _extract_docx(self, path: Path, encoding: str = None) -> str:
        """Extract text from DOCX files."""
        import importlib.util
        if importlib.util.find_spec("docx") is None:
            raise ImportError("DOCX ingestion requires python-docx. Install it with: pip install python-docx")

        from docx import Document  # type: ignore
        doc = Document(str(path))
        parts = []
        for para in doc.paragraphs:
            if para.text:
                parts.append(para.text)

        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                parts.append("\t".join(cells))

        return "\n".join([p for p in parts if p]).strip()

    def _extract_doc(self, path: Path, encoding: str = None) -> str:
        """Extract text from legacy DOC files."""
        import importlib.util
        if importlib.util.find_spec("textract") is None:
            raise ImportError(
                "DOC ingestion requires textract (and an external parser). "
                "Install with: pip install textract or convert .doc to .docx."
            )

        import textract  # type: ignore
        content = textract.process(str(path))
        return content.decode("utf-8", errors="ignore")

    def _extract_xlsx(self, path: Path, encoding: str = None) -> str:
        """Extract text from XLSX files."""
        import importlib.util
        if importlib.util.find_spec("openpyxl") is None:
            raise ImportError("XLSX ingestion requires openpyxl. Install it with: pip install openpyxl")

        import openpyxl  # type: ignore
        wb = openpyxl.load_workbook(filename=str(path), read_only=True, data_only=True)
        parts = []
        for sheet in wb.worksheets:
            parts.append(f"Sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                row_vals = ["" if v is None else str(v) for v in row]
                parts.append("\t".join(row_vals))
        return "\n".join(parts).strip()

    def _extract_xls(self, path: Path, encoding: str = None) -> str:
        """Extract text from XLS files."""
        import importlib.util
        if importlib.util.find_spec("xlrd") is None:
            raise ImportError("XLS ingestion requires xlrd. Install it with: pip install xlrd")

        import xlrd  # type: ignore
        wb = xlrd.open_workbook(str(path))
        parts = []
        for sheet in wb.sheets():
            parts.append(f"Sheet: {sheet.name}")
            for r in range(sheet.nrows):
                row_vals = ["" if v is None else str(v) for v in sheet.row_values(r)]
                parts.append("\t".join(row_vals))
        return "\n".join(parts).strip()
