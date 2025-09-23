from typing import List, Optional

from src.product_mapping.depends.repositories import IProductMappingRepository
from src.product_mapping.dto import (
    CreateProductsMappingDTO,
    UpdateProductsMappingDTO,
    ProductsMappingDTO,
    FindProductsMappingDTO
)
from src.libs.exceptions import PaginationError

class ProductMappingService:
    """
    **Description**: Service class for product mapping operations.

    **Dependencies**:
    - `repository`: *IProductMappingRepository* - Handles database interactions.

    **Methods**:
    - `get`: Retrieves a product mapping by ID.
    - `get_list`: Retrieves a list of product mappings with optional pagination.
    - `create`: Creates a new product mapping.
    - `update`: Updates an existing product mapping.
    - `find`: Finds a single product mapping based on criteria.
    - `filter`: Filters product mappings based on criteria with pagination.
    - `delete`: Deletes a product mapping by ID.

    **Usage**: Acts as an intermediary between the API layer and the repository.
    """
    def __init__(self, product_mapping_repo: IProductMappingRepository):
        self.product_mapping_repo = product_mapping_repo

    async def create(self, dto: CreateProductsMappingDTO) -> ProductsMappingDTO:
        """
        **Description**: Creates a new product mapping.

        **Input**:
        - `dto`: *CreateProductsMappingDTO* - Product mapping data.

        **Output**:
        - *ProductsMappingDTO* - Details of the created mapping.

        **Exceptions**:
        - `ProductMappingAlreadyExists`: If a mapping with the same unique constraints already exists (handled by repository).

        **How It Works**:
        - Delegates to `repository.create` to persist the mapping.
        """
        return await self.product_mapping_repo.create(dto)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductsMappingDTO]:
        """
        **Description**: Retrieves a list of product mappings with optional pagination.

        **Input**:
        - `limit`: *Optional[int]* - Maximum number of mappings to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[ProductsMappingDTO]* - List of mapping details.

        **Exceptions**:
        - `PaginationError`: If limit or offset is negative.

        **How It Works**:
        - Validates pagination parameters.
        - Delegates to `repository.get_list` to fetch the list.
        """
        if (limit is not None and limit < 0) or (offset is not None and offset < 0):
            raise PaginationError("limit and offset must be non-negative")
        return await self.product_mapping_repo.get_list(limit, offset)

    async def get(self, pk: int) -> ProductsMappingDTO:
        """
        **Description**: Retrieves a product mapping by its ID.

        **Input**:
        - `pk`: *int* - Mapping ID.

        **Output**:
        - *ProductsMappingDTO* - Mapping details.

        **Exceptions**:
        - `ProductMappingNotFound`: If the mapping doesn’t exist (handled by repository).

        **How It Works**:
        - Delegates to `repository.get` to fetch the mapping.
        """
        return await self.product_mapping_repo.get(pk)

    async def find(self, dto: FindProductsMappingDTO) -> ProductsMappingDTO:
        """
        **Description**: Finds a single product mapping based on criteria.

        **Input**:
        - `dto`: *FindProductsMappingDTO* - Search criteria.

        **Output**:
        - *ProductsMappingDTO* - Mapping details if found and unique.

        **Exceptions**:
        - `ProductMappingNotFound`: If no mapping matches (handled by repository).
        - `ProductMappingIsNotUnique`: If multiple mappings match (handled by repository).

        **How It Works**:
        - Delegates to `repository.find` to search for a unique mapping.
        """
        return await self.product_mapping_repo.find(dto)


    async def filter(self, dto: FindProductsMappingDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductsMappingDTO]:
        """
        **Description**: Filters product mappings based on criteria with optional pagination.

        **Input**:
        - `dto`: *FindProductsMappingDTO* - Search criteria.
        - `limit`: *Optional[int]* - Maximum number of mappings to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[ProductsMappingDTO]* - List of matching mappings.

        **Exceptions**:
        - `PaginationError`: If limit or offset is negative.

        **How It Works**:
        - Validates pagination parameters.
        - Delegates to `repository.filter` to fetch filtered mappings.
        """
        if (limit is not None and limit < 0) or (offset is not None and offset < 0):
            raise PaginationError("limit and offset must be non-negative")
        return await self.product_mapping_repo.filter(dto, limit, offset)


    async def update(self, pk: int, dto: UpdateProductsMappingDTO) -> ProductsMappingDTO:
        """
        **Description**: Updates a product mapping’s details by its ID.

        **Input**:
        - `pk`: *int* - Mapping ID.
        - `dto`: *UpdateProductsMappingDTO* - New mapping data.

        **Output**:
        - *ProductsMappingDTO* - Updated mapping details.

        **Exceptions**:
        - `ProductMappingNotFound`: If the mapping doesn’t exist (handled by repository).
        - `ProductMappingAlreadyExists`: If the update violates unique constraints (handled by repository).

        **How It Works**:
        - Delegates to `repository.update` to modify the mapping.
        """
        return await self.product_mapping_repo.update(pk, dto)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a product mapping by its ID.

        **Input**:
        - `pk`: *int* - Mapping ID.

        **Output**:
        - None

        **Exceptions**:
        - `ProductMappingNotFound`: If the mapping doesn’t exist (handled by repository).

        **How It Works**:
        - Delegates to `repository.delete` to remove the mapping.
        """
        return await self.product_mapping_repo.delete(pk)