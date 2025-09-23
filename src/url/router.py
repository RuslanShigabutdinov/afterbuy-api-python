from fastapi import APIRouter, status, Query
from typing import List, Optional

from src.url.dto import UrlDTO, UpdateUrlDTO, FilterUrlsDTO
from src.url.depends.service import IUrlService
from src.url.entity import UrlEntity

from src.protection import RequireUserToken


router = APIRouter(prefix="/urls", tags=["URLs"], dependencies=[RequireUserToken])

@router.post(
    "/",
    response_model=UrlDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new URL",
    description="Creates a new URL with the provided details."
)
async def create_url(url_entity: UrlEntity, service: IUrlService):
    """

    **Requires user privileges**

    """
    return await service.create(url_entity)

@router.get(
    "/{url_id}",
    response_model=UrlDTO,
    summary="Get URL by ID",
    description="Retrieves details for a specific URL by its ID.",
    responses={404: {"description": "URL not found"}}
)
async def get_url(url_id: int, service: IUrlService):
    """

    **Requires user privileges**

    """
    return await service.get(url_id)

@router.get(
    "/",
    response_model=List[UrlDTO],
    summary="List all URLs",
    description="Retrieves a list of all URLs, optionally paginated."
)
async def list_urls(
    service: IUrlService,
    limit: Optional[int] = Query(100, ge=1, le=10000, description="Maximum number of URLS to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of URLs to skip"),
):
    """

    **Requires user privileges**

    """
    return await service.get_list(limit=limit, offset=offset)

@router.post(
    "/filter",
    response_model=List[UrlDTO],
    summary="Filter URLs",
    description="Filters URLs based on the provided criteria, with optional pagination."
)
async def filter_urls(
    service: IUrlService,
    dto: FilterUrlsDTO,
    limit: Optional[int] = Query(100, ge=1, le=10000, description="Maximum number of URLs to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of URLs to skip"),
):
    """

    **Requires user privileges**

    """
    return await service.filter(dto, limit=limit, offset=offset)

@router.patch(
    "/{url_id}",
    response_model=UrlDTO,
    summary="Update URL details",
    description="Updates the details for a specific URL.",
    responses={404: {"description": "URL not found"}}
)
async def update_url(
    url_id: int,
    dto: UpdateUrlDTO,
    service: IUrlService
):
    """

    **Requires user privileges**

    """
    return await service.update(dto, url_id)

@router.delete(
    "/{url_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a URL",
    description="Deletes a URL by its ID."
)
async def delete_url(url_id: int, service: IUrlService):
    """

    **Requires user privileges**

    """
    await service.delete(url_id)