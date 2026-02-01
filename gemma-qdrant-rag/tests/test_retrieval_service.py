#!/usr/bin/env python3
"""
Unit tests for the Retrieval microservice (app.retrieval).
Tests GemmaLLM with mocked ollama/OpenAI so no real LLM is required.
"""
import sys
import os
import logging
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_llm_ollama_mock():
    """GemmaLLM (ollama) returns response from mocked client."""
    with patch("app.retrieval.llm.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "ollama"
        mock_settings.LLM_MODEL = "gemma:2b"
        mock_settings.OLLAMA_HOST = "http://fake"
        mock_settings.LLM_MAX_TOKENS = 100
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_TOP_P = 0.9
        with patch("app.retrieval.llm.ollama") as mock_ollama:
            mock_client = MagicMock()
            mock_client.generate.return_value = {"response": "Mocked answer"}
            mock_ollama.Client.return_value = mock_client
            from app.retrieval import GemmaLLM
            llm = GemmaLLM()
            out = llm.generate("What is RAG?", context="RAG is retrieval-augmented generation.")
            assert out == "Mocked answer"
            mock_client.generate.assert_called_once()
            call_kw = mock_client.generate.call_args[1]
            assert "prompt" in call_kw
            assert "RAG" in call_kw["prompt"]
    logger.info("PASS: test_llm_ollama_mock")
    return True


def test_llm_builds_prompt():
    """GemmaLLM.generate builds prompt with context and question."""
    with patch("app.retrieval.llm.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "ollama"
        mock_settings.LLM_MODEL = "gemma:2b"
        mock_settings.OLLAMA_HOST = "http://fake"
        mock_settings.LLM_MAX_TOKENS = 100
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_TOP_P = 0.9
        with patch("app.retrieval.llm.ollama") as mock_ollama:
            mock_client = MagicMock()
            mock_client.generate.return_value = {"response": "ok"}
            mock_ollama.Client.return_value = mock_client
            from app.retrieval import GemmaLLM
            llm = GemmaLLM()
            llm.generate("Q?", context="Ctx here")
            call_kw = mock_client.generate.call_args[1]
            assert "Q?" in call_kw["prompt"]
            assert "Ctx here" in call_kw["prompt"]
    logger.info("PASS: test_llm_builds_prompt")
    return True


def test_llm_unsupported_provider():
    """GemmaLLM returns message for unsupported provider."""
    with patch("app.retrieval.llm.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "unknown_provider"
        mock_settings.LLM_MODEL = "x"
        from app.retrieval import GemmaLLM
        llm = GemmaLLM()
        out = llm.generate("Hi", context="")
        assert "Unsupported" in out or "unknown" in out.lower()
    logger.info("PASS: test_llm_unsupported_provider")
    return True


def main():
    logger.info("Retrieval service tests...")
    tests = [
        test_llm_ollama_mock,
        test_llm_builds_prompt,
        test_llm_unsupported_provider,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            logger.exception("FAIL: %s", t.__name__)
            failed.append((t.__name__, e))
    logger.info("=" * 60)
    logger.info("Retrieval: %d passed, %d failed", len(tests) - len(failed), len(failed))
    if failed:
        for name, err in failed:
            logger.error("  %s: %s", name, err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
