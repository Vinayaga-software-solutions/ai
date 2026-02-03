# Gemma-Qdrant RAG Service

A professional, microservice-oriented Retrieval-Augmented Generation (RAG) system using **Gemma 2B**, **Qdrant**, and **BGE Embeddings**.

## 🚀 Quick Start (Docker)

The fastest way to get started is using Docker Compose, which orchestrates the Orchestrator, Vector DB (Qdrant), Embedding Service, LLM, and several new lightweight placeholder services (ingestion, chunking, retrieval, auth, gateway) plus an automated data seeder. All services are now part of the same `docker-compose.yml` so a single command will start or stop everything together.

### 1. Build and Run
```powershell
# Start all services (or stop them with CTRL+C or `docker compose down`)
docker compose up --build
```
*Note: The first run will take a few minutes as it downloads the Gemma model (approx 2GB) and embedding weights.*

During `docker compose up --build` a one-shot smoke test runs automatically (service `smoke`) which polls all service `/health` endpoints and validates readiness (*including the original services like Qdrant / LLM / Embedding*). If the smoke test fails it will exit non-zero and the smoke container will show the logs with details for quick troubleshooting.

**New skeleton services:**
- `ingestion` — port `8010` (placeholder)
- `chunking` — port `8011` (placeholder)
- `retrieval` — port `8012` (placeholder)
- `auth` — port `8013` (placeholder)
- `gateway` — port `8005` (placeholder)

These are minimal FastAPI skeletons (health endpoints and placeholders) intended to be expanded as you implement your features.

### 2. Test the API
Once the logs show `Uvicorn running on http://0.0.0.0:8000`, open a new terminal and run:

**Ask your own question (PowerShell — full response: answer + sources):**
```powershell
$r = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json" -Body '{"question": "What is Gemma?"}'
$r | ConvertTo-Json -Depth 10
```
*Use `ConvertTo-Json -Depth 10` so the full answer and all source chunks print without truncation.*

**Just the answer text:**
```powershell
(Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json" -Body '{"question": "What is Gemma?"}').answer
```
*Bash:* `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question": "What is Gemma?"}'`

**Ingest your own text:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ingest" -Method Post -ContentType "application/json" -Body '{"text": "Your content here.", "metadata": {"source": "manual"}}'
```
*Bash:* `curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"text": "Your content here."}'`

**Clear Qdrant (delete all ingested documents):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/memory" -Method Delete
```
*Bash:* `curl -X DELETE http://localhost:8000/memory`  
*On success: `{"status": "ok", "message": "Qdrant memory cleared."}` — collection is recreated empty.*

For **automated unit and integration tests**, see [tests/README.md](tests/README.md). Note: unit tests are designed to run without Docker by mocking service HTTP calls; run the integration smoke test using Docker Compose (`docker compose up smoke`) for end-to-end validation.

---

## 🖥️ Run Manually (Command Line)

Run the app without Docker from the project root. You need Qdrant, an embedding source, and an LLM (e.g. Ollama) available.

### 1. Prerequisites
- Python 3.10+
- Qdrant running (e.g. `docker run -p 6333:6333 qdrant/qdrant`) or use a remote URL
- Embeddings: **remote** embedding service (Text Embeddings Inference, TEI). The previous in-process local fallback (fastembed) has been removed — run the embedding microservice in Docker Compose or point `EMBEDDING_API_URL` to a hosted TEI endpoint.
- LLM: Ollama with `gemma:2b` or an OpenAI-compatible API (set `LLM_BASE_URL` / `LLM_API_KEY` in `.env`)

### 2. Install and configure
```powershell
cd gemma-qdrant-rag
# Install orchestrator (top-level) dependencies
pip install -r requirements.txt

# If you are developing a specific service, install its deps separately
pip install -r services/embedding/requirements.txt
pip install -r services/retrieval/requirements.txt
pip install -r services/chunking/requirements.txt

copy .env.example .env
# Edit .env: QDRANT_HOST, QDRANT_PORT, EMBEDDING_API_URL, LLM_BASE_URL, etc.
```
### 3. Start the API
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*Bash:* `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Once you see `Uvicorn running on http://0.0.0.0:8000`, use the same **Test the API** and **Ingestion CLI** commands as with Docker (e.g. `Invoke-RestMethod`, `python scripts/ingest_cli.py`, etc.).

---

## 🏗️ Architecture Overview

The system is split into independent services to ensure high performance, scalability, and easy maintenance.

### Microservices
1.  **Orchestrator (FastAPI)**: The central entry point. It receives user requests, handles RAG logic flows, and coordinates communication between all other services.
2.  **Embedding Service (BGE)**: Uses Hugging Face's **Text Embeddings Inference (TEI)**. This is a high-performance Rust-based server dedicated to converting text into vectors extremely quickly.
3.  **Vector DB (Qdrant)**: A specialized database for high-dimensional vector search. It handles the "Retrieval" part of RAG by finding the most relevant context for any given question.
4.  **LLM Service (Gemma)**: Powered by **Ollama**. It runs the `gemma:2b` model locally and generates human-like responses based on the context retrieved from Qdrant.

