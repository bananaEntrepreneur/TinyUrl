from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.url import UrlEntity


class UrlRepository(ABC):
    """Interface for URL repository implementations."""

    @abstractmethod
    def create(self, url_entity: UrlEntity) -> UrlEntity:
        pass

    @abstractmethod
    def get_by_key(self, key: str) -> Optional[UrlEntity]:
        pass

    @abstractmethod
    def get_by_secret_key(self, secret_key: str) -> Optional[UrlEntity]:
        pass

    @abstractmethod
    def update(self, url_entity: UrlEntity) -> UrlEntity:
        pass

    @abstractmethod
    def delete_by_secret_key(self, secret_key: str) -> Optional[UrlEntity]:
        pass

    @abstractmethod
    def get_all(self) -> List[UrlEntity]:
        pass