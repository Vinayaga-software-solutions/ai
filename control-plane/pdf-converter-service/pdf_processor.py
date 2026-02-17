"""
PDF to Markdown Converter
Converts PDF files to Markdown format while preserving formatting.
"""

import logging
from typing import Optional
import fitz  # PyMuPDF
import re

logger = logging.getLogger(__name__)


class PDFToMarkdownConverter:
    """Converts PDF documents to Markdown format."""
    
    def __init__(self):
        """Initialize the converter."""
        self.current_font_size = None
        self.current_font_flags = None
    
    def convert(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown format.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Markdown formatted string
        """
        try:
            doc = fitz.open(pdf_path)
            markdown_content = []
            
            # Add document metadata
            metadata = doc.metadata
            if metadata.get('title'):
                markdown_content.append(f"# {metadata['title']}\n")
            if metadata.get('author'):
                markdown_content.append(f"**Author:** {metadata['author']}\n")
            if metadata.get('subject'):
                markdown_content.append(f"**Subject:** {metadata['subject']}\n")
            
            if metadata.get('title') or metadata.get('author') or metadata.get('subject'):
                markdown_content.append("\n---\n\n")
            
            # Process each page
            for page_num, page in enumerate(doc, start=1):
                logger.info(f"Processing page {page_num}/{len(doc)}")
                
                # Extract text blocks with formatting information
                blocks = page.get_text("dict")["blocks"]
                page_content = self._process_blocks(blocks)
                
                if page_content.strip():
                    markdown_content.append(page_content)
                    markdown_content.append(f"\n\n---\n*Page {page_num}*\n\n")
            
            doc.close()
            
            # Join and clean up the markdown
            markdown = "\n".join(markdown_content)
            markdown = self._clean_markdown(markdown)
            
            return markdown
            
        except Exception as e:
            logger.error(f"Error converting PDF to Markdown: {e}", exc_info=True)
            raise
    
    def _process_blocks(self, blocks: list) -> str:
        """Process text blocks and convert to Markdown."""
        markdown_lines = []
        
        for block in blocks:
            if block.get("type") == 0:  # Text block
                block_text = self._process_text_block(block)
                if block_text:
                    markdown_lines.append(block_text)
            elif block.get("type") == 1:  # Image block
                markdown_lines.append("![Image](image)\n")
        
        return "\n\n".join(markdown_lines)
    
    def _process_text_block(self, block: dict) -> str:
        """Process a single text block."""
        lines = []
        
        for line in block.get("lines", []):
            line_text = ""
            
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                
                font_size = span.get("size", 12)
                font_flags = span.get("flags", 0)
                
                # Determine formatting based on font properties
                formatted_text = self._format_text(text, font_size, font_flags)
                line_text += formatted_text + " "
            
            line_text = line_text.strip()
            if line_text:
                lines.append(line_text)
        
        return "\n".join(lines)
    
    def _format_text(self, text: str, font_size: float, font_flags: int) -> str:
        """
        Format text based on font properties.
        
        Font flags:
        - 2^0 (1): superscript
        - 2^1 (2): italic
        - 2^2 (4): serifed
        - 2^3 (8): monospaced
        - 2^4 (16): bold
        """
        # Detect headings based on font size
        if font_size > 20:
            return f"# {text}"
        elif font_size > 16:
            return f"## {text}"
        elif font_size > 14:
            return f"### {text}"
        elif font_size > 13:
            return f"#### {text}"
        
        # Apply text formatting
        is_bold = bool(font_flags & 16)
        is_italic = bool(font_flags & 2)
        is_monospace = bool(font_flags & 8)
        
        if is_monospace:
            return f"`{text}`"
        elif is_bold and is_italic:
            return f"***{text}***"
        elif is_bold:
            return f"**{text}**"
        elif is_italic:
            return f"*{text}*"
        
        return text
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up the generated Markdown."""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{4,}', '\n\n\n', markdown)
        
        # Fix spacing around headers
        markdown = re.sub(r'\n(#{1,6} )', r'\n\n\1', markdown)
        
        # Ensure proper spacing after headers
        markdown = re.sub(r'(#{1,6} .+)\n([^#\n])', r'\1\n\n\2', markdown)
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in markdown.split('\n')]
        markdown = '\n'.join(lines)
        
        # Remove multiple consecutive spaces
        markdown = re.sub(r' {2,}', ' ', markdown)
        
        return markdown.strip()


class AdvancedPDFToMarkdownConverter(PDFToMarkdownConverter):
    """
    Advanced converter with better table and list detection.
    """
    
    def _process_text_block(self, block: dict) -> str:
        """Process text block with enhanced table and list detection."""
        lines = []
        block_bbox = block.get("bbox", [])
        
        # Check if this looks like a table (multiple aligned columns)
        if self._is_table_block(block):
            table_md = self._convert_table(block)
            if table_md:
                return table_md
        
        # Check if this looks like a list
        if self._is_list_block(block):
            list_md = self._convert_list(block)
            if list_md:
                return list_md
        
        # Default processing
        return super()._process_text_block(block)
    
    def _is_table_block(self, block: dict) -> bool:
        """Detect if a block represents a table."""
        lines = block.get("lines", [])
        if len(lines) < 2:
            return False
        
        # Check for consistent column alignment
        # This is a simplified heuristic
        return False  # Placeholder - implement proper table detection
    
    def _convert_table(self, block: dict) -> str:
        """Convert a table block to Markdown table format."""
        # Placeholder for table conversion
        return ""
    
    def _is_list_block(self, block: dict) -> bool:
        """Detect if a block represents a list."""
        lines = block.get("lines", [])
        if not lines:
            return False
        
        # Check if lines start with bullet points or numbers
        first_line_text = ""
        for span in lines[0].get("spans", []):
            first_line_text += span.get("text", "")
        
        first_line_text = first_line_text.strip()
        
        # Check for common list markers
        list_markers = ['-', '•', '◦', '▪', '▫', '*']
        if any(first_line_text.startswith(marker) for marker in list_markers):
            return True
        
        # Check for numbered lists
        if re.match(r'^\d+[\.\)]\s', first_line_text):
            return True
        
        return False
    
    def _convert_list(self, block: dict) -> str:
        """Convert a list block to Markdown list format."""
        lines = []
        
        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")
            
            line_text = line_text.strip()
            if not line_text:
                continue
            
            # Ensure proper Markdown list formatting
            if not line_text.startswith(('-', '*', '•', '1.', '2.', '3.')):
                # If not already formatted, add a dash
                if re.match(r'^\d+[\.\)]', line_text):
                    # It's a numbered list, keep the number
                    pass
                else:
                    line_text = f"- {line_text}"
            else:
                # Normalize bullet points
                line_text = re.sub(r'^[•◦▪▫]\s*', '- ', line_text)
            
            lines.append(line_text)
        
        return "\n".join(lines)
