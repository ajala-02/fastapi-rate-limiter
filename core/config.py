from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./limiter.db"
    DEFAULT_REFILL_RATE: float = 1.666 # Tokens per second (~100/min)
    DEFAULT_BUCKET_CAPACITY: int = 100

    class Config:
        env_file = ".env"

settings = Settings()
