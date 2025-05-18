from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str  # Plus de valeur par défaut dans le code
    MODEL: str = "deepseek/deepseek-chat:free"
    API_URL: str = "https://openrouter.ai/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()