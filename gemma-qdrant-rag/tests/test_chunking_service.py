#!/usr/bin/env python3
"""
Unit tests for the Chunking microservice (app.chunking).
Tests TextCleaner, TextChunker, DocumentChunker without external services.
"""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.chunking import TextCleaner, DocumentChunker
from app.chunking.chunker import TextChunker

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_text_cleaner_basic():
    """TextCleaner normalizes whitespace and line endings."""
    cleaner = TextCleaner()
    raw = "  hello   world  \n\n\n  foo  "
    out = cleaner.clean(raw)
    assert out.strip() == out
    assert len(out) > 0
    assert "hello" in out and "world" in out
    logger.info("PASS: test_text_cleaner_basic")
    return True


def test_text_cleaner_line_endings():
    """TextCleaner normalizes \\r\\n and \\r to \\n."""
    cleaner = TextCleaner()
    raw = "a\r\nb\rc"
    out = cleaner.clean(raw)
    assert "\r" not in out
    assert out == "a\nb\nc"
    logger.info("PASS: test_text_cleaner_line_endings")
    return True


def test_text_chunker_creates_chunks():
    """TextChunker produces chunks with token_count and text."""
    chunker = TextChunker(min_tokens=10, max_tokens=50)
    text = "One two three four five. " * 20
    chunks = chunker.chunk_by_tokens(text)
    assert len(chunks) >= 1
    for c in chunks:
        assert "text" in c and "token_count" in c and "chunk_index" in c
        assert c["token_count"] >= 0
    logger.info("PASS: test_text_chunker_creates_chunks")
    return True


def test_text_chunker_empty():
    """TextChunker returns empty list for empty or whitespace-only text."""
    chunker = TextChunker(min_tokens=10, max_tokens=50)
    assert chunker.chunk_by_tokens("") == []
    assert chunker.chunk_by_tokens("   ") == []
    logger.info("PASS: test_text_chunker_empty")
    return True


def test_document_chunker_metadata():
    """DocumentChunker adds doc_id, source, chunk_id, total_chunks to each chunk.

    This test mocks the chunking microservice HTTP response so it runs without Docker.
    """
    from unittest.mock import patch, MagicMock

    doc_chunker = DocumentChunker()
    text = "Some content. " * 50

    # Mock requests.post to return a deterministic chunk list
    with patch("requests.post") as mock_post:
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {
            "chunks": [
                {"text": "Some content.", "chunk_index": 0, "token_count": 50, "doc_id": "doc_1", "source": "test.txt", "author": "test", "chunk_id": "doc_1_chunk_0", "total_chunks": 2},
                {"text": "Some content.", "chunk_index": 1, "token_count": 50, "doc_id": "doc_1", "source": "test.txt", "author": "test", "chunk_id": "doc_1_chunk_1", "total_chunks": 2},
            ]
        }
        mock_post.return_value = resp

        chunks = doc_chunker.chunk_document(
            text=text, doc_id="doc_1", source="test.txt", metadata={"author": "test"}
        )

    assert len(chunks) >= 1
    for i, c in enumerate(chunks):
        assert c["doc_id"] == "doc_1"
        assert c["source"] == "test.txt"
        assert c["chunk_id"] == f"doc_1_chunk_{i}"
        assert c["total_chunks"] == len(chunks)
        assert c.get("author") == "test"
    logger.info("PASS: test_document_chunker_metadata")
    return True


def main():
    logger.info("Chunking service tests...")
    tests = [
        test_text_cleaner_basic,
        test_text_cleaner_line_endings,
        test_text_chunker_creates_chunks,
        test_text_chunker_empty,
        test_document_chunker_metadata,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            logger.exception("FAIL: %s", t.__name__)
            failed.append((t.__name__, e))
    logger.info("=" * 60)
    logger.info("Chunking: %d passed, %d failed", len(tests) - len(failed), len(failed))
    if failed:
        for name, err in failed:
            logger.error("  %s: %s", name, err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
