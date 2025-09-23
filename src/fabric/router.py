from fastapi import APIRouter, Query
from typing import List, Optional
from src.fabric.depends.service import IFabricService, FabricService
from src.fabric.dto import FabricDTO, UpdateFabricDTO, FindFabricDTO
from src.fabric.entity import FabricEntity

from src.protection import RequireUserToken


router = APIRouter(prefix="/fabrics", tags=["Fabrics"], dependencies=[RequireUserToken])

@router.post("/", response_model=FabricDTO)
async def create_fabric(
    fabric_entity: FabricEntity,
    service: IFabricService
):
    """
    **Description**: Creates a new fabric in the system.

    **Parameters**:
    - `fabric_entity`: *FabricEntity* - Data for the new fabric (name, afterbuy_id, etc.).
    - `service`: *IFabricService* - Dependency-injected fabric service.

    **Returns**:
    - *FabricDTO*: Details of the newly created fabric.

    **Raises**:
    - `AlreadyExistError`: If a fabric with the same `afterbuy_id` already exists.

    **Requires user privileges**

    **Usage**: Endpoint to add a new fabric via POST request.
    """
    service: FabricService
    return await service.create(fabric_entity)

@router.get("/", response_model=List[FabricDTO])
async def get_fabrics(
    service: IFabricService,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(None, ge=0),
):
    """
    **Description**: Retrieves a paginated list of fabrics.

    **Parameters**:
    - `service`: *IFabricService* - Dependency-injected fabric service.
    - `limit`: *Optional[int]* - Maximum number of fabrics to return (default: 100).
    - `offset`: *Optional[int]* - Starting index for pagination (optional).

    **Returns**:
    - *List[FabricDTO]*: List of fabric details.

    **Raises**:
    - `PaginationError`: If `limit` or `offset` is negative.

    **Requires user privileges**

    **Usage**: Endpoint to fetch all fabrics with optional pagination.
    """
    service: FabricService
    return await service.get_list(limit, offset)

@router.get("/{pk}", response_model=FabricDTO)
async def get_fabric(
    pk: int,
    service: IFabricService
):
    """
    **Description**: Retrieves a single fabric by its ID.

    **Parameters**:
    - `pk`: *int* - Unique identifier of the fabric.
    - `service`: *IFabricService* - Dependency-injected fabric service.

    **Returns**:
    - *FabricDTO*: Details of the requested fabric.

    **Raises**:
    - `FabricNotFound`: If no fabric exists with the given ID.

    **Requires user privileges**

    **Usage**: Endpoint to fetch a specific fabric by its ID.
    """
    service: FabricService
    return await service.get(pk)

@router.post("/find", response_model=FabricDTO)
async def find_fabric(
    dto: FindFabricDTO,
    service: IFabricService
):
    """
    **Description**: Finds a single fabric based on provided criteria.

    **Parameters**:
    - `dto`: *FindFabricDTO* - Search criteria (e.g., ID, name, etc.).
    - `service`: *IFabricService* - Dependency-injected fabric service.

    **Returns**:
    - *FabricDTO*: Details of the found fabric.

    **Raises**:
    - `FabricNotFound`: If no fabric matches the criteria.
    - `FabricIsNotUnique`: If multiple fabrics match the criteria.

    **Requires user privileges**

    **Usage**: Endpoint to locate a unique fabric based on search parameters.
    """
    service: FabricService
    return await service.find(dto)

@router.post("/filter", response_model=List[FabricDTO])
async def filter_fabrics(
    service: IFabricService,
    dto: FindFabricDTO,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(None, ge=0),
):
    """
    **Description**: Filters fabrics based on criteria with optional pagination.

    **Parameters**:
    - `service`: *IFabricService* - Dependency-injected fabric service.
    - `dto`: *FindFabricDTO* - Search criteria (e.g., name, brand_id).
    - `limit`: *Optional[int]* - Maximum number of fabrics to return (default: 100).
    - `offset`: *Optional[int]* - Starting index for pagination (optional).

    **Returns**:
    - *List[FabricDTO]*: List of matching fabrics.

    **Raises**:
    - `PaginationError`: If `limit` or `offset` is negative.

    **Requires user privileges**

    **Usage**: Endpoint to retrieve a filtered list of fabrics.
    """
    service: FabricService
    return await service.filter(dto, limit, offset)

@router.put("/{pk}", response_model=FabricDTO)
async def update_fabric(
    pk: int,
    dto: UpdateFabricDTO,
    service: IFabricService
):
    """
    **Description**: Updates the details of an existing fabric by its ID.

    **Parameters**:
    - `pk`: *int* - Unique identifier of the fabric.
    - `dto`: *UpdateFabricDTO* - New details for the fabric.
    - `service`: *IFabricService* - Dependency-injected fabric service.

    **Returns**:
    - *FabricDTO*: Updated fabric details.

    **Raises**:
    - `FabricNotFound`: If no fabric exists with the given ID.

    **Requires user privileges**

    **Usage**: Endpoint to modify an existing fabric via PUT request.
    """
    service: FabricService
    return await service.update(dto, pk)

@router.delete("/{pk}", status_code=204)
async def delete_fabric(
    pk: int,
    service: IFabricService
):
    """
    **Description**: Deletes a fabric by its ID.

    **Parameters**:
    - `pk`: *int* - Unique identifier of the fabric.
    - `service`: *IFabricService* - Dependency-injected fabric service.

    **Returns**:
    - None: Returns HTTP 204 No Content on success.

    **Raises**:
    - `FabricNotFound`: If no fabric exists with the given ID.

    **Requires user privileges**

    **Usage**: Endpoint to remove a fabric from the system.
    """
    service: FabricService
    await service.delete(pk)