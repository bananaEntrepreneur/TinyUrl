from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.url import UrlEntity
from app.domain.repositories.url_repository import UrlRepository
from app.models.urls import URL as URLModel


class SqlAlchemyUrlRepository(UrlRepository):
    """SQL Alchemy implementation of the URL repository."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, url_entity: UrlEntity) -> UrlEntity:
        db_url = URLModel(
            target_url=url_entity.target_url,
            key=url_entity.key,
            secret_key=url_entity.secret_key,
            is_active=url_entity.is_active,
            clicks=url_entity.clicks
        )

        self.db_session.add(db_url)
        self.db_session.commit()
        self.db_session.refresh(db_url)

        return self._map_to_entity(db_url)

    def get_by_key(self, key: str) -> Optional[UrlEntity]:
        db_url = (
            self.db_session.query(URLModel)
            .filter(URLModel.key == key, URLModel.is_active)
            .first()
        )
        return self._map_to_entity(db_url) if db_url else None

    def get_by_secret_key(self, secret_key: str) -> Optional[UrlEntity]:
        db_url = (
            self.db_session.query(URLModel)
            .filter(URLModel.secret_key == secret_key, URLModel.is_active)
            .first()
        )
        return self._map_to_entity(db_url) if db_url else None

    def update(self, url_entity: UrlEntity) -> UrlEntity:
        db_url = (
            self.db_session.query(URLModel)
            .filter(URLModel.key == url_entity.key)
            .first()
        )

        if db_url:
            db_url.target_url = url_entity.target_url
            db_url.is_active = url_entity.is_active
            db_url.clicks = url_entity.clicks
            db_url.secret_key = url_entity.secret_key

            self.db_session.commit()
            self.db_session.refresh(db_url)

            return self._map_to_entity(db_url)
        return None

    def delete_by_secret_key(self, secret_key: str) -> Optional[UrlEntity]:
        db_url = (
            self.db_session.query(URLModel)
            .filter(URLModel.secret_key == secret_key)
            .first()
        )

        if db_url:
            db_url.is_active = False
            self.db_session.commit()
            self.db_session.refresh(db_url)

            return self._map_to_entity(db_url)
        return None

    def get_all(self) -> List[UrlEntity]:
        db_urls = self.db_session.query(URLModel).all()
        return [self._map_to_entity(db_url) for db_url in db_urls]

    def _map_to_entity(self, db_url) -> UrlEntity:
        return UrlEntity(
            target_url=db_url.target_url,
            key=db_url.key,
            secret_key=db_url.secret_key,
            is_active=db_url.is_active,
            clicks=db_url.clicks
        )