from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .embeddings import BGEEmbeddings
from .vector_store import VectorDB
from .llm import GemmaLLM
from .config import settings
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
    try:
        vector = embeddings.embed_query(request.text)
        # Using hash of text as a simple ID method for demo
        point_id = hash(request.text) % (10**8) 
        db.upsert(
            ids=[point_id],
            vectors=[vector],
            payloads=[{"text": request.text, **request.metadata}]
        )
        return {"status": "success", "id": point_id}
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
            "sources": [r.payload for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
