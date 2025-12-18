from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./tiny.db"

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings from {settings.env_name}")
    return settings

if __name__ == "__main__":
    settings = get_settings()
    print(f"Environment: {settings.env_name}")
    print(f"Base URL: {settings.base_url}")
    print(f"Database URL: {settings.db_url}")