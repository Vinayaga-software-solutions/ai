import requests
from fastembed import TextEmbedding
from typing import List
from .config import settings

class BGEEmbeddings:
    def __init__(self):
        self.strategy = settings.EMBEDDING_STRATEGY
        if self.strategy == "local":
            self.model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        if self.strategy == "local":
            embeddings = list(self.model.embed(documents))
            return [e.tolist() for e in embeddings]
        else:
            # Call external microservice
            response = requests.post(
                settings.EMBEDDING_API_URL, 
                json={"inputs": documents}
            )
            return response.json()

    def embed_query(self, query: str) -> List[float]:
        if self.strategy == "local":
            embedding = list(self.model.embed([query]))[0]
            return embedding.tolist()
        else:
            # Call external microservice
            response = requests.post(
                settings.EMBEDDING_API_URL, 
                json={"inputs": [query]}
            )
            return response.json()[0]
