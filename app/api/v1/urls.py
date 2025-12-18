from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL as StarletteURL

from app import schemas, crud
from ...dependencies.database import get_db
from app.models.urls import URL as URLModel
from ...utils.keygen import create_random_key
from ...core.config import get_settings


router = APIRouter(
    tags=["URL Shortener"],
    responses={404: {"description": "URL not found"}}
)


def raise_bad_request(message: str) -> None:
    """
    Provides a standardized way to return bad request errors
    to clients with detailed error messages explaining what went wrong.

    Args:
        message (str): Detailed error description for the client

    Raises:
        HTTPException: HTTP 400 Bad Request with the provided message
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


def raise_not_found(request: Request) -> None:
    """
    Generates a standardized 404 response when requested
    resources (URLs, admin endpoints) cannot be found in the system.

    Args:
        request (Request): The incoming request object to extract URL from

    Raises:
        HTTPException: HTTP 404 Not Found with a descriptive message
    """
    message = f"URL '{request.url}' doesn't exist."
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message
    )


def get_admin_info(db_url: URLModel) -> schemas.URLInfo:
    """
    Takes a database URL model and adds fully-formed URLs
    for both the shortened URL and the admin endpoint, making them
    immediately usable by clients without reconstruction.

    Args:
        db_url (URLModel): Database URL model retrieved from storage

    Returns:
        schemas.URLInfo: Enhanced URL info schema with complete URLs
    """
    base_url = StarletteURL(get_settings().base_url)
    db_url.url = str(base_url.replace(path=f"/{db_url.key}"))
    admin_path = f"/admin/{db_url.secret_key}"
    db_url.admin_url = str(base_url.replace(path=admin_path))
    return db_url


@router.get("/",
            summary="Get API Information",
            description="Returns basic information about the URL shortener API.")
async def read_root() -> dict:
    """
    Root endpoint returning API welcome message and status.

    Returns:
        dict: Dictionary containing API metadata including message, version, and status
    """
    return {
        "message": "Welcome to the URL shortener API :)",
        "version": "1.0",
        "status": "active"
    }


@router.post("/url",
             summary="Create Shortened URL",
             description="Creates a new shortened URL from a target URL.",
             response_description="Created shortened URL with admin access info")
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)) -> schemas.URLInfo:
    """
    Create a new shortened URL from the provided target URL.

    Args:
        url (schemas.URLBase): Request containing the target URL to be shortened
        db (Session): Database session dependency for database operations

    Returns:
        schemas.URLInfo: Response containing the created short URL and admin link

    Raises:
        HTTPException: If there are issues with URL validation or database operations
    """
    db_url = crud.create_db_url(db=db, url=url)
    return get_admin_info(db_url=db_url)


@router.post("/custom_url",
             summary="Create Custom Shortened URL",
             description="Creates a new shortened URL with a user-defined custom key.",
             response_description="Created custom shortened URL with admin access info")
def create_custom_url(
        custom_url: schemas.URLCustom,
        db: Session = Depends(get_db)
) -> schemas.URLInfo:
    """
    Create a new shortened URL with a custom key specified by the user.

    Args:
        custom_url (schemas.URLCustom): Request containing target URL and custom key
        db (Session): Database session dependency for database operations

    Returns:
        schemas.URLInfo: Response containing the created short URL and admin link

    Raises:
        HTTPException: 400 Bad Request if the custom key already exists
    """
    try:
        db_custom_url = crud.create_custom_db_url(
            db=db,
            url=custom_url,
            custom_key=custom_url.custom_key
        )
        return get_admin_info(db_url=db_custom_url)
    except Exception as error:
        raise_bad_request(message=str(error))


@router.get("/{url_key}",
            summary="Redirect Shortened URL",
            description="Redirects a short URL key to its original target URL and increments click count.")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)
) -> RedirectResponse:
    """
    Redirects a short URL key to its original target URL.

    Args:
        url_key (str): The short key part of the URL to be resolved
        request (Request): The incoming request object for error reporting
        db (Session): Database session dependency for database operations

    Returns:
        RedirectResponse: HTTP redirect to the target URL

    Raises:
        HTTPException: 404 Not Found if the short key doesn't exist
    """
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@router.get("/admin/{secret_key}",
         name="administration info",
         summary="Get URL Admin Info",
         description="Retrieves administrative information about a shortened URL.",
         response_description="Complete URL information with admin access details")
def get_url_info(secret_key: str, db: Session = Depends(get_db)) -> schemas.URLInfo:
    """
    Retrieve administrative information about a shortened URL.

    Args:
        secret_key (str): Secret key for accessing admin information
        db (Session): Database session dependency for database operations

    Returns:
        schemas.URLInfo: Detailed information about the short URL including analytics

    Raises:
        HTTPException: 404 Not Found if the secret key doesn't exist
    """
    if db_url := crud.get_db_url_by_secret_key(db=db, secret_key=secret_key):
        return get_admin_info(db_url=db_url)
    else:
        raise_not_found(request)


@router.delete("/admin/{secret_key}",
               summary="Delete URL",
               description="Deactivates and removes a shortened URL from the system.")
def delete_url(secret_key: str,
               request: Request,
               db: Session = Depends(get_db)
               ) -> dict:
    """
    Delete (deactivate) a shortened URL from the system.

    Args:
        secret_key (str): Secret key for identifying the URL to delete
        request (Request): The incoming request object for error reporting
        db (Session): Database session dependency for database operations

    Returns:
        dict: Success message confirming the deletion

    Raises:
        HTTPException: 404 Not Found if the secret key doesn't exist
    """
    if db_url := crud.deactivate_db_url_by_secret_key(db=db, secret_key=secret_key):
        message = f"Successfully deleted short URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)