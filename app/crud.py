from sqlalchemy.orm import Session
from .utils import keygen
from app import schemas
from app.models import URL


def get_db_url_by_key(db: Session, url_key: str) -> URL:
    return (
        db.query(URL)
        .filter(URL.key == url_key, URL.is_active)
        .first()
    )


def get_db_url_by_secret_key(db: Session, secret_key: str) -> URL:
    return (
        db.query(URL)
        .filter(URL.secret_key == secret_key, URL.is_active)
        .first()
    )


def create_unique_random_key(db: Session) -> str:
    """
    Creates a unique key for short url and returns it.

    Args:
        db: Database session

    Returns:
        Unique key
    """
    from .utils.keygen import create_random_key
    key = create_random_key()
    while get_db_url_by_key(db, key):
        key = create_random_key()
    return key


def create_db_url(db: Session, url: schemas.URLBase) -> URL:
    key = create_unique_random_key(db)
    secret_key = f"{key}_{keygen.create_random_key(length=8)}"
    db_url = URL(
        target_url=str(url.target_url),
        key=key,
        secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def create_custom_db_url(db: Session, url: schemas.URLBase, custom_key: str) -> URL:
    """
    Create custom URL with key

    Args:
        db: Database session
        url: URLBase object with target_url
        custom_key: Custom key for short url

    Returns:
        Created URL record
    """
    custom_url_in_db = (
        db.query(URL)
        .filter(URL.key == custom_key)
        .first()
    )
    if not custom_url_in_db:
        secret_key = f"{custom_key}_{keygen.create_random_key(length=8)}"
        db_custom_url = URL(
            target_url=str(url.target_url),
            key=custom_key,
            secret_key=secret_key
        )
        db.add(db_custom_url)
        db.commit()
        db.refresh(db_custom_url)
        return db_custom_url
    else:
        raise Exception(f"Key {custom_key} already exists")


def update_db_clicks(db: Session, db_url: URL) -> URL:
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def deactivate_db_url_by_secret_key(db: Session, secret_key: str) -> URL:
    db_url = get_db_url_by_secret_key(db=db, secret_key=secret_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url