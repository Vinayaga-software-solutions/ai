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


def test_vector_db_proxy_upsert_search():
    """VectorDB proxies upsert and search calls to retrieval microservice."""
    with patch("app.embedding.vector_store.settings") as mock_settings:
        mock_settings.QDRANT_COLLECTION = "test_collection"
        mock_settings.RETRIEVAL_HOST = "fakehost"
        mock_settings.RETRIEVAL_PORT = 1234
        from app.embedding import VectorDB
        db = VectorDB()
        # Mock requests.post for upsert and search
        with patch("requests.post") as mock_post:
            # upsert call returns 200
            mock_post.return_value.raise_for_status = MagicMock()
            db.upsert(ids=[1], vectors=[[0.1, 0.2, 0.3, 0.4]], payloads=[{"text": "hello", "source": "test"}])
            # Ensure first call was to /vectors/upsert
            assert any("/vectors/upsert" in args[0] for args, _ in mock_post.call_args_list)

            # Now mock search response
            mock_post.reset_mock()
            resp = MagicMock()
            resp.raise_for_status = MagicMock()
            resp.json.return_value = {"results": [{"payload": {"text": "hello"}, "score": 0.9}]}
            mock_post.return_value = resp
            results = db.search([0.1, 0.2, 0.3, 0.4], limit=1, score_threshold=0.0)
            assert len(results) == 1
            assert results[0]["payload"]["text"] == "hello"
    logger.info("PASS: test_vector_db_proxy_upsert_search")
    return True


def test_vector_db_proxy_clear():
    """VectorDB.clear() will call the retrieval service clear endpoint."""
    with patch("app.embedding.vector_store.settings") as mock_settings:
        mock_settings.QDRANT_COLLECTION = "test_clear"
        mock_settings.RETRIEVAL_HOST = "fakehost"
        mock_settings.RETRIEVAL_PORT = 1234
        from app.embedding import VectorDB
        db = VectorDB()
        with patch("requests.post") as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            db.clear()
            assert any("/vectors/clear" in args[0] for args, _ in mock_post.call_args_list)
    logger.info("PASS: test_vector_db_proxy_clear")
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
        test_vector_db_proxy_upsert_search,
        test_vector_db_proxy_clear,
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
