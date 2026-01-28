## Distributed Microservices Architecture

The application is now structured as a professional RAG system with 4 separate services:

1.  **Orchestrator (FastAPI)**: The central brain that handles logic, coordinates between services, and provides the API.
2.  **Embedding Service (BGE)**: A dedicated high-performance server (using Hugging Face TEI) for turning text into vectors.
3.  **Vector DB (Qdrant)**: Stores and searches through your high-dimensional vectors.
4.  **LLM Service (Gemma via Ollama)**: A dedicated service for running the large language model.

### Why this structure?
-   **Independent Scaling**: You can scale the Embedding service separately from the LLM service.
-   **Flexibility**: You can swap the LLM service for a cloud provider (like Groq) just by changing one environment variable.
-   **Performance**: Using dedicated tools like TEI for embeddings is much faster than running them inside your main Python app.

### Deployment (Full Stack)

To run the entire distributed stack at once:
```bash
docker-compose up --build
```

### Configuration (The Orchestrator)
Edit `.env` to point the Orchestrator to your remote services:
- `EMBEDDING_STRATEGY=remote` (Uses the separate BGE service)
- `LLM_PROVIDER=ollama`
- `QDRANT_HOST=qdrant`

## Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Query**:
   ```bash
   Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -ContentType "application/json" -Body '{"question": "What is Gemma?"}'
   ```
