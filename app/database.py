from sqlalchemy.ext.declarative import declarative_base
from .core.config import get_session_local, get_engine

engine = get_engine()
SessionLocal = get_session_local
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()