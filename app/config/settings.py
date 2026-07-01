from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # Groq API
    GROQ_API_KEY: str = ""

    # App
    PORT: int = 8000
    ENV: str = "development"
    WEBHOOK_URL: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
