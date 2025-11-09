from fastapi import FastAPI, HTTPException, status
from . import schemas
import validators

app = FastAPI()

def raise_bad_request(message: str) -> None:
    """
    Raise HTTP 400 Bad Request exception with custom message.

    Args:
        message: Detailed error description for the client
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )

@app.get("/")
async def read_root() -> dict:
    """
    Root endpoint returning API welcome message.

    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to the URL shortener API :)",
        "version": "0.1",
        "status": "active"
    }

@app.post("/url")
def create_short_url(url: schemas.URLBase) -> str:
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")
    return f"TODO: Create database entry for {url.target_url}"