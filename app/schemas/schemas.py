from pydantic import BaseModel, Field


class URLBase(BaseModel):
    target_url: str


class URLCustom(URLBase):
    custom_key: str = Field(
        min_length=3,
        max_length=20,
        description="Custom key for the short URL (3-20 characters, letters, numbers, hyphens, underscores)"
    )


class URLInfo(URLBase):
    is_active: bool = True
    clicks: int = 0
    key: str
    secret_key: str
    url: str
    admin_url: str