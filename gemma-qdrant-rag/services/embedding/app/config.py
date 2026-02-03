from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    service_name: str = "embedding"
    host: str = "0.0.0.0"
    port: int = 80

    EMBEDDING_STRATEGY: str = "local"  # local or remote
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384
    EMBEDDING_REMOTE_URL: Optional[str] = None  # If strategy=remote, proxy to this

    class Config:
        env_file = ".env.services"

settings = Settings()
