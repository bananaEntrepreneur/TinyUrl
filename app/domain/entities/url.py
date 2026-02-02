from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import validators
from urllib.parse import urlparse


@dataclass
class UrlEntity:
    """
    Domain entity representing a URL shortener entry.

    This entity contains the core business logic and data for a shortened URL.
    """
    target_url: str
    key: str
    secret_key: str
    is_active: bool = True
    clicks: int = 0
    created_at: Optional[datetime] = None

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def increment_clicks(self) -> None:
        self.clicks += 1

    def validate_url(self) -> bool:
        try:
            if not validators.url(str(self.target_url)):
                return False

            parsed = urlparse(str(self.target_url))

            if parsed.scheme not in ['http', 'https']:
                return False

            if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                return False

            if parsed.scheme in ['file', 'javascript', 'data', 'vbscript']:
                return False

            return True
        except:
            return False