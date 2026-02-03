from typing import List, Dict, Any
from app.config import settings
import logging
import requests

logger = logging.getLogger(__name__)

class VectorDB:
    """Proxy client that interacts with the retrieval microservice for vector operations.

    This class no longer supports local qdrant usage and will always forward
    upsert/search/clear operations to the retrieval service defined by
    RETRIEVAL_HOST/RETRIEVAL_PORT.
    """

    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        host = getattr(settings, "RETRIEVAL_HOST", "retrieval")
        port = getattr(settings, "RETRIEVAL_PORT", 80)
        self.base_url = f"http://{host}:{port}"

    def upsert(self, ids: List[int], vectors: List[List[float]], payloads: List[Dict[str, Any]]):
        url = f"{self.base_url}/vectors/upsert"
        resp = requests.post(url, json={"ids": ids, "vectors": vectors, "payloads": payloads}, timeout=30)
        resp.raise_for_status()
        logger.info("Proxied upsert to retrieval service.")

    def search(self, query_vector: List[float], limit: int = 3, score_threshold: float = 0.75):
        url = f"{self.base_url}/search"
        resp = requests.post(url, json={"query_vector": query_vector, "limit": limit, "score_threshold": score_threshold}, timeout=30)
        resp.raise_for_status()
        return resp.json().get("results", [])

    def clear(self) -> None:
        url = f"{self.base_url}/vectors/clear"
        resp = requests.post(url, timeout=30)
        resp.raise_for_status()
        logger.info("Requested retrieval service to clear vectors.")
