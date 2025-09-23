from typing import List, Optional
from fastapi import APIRouter, status, Query

from src.product_mapping.depends.services import IProductMappingService
from src.product_mapping.dto import (
    ProductsMappingDTO,
    CreateProductsMappingDTO,
    UpdateProductsMappingDTO,
    FindProductsMappingDTO
)

from src.protection import RequireUserToken


router = APIRouter(prefix="/product-mappings", tags=["Product Mappings"], dependencies=[RequireUserToken])


@router.post("/", response_model=ProductsMappingDTO, status_code=status.HTTP_201_CREATED)
async def create_product_mapping(
    dto: CreateProductsMappingDTO,
    product_mapping_service: IProductMappingService
):
    """
    **Description**: Creates a new product mapping.

    **Input**:
    - `dto`: *CreateProductsMappingDTO* - Product mapping data.
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.

    **Output**:
    - *ProductsMappingDTO* - Details of the created mapping.

    **Exceptions**:
    - `ProductMappingAlreadyExists`: If a mapping with the same unique constraints already exists (handled by exception_handler).

    **How It Works**:
    - Validates the input DTO.
    - Delegates to `ProductMappingService.create` to persist the mapping.
    - Returns the created mapping’s details.

    **Requires user privileges**

    **HTTP Status**: 201 Created
    """
    return await product_mapping_service.create(dto)

@router.get("/", response_model=List[ProductsMappingDTO])
async def get_product_mappings_list(
    product_mapping_service: IProductMappingService,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(0, ge=0),
):
    """
    **Description**: Retrieves a list of product mappings with optional pagination.

    **Input**:
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.
    - `limit`: *Optional[int]* - Maximum number of mappings to return (default: 100).
    - `offset`: *Optional[int]* - Starting index for the list (default: 0).

    **Output**:
    - *List[ProductsMappingDTO]* - List of mapping details.

    **Exceptions**:
    - `PaginationError`: If limit or offset is negative (handled by exception_handler).

    **How It Works**:
    - Fetches mappings via `ProductMappingService.get_list` with pagination.
    - Returns the list of mappings.

    **HTTP Status**: 200 OK
    """
    # Exceptions are handled by the global exception_handler
    return await product_mapping_service.get_list(limit=limit, offset=offset)

@router.get("/{mapping_id}", response_model=ProductsMappingDTO)
async def get_product_mapping_by_id(mapping_id: int, product_mapping_service: IProductMappingService):
    """
    **Description**: Retrieves a product mapping by its ID.

    **Input**:
    - `mapping_id`: *int* - Unique identifier of the mapping.
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.

    **Output**:
    - *ProductsMappingDTO* - Details of the mapping.

    **Exceptions**:
    - `ProductMappingNotFound`: If the mapping doesn’t exist (handled by exception_handler).

    **How It Works**:
    - Uses `ProductMappingService.get` to fetch the mapping by ID.
    - Returns the mapping’s details.

    **HTTP Status**: 200 OK
    """
    return await product_mapping_service.get(mapping_id)

@router.post("/find", response_model=ProductsMappingDTO)
async def find_product_mapping(
    find_dto: FindProductsMappingDTO,
    product_mapping_service: IProductMappingService
):
    """
    **Description**: Finds a single product mapping based on criteria (ID, fabric_mapping_id, jv_product_id, or xl_product_id).

    **Input**:
    - `find_dto`: *FindProductsMappingDTO* - Search criteria.
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.

    **Output**:
    - *ProductsMappingDTO* - Mapping details if found.

    **Exceptions**:
    - `ProductMappingNotFound`: If no mapping matches the criteria (handled by exception_handler).
    - `ProductMappingIsNotUnique`: If multiple mappings match the criteria (handled by exception_handler).

    **How It Works**:
    - Uses `ProductMappingService.find` to search for a unique mapping.
    - Returns the mapping if found and unique.

    **HTTP Status**: 200 OK
    """
    return await product_mapping_service.find(dto=find_dto)

@router.post("/filter", response_model=List[ProductsMappingDTO])
async def filter_product_mappings(
    product_mapping_service: IProductMappingService,
    filter_dto: FindProductsMappingDTO,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(None, ge=0),
):
    """
    **Description**: Filters product mappings based on criteria with optional pagination.

    **Input**:
    - `filter_dto`: *FindProductsMappingDTO* - Search criteria.
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.
    - `limit`: *Optional[int]* - Maximum number of mappings to return.
    - `offset`: *Optional[int]* - Starting index for the list.

    **Output**:
    - *List[ProductsMappingDTO]* - List of matching mappings.

    **Exceptions**:
    - `PaginationError`: If limit or offset is negative (handled by exception_handler).

    **How It Works**:
    - Uses `ProductMappingService.filter` to retrieve filtered mappings with pagination.
    - Returns the list of matching mappings.

    **HTTP Status**: 200 OK
    """
    return await product_mapping_service.filter(dto=filter_dto, limit=limit, offset=offset)


@router.put("/{mapping_id}", response_model=ProductsMappingDTO)
async def update_product_mapping(
    mapping_id: int,
    update_dto: UpdateProductsMappingDTO,
    product_mapping_service: IProductMappingService,
):
    """
    **Description**: Updates a product mapping’s details by its ID.

    **Input**:
    - `mapping_id`: *int* - Unique identifier of the mapping.
    - `update_dto`: *UpdateProductsMappingDTO* - New mapping data.
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.

    **Output**:
    - *ProductsMappingDTO* - Updated mapping details.

    **Exceptions**:
    - `ProductMappingNotFound`: If the mapping doesn’t exist (handled by exception_handler).
    - `ProductMappingAlreadyExists`: If the update violates unique constraints (handled by exception_handler).

    **How It Works**:
    - Validates the input DTO.
    - Delegates to `ProductMappingService.update` to modify the mapping.
    - Returns the updated mapping’s details.

    **HTTP Status**: 200 OK
    """
    return await product_mapping_service.update(pk=mapping_id, dto=update_dto)


@router.delete("/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_mapping(mapping_id: int, product_mapping_service: IProductMappingService):
    """
    **Description**: Deletes a product mapping by its ID.

    **Input**:
    - `mapping_id`: *int* - Unique identifier of the mapping.
    - `product_mapping_service`: *IProductMappingService* - Dependency-injected product mapping service.

    **Output**:
    - None (204 No Content).

    **Exceptions**:
    - `ProductMappingNotFound`: If the mapping doesn’t exist (handled by exception_handler).

    **How It Works**:
    - Delegates to `ProductMappingService.delete` to remove the mapping.
    - Returns no content upon success.

    **HTTP Status**: 204 No Content
    """
    await product_mapping_service.delete(pk=mapping_id)