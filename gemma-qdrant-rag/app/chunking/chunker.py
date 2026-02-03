"""
Text Chunking Module (deprecated local implementation)
Prefer using the `chunking` microservice. The local chunker remains as a
fallback for backward compatibility but will be removed in future.
"""
import warnings
from typing import List, Dict, Any
import re

warnings.warn("app.chunking.* is deprecated: use the chunking microservice instead", DeprecationWarning, stacklevel=2)


class TextChunker:
    """
    Handles text chunking with configurable token limits.
    Based on DESIGN_KNOWLEDGE.md chunking strategies.

    Note: `tiktoken` is imported lazily so the orchestrator can start even if the
    local chunker native dependency is not installed (we encourage using the
    chunking microservice instead).
    """
    
    def __init__(
        self, 
        min_tokens: int = 100, 
        max_tokens: int = 500,  # Reduced to fit BGE 512 context limit
        overlap_tokens: int = 50,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize the chunker.
        
        Args:
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            encoding_name: Tiktoken encoding to use
        """
        # Import tiktoken lazily and raise an informative error if missing
        try:
            import tiktoken  # type: ignore
        except Exception as e:
            raise ImportError(
                "tiktoken is required to use TextChunker locally. "
                "Install it (pip install tiktoken) or use the chunking microservice instead."
            ) from e

        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding = tiktoken.get_encoding(encoding_name)


class TextChunker:
    """
    Handles text chunking with configurable token limits.
    Based on DESIGN_KNOWLEDGE.md chunking strategies.
    """
    
    def __init__(
        self, 
        min_tokens: int = 100, 
        max_tokens: int = 500,  # Reduced to fit BGE 512 context limit
        overlap_tokens: int = 50,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize the chunker.
        
        Args:
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            encoding_name: Tiktoken encoding to use
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoding.encode(text))
    
    def chunk_by_tokens(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Chunk text into segments of 400-600 tokens with overlap.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split into sentences first for better semantic boundaries
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed max_tokens
            if current_tokens + sentence_tokens > self.max_tokens:
                # Save current chunk if it meets minimum
                if current_tokens >= self.min_tokens:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
                    
                    # Start new chunk with overlap
                    current_chunk = self._get_overlap_sentences(current_chunk)
                    current_tokens = self.count_tokens(" ".join(current_chunk))
                
                # If single sentence is too large, split it
                if sentence_tokens > self.max_tokens:
                    # Split long sentence into smaller parts
                    sub_chunks = self._split_long_sentence(sentence)
                    for sub_chunk in sub_chunks:
                        chunks.append(self._create_chunk(sub_chunk, len(chunks), metadata))
                    current_chunk = []
                    current_tokens = 0
                else:
                    current_chunk.append(sentence)
                    current_tokens += sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add remaining chunk
        if current_chunk and current_tokens >= self.min_tokens:
            chunk_text = " ".join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
        elif current_chunk and chunks:
            # If last chunk is too small, merge with previous
            last_chunk_text = " ".join(current_chunk)
            chunks[-1]["text"] += " " + last_chunk_text
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Simple sentence splitter - can be enhanced
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split a very long sentence into smaller chunks."""
        words = sentence.split()
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self.count_tokens(word)
            if current_tokens + word_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_tokens = word_tokens
            else:
                current_chunk.append(word)
                current_tokens += word_tokens
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get the last few sentences for overlap."""
        overlap_text = ""
        overlap_sentences = []
        
        # Work backwards to get overlap_tokens worth of sentences
        for sentence in reversed(sentences):
            test_text = sentence + " " + overlap_text
            if self.count_tokens(test_text) <= self.overlap_tokens:
                overlap_sentences.insert(0, sentence)
                overlap_text = test_text
            else:
                break
        
        return overlap_sentences
    
    def _create_chunk(self, text: str, chunk_index: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a chunk dictionary with text and metadata."""
        chunk = {
            "text": text,
            "chunk_index": chunk_index,
            "token_count": self.count_tokens(text)
        }
        
        if metadata:
            chunk.update(metadata)
        
        return chunk


class DocumentChunker:
    """Document chunker that delegates to the chunking microservice.

    This implementation will raise an exception if the chunking service cannot
    be reached. Local chunking support has been removed.
    """

    def __init__(self):
        from app.config import settings
        self.chunking_host = getattr(settings, "CHUNKING_HOST", "chunking")
        self.chunking_port = getattr(settings, "CHUNKING_PORT", 80)
        self.chunk_url = f"http://{self.chunking_host}:{self.chunking_port}/chunk"

    def chunk_document(
        self,
        text: str,
        doc_id: str,
        source: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        payload = {"text": text, "doc_id": doc_id, "source": source}
        if metadata:
            payload["metadata"] = metadata

        import requests
        resp = requests.post(self.chunk_url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        chunks = data.get("chunks", [])
        # Ensure chunk ids and totals exist
        for i, chunk in enumerate(chunks):
            if "chunk_id" not in chunk:
                chunk["chunk_id"] = f"{doc_id}_chunk_{i}"
            if "total_chunks" not in chunk:
                chunk["total_chunks"] = len(chunks)
        return chunks