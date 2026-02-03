from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.retrieval import GemmaLLM
from app.config import settings
import uvicorn
import requests

app = FastAPI(title="Gemma-Qdrant RAG Service")

# Initialize LLM (kept local, uses external LLM service via settings)
llm = GemmaLLM()

# Service endpoints (use settings if available, fallback to Docker service names)
INGESTION_HOST = getattr(settings, "INGESTION_HOST", "ingestion")
INGESTION_PORT = getattr(settings, "INGESTION_PORT", 80)
INGESTION_URL = f"http://{INGESTION_HOST}:{INGESTION_PORT}/ingest/text"

EMBEDDING_URL = getattr(settings, "EMBEDDING_API_URL", None) or f"http://{getattr(settings, 'EMBEDDING_SERVICE_HOST', 'embedding-service')}:{getattr(settings, 'EMBEDDING_SERVICE_PORT', 80)}/embed"

RETRIEVAL_HOST = getattr(settings, "RETRIEVAL_HOST", "retrieval")
RETRIEVAL_PORT = getattr(settings, "RETRIEVAL_PORT", 80)
RETRIEVAL_BASE = f"http://{RETRIEVAL_HOST}:{RETRIEVAL_PORT}"

class QueryRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    text: str
    metadata: dict = {}

@app.post("/ingest")
async def ingest_data(request: IngestRequest):
    """Proxy ingestion requests to the ingestion microservice."""
    try:
        payload = {
            "text": request.text,
            "doc_id": request.metadata.get("doc_id") if request.metadata else None,
            "source": request.metadata.get("source") if request.metadata else None,
        }
        resp = requests.post(INGESTION_URL, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()

        if result.get("success"):
            return {
                "status": "success",
                "id": result.get("doc_id"),
                "chunks_created": result.get("chunks_created", result.get("chunks", 0)),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "ingestion failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        if not request.question.strip():
            return {"answer": "I'm sorry, I cannot process an empty question.", "sources": []}

        # 1. Embed query via embedding microservice
        embed_resp = requests.post(EMBEDDING_URL, json={"inputs": [request.question]}, timeout=30)
        embed_resp.raise_for_status()
        embeddings = embed_resp.json().get("embeddings", [])
        if not embeddings:
            raise HTTPException(status_code=502, detail="Embedding service returned no embeddings")
        query_vector = embeddings[0]

        # 2. Search via retrieval microservice
        search_body = {"query_vector": query_vector, "limit": settings.RAG_TOP_K, "score_threshold": settings.RAG_THRESHOLD}
        search_resp = requests.post(f"{RETRIEVAL_BASE}/search", json=search_body, timeout=30)
        search_resp.raise_for_status()
        results = search_resp.json().get("results", [])

        if not results:
            return {
                "answer": "I'm sorry, I don't have enough verified context to answer this question.",
                "sources": []
            }

        # Build context and source list from retrieval results
        context_parts = []
        sources = []
        for r in results:
            payload = r.get("payload") or {}
            text = payload.get("text") if isinstance(payload, dict) else (payload or "")
            context_parts.append(text)
            s = {**(payload if isinstance(payload, dict) else {}), "score": r.get("score")}
            sources.append(s)

        context = "\n".join([c for c in context_parts if c])

        # 3. Generate answer with LLM
        answer = llm.generate(request.question, context)

        return {"answer": answer, "sources": sources}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory")
async def clear_memory():
    """Clear the Qdrant memory by calling the retrieval service admin endpoint."""
    try:
        resp = requests.post(f"{RETRIEVAL_BASE}/vectors/clear", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
