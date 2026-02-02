import os
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Settings:
    def __init__(self):
        self.env_name = os.getenv("ENV_NAME", "dev")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        self.db_url = os.getenv("DB_URL", "postgresql://user:password@localhost/dbname")

    @property
    def engine(self):
        return create_engine(
            self.db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
        )

    @property
    def session_local(self):
        return sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )


@lru_cache()
def get_settings():
    settings = Settings()
    print(f"Loading settings from {settings.env_name}")
    return settings


def get_engine():
    return get_settings().engine


def get_session_local():
    return get_settings().session_local()