from pydantic import BaseModel, HttpUrl, field_validator, Field


class URLBase(BaseModel):
    """
    Base schema for URL
    """
    target_url: HttpUrl

    @field_validator('target_url')
    @classmethod
    def convert_httpurl_to_str(cls, v: HttpUrl) -> str:
        """Convert HttpUrl to string for storaging in DB"""
        return str(v)


class URLCustom(URLBase):
    """
    Schema for creating custom short URL with custom key
    """
    custom_key: str = Field(
        min_length=3,
        max_length=20,
        description="Custom key for the short URL (3-20 characters, letters, numbers, hyphens, underscores)"
    )


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
    url: str
    admin_url: str