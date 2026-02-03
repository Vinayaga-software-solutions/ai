from pydantic import BaseSettings

class Settings(BaseSettings):
    service_name: str = "ingestion"
    host: str = "0.0.0.0"
    port: int = 80

    CHUNKING_HOST: str = "chunking"
    CHUNKING_PORT: int = 80

    EMBEDDING_SERVICE_HOST: str = "embedding-service"
    EMBEDDING_SERVICE_PORT: int = 80

    RETRIEVAL_HOST: str = "retrieval"
    RETRIEVAL_PORT: int = 80

    class Config:
        env_file = ".env.services"

settings = Settings()
