from typing import Optional
from app.domain.entities.url import UrlEntity
from app.domain.repositories.url_repository import UrlRepository
from app.utils.keygen import create_random_key
from app.utils.logging import get_logger

logger = get_logger()


class UrlService:
    """Application service for URL operations."""

    def __init__(self, url_repository: UrlRepository):
        self.url_repository = url_repository

    def create_short_url(self, target_url: str) -> UrlEntity:
        logger.info("Creating short URL", target_url=target_url)
        key = self._generate_unique_key()
        secret_key = f"{key}_{create_random_key(length=8)}"

        url_entity = self._create_url_entity(target_url, key, secret_key)
        self._validate_url(url_entity, target_url)

        result = self.url_repository.create(url_entity)
        logger.info("Successfully created short URL", key=key, target_url=target_url)
        return result

    def create_custom_short_url(self, target_url: str, custom_key: str) -> UrlEntity:
        logger.info("Creating custom short URL", target_url=target_url, custom_key=custom_key)
        existing_url = self.url_repository.get_by_key(custom_key)
        if existing_url:
            logger.warning("Attempt to create duplicate custom key", custom_key=custom_key)
            raise ValueError(f"Key '{custom_key}' already exists")

        secret_key = f"{custom_key}_{create_random_key(length=8)}"
        url_entity = self._create_url_entity(target_url, custom_key, secret_key)
        self._validate_url(url_entity, target_url)

        result = self.url_repository.create(url_entity)
        logger.info("Successfully created custom short URL", custom_key=custom_key, target_url=target_url)
        return result

    def get_url_by_key(self, key: str) -> Optional[UrlEntity]:
        logger.info("Retrieving URL by key", key=key)
        url_entity = self.url_repository.get_by_key(key)
        if url_entity and url_entity.is_active:
            logger.info("Found active URL for key", key=key)
            return url_entity
        else:
            logger.info("No active URL found for key", key=key)
            return None

    def get_url_by_secret_key(self, secret_key: str) -> Optional[UrlEntity]:
        logger.info("Retrieving URL by secret key", secret_key_preview=secret_key[:8])
        url_entity = self.url_repository.get_by_secret_key(secret_key)
        if url_entity and url_entity.is_active:
            logger.info("Found active URL for secret key", secret_key_preview=secret_key[:8])
            return url_entity
        else:
            logger.info("No active URL found for secret key", secret_key_preview=secret_key[:8])
            return None

    def increment_click_count(self, url_entity: UrlEntity) -> UrlEntity:
        logger.info("Incrementing click count", url_key=url_entity.key)
        url_entity.increment_clicks()
        result = self.url_repository.update(url_entity)
        logger.info("Updated click count", url_key=url_entity.key, new_clicks=result.clicks)
        return result

    def delete_url_by_secret_key(self, secret_key: str) -> Optional[UrlEntity]:
        logger.info("Deactivating URL by secret key", secret_key_preview=secret_key[:8])
        url_entity = self.url_repository.get_by_secret_key(secret_key)
        if url_entity:
            url_entity.deactivate()
            result = self.url_repository.update(url_entity)
            logger.info("Successfully deactivated URL", secret_key_preview=secret_key[:8])
            return result
        logger.warning("Attempt to deactivate non-existent URL", secret_key_preview=secret_key[:8])
        return None

    def _generate_unique_key(self, max_attempts: int = 10) -> str:
        for _ in range(max_attempts):
            key = create_random_key()
            if not self.url_repository.get_by_key(key):
                return key

        extended_key = create_random_key(length=12)
        attempts = 0
        while self.url_repository.get_by_key(extended_key) and attempts < max_attempts:
            extended_key = create_random_key(length=12)
            attempts += 1

        if self.url_repository.get_by_key(extended_key):
            raise Exception("Unable to generate unique key after multiple attempts. Namespace may be exhausted.")

        return extended_key

    def _create_url_entity(self, target_url: str, key: str, secret_key: str) -> UrlEntity:
        return UrlEntity(
            target_url=target_url,
            key=key,
            secret_key=secret_key
        )

    def _validate_url(self, url_entity: UrlEntity, target_url: str) -> None:
        if not url_entity.validate_url():
            raise ValueError(f"Invalid URL format: {target_url}")