from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    meili_url: str = "http://localhost:7700"
    meili_api_key: Optional[str] = None
    meili_master_key: Optional[str] = None
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    openai_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
