from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import settings
from .chunker import DocumentChunker
from .tree_chunker import TreeChunker

app = FastAPI(title=settings.service_name)

chunker = DocumentChunker()
tree_chunker = TreeChunker()

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}

class ChunkRequest(BaseModel):
    text: str
    doc_id: str
    source: str = ""

class TreeChunkRequest(BaseModel):
    text: str
    doc_id: str
    source: str = ""
    doc_type: str = "plain"
    semantic_mapping: Dict[str, Dict[str, Any]] | None = None

@app.post("/chunk")
async def chunk(req: ChunkRequest):
    try:
        chunks = chunker.chunk_document(req.text, req.doc_id, req.source)
        return {"chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chunk/tree")
async def chunk_tree(req: TreeChunkRequest):
    try:
        chunks = tree_chunker.chunk_document(
            text=req.text,
            doc_id=req.doc_id,
            source=req.source,
            doc_type=req.doc_type,
            semantic_mapping=req.semantic_mapping,
        )
        return {"chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
