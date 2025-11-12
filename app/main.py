from urllib import request

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from . import schemas, models, crud
from .database import SessionLocal, engine
from .config import get_settings


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def raise_not_found(request: Request):
    """
    Raise HTTP 404 Not Found exception with custom message.

    Args:
        message: Detailed error description for the client
    """
    message = f"URL '{request.url}' doesn't exist."
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message
    )


def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url

@app.get("/")
async def read_root() -> dict:
    """
    Root endpoint returning API welcome message.

    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to the URL shortener API :)",
        "version": "1.0",
        "status": "active"
    }

@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    db_url = crud.create_db_url(db=db, url=url)
    return get_admin_info(db_url=db_url)

@app.post("/custom_url", response_model=schemas.URLInfo)
def create_custom_url(
        custom_url: schemas.URLCustom,
        db: Session = Depends(get_db)
):
    try:
        db_custom_url = crud.create_custom_db_url(
            db=db,
            url=custom_url,
            custom_key=custom_url.custom_key
        )
        return get_admin_info(db_url=db_custom_url)
    except Exception as error:
        raise_bad_request(message=str(error))

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
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)

@app.get("/admin/{secret_key}",
         name="administration info",
         response_model=schemas.URLInfo)
def get_url_info(secret_key: str, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_secret_key(db=db, secret_key=secret_key):
        return get_admin_info(db_url=db_url)
    else:
        raise_not_found(request)

@app.delete("/admin/{secret_key}")
def delete_url(secret_key: str,
               request: Request,
               db: Session = Depends(get_db)
               ):
    if db_url := crud.deactivate_db_url_by_secret_key(db=db, secret_key=secret_key):
        message = f"Successfully deleted short URL for'{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)