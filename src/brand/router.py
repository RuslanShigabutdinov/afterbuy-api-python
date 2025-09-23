from typing import List, Optional
from fastapi import APIRouter, status, Query

from src.brand.depends.service import IBrandService
from src.brand.dto import BrandDTO, UpdateBrandDTO, FindBrandDTO
from src.brand.entity import BrandEntity

from src.protection import RequireUserToken

router = APIRouter(prefix="/brands", tags=["Brands"], dependencies=[RequireUserToken])

@router.post("/", response_model=BrandDTO, status_code=status.HTTP_201_CREATED)
async def create_brand(entity: BrandEntity, brand_service: IBrandService):
    """
    **Description**: Creates a new brand.

    **Input**:
    - `entity`: *BrandEntity* - Brand data (name).
    - `brand_service`: *IBrandService* - Dependency-injected brand service.

    **Output**:
    - *BrandDTO* - Details of the created brand (id, name).

    **Exceptions**:
    - `AlreadyExistError`: If a brand with the same name already exists.

    **How It Works**:
    - Validates the input entity.
    - Delegates to `BrandService.create` to persist the brand.
    - Returns the created brand’s details.

    **Requires user privileges**

    **HTTP Status**: 201 Created
    """
    return await brand_service.create(entity)

@router.get("/", response_model=List[BrandDTO])
async def get_brands_list(
    brand_service: IBrandService,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(0, ge=0),
):
    """
    **Description**: Retrieves a list of brands with optional pagination.

    **Input**:
    - `brand_service`: *IBrandService* - Dependency-injected brand service.
    - `limit`: *Optional[int]* - Maximum number of brands to return (default: 100).
    - `offset`: *Optional[int]* - Starting index for the list (default: 0).

    **Output**:
    - *List[BrandDTO]* - List of brand details.

    **Exceptions**:
    - `PaginationError`: If limit or offset is negative.

    **How It Works**:
    - Fetches brands via `BrandService.get_list` with pagination.
    - Returns the list of brands.

    **Requires user privileges**

    **HTTP Status**: 200 OK
    """
    return await brand_service.get_list(limit=limit, offset=offset)

@router.get("/{brand_id}", response_model=BrandDTO)
async def get_brand_by_id(brand_id: int, brand_service: IBrandService):
    """
    **Description**: Retrieves a brand by its ID.

    **Input**:
    - `brand_id`: *int* - Unique identifier of the brand.
    - `brand_service`: *IBrandService* - Dependency-injected brand service.

    **Output**:
    - *BrandDTO* - Details of the brand.

    **Exceptions**:
    - `BrandNotFound`: If the brand doesn’t exist.

    **How It Works**:
    - Uses `BrandService.get` to fetch the brand by ID.
    - Returns the brand’s details.

    **Requires user privileges**

    **HTTP Status**: 200 OK
    """
    return await brand_service.get(brand_id)

@router.put("/{brand_id}", response_model=BrandDTO)
async def update_brand(
    brand_id: int,
    update_dto: UpdateBrandDTO,
    brand_service: IBrandService,
):
    """
    **Description**: Updates a brand’s name by its ID.

    **Input**:
    - `brand_id`: *int* - Unique identifier of the brand.
    - `update_dto`: *UpdateBrandDTO* - New brand name.
    - `brand_service`: *IBrandService* - Dependency-injected brand service.

    **Output**:
    - *BrandDTO* - Updated brand details.

    **Exceptions**:
    - `BrandNotFound`: If the brand doesn’t exist.
    - `AlreadyExistError`: If the new name is already taken.

    **How It Works**:
    - Validates the input DTO.
    - Delegates to `BrandService.update` to modify the brand.
    - Returns the updated brand’s details.

    **Requires user privileges**

    **HTTP Status**: 200 OK
    """
    return await brand_service.update(dto=update_dto, pk=brand_id)

@router.post("/find", response_model=Optional[BrandDTO])
async def find_brand(find_dto: FindBrandDTO, brand_service: IBrandService):
    """
    **Description**: Finds a single brand based on criteria (ID or name).

    **Input**:
    - `find_dto`: *FindBrandDTO* - Search criteria (ID or name).
    - `brand_service`: *IBrandService* - Dependency-injected brand service.

    **Output**:
    - *Optional[BrandDTO]* - Brand details if found, else None.

    **Exceptions**:
    - `BrandNotFound`: If no brand matches the criteria.
    - `BrandIsNotUnique`: If multiple brands match the criteria.

    **How It Works**:
    - Uses `BrandService.find` to search for a unique brand.
    - Returns the brand if found and unique.

    **Requires user privileges**

    **HTTP Status**: 200 OK
    """
    return await brand_service.find(dto=find_dto)

@router.post("/filter", response_model=List[BrandDTO])
async def filter_brands(
    filter_dto: FindBrandDTO,
    brand_service: IBrandService,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(None, ge=0),
):
    """
    **Description**: Filters brands based on criteria with optional pagination.

    **Input**:
    - `filter_dto`: *FindBrandDTO* - Search criteria (ID or name).
    - `brand_service`: *IBrandService* - Dependency-injected brand service.
    - `limit`: *Optional[int]* - Maximum number of brands to return.
    - `offset`: *Optional[int]* - Starting index for the list.

    **Output**:
    - *List[BrandDTO]* - List of matching brands.

    **Exceptions**:
    - `PaginationError`: If limit or offset is negative.

    **How It Works**:
    - Uses `BrandService.filter` to retrieve filtered brands with pagination.
    - Returns the list of matching brands.

    **Requires user privileges**

    **HTTP Status**: 200 OK
    """
    return await brand_service.filter(dto=filter_dto, limit=limit, offset=offset)

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: int, brand_service: IBrandService):
    """
    **Description**: Deletes a brand by its ID.

    **Input**:
    - `brand_id`: *int* - Unique identifier of the brand.
    - `brand_service`: *IBrandService* - Dependency-injected brand service.

    **Output**:
    - None (204 No Content).

    **Exceptions**:
    - `BrandNotFound`: If the brand doesn’t exist (handled by service).

    **How It Works**:
    - Delegates to `BrandService.delete` to remove the brand.
    - Returns no content upon success.

    **Requires user privileges**

    **HTTP Status**: 204 No Content
    """
    await brand_service.delete(pk=brand_id)