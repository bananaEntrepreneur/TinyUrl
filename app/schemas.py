from pydantic import BaseModel, HttpUrl, field_validator

class URLBase(BaseModel):
    """Base schema for URL"""
    target_url: HttpUrl # URL validation with built-in Pydantic HttpUrl

    @field_validator('target_url')
    @classmethod
    def validate_target_url(cls, value: HttpUrl) -> HttpUrl:
        """
        Validate target URL for safety and compatibility.

        Args:
            v: The URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is not allowed or invalid
        """
        # Example validation: prevent redirects to same domain to avoid loops
        forbidden_domains = ['localhost', '127.0.0.1', '0.0.0.0']
        if any(domain in str(value) for domain in forbidden_domains):
            raise ValueError('Redirects to local domains are not allowed')
        return value

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