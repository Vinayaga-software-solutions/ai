from pydantic import BaseSettings

class Settings(BaseSettings):
    service_name: str = "retrieval"
    host: str = "0.0.0.0"
    port: int = 80

settings = Settings()
