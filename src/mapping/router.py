from fastapi import APIRouter
from typing import Dict

from src.mapping.depends.service import IMappingService

from src.protection import RequireAdminToken

router = APIRouter(prefix="/mapping", tags=["Mapping"], dependencies=[RequireAdminToken])



@router.post(
    "/mappings",
    summary="Map everything, Fabrics and Products (Deletes previous mappings!)"
)
async def create_mapping(service: IMappingService):
    """

    **Requires admin privileges**

    """
    return await service.map_all()


@router.post(
    "/map_products"
)
async def map_product(service: IMappingService):
    """

    **Requires admin privileges**

    """

    return await service.map_products()

