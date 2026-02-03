# RAG Test Suite

Automated unit and integration tests for the Gemma-Qdrant RAG service.  
**Run all commands from the project root** (`gemma-qdrant-rag/`). Install dependencies first: `pip install -r requirements.txt`.

---

## One command: all unit tests (no services)

```powershell
python tests/run_unit_tests.py
```

Runs all unit tests including per-microservice tests. No API, Qdrant, or LLM required.

---

## One command: all integration tests (API must be up)

```powershell
python tests/run_integration_tests.py
```

Waits for `http://localhost:8000`, then runs the full suite (ingest sample data + answerable/refusal/edge questions). Results in `tests/test_results.json`. Start the API first (e.g. `docker-compose up -d` or `uvicorn app.main:app --port 8000`).

---

## Individual tests

| What to test | Command | Prerequisites |
| :--- | :--- | :--- |
| **All unit tests** | `python tests/run_unit_tests.py` | None |
| **All integration tests** | `python tests/run_integration_tests.py` | API at `http://localhost:8000` |
| **RAG API** (query smoke) | `python tests/test_rag_api.py` | API running |
| **Full integration** (ingest + Q&A) | `cd tests; python run_tests.py` | API running |
| **Ingestion pipeline** | `python tests/test_ingestion_simple.py` | None |
| **Document storage** | `python tests/test_document_storage.py` | None |
| **Chunking service** | `python tests/test_chunking_service.py` | None |
| **Ingestion service** | `python tests/test_ingestion_service.py` | None |
| **Embedding service** | `python tests/test_embedding_service.py` | None |
| **Retrieval service** | `python tests/test_retrieval_service.py` | None |

---

## Test case coverage

### Unit (no services)
- **`test_ingestion_simple.py`**: Extract, clean, chunk pipeline (no Qdrant/embeddings).
- **`test_document_storage.py`**: Local save/copy, directory creation, GCS config (local vs gcs). Uses a temp dir; no GCS credentials needed.
- **`test_chunking_service.py`**: Chunking microservice — TextCleaner, TextChunker, DocumentChunker.
- **`test_ingestion_service.py`**: Ingestion microservice — TextExtractor, document storage, IngestionPipeline (with mocked embed/store).
- **`test_embedding_service.py`**: Embedding microservice — VectorDB (local path, no server), BGEEmbeddings (mocked remote).
- **`test_retrieval_service.py`**: Retrieval microservice — GemmaLLM with mocked ollama/OpenAI.

### Integration (API running)
- **`run_tests.py`**: Ingest sample data, then ~20 cases — answerable, refusal, and edge questions; writes `test_results.json`.
- **`test_rag_api.py`**: Smoke test — sends questions to `/query` and prints answers/sources.

### Question categories (in `run_tests.py`)
1. **Answerable**: Based on sample data (e.g. NovaStream AI).
2. **Refusal**: Malicious, private, or out-of-scope requests.
3. **Edge**: Empty strings, special characters, long queries, multilingual input.

---

## Prerequisites and results

1. **Start the API** (for integration tests): `docker compose up -d` or `uvicorn app.main:app --port 8000`.
2. **Install deps**: From project root, `pip install -r requirements.txt`. If you are developing a specific service, install its dependencies with `pip install -r services/<service>/requirements.txt` (e.g., `services/retrieval/requirements.txt` includes `qdrant-client`).
3. **Notes**: Unit tests are designed to run without Docker — they mock external service HTTP calls. For full integration testing (Qdrant + LLM + embedders) run the integration suite with the API and dependent services up.
4. **Results**: Integration suite writes `tests/test_results.json`.
