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

## 🛠️ Configuration (The Orchestrator)
You can tune the system behavior by editing the `.env` file:
- `EMBEDDING_STRATEGY`: Set to `remote` to use the TEI service (fastest) or `local` for zero-dependency runs.
- `LLM_MODEL`: Change this to `gemma:7b` (if your hardware supports it) or any other Ollama-supported model.
- `QDRANT_HOST`: Points to the vector database address.
