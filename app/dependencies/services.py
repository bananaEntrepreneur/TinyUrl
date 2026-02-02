from sqlalchemy.orm import Session
from fastapi import Depends
from ..application import UrlService
from ..infrastructure.repositories import SqlAlchemyUrlRepository
from .database import get_db


def get_url_service(db: Session = Depends(get_db)) -> UrlService:
    repository = SqlAlchemyUrlRepository(db_session=db)
    return UrlService(url_repository=repository)