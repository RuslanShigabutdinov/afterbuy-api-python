from typing import List, Optional

from src.brand.depends.repository import IBrandRepository
from src.brand.dto import BrandDTO, UpdateBrandDTO, FindBrandDTO
from src.brand.entity import BrandEntity
from src.libs.exceptions import PaginationError

class BrandService:
    """
    **Description**: Service class for brand-related operations.

    **Dependencies**:
    - `repository`: *IBrandRepository* - Handles database interactions.

    **Methods**:
    - `get`: Retrieves a brand by ID.
    - `get_list`: Retrieves a list of brands with optional pagination.
    - `create`: Creates a new brand.
    - `update`: Updates an existing brand.
    - `find`: Finds a single brand based on criteria.
    - `filter`: Filters brands based on criteria with pagination.
    - `delete`: Deletes a brand by ID.

    **Usage**: Acts as an intermediary between the API layer and the repository.
    """
    def __init__(self, repository: IBrandRepository):
        self.repository = repository

    async def get(self, pk: int) -> Optional[BrandDTO]:
        """
        **Description**: Retrieves a brand by its ID.

        **Input**:
        - `pk`: *int* - Brand ID.

        **Output**:
        - *Optional[BrandDTO]* - Brand details if found, else None.

        **Exceptions**:
        - `BrandNotFound`: If the brand doesn’t exist.

        **How It Works**:
        - Delegates to `repository.get` to fetch the brand.
        """
        return await self.repository.get(pk)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[BrandDTO]:
        """
        **Description**: Retrieves a list of brands with optional pagination.

        **Input**:
        - `limit`: *Optional[int]* - Maximum number of brands to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[BrandDTO]* - List of brand details.

        **Exceptions**:
        - `PaginationError`: If limit or offset is negative.

        **How It Works**:
        - Validates pagination parameters.
        - Delegates to `repository.get_list` to fetch the list.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError("limit or offset must be positive")
        return await self.repository.get_list(limit, offset)

    async def create(self, brand_entity: BrandEntity) -> BrandDTO:
        """
        **Description**: Creates a new brand.

        **Input**:
        - `brand_entity`: *BrandEntity* - Brand data (name).

        **Output**:
        - *BrandDTO* - Details of the created brand.

        **Exceptions**:
        - `AlreadyExistError`: If a brand with the same name exists.

        **How It Works**:
        - Delegates to `repository.create` to persist the brand.
        """
        return await self.repository.create(brand_entity)

    async def update(self, dto: UpdateBrandDTO, pk: int) -> BrandDTO:
        """
        **Description**: Updates a brand’s name by its ID.

        **Input**:
        - `dto`: *UpdateBrandDTO* - New brand name.
        - `pk`: *int* - Brand ID.

        **Output**:
        - *BrandDTO* - Updated brand details.

        **Exceptions**:
        - `BrandNotFound`: If the brand doesn’t exist.
        - `AlreadyExistError`: If the new name is already taken.

        **How It Works**:
        - Delegates to `repository.update` to modify the brand.
        """
        return await self.repository.update(dto=dto, pk=pk)

    async def find(self, dto: FindBrandDTO) -> Optional[BrandDTO]:
        """
        **Description**: Finds a single brand based on criteria.

        **Input**:
        - `dto`: *FindBrandDTO* - Search criteria (ID or name).

        **Output**:
        - *Optional[BrandDTO]* - Brand details if found and unique.

        **Exceptions**:
        - `BrandNotFound`: If no brand matches.
        - `BrandIsNotUnique`: If multiple brands match.

        **How It Works**:
        - Delegates to `repository.find` to search for the brand.
        """
        return await self.repository.find(dto)

    async def filter(self, dto: FindBrandDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[BrandDTO]:
        """
        **Description**: Filters brands based on criteria with optional pagination.

        **Input**:
        - `dto`: *FindBrandDTO* - Search criteria (ID or name).
        - `limit`: *Optional[int]* - Maximum number of brands to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[BrandDTO]* - List of matching brands.

        **Exceptions**:
        - `PaginationError`: If limit or offset is negative.

        **How It Works**:
        - Validates pagination parameters.
        - Delegates to `repository.filter` to fetch filtered brands.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError("limit or offset must be positive")
        return await self.repository.filter(dto, limit, offset)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a brand by its ID.

        **Input**:
        - `pk`: *int* - Brand ID.

        **Output**:
        - None

        **Exceptions**:
        - `BrandNotFound`: If the brand doesn’t exist (handled by repository).

        **How It Works**:
        - Delegates to `repository.delete` to remove the brand.
        """
        return await self.repository.delete(pk)