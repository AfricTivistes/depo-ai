from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str ="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"
    MODEL: str = "deepseek/deepseek-chat"
    API_URL: str = "https://openrouter.ai/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()