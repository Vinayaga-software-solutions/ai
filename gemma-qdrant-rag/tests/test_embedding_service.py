#!/usr/bin/env python3
"""
Unit tests for the Embedding microservice (app.embedding).
Tests BGEEmbeddings (with mock or local) and VectorDB (local path, no server).
"""
import sys
import os
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_vector_db_local_upsert_search():
    """VectorDB with QDRANT_PATH (local) can upsert and search without a server."""
    tmp = tempfile.mkdtemp(prefix="qdrant_test_")
    try:
        with patch("app.embedding.vector_store.settings") as mock_settings:
            mock_settings.QDRANT_PATH = tmp
            mock_settings.QDRANT_HOST = None
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_API_KEY = None
            mock_settings.QDRANT_COLLECTION = "test_collection"
            mock_settings.EMBEDDING_DIM = 4
            from app.embedding import VectorDB
            db = VectorDB()
            try:
                db.upsert(
                    ids=[1],
                    vectors=[[0.1, 0.2, 0.3, 0.4]],
                    payloads=[{"text": "hello", "source": "test"}],
                )
                points = db.search([0.1, 0.2, 0.3, 0.4], limit=1, score_threshold=0.0)
                assert len(points) >= 1
                assert points[0].payload.get("text") == "hello"
            finally:
                del db
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    logger.info("PASS: test_vector_db_local_upsert_search")
    return True


def test_vector_db_clear():
    """VectorDB.clear() recreates collection; after clear, only new points exist."""
    tmp = tempfile.mkdtemp(prefix="qdrant_test_clear_")
    try:
        with patch("app.embedding.vector_store.settings") as mock_settings:
            mock_settings.QDRANT_PATH = tmp
            mock_settings.QDRANT_HOST = None
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_API_KEY = None
            mock_settings.QDRANT_COLLECTION = "test_clear"
            mock_settings.EMBEDDING_DIM = 4
            from app.embedding import VectorDB
            db = VectorDB()
            try:
                db.upsert(ids=[1], vectors=[[0.1] * 4], payloads=[{"t": "old"}])
                db.clear()
                # After clear, upsert one new point; search should return only that one.
                db.upsert(ids=[2], vectors=[[0.2] * 4], payloads=[{"t": "new"}])
                points = db.search([0.2] * 4, limit=10, score_threshold=0.0)
                assert len(points) >= 1
                assert points[0].payload.get("t") == "new"
            finally:
                del db
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    logger.info("PASS: test_vector_db_clear")
    return True


def test_bge_embeddings_remote_mock():
    """BGEEmbeddings (remote strategy) returns vectors from mocked API."""
    dim = 384
    with patch("app.embedding.embeddings.settings") as mock_settings:
        mock_settings.EMBEDDING_STRATEGY = "remote"
        mock_settings.EMBEDDING_API_URL = "http://fake/embed"
        mock_settings.EMBEDDING_MODEL = "test"
        from app.embedding import BGEEmbeddings
        emb = BGEEmbeddings()
        assert emb.strategy == "remote"
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = [[0.1] * dim]
            mock_post.return_value.raise_for_status = MagicMock()
            vec = emb.embed_query("hello")
            assert len(vec) == dim
            mock_post.assert_called_once()
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = [[0.1] * dim, [0.2] * dim]
            mock_post.return_value.raise_for_status = MagicMock()
            vecs = emb.embed_documents(["a", "b"])
            assert len(vecs) == 2
            assert len(vecs[0]) == dim
    logger.info("PASS: test_bge_embeddings_remote_mock")
    return True


def main():
    logger.info("Embedding service tests...")
    tests = [
        test_vector_db_local_upsert_search,
        test_vector_db_clear,
        test_bge_embeddings_remote_mock,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            logger.exception("FAIL: %s", t.__name__)
            failed.append((t.__name__, e))
    logger.info("=" * 60)
    logger.info("Embedding: %d passed, %d failed", len(tests) - len(failed), len(failed))
    if failed:
        for name, err in failed:
            logger.error("  %s: %s", name, err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
