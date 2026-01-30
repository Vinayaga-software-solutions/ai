from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from .config import settings

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
        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )
        )

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
