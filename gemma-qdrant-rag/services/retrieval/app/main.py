from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import settings
from .vector_store import VectorDB
from typing import List, Dict, Any

app = FastAPI(title=settings.service_name)

db = VectorDB()

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}

class UpsertRequest(BaseModel):
    ids: List[int]
    vectors: List[List[float]]
    payloads: List[Dict[str, Any]] | None = None

@app.post("/vectors/upsert")
async def upsert(req: UpsertRequest):
    try:
        db.upsert(req.ids, req.vectors, req.payloads or [])
        return {"status": "ok", "upserted": len(req.ids)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class SearchRequest(BaseModel):
    query_vector: List[float]
    limit: int = 3
    score_threshold: float = 0.75

@app.post("/search")
async def search(req: SearchRequest):
    try:
        points = db.search(req.query_vector, req.limit, req.score_threshold)
        return {"results": points}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/vectors/clear")
async def clear_vectors():
    """Clear the entire vector collection (admin operation).
    """
    try:
        db.clear()
        return {"status": "ok", "cleared": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
