from typing import Generator
from sqlalchemy.orm import Session
from ..database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency that provides database sessions to API endpoints.

    Yields:
        Session: Database session for the request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()