from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.embedding import BGEEmbeddings, VectorDB
from app.retrieval import GemmaLLM
from app.config import settings
from app.ingestion import IngestionPipeline
import uvicorn

app = FastAPI(title="Gemma-Qdrant RAG Service")

# Initialize components
embeddings = BGEEmbeddings()
db = VectorDB()
llm = GemmaLLM()

class QueryRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    text: str
    metadata: dict = {}

@app.post("/ingest")
async def ingest_data(request: IngestRequest):
    """Use the full ingestion pipeline for /ingest requests so behavior matches file ingestion.
    This will apply cleaning, chunking, embedding generation, and proper metadata payloads.
    """
    try:
        pipeline = IngestionPipeline()
        doc_id = None
        source = None
        additional_metadata = None
        if request.metadata:
            additional_metadata = request.metadata
            doc_id = request.metadata.get("doc_id")
            source = request.metadata.get("source")

        result = pipeline.ingest_text(
            text=request.text,
            doc_id=doc_id,
            source=source or "api",
            additional_metadata=additional_metadata
        )

        if result.get("success"):
            return {
                "status": "success",
                "id": result.get("doc_id"),
                "chunks_created": result.get("chunks_created"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "ingestion failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        # 0. Basic Validation
        if not request.question.strip():
            return {"answer": "I'm sorry, I cannot process an empty question.", "sources": []}

        # 1. Embed query
        query_vector = embeddings.embed_query(request.question)
        
        # 2. Search Vector DB with dynamic settings
        results = db.search(
            query_vector, 
            limit=settings.RAG_TOP_K, 
            score_threshold=settings.RAG_THRESHOLD
        )
        
        # Log scores for calibration
        print(f"Query: '{request.question}'")
        print(f"Hits: {[f'{r.score:.3f}' for r in results]}")
        
        # 3. Handle "No context found" or Low Similarity
        if not results:
            return {
                "answer": "I'm sorry, I don't have enough verified context to answer this question. I can only provide information based on the documents I've been given.",
                "sources": []
            }

        context = "\n".join([r.payload["text"] for r in results])
        
        # 4. Generate Answer
        answer = llm.generate(request.question, context)
        
        return {
            "answer": answer,
            "sources": [{**r.payload, "score": r.score} for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory")
async def clear_memory():
    """Clear the full Qdrant vector store (all ingested documents)."""
    try:
        db.clear()
        return {"status": "ok", "message": "Qdrant memory cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
