from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL as StarletteURL

from app.schemas.schemas import URLBase, URLCustom, URLInfo
from app.application import UrlService
from app.infrastructure.repositories.sqlalchemy_url_repository import SqlAlchemyUrlRepository
from app.core.config import get_settings
from app.dependencies.database import get_db


router = APIRouter(
    tags=["URL Shortener"],
    responses={404: {"description": "URL not found"}}
)


def get_url_service(db: Session = Depends(get_db)) -> UrlService:
    repository = SqlAlchemyUrlRepository(db_session=db)
    return UrlService(url_repository=repository)


def raise_bad_request(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


def raise_not_found(request: Request) -> None:
    message = f"URL '{request.url}' doesn't exist."
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message
    )


def get_admin_info(url_entity) -> URLInfo:
    base_url = StarletteURL(get_settings().base_url)
    url = str(base_url.replace(path=f"/{url_entity.key}"))
    admin_path = f"/admin/{url_entity.secret_key}"
    admin_url = str(base_url.replace(path=admin_path))

    return URLInfo(
        target_url=url_entity.target_url,
        is_active=url_entity.is_active,
        clicks=url_entity.clicks,
        key=url_entity.key,
        secret_key=url_entity.secret_key,
        url=url,
        admin_url=admin_url
    )


@router.get("/",
            summary="Get API Information",
            description="Returns basic information about the URL shortener API.")
async def read_root() -> dict:
    return {
        "message": "Welcome to the URL shortener API :)",
        "version": "1.0",
        "status": "active"
    }


@router.post("/url",
             summary="Create Shortened URL",
             description="Creates a new shortened URL from a target URL.",
             response_description="Created shortened URL with admin access info")
def create_url(url: URLBase, url_service: UrlService = Depends(get_url_service)) -> URLInfo:
    target_url_str = str(url.target_url)
    url_entity = url_service.create_short_url(target_url=target_url_str)
    return get_admin_info(url_entity)


@router.post("/custom_url",
             summary="Create Custom Shortened URL",
             description="Creates a new shortened URL with a user-defined custom key.",
             response_description="Created custom shortened URL with admin access info")
def create_custom_url(
        custom_url: URLCustom,
        url_service: UrlService = Depends(get_url_service)
) -> URLInfo:
    try:
        target_url_str = str(custom_url.target_url)
        url_entity = url_service.create_custom_short_url(
            target_url=target_url_str,
            custom_key=custom_url.custom_key
        )
        return get_admin_info(url_entity)
    except Exception as error:
        raise_bad_request(message=str(error))


@router.get("/{url_key}",
            summary="Redirect Shortened URL",
            description="Redirects a short URL key to its original target URL and increments click count.")
def forward_to_target_url(
        url_key: str,
        request: Request,
        url_service: UrlService = Depends(get_url_service)
) -> RedirectResponse:
    url_entity = url_service.get_url_by_key(url_key)
    if url_entity:
        url_service.increment_click_count(url_entity)
        return RedirectResponse(url_entity.target_url)
    else:
        raise_not_found(request)


@router.get("/admin/{secret_key}",
         name="administration info",
         summary="Get URL Admin Info",
         description="Retrieves administrative information about a shortened URL.",
         response_description="Complete URL information with admin access details")
def get_url_info(
        secret_key: str,
        request: Request,
        url_service: UrlService = Depends(get_url_service)
) -> URLInfo:
    url_entity = url_service.get_url_by_secret_key(secret_key)
    if not url_entity:
        raise_not_found(request)
    admin_info = get_admin_info(url_entity)
    admin_info_dict = admin_info.model_dump()
    admin_info_dict['secret_key'] = "***PROTECTED***"
    return URLInfo(**admin_info_dict)


@router.delete("/admin/{secret_key}",
               summary="Delete URL",
               description="Deactivates a shortened URL.")
def delete_url(
        secret_key: str,
        request: Request,
        url_service: UrlService = Depends(get_url_service)
) -> dict:
    url_entity = url_service.delete_url_by_secret_key(secret_key)
    if url_entity:
        message = f"Successfully deactivated short URL for '{url_entity.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)