# Configuration management
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Yuzuriha Rin Virtual Chat"
    debug: bool = True
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()