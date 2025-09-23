from typing import List, Optional
from fastapi import APIRouter, status, Query

from src.fabric_mapping.dto import (
    FabricMappingDTO,
    CreateFabricMappingDTO,
    UpdateFabricMappingDTO,
)
from src.fabric_mapping.depends.services import IFabricMappingService

from src.protection import RequireUserToken


router = APIRouter(prefix="/fabric-mappings",tags=["Fabric Mappings"], dependencies=[RequireUserToken])

@router.post(
    "/",
    response_model=FabricMappingDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Fabric Mapping",
    description="Creates a new fabric mapping record between a JV and XL fabric ID. Avoids creating exact duplicates.",
)
async def create_fabric_mapping(
    dto: CreateFabricMappingDTO,
    service: IFabricMappingService,
):
    """
    Creates a new fabric mapping entry.

    **Requires user privileges**

    - **dto**: Data containing the fabric IDs (JV and/or XL) to map.
    """
    return await service.create(dto)

@router.get(
    "/",
    response_model=List[FabricMappingDTO],
    summary="List Fabric Mappings",
    description="Retrieves a list of fabric mapping records with optional pagination.",
)
async def list_fabric_mappings(
    service: IFabricMappingService,
    limit: Optional[int] = Query(100, ge=1, le=10000, description="Maximum number of mappings to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of mappings to skip for pagination"),
):
    """
    Retrieves a list of all fabric mappings. Supports pagination via `limit` and `offset`.

    **Requires user privileges**

    """
    return await service.get_list(limit=limit, offset=offset)

@router.get(
    "/{pk}",
    response_model=FabricMappingDTO,
    summary="Get Fabric Mapping by ID",
    description="Retrieves the details of a specific fabric mapping record by its unique primary key.",
)
async def get_fabric_mapping(
    service: IFabricMappingService,
    pk: int,
):
    """
    Fetches a single fabric mapping by its primary key (`pk`).
    Raises 404 if not found (handled by global exception handler).

    **Requires user privileges**

    """
    return await service.get(pk)

@router.get(
    "/find-pairs/{fabric_id}",
    response_model=List[FabricMappingDTO],
    summary="Find Mapping Pairs by Fabric ID",
    description="Finds all mapping records where the given Fabric ID exists in either the JV or XL field.",
)
async def find_mapping_pairs(
    fabric_id: int,
    service: IFabricMappingService,
):
    """
    Searches for fabric mapping pairs associated with a specific `fabric_id`.
    Returns a list of matching mappings.

    **Requires user privileges**

    """
    return await service.find_pairs(fabric_id)

@router.patch(
    "/{pk}",
    response_model=FabricMappingDTO,
    summary="Update Fabric Mapping",
    description="Updates specific fields of an existing fabric mapping record identified by its primary key.",
)
async def update_fabric_mapping(
    pk: int,
    dto: UpdateFabricMappingDTO,
    service: IFabricMappingService,
):
    """
    Updates an existing fabric mapping record. Only fields provided in the request body (`dto`) are updated.
    Raises 404 if the mapping with the given `pk` is not found (handled by global exception handler).

    **Requires user privileges**

    """
    return await service.update(pk, dto)

@router.delete(
    "/{pk}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Fabric Mapping by ID",
    description="Deletes a specific fabric mapping record identified by its primary key.",
)
async def delete_fabric_mapping(
    pk: int,
    service: IFabricMappingService,
):
    """
    Deletes a fabric mapping record by its primary key (`pk`).
    Returns 204 No Content on successful deletion.

    **Requires user privileges**

    """
    await service.delete(pk)
    return None

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete All Fabric Mappings",
    description="**Caution:** Deletes all fabric mapping records from the database. Use with extreme care.",
)
async def delete_all_fabric_mappings(
    service: IFabricMappingService,
):
    """
    Deletes **ALL** fabric mapping records. This is a destructive operation.
    Ensure proper authorization/confirmation if exposing this widely.

    **Requires user privileges**

    """
    await service.delete_all()
    return None

