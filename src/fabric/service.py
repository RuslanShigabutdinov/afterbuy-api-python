from typing import List, Optional
from src.fabric.depends.repository import IFabricRepository
from src.fabric.dto import FabricDTO, UpdateFabricDTO, FindFabricDTO
from src.fabric.entity import FabricEntity
from src.libs.exceptions import PaginationError

class FabricService:
    """
    **Description**: Service layer for managing fabric-related business logic.

    **Attributes**:
    - `repository`: *IFabricRepository* - Injected repository for database operations.

    **Methods**:
    - `create`: Creates a new fabric.
    - `get_list`: Retrieves a list of fabrics with pagination.
    - `get`: Retrieves a fabric by ID.
    - `find`: Finds a single fabric by criteria.
    - `filter`: Filters fabrics by criteria with pagination.
    - `update`: Updates an existing fabric.
    - `delete`: Deletes a fabric by ID.

    **Usage**: Acts as an intermediary between the API and repository layers.
    """
    def __init__(self, repository: IFabricRepository):
        """
        **Description**: Initializes the FabricService with a repository.

        **Parameters**:
        - `repository`: *IFabricRepository* - Repository instance for database access.
        """
        self.repository = repository

    async def create(self, fabric_entity: FabricEntity) -> FabricDTO:
        """
        **Description**: Creates a new fabric in the system.

        **Parameters**:
        - `fabric_entity`: *FabricEntity* - Data for the new fabric.

        **Returns**:
        - *FabricDTO*: Details of the created fabric.

        **Raises**:
        - `AlreadyExistError`: If a fabric with the same `afterbuy_id` exists.

        **Usage**: Persists a new fabric via the repository.
        """
        return await self.repository.create(fabric_entity)

    async def get_list(self, limit: Optional[int], offset: Optional[int]) -> List[FabricDTO]:
        """
        **Description**: Retrieves a list of fabrics with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of fabrics to return.
        - `offset`: *Optional[int]* - Starting index for pagination.

        **Returns**:
        - *List[FabricDTO]*: List of fabric details.

        **Raises**:
        - `PaginationError`: If `limit` or `offset` is negative.

        **Usage**: Fetches a paginated list of fabrics from the repository.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError(f"Limit({limit}) or offset({offset}) is invalid (must be positive)")
        return await self.repository.get_list(limit, offset)

    async def get(self, pk: int):
        """
        **Description**: Retrieves a fabric by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the fabric.

        **Returns**:
        - *FabricDTO*: Details of the fabric.

        **Raises**:
        - `FabricNotFound`: If no fabric exists with the given ID.

        **Usage**: Fetches a specific fabric from the repository.
        """
        return await self.repository.get(pk)

    async def find(self, dto: FindFabricDTO) -> Optional[FabricDTO]:
        """
        **Description**: Finds a single fabric based on search criteria.

        **Parameters**:
        - `dto`: *FindFabricDTO* - Search criteria for the fabric.

        **Returns**:
        - *Optional[FabricDTO]*: Details of the found fabric, if unique.

        **Raises**:
        - `FabricNotFound`: If no fabric matches the criteria.
        - `FabricIsNotUnique`: If multiple fabrics match the criteria.

        **Usage**: Searches for a unique fabric via the repository.
        """
        return await self.repository.find(dto)

    async def filter(self, dto: FindFabricDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[FabricDTO]:
        """
        **Description**: Filters fabrics based on criteria with optional pagination.

        **Parameters**:
        - `dto`: *FindFabricDTO* - Search criteria for filtering fabrics.
        - `limit`: *Optional[int]* - Maximum number of fabrics to return.
        - `offset`: *Optional[int]* - Starting index for pagination.

        **Returns**:
        - *List[FabricDTO]*: List of matching fabrics.

        **Raises**:
        - `PaginationError`: If `limit` or `offset` is negative.

        **Usage**: Retrieves a filtered list of fabrics from the repository.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError(f"Limit({limit}) or offset({offset}) is invalid (must be positive)")
        return await self.repository.filter(dto, limit, offset)

    async def update(self, dto: UpdateFabricDTO, pk: int) -> FabricDTO:
        """
        **Description**: Updates an existing fabric by its ID.

        **Parameters**:
        - `dto`: *UpdateFabricDTO* - New details for the fabric.
        - `pk`: *int* - Unique identifier of the fabric.

        **Returns**:
        - *FabricDTO*: Updated fabric details.

        **Raises**:
        - `FabricNotFound`: If no fabric exists with the given ID.

        **Usage**: Modifies a fabric’s details via the repository.
        """
        return await self.repository.update(dto, pk)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a fabric by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the fabric.

        **Returns**:
        - None

        **Raises**:
        - `FabricNotFound`: If no fabric exists with the given ID.

        **Usage**: Removes a fabric from the system via the repository.
        """
        await self.repository.delete(pk)