import requests
from typing import List
from .config import settings
import logging

logger = logging.getLogger(__name__)

class BGEEmbeddings:
    def __init__(self):
        self.strategy = settings.EMBEDDING_STRATEGY
        if self.strategy == "local":
            try:
                from fastembed import TextEmbedding
                self.model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
            except ImportError:
                logger.warning("FastEmbed not found, falling back to remote strategy")
                self.strategy = "remote"

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        if self.strategy == "local":
            embeddings = list(self.model.embed(documents))
            return [e.tolist() for e in embeddings]
        else:
            # Call external microservice
            try:
                response = requests.post(
                    settings.EMBEDDING_API_URL, 
                    json={"inputs": documents}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Embedding service failed: {e}")
                if 'response' in locals():
                    logger.error(f"Response content: {response.text}")
                raise e

    def embed_query(self, query: str) -> List[float]:
        if self.strategy == "local":
            try:
                embedding = list(self.model.embed([query]))[0]
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Local embedding failed: {e}")
                raise e
        else:
            # Call external microservice
            try:
                response = requests.post(
                    settings.EMBEDDING_API_URL, 
                    json={"inputs": [query]}
                )
                response.raise_for_status()
                return response.json()[0]
            except Exception as e:
                logger.error(f"Embedding service failed: {e}")
                raise e