---

## 📂 Project Structure & Component Details

### Core Application (`/app`)
- **`main.py`**: The FastAPI application setup. Defines the `/query`, `/ingest`, `DELETE /memory` (clear Qdrant), and `/health` endpoints. It acts as the "Controller" in the MVC pattern.
- **`vector_store.py`**: A wrapper around the `qdrant-client`. It manages collection creation and abstraction of the `query_points` API.
- **`llm.py`**: Handles communication with the LLM provider. It supports both local Ollama and OpenAI-compatible APIs (like Groq or vLLM).
- **`embeddings.py`**: Manages how text is turned into vectors. It supports a "local" mode (running inside the orchestrator) or "remote" mode (calling the dedicated embedding service).
- **`config.py`**: Centralized configuration management using `pydantic-settings`. It reads from environment variables and the `.env` file.

### Infrastructure & Operations
- **`docker-compose.yml`**: The "blueprint" for the entire system. It defines how containers are linked, what ports are exposed, and how data volumes are mounted.
- **`Dockerfile`**: Defines the environment for the Orchestrator service (Python 3.11-slim, dependencies, etc.).
- **`ollama-entrypoint.sh`**: A helper script that automatically pulls the `gemma:2b` model when the LLM container starts up, so you don't have to do it manually.
- **`seed_data.py`**: An automated script that runs after the services are healthy to populate your database with initial knowledge about Gemma and RAG.
- **`.env`**: Stores configuration like model names and service URLs.

---

### 🛠️ Development (Hot Reload)
To enable fast development without rebuilding containers:
1.  **Mount Code**: The `docker-compose.yml` is now configured to mount your local `./app` directory into the container.
2.  **Auto-Reload**: The Orchestrator uses `uvicorn --reload`. Simply save a file in `/app` and the service will restart instantly inside the container.

---

## 🛠️ Configuration
You can tune the system behavior by editing the `.env` file or mapping environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LLM_MODEL` | `gemma:2b` | The model name (e.g., `llama3`, `phi3`) |
| `RAG_THRESHOLD` | `0.75` | Minimum similarity score (0.0 to 1.0) |
| `RAG_TOP_K` | `3` | Number of context chunks to retrieve |
| `LLM_MAX_TOKENS`| `512` | Max tokens for generation |
| `LLM_TEMPERATURE`| `0.7` | Randomness of response |
| `LLM_TOP_P` | `0.9` | Diversity of response |
| `EMBEDDING_STRATEGY`| `remote` | `remote` (TEI). **Local in-process mode has been removed.** |

---

## 🚀 Ingestion CLI (manual: your own document)

Ingest **your own files or text** from the command line (works with Docker or a manually started API). Connects to Qdrant and the embedding service.

### Prerequisites
- Python 3.10+, `pip install -r requirements.txt`
- API (and Qdrant/embedding) running — e.g. Docker or `uvicorn app.main:app --port 8000`

### Ingest a file
**PowerShell (Docker):**
```powershell
$env:QDRANT_HOST="localhost"; $env:QDRANT_PORT="6333"; $env:EMBEDDING_STRATEGY="remote"; $env:EMBEDDING_API_URL="http://localhost:8081/embed"
python scripts/ingest_cli.py --file "data/sample_document.txt"
```

**PowerShell (Local host, talking to Docker services):**
```powershell
$env:QDRANT_HOST="localhost"; $env:QDRANT_PORT="6333"
$env:EMBEDDING_STRATEGY="remote"; $env:EMBEDDING_API_URL="http://localhost:8081/embed"
$env:INGESTION_HOST="localhost"; $env:INGESTION_PORT="8010"
python scripts/ingest_cli.py --file "data/sample_document.txt"
```

**Bash:**
```bash
export QDRANT_HOST=localhost QDRANT_PORT=6333
export EMBEDDING_STRATEGY=remote EMBEDDING_API_URL="http://localhost:8081/embed"
export INGESTION_HOST=localhost INGESTION_PORT=8010
python scripts/ingest_cli.py --file data/sample_document.txt
```

### Ingest raw text
```powershell
python scripts/ingest_cli.py --text "Your own content here."
```

### Document storage (local vs GCS)
In `.env`: **Local** — `STORAGE_BACKEND=local`, `LOCAL_STORAGE_PATH=./storage/documents`. **GCS** — `STORAGE_BACKEND=gcs`, `GCS_BUCKET_NAME=your-bucket-name`. Ingested content is saved to the configured backend after successful ingestion.

