from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # --- Orchestrator Settings ---
    APP_NAME: str = "RAG-Orchestrator"
    
    # --- LLM Service (Gemma) ---
    # Can point to a local Ollama service or a Cloud/vLLM endpoint
    LLM_PROVIDER: str = "ollama"  # "ollama" or "openai_compatible"
    LLM_MODEL: str = "gemma:2b"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = "http://llm-service:11434" # Internal docker name
    OLLAMA_HOST: str = "http://llm-service:11434"

    # --- Embedding Service (BGE) ---
    # Use 'local' to keep using fastembed, or 'remote' to call an external API
    EMBEDDING_STRATEGY: str = "local" 
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_API_URL: Optional[str] = "http://embedding-service:80/embed"
    EMBEDDING_DIM: int = 384

    # --- Vector DB (Qdrant) ---
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PATH: Optional[str] = None
    QDRANT_COLLECTION: str = "rag_collection"

    # --- Document Storage (ingest-cli) ---
    # Use 'local' for dev (saves to folder) or 'gcs' for prod (saves to Google Cloud Storage)
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage/documents"
    GCS_BUCKET_NAME: Optional[str] = None
    GCS_CREDENTIALS_PATH: Optional[str] = None  # Optional; uses default credentials if unset

    # --- RAG Specific Settings ---
    RAG_THRESHOLD: float = 0.6
    RAG_TOP_K: int = 5

    # --- Service hosts (for microservice delegation) ---
    INGESTION_HOST: str = "ingestion"
    INGESTION_PORT: int = 80

    CHUNKING_HOST: str = "chunking"
    CHUNKING_PORT: int = 80

    RETRIEVAL_HOST: str = "retrieval"
    RETRIEVAL_PORT: int = 80

    # --- LLM Generation Settings ---
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_P: float = 0.9

    class Config:
        env_file = ".env"

settings = Settings()
