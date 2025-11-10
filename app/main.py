import secrets

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import validators

from . import schemas, models
from .database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def raise_not_found(request: Request):
    message = f"URL '{request.url}' doesn't exist."
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


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

@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = "".join(secrets.choice(chars) for _ in range(5))
    secret_key = "".join(secrets.choice(chars) for _ in range(8))

    db_url = models.URL(
        target_url=url.target_url,
        key=key,
        secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db_url.url = key
    db_url.admin_url = secret_key

    return db_url

@app.get("/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)
):
    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )
    if db_url:
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)