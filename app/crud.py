from sqlalchemy.orm import Session
from . import keygen, models, schemas


def create_db_url(db: Session, url: schemas.URLBase) -> models.URL :
    key = keygen.create_random_key()
    secret_key = f"{key}_{keygen.create_random_key(length=8)}"
    db_url = models.URL(
        target_url=str(url.target_url),
        key=key,
        secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def create_custom_db_url(db: Session, url: schemas.URLBase, custom_key: str) -> models.URL:
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
        db.query(models.URL)
        .filter(models.URL.key == custom_key)
        .first()
    )
    if not custom_url_in_db:
        secret_key = f"{custom_key}_{keygen.create_random_key(length=8)}"
        db_custom_url = models.URL(
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


def get_db_url_by_key(db: Session, url_key: str) -> models.URL :
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )


def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL :
    return (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active)
        .first()
    )


def update_db_clicks(db: Session, db_url: schemas.URL) -> models.URL :
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def deactivate_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL :
    db_url = get_db_url_by_secret_key(db=db, secret_key=secret_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url