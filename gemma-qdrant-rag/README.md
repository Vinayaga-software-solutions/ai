# Gemma-Qdrant RAG Service

A professional, microservice-oriented Retrieval-Augmented Generation (RAG) system using **Gemma 2B**, **Qdrant**, and **BGE Embeddings**.

## 🚀 Quick Start (Docker)

The fastest way to get started is using Docker Compose, which orchestrates all 4 microservices plus an automated data seeder.

### 1. Build and Run
```powershell
docker-compose up --build
```
*Note: The first run will take a few minutes as it downloads the Gemma model (approx 2GB) and embedding weights.*

### 2. Test the API
Once the logs show `Uvicorn running on http://0.0.0.0:8000`, open a new terminal and run:

**Search for information:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json" -Body '{"question": "What is Gemma?"}'
```

**Ingest new data:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ingest" -Method Post -ContentType "application/json" -Body '{"text": "Antigravity is a specialized AI coding assistant.", "metadata": {"source": "manual"}}'
```

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
- **`main.py`**: The FastAPI application setup. Defines the `/query`, `/ingest`, and `/health` endpoints. It acts as the "Controller" in the MVC pattern.
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
| `EMBEDDING_STRATEGY`| `remote` | `local` (fastembed) or `remote` (TEI) |

---

## 🚀 Ingestion CLI (Local Run)

You can run the ingestion tool locally while connecting to the Docker services (Qdrant & Embeddings).

### 1. Prerequisites
- Python 3.10+
- `pip install -r requirements.txt`

### 2. Run Ingestion
This connects to Qdrant (port 6333) and Embedding Service (port 8081) running in Docker.

**PowerShell:**
```powershell
$env:QDRANT_HOST="localhost"; $env:QDRANT_PORT="6333"; $env:EMBEDDING_STRATEGY="remote"; $env:EMBEDDING_API_URL="http://localhost:8081/embed"; python scripts/ingest_cli.py --file "data/sample_document.txt"
```

**Bash:**
```bash
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export EMBEDDING_STRATEGY="remote"
export EMBEDDING_API_URL="http://localhost:8081/embed"
python ingest_cli.py --file sample_document.txt
```

### 3. Verify Retrieval
```bash
python test_rag_api.py
```

