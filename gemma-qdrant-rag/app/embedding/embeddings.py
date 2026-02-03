import requests
from typing import List
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class BGEEmbeddings:
    """Thin client for the embedding microservice.

    This class purposely delegates to an external embedding service defined by
    settings.EMBEDDING_API_URL. Local model usage has been deprecated in favor
    of the dedicated `services/embedding` microservice.
    """

    def __init__(self):
        # Keep a compatibility attribute expected by tests
        self.strategy = "remote"
        self.api_url = settings.EMBEDDING_API_URL
        if not self.api_url:
            # Fallback to embedding-service host in .env.services
            host = getattr(settings, "EMBEDDING_SERVICE_HOST", "embedding-service")
            port = getattr(settings, "EMBEDDING_SERVICE_PORT", 80)
            self.api_url = f"http://{host}:{port}/embed"

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        try:
            resp = requests.post(self.api_url, json={"inputs": documents}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            return data.get("embeddings", [])
        except Exception as e:
            logger.error(f"Embedding service call failed: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        res = self.embed_documents([query])
        return res[0] if res else []
