from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    service_name: str = "retrieval"
    host: str = "0.0.0.0"
    port: int = 80

    # Qdrant settings
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PATH: Optional[str] = None
    QDRANT_COLLECTION: str = "rag_collection"

    # Embedding dim (must match embedding service)
    EMBEDDING_DIM: int = 384

    class Config:
        env_file = ".env.services"

settings = Settings()
