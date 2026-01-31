from fastapi import FastAPI
from .config import settings

app = FastAPI(title=settings.service_name)

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}

@app.get("/summarize")
async def summarize():
    return {"message": "summary placeholder"}
