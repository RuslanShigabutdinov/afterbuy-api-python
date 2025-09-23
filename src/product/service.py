import pandas as pd

from io import BytesIO
from typing import List, Optional

from src.product.depends.repository import IProductsRepository, ProductsRepository
from src.product.dto import ProductDTO, UpdateProductDTO, FilterProductsDTO, FindProductDTO, ProductPreviewDTO
from src.product.entity import ProductEntity

from src.libs.exceptions import PaginationError


class ProductService:
    """
    **Description**: Service layer for managing product-related business logic.

    **Attributes**:
    - `repository`: *IProductsRepository* - Injected repository for database operations.

    **Methods**:
    - `create`: Creates a new product.
    - `get_list`: Retrieves a list of products with optional pagination.
    - `get`: Retrieves a product by ID.
    - `filter`: Filters products by criteria with optional pagination.
    - `find`: Finds a single product by criteria.
    - `update`: Updates a product’s details.
    - `delete`: Deletes a product by ID.

    **Usage**: Acts as an intermediary between the API router and repository layers for product management.
    """
    def __init__(self, repository: IProductsRepository):
        """
        **Description**: Initializes the ProductService with a repository instance.

        **Parameters**:
        - `repository`: *IProductsRepository* - Repository for product data access.
        """
        self.repository: ProductsRepository = repository

    async def create(self, product: ProductEntity) -> ProductDTO:
        """
        **Description**: Creates a new product in the system.

        **Parameters**:
        - `product`: *ProductEntity* - Data for the new product.

        **Returns**:
        - *ProductDTO*: The created product data.

        **Raises**:
        - `AlreadyExistError`: If the product already exists (e.g., duplicate product_num).

        **Usage**: Persists a new product via the repository.
        """
        return await self.repository.create(product)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductPreviewDTO]:
        """
        **Description**: Retrieves a list of all products with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of products to return.
        - `offset`: *Optional[int]* - Number of products to skip for pagination.

        **Returns**:
        - *List[ProductDTO]*: List of product details.

        **Raises**:
        - `PaginationError`: If limit or offset is negative.

        **Usage**: Fetches a paginated list of products from the repository.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError(f"Limit({limit}) or offset({offset}) is invalid (must be positive)")
        return await self.repository.get_list(limit, offset)

    async def get(self, pk: int) -> Optional[ProductDTO]:
        """
        **Description**: Retrieves a product by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the product.

        **Returns**:
        - *Optional[ProductDTO]*: The product data if found, otherwise None.

        **Usage**: Fetches a specific product from the repository.
        """
        return await self.repository.get(pk)

    async def filter(self, dto: FilterProductsDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductPreviewDTO]:
        """
        **Description**: Filters products based on criteria with optional pagination.

        **Parameters**:
        - `dto`: *FilterProductsDTO* - Search criteria for filtering products.
        - `limit`: *Optional[int]* - Maximum number of products to return.
        - `offset`: *Optional[int]* - Number of products to skip for pagination.

        **Returns**:
        - *List[ProductDTO]*: List of matching products.

        **Raises**:
        - `PaginationError`: If limit or offset is negative.

        **Usage**: Retrieves a filtered list of products from the repository.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError(f"Limit({limit}) or offset({offset}) is invalid (must be positive)")

        return await self.repository.filter(dto, limit, offset)

    async def find(self, dto: FindProductDTO) -> Optional[ProductDTO]:
        """
        **Description**: Finds a single product based on specified criteria.

        **Parameters**:
        - `dto`: *FindProductDTO* - Criteria for finding the product.

        **Returns**:
        - *Optional[ProductDTO]*: The product data if found, otherwise None.

        **Usage**: Locates a unique product via the repository.
        """
        return await self.repository.find(dto)

    async def update(self, dto: UpdateProductDTO, pk: int) -> ProductDTO:
        """
        **Description**: Updates an existing product by its ID.

        **Parameters**:
        - `dto`: *UpdateProductDTO* - New details for the product.
        - `pk`: *int* - Unique identifier of the product.

        **Returns**:
        - *ProductDTO*: The updated product data.

        **Raises**:
        - `NoResultFound`: If no product with the given ID is found.

        **Usage**: Modifies a product’s details via the repository.
        """
        return await self.repository.update(dto, pk)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a product by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the product.

        **Returns**:
        - None

        **Usage**: Removes a product from the system via the repository.
        """
        await self.repository.delete(pk)

