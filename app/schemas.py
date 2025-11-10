from pydantic import BaseModel, HttpUrl, field_validator

class URLBase(BaseModel):
    """Base schema for URL"""
    target_url: HttpUrl # URL validation with built-in Pydantic HttpUrl

class URL(URLBase):
    """
    Main URL schema for database operations and API responses.
    Includes operational fields like activity status and click counter.
    """
    is_active: bool = True
    clicks: int = 0

    class Config:
        """Pydantic configuration for database compatibility"""
        orm_mode = True
        from_attributes = True

class URLInfo(URL):
    """
    Extended URL information schema for client responses.
    Includes generated URLs for both redirection and administration.
    """
    url: str # The complete short URL
    admin_url: str # Administrative URL for managing the short URL