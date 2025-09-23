from typing import List, Optional

from src.fabric_mapping.depends.repositories import IFabricMappingsRepository
from src.fabric_mapping.dto import FabricMappingDTO, CreateFabricMappingDTO, UpdateFabricMappingDTO
from src.libs.exceptions import PaginationError # Assuming PaginationError exists here

class FabricMappingService:
    """
    **Description**: Service layer handling business logic for Fabric Mappings.

    **Attributes**:
    - `repository`: *IFabricMappingsRepository* - Injected repository for data access operations.

    **Methods**:
    - `create`: Creates a new fabric mapping, preventing exact duplicates.
    - `get_list`: Retrieves a list of fabric mappings with pagination.
    - `get`: Retrieves a single fabric mapping by its primary key.
    - `find_pairs`: Finds all mapping pairs associated with a given fabric ID (either JV or XL).
    - `update`: Updates an existing fabric mapping.
    - `delete`: Deletes a specific fabric mapping by its primary key.
    - `delete_all`: Deletes all fabric mapping records (use with caution).

    **Usage**: Acts as an intermediary between API endpoints (routers) and the data access layer (repository)
               for fabric mapping operations. Encapsulates business rules and orchestrates repository calls.
    """
    def __init__(self, repository: IFabricMappingsRepository):
        """
        **Description**: Initializes the FabricMappingService with a repository instance.

        **Parameters**:
        - `repository`: *IFabricMappingsRepository* - The repository implementation dependency providing data access methods.
        """
        # Use the interface type hint for consistency with dependency injection
        self.repository: IFabricMappingsRepository = repository

    async def create(self, dto: CreateFabricMappingDTO) -> FabricMappingDTO:
        """
        **Description**: Creates a new Fabric Mapping record if an identical pair doesn't already exist.

        **Parameters**:
        - `dto`: *CreateFabricMappingDTO* - Data Transfer Object containing the details for the new mapping.

        **Returns**:
        - *FabricMappingDTO*: The DTO representation of the created or existing mapping record.

        **Usage**: Called to persist a new association between fabric IDs from different sources.
                   Checks for duplicates before insertion.
        """
        # Repository handles duplicate check logic
        return await self.repository.create(dto)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[FabricMappingDTO]:
        """
        **Description**: Retrieves a list of Fabric Mapping records, supporting pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of records to return. Defaults to no limit.
        - `offset`: *Optional[int]* - Number of records to skip for pagination. Defaults to 0.

        **Returns**:
        - *List[FabricMappingDTO]*: A list of fabric mapping DTOs.

        **Raises**:
        - `PaginationError`: If `limit` or `offset` are provided and are negative.

        **Usage**: Fetches multiple mapping records, typically for display in lists or tables.
        """
        if limit is not None and limit < 0:
            raise PaginationError(f"Limit ({limit}) must be non-negative.")
        if offset is not None and offset < 0:
            raise PaginationError(f"Offset ({offset}) must be non-negative.")

        return await self.repository.get_list(limit=limit, offset=offset)

    async def get(self, pk: int) -> Optional[FabricMappingDTO]:
        """
        **Description**: Retrieves a single Fabric Mapping record by its unique primary key (`id`).

        **Parameters**:
        - `pk`: *int* - The primary key identifier of the fabric mapping record.

        **Returns**:
        - *Optional[FabricMappingDTO]*: The DTO of the found mapping, or None if not found (though repository raises).

        **Raises**:
        - `FabricMappingNotFoundException`: If no mapping with the given `pk` exists (raised by the repository).

        **Usage**: Fetches the details of a specific known mapping record.
        """
        # Repository handles the "not found" case by raising an exception
        return await self.repository.get(pk)

    async def find_pairs(self, fabric_id: int) -> List[FabricMappingDTO]:
        """
        **Description**: Finds all mapping records where the given `fabric_id` appears
                         in either the `fabric_id_JV` or `fabric_id_XL` field.

        **Parameters**:
        - `fabric_id`: *int* - The fabric identifier to search for in mapping pairs.

        **Returns**:
        - *List[FabricMappingDTO]*: A list of DTOs representing the mapping pairs found.
                                      Returns an empty list if no pairs are found.

        **Usage**: Useful for finding all associated fabric IDs when given one ID from either source system.
        """
        return await self.repository.find_pairs(fabric_id)

    async def update(self, pk: int, dto: UpdateFabricMappingDTO) -> FabricMappingDTO:
        """
        **Description**: Updates an existing Fabric Mapping record identified by its primary key.

        **Parameters**:
        - `pk`: *int* - The primary key identifier of the record to update.
        - `dto`: *UpdateFabricMappingDTO* - DTO containing the fields and values to update.
                                          Only non-None fields in the DTO are typically used for updates.

        **Returns**:
        - *FabricMappingDTO*: The DTO representation of the mapping record *after* the update.

        **Raises**:
        - `FabricMappingNotFoundException`: If no mapping with the given `pk` exists (raised by the repository).

        **Usage**: Modifies the details of an existing fabric mapping record.
        """
        # Repository handles the update logic and "not found" case
        return await self.repository.update(pk, dto)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a Fabric Mapping record identified by its primary key.

        **Parameters**:
        - `pk`: *int* - The primary key identifier of the record to delete.

        **Returns**:
        - *None*

        **Raises**:
        - Potentially database-level errors if constraints are violated during delete,
          though `FabricMappingNotFoundException` is *not* typically raised here if the item
          doesn't exist (deletion is often idempotent). Check repository implementation if specific
          behavior is needed.

        **Usage**: Permanently removes a specific fabric mapping record from the system.
        """
        await self.repository.delete(pk)

    async def delete_all(self) -> None:
        """
        **Description**: Deletes **ALL** Fabric Mapping records from the database.
                         This is a destructive operation and should be used with extreme caution.

        **Parameters**:
        - None

        **Returns**:
        - *None*

        **Usage**: Primarily for testing, data reset, or specific administrative tasks.
                   Ensure proper authorization and confirmation mechanisms if exposed via an API.
        """
        await self.repository.delete_all()

