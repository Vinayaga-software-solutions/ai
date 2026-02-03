from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import settings
from .chunker import DocumentChunker

app = FastAPI(title=settings.service_name)

chunker = DocumentChunker()

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}

class ChunkRequest(BaseModel):
    text: str
    doc_id: str
    source: str = ""

@app.post("/chunk")
async def chunk(req: ChunkRequest):
    try:
        chunks = chunker.chunk_document(req.text, req.doc_id, req.source)
        return {"chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
