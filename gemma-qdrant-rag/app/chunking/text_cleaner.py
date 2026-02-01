"""
Text cleaning for pre-processing step (Chunking Service).
Implements the Pre-processing step from DESIGN_KNOWLEDGE.md
"""
import re


class TextCleaner:
    """
    Cleans and preprocesses extracted text.
    Implements the Pre-processing step from DESIGN_KNOWLEDGE.md
    """
    
    @staticmethod
    def clean(text: str, remove_extra_whitespace: bool = True) -> str:
        """
        Clean extracted text.
        
        Args:
            text: Raw extracted text
            remove_extra_whitespace: Whether to normalize whitespace
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        cleaned = text
        
        # Remove null bytes
        cleaned = cleaned.replace('\x00', '')
        
        # Normalize line endings
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove extra whitespace if requested
        if remove_extra_whitespace:
            # Replace multiple spaces with single space
            cleaned = re.sub(r' +', ' ', cleaned)
            # Replace multiple newlines with max 2
            cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
