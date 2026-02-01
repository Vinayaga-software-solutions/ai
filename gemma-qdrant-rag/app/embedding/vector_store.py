from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self):
        if settings.QDRANT_PATH:
            # Local storage mode
            self.client = QdrantClient(path=settings.QDRANT_PATH)
        else:
            # Server or Cloud mode
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY
            )
        
        self.collection_name = settings.QDRANT_COLLECTION
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIM, 
                    distance=models.Distance.COSINE
                ),
            )

    def upsert(self, ids: List[int], vectors: List[List[float]], payloads: List[Dict[str, Any]]):
        # Validate and log vector dimensions to ensure they match collection config
        if vectors:
            dims = [len(v) for v in vectors]
            logger.info(f"Upserting {len(ids)} vectors; dims={dims}; expected={settings.EMBEDDING_DIM}")
            for i, v in enumerate(vectors):
                if len(v) != settings.EMBEDDING_DIM:
                    raise ValueError(f"Vector dimension mismatch for index {i}: got {len(v)}, expected {settings.EMBEDDING_DIM}")

        # Log payload keys for debugging
        try:
            sample_keys = [list(p.keys()) for p in (payloads or [])[:3]]
            logger.info(f"Payload keys sample (up to 3): {sample_keys}")
        except Exception as e:
            logger.warning(f"Could not inspect payloads before upsert: {e}")

        result = self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )
        )

        # Log result or basic confirmation
        try:
            logger.info(f"Upsert returned: {result}")
        except Exception:
            logger.info("Upsert completed (result not displayed)")

    def search(self, query_vector: List[float], limit: int = 3, score_threshold: float = 0.75):
        # Search Vector DB with score threshold
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        return response.points

    def clear(self) -> None:
        """Delete all points in the collection by recreating it with the same config."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()
