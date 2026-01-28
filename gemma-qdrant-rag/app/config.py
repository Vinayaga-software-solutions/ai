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
    EMBEDDING_API_URL: Optional[str] = "http://embedding-service:8080/embed"
    EMBEDDING_DIM: int = 384

    # --- Vector DB (Qdrant) ---
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PATH: Optional[str] = None
    QDRANT_COLLECTION: str = "rag_collection"

    class Config:
        env_file = ".env"

settings = Settings()
