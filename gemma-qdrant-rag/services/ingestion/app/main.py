from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import settings
import requests
import hashlib

app = FastAPI(title=settings.service_name)

CHUNKING_URL = f"http://{settings.CHUNKING_HOST}:{settings.CHUNKING_PORT}/chunk"
EMBEDDING_URL = f"http://{settings.EMBEDDING_SERVICE_HOST}:{settings.EMBEDDING_SERVICE_PORT}/embed"
RETRIEVAL_URL = f"http://{settings.RETRIEVAL_HOST}:{settings.RETRIEVAL_PORT}/vectors/upsert"

class IngestTextRequest(BaseModel):
    text: str
    doc_id: str | None = None
    source: str | None = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}

@app.post("/ingest/text")
async def ingest_text(req: IngestTextRequest):
    doc_id = req.doc_id or f"text_{hashlib.md5(req.text.encode()).hexdigest()[:8]}"
    source = req.source or "direct_text"

    # Step 1: Chunk
    try:
        chunk_resp = requests.post(CHUNKING_URL, json={"text": req.text, "doc_id": doc_id, "source": source}, timeout=30)
        chunk_resp.raise_for_status()
        chunks = chunk_resp.json().get("chunks", [])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chunking failed: {e}")

    if not chunks:
        return {"success": False, "error": "No chunks created", "doc_id": doc_id}

    # Step 2: Embed
    texts = [c["text"] for c in chunks]
    try:
        embed_resp = requests.post(EMBEDDING_URL, json={"inputs": texts}, timeout=60)
        embed_resp.raise_for_status()
        embeddings = embed_resp.json().get("embeddings", [])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embedding failed: {e}")

    if not embeddings or len(embeddings) != len(chunks):
        raise HTTPException(status_code=502, detail="Embedding service returned invalid result")

    # Step 3: Prepare upsert
    ids = []
    payloads = []
    for i, c in enumerate(chunks):
        chunk_id = c.get("chunk_id") or f"{doc_id}_chunk_{i}"
        # Create deterministic int id
        uid = int(hashlib.sha256(chunk_id.encode()).hexdigest(), 16) & ((1 << 63) - 1)
        ids.append(uid)
        payload = {
            "text": c.get("text", ""),
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "chunk_index": c.get("chunk_index", i),
            "total_chunks": c.get("total_chunks", len(chunks)),
            "token_count": c.get("token_count", 0),
            "source": source,
        }
        payloads.append(payload)

    upsert_body = {"ids": ids, "vectors": embeddings, "payloads": payloads}
    try:
        upsert_resp = requests.post(RETRIEVAL_URL, json=upsert_body, timeout=30)
        upsert_resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upsert failed: {e}")

    return {"success": True, "doc_id": doc_id, "chunks": len(chunks)}
