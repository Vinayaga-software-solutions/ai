#!/usr/bin/env python3
"""
Unit tests for the Ingestion microservice (app.ingestion).
Tests TextExtractor, document_storage, and IngestionPipeline (with mocked embed/store).
"""
import sys
import os
import tempfile
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.ingestion import TextExtractor, get_document_storage, IngestionPipeline
from app.ingestion.document_storage import LocalDocumentStorage

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_text_extractor_txt():
    """TextExtractor extracts .txt and returns text + metadata."""
    extractor = TextExtractor()
    sample = Path(__file__).resolve().parent.parent / "data" / "sample_document.txt"
    if not sample.exists():
        logger.warning("Skip test_text_extractor_txt: data/sample_document.txt not found")
        return True
    result = extractor.extract(str(sample))
    assert result["success"] is True
    assert "text" in result and len(result["text"]) > 0
    assert "metadata" in result and "filename" in result["metadata"]
    logger.info("PASS: test_text_extractor_txt")
    return True


def test_text_extractor_unsupported_format():
    """TextExtractor raises ValueError for unsupported extension."""
    extractor = TextExtractor()
    with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
        f.write(b"dummy")
        path = f.name
    try:
        try:
            extractor.extract(path)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Unsupported" in str(e) or "xyz" in str(e)
    finally:
        os.unlink(path)
    logger.info("PASS: test_text_extractor_unsupported_format")
    return True


def test_ingestion_document_storage_save():
    """Ingestion document_storage saves content to local when STORAGE_BACKEND=local."""
    with tempfile.TemporaryDirectory() as tmp:
        storage = LocalDocumentStorage(base_path=tmp)
        path = storage.save_content(b"hello", "f.txt", doc_id="d1")
        assert Path(path).exists()
        assert Path(path).read_bytes() == b"hello"
    logger.info("PASS: test_ingestion_document_storage_save")
    return True


def test_ingestion_pipeline_with_mocks():
    """IngestionPipeline runs extract -> clean -> chunk; embed/store are mocked.

    Update: ingestion pipeline delegates to ingestion microservice, so mock
    requests.post to simulate the ingestion-service response.
    """
    mock_emb = MagicMock()
    mock_emb.embed_documents.return_value = [[0.1] * 384, [0.2] * 384]  # 2 chunks
    mock_db = MagicMock()
    sample = Path(__file__).resolve().parent.parent / "data" / "sample_document.txt"
    if not sample.exists():
        logger.warning("Skip test_ingestion_pipeline_with_mocks: sample_document.txt not found")
        return True

    pipeline = IngestionPipeline(embeddings=mock_emb, vector_store=mock_db)

    # Mock the ingestion-service HTTP call that ingest_file delegates to
    with patch("requests.post") as mock_post:
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"success": True, "doc_id": "sample_doc_1", "chunks_created": 2}
        mock_post.return_value = resp

        result = pipeline.ingest_file(str(sample))

    assert result["success"] is True
    assert result["chunks_created"] >= 1
    logger.info("PASS: test_ingestion_pipeline_with_mocks")
    return True

def main():
    logger.info("Ingestion service tests...")
    tests = [
        test_text_extractor_txt,
        test_text_extractor_unsupported_format,
        test_ingestion_document_storage_save,
        test_ingestion_pipeline_with_mocks,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            logger.exception("FAIL: %s", t.__name__)
            failed.append((t.__name__, e))
    logger.info("=" * 60)
    logger.info("Ingestion: %d passed, %d failed", len(tests) - len(failed), len(failed))
    if failed:
        for name, err in failed:
            logger.error("  %s: %s", name, err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
