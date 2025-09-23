from fastapi import APIRouter, status, Query, Request
from typing import List, Optional

from src.product.dto import ProductDTO, UpdateProductDTO, FilterProductsDTO, FindProductDTO, ProductPreviewDTO
from src.product.depends.service import IProductService
from src.product.entity import ProductEntity

from src.protection import RequireUserToken

from src.libs.cache import cache


router = APIRouter(prefix="/products", tags=["Products"], dependencies=[RequireUserToken])


@router.post(
    "/",
    response_model=ProductDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Creates a new product with the provided details."
)
async def create_product(product_entity: ProductEntity, service: IProductService):
    """
    **Description**: Endpoint to create a new product.

    **Parameters**:
    - `product_entity`: *ProductEntity* - Data for the new product.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - *ProductDTO*: The created product data.

    **Raises**:
    - `HTTPException(409)`: If the product already exists.

    **Requires user privileges**

    """
    return await service.create(product_entity)


@router.get(
    "/{product_id}",
    response_model=ProductDTO,
    summary="Get product by ID",
    description="Retrieves details for a specific product by its ID.",
    responses={404: {"description": "Product not found"}}
)
async def get_product(product_id: int, service: IProductService):
    """
    **Description**: Endpoint to retrieve a product by its ID.

    **Parameters**:
    - `product_id`: *int* - Unique identifier of the product.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - *ProductDTO*: The product data.

    **Raises**:
    - `HTTPException(404)`: If the product is not found.
    """
    product = await service.get(product_id)
    return product


@router.get(
    "/",
    response_model=List[ProductPreviewDTO],
    summary="List all products",
    description="Retrieves a list of all products, optionally paginated."
)
@cache(hours=12)
async def list_products(
    request: Request,
    service: IProductService,
    limit: Optional[int] = Query(100, ge=1, le=10000, description="Maximum number of products to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of products to skip"),
):
    """
    **Description**: Endpoint to list all products with optional pagination.

    **Parameters**:
    - `limit`: *Optional[int]* - Maximum number of products to return.
    - `offset`: *Optional[int]* - Number of products to skip.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - *List[ProductDTO]*: List of product details.
    """
    return await service.get_list(limit=limit, offset=offset)


@router.post(
    "/filter",
    response_model=List[ProductPreviewDTO],
    summary="Filter products",
    description="Filters products based on the provided criteria, with optional pagination."
)
@cache(hours=12)
async def filter_products(
    request: Request,
    dto: FilterProductsDTO,
    service: IProductService,
    limit: Optional[int] = Query(100, ge=1, le=10000, description="Maximum number of products to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of products to skip"),
):
    """
    **Description**: Endpoint to filter products based on criteria.

    **Parameters**:
    - `dto`: *FilterProductsDTO* - Search criteria for filtering products.
    - `limit`: *Optional[int]* - Maximum number of products to return.
    - `offset`: *Optional[int]* - Number of products to skip.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - *List[ProductDTO]*: List of matching products.
    """
    return await service.filter(dto, limit=limit, offset=offset)


@router.post(
    "/find",
    response_model=Optional[ProductDTO],
    summary="Find a product",
    description="Finds a single product based on the provided criteria."
)
async def find_product(dto: FindProductDTO, service: IProductService):
    """
    **Description**: Endpoint to find a single product based on criteria.

    **Parameters**:
    - `dto`: *FindProductDTO* - Criteria for finding the product.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - *Optional[ProductDTO]*: The product data if found, otherwise None.
    """
    return await service.find(dto)


@router.patch(
    "/{product_id}",
    response_model=ProductDTO,
    summary="Update product details",
    description="Updates the details for a specific product.",
    responses={404: {"description": "Product not found"}}
)
async def update_product(product_id: int, dto: UpdateProductDTO, service: IProductService):
    """
    **Description**: Endpoint to update a product’s details.

    **Parameters**:
    - `product_id`: *int* - Unique identifier of the product.
    - `dto`: *UpdateProductDTO* - New details for the product.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - *ProductDTO*: The updated product data.

    **Raises**:
    - `HTTPException(404)`: If the product is not found.
    """
    return await service.update(dto, product_id)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="Deletes a product by its ID."
)
async def delete_product(product_id: int, service: IProductService):
    """
    **Description**: Endpoint to delete a product by its ID.

    **Parameters**:
    - `product_id`: *int* - Unique identifier of the product.
    - `service`: *IProductService* - Injected product service dependency.

    **Returns**:
    - None
    """
    await service.delete(product_id)