#!/usr/bin/env python3
"""
Tests for document storage (local folder and GCS config).
Runs without Qdrant or embedding services. Uses temp dir for local storage.
"""
import sys
import os
import tempfile
import logging
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.document_storage import (
    LocalDocumentStorage,
    GCSDocumentStorage,
    get_document_storage,
)
from app import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_local_storage_save_content():
    """LocalDocumentStorage saves raw content to a file."""
    with tempfile.TemporaryDirectory() as tmp:
        storage = LocalDocumentStorage(base_path=tmp)
        content = b"Hello, document storage!"
        path = storage.save_content(content, "test.txt", doc_id="doc_001")
        assert Path(path).exists()
        assert Path(path).read_bytes() == content
        assert "doc_001" in path or "test" in path
    logger.info("PASS: test_local_storage_save_content")


def test_local_storage_save_file():
    """LocalDocumentStorage copies an existing file."""
    with tempfile.TemporaryDirectory() as tmp:
        storage = LocalDocumentStorage(base_path=tmp)
        source = Path(tmp) / "original.txt"
        source.write_text("Original file content")
        path = storage.save_file(str(source), doc_id="doc_002")
        assert Path(path).exists()
        assert Path(path).read_text() == "Original file content"
    logger.info("PASS: test_local_storage_save_file")


def test_local_storage_creates_directory():
    """LocalDocumentStorage creates base directory if missing."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "nested" / "documents"
        assert not base.exists()
        storage = LocalDocumentStorage(base_path=str(base))
        assert base.exists()
        storage.save_content(b"x", "f.txt")
        assert (base / "f.txt").exists()
    logger.info("PASS: test_local_storage_creates_directory")


def test_local_storage_file_not_found():
    """LocalDocumentStorage.save_file raises FileNotFoundError for missing file."""
    with tempfile.TemporaryDirectory() as tmp:
        storage = LocalDocumentStorage(base_path=tmp)
        try:
            storage.save_file("/nonexistent/file.txt")
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError as e:
            assert "nonexistent" in str(e) or "file" in str(e).lower()
    logger.info("PASS: test_local_storage_file_not_found")


def test_gcs_storage_requires_bucket():
    """GCSDocumentStorage raises ValueError when bucket name is not set."""
    # Ensure we don't accidentally use env bucket
    original_bucket = getattr(config.settings, "GCS_BUCKET_NAME", None)
    try:
        config.settings.GCS_BUCKET_NAME = None
        try:
            GCSDocumentStorage(bucket_name=None)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "GCS_BUCKET_NAME" in str(e) or "bucket" in str(e).lower()
    finally:
        if original_bucket is not None:
            config.settings.GCS_BUCKET_NAME = original_bucket
    logger.info("PASS: test_gcs_storage_requires_bucket")


def test_get_document_storage_local():
    """get_document_storage returns LocalDocumentStorage when STORAGE_BACKEND=local."""
    original = config.settings.STORAGE_BACKEND
    try:
        config.settings.STORAGE_BACKEND = "local"
        storage = get_document_storage()
        assert isinstance(storage, LocalDocumentStorage)
    finally:
        config.settings.STORAGE_BACKEND = original
    logger.info("PASS: test_get_document_storage_local")


def test_get_document_storage_gcs_returns_gcs_class():
    """get_document_storage returns GCSDocumentStorage when STORAGE_BACKEND=gcs (with bucket set)."""
    original_backend = config.settings.STORAGE_BACKEND
    original_bucket = config.settings.GCS_BUCKET_NAME
    try:
        config.settings.STORAGE_BACKEND = "gcs"
        config.settings.GCS_BUCKET_NAME = "test-bucket"
        storage = get_document_storage()
        assert isinstance(storage, GCSDocumentStorage)
        assert storage.bucket_name == "test-bucket"
    finally:
        config.settings.STORAGE_BACKEND = original_backend
        config.settings.GCS_BUCKET_NAME = original_bucket
    logger.info("PASS: test_get_document_storage_gcs_returns_gcs_class")


def test_get_document_storage_default_local():
    """get_document_storage defaults to local when STORAGE_BACKEND is empty or invalid."""
    original = config.settings.STORAGE_BACKEND
    try:
        for value in ("", "  ", "s3", "LOCAL"):
            config.settings.STORAGE_BACKEND = value
            storage = get_document_storage()
            assert isinstance(storage, LocalDocumentStorage), f"Expected local for {value!r}"
    finally:
        config.settings.STORAGE_BACKEND = original
    logger.info("PASS: test_get_document_storage_default_local")


def main():
    logger.info("Running document storage tests...")
    tests = [
        test_local_storage_save_content,
        test_local_storage_save_file,
        test_local_storage_creates_directory,
        test_local_storage_file_not_found,
        test_gcs_storage_requires_bucket,
        test_get_document_storage_local,
        test_get_document_storage_gcs_returns_gcs_class,
        test_get_document_storage_default_local,
    ]
    failed = []
    for test_fn in tests:
        try:
            test_fn()
        except Exception as e:
            logger.exception("FAIL: %s", test_fn.__name__)
            failed.append((test_fn.__name__, e))
    logger.info("=" * 60)
    logger.info("SUMMARY: %d passed, %d failed", len(tests) - len(failed), len(failed))
    if failed:
        for name, err in failed:
            logger.error("  FAIL: %s - %s", name, err)
        return 1
    logger.info("All document storage tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
