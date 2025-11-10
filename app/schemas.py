from pydantic import BaseModel, HttpUrl, field_validator

class URLBase(BaseModel):
    """Base schema for URL"""
    target_url: HttpUrl # URL validation with built-in Pydantic HttpUrl

    @field_validator('target_url')
    @classmethod
    def convert_httpurl_to_str(cls, v: HttpUrl) -> str:
        """Convert HttpUrl to string for storaging in DB"""
        return str(v)

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