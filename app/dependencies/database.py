from typing import Generator
from sqlalchemy.orm import Session
from ..core.config import get_session_local


def get_db() -> Generator[Session, None, None]:
    db = get_session_local()
    try:
        yield db
    finally:
        db.close()