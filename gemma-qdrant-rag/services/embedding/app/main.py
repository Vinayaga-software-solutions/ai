from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import settings
import numpy as np
import hashlib
import requests

app = FastAPI(title=settings.service_name)

class EmbedRequest(BaseModel):
    inputs: list[str]

class EmbedResponse(BaseModel):
    embeddings: list[list[float]]

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}

@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest):
    if settings.EMBEDDING_STRATEGY == "remote":
        if not settings.EMBEDDING_REMOTE_URL:
            raise HTTPException(status_code=500, detail="EMBEDDING_REMOTE_URL not configured")
        try:
            resp = requests.post(settings.EMBEDDING_REMOTE_URL, json={"inputs": req.inputs}, timeout=30)
            resp.raise_for_status()
            return {"embeddings": resp.json()}
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

    # Local deterministic embedding (hash-based) for reproducibility and lightweight behavior
    embeddings = []
    for text in req.inputs:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Expand hash to desired dim using repeated hashing
        vec = []
        seed = h
        while len(vec) < settings.EMBEDDING_DIM:
            seed = hashlib.sha256(seed).digest()
            arr = np.frombuffer(seed, dtype=np.uint8).astype(np.float32)
            vec.extend((arr / 255.0).tolist())
        embeddings.append(vec[: settings.EMBEDDING_DIM])

    return {"embeddings": embeddings}
