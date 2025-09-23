from typing import List, Optional

from src.url.depends.repository import IUrlsRepository
from src.url.dto import FilterUrlsDTO, UpdateUrlDTO, UrlDTO
from src.url.entity import UrlEntity

from src.libs.exceptions import PaginationError

class UrlService:
    """
    **Description**: Service layer for managing URL-related business logic.

    **Attributes**:
    - `repository`: *IUrlsRepository* - Injected repository for database operations.

    **Methods**:
    - `create`: Creates a new URL.
    - `get`: Retrieves a URL by ID.
    - `get_list`: Retrieves a list of URLs with pagination.
    - `filter`: Filters URLs by criteria with pagination.
    - `update`: Updates a URL’s details.
    - `delete`: Deletes a URL by ID.

    **Usage**: Acts as an intermediary between the API router and repository layers for URL management.
    """
    def __init__(self, urls_repo: IUrlsRepository):
        """
        **Description**: Initializes the UrlService with a repository instance.

        **Parameters**:
        - `urls_repo`: *IUrlsRepository* - Repository for URL data access.
        """
        self.repository = urls_repo

    async def create(self, entity: UrlEntity) -> Optional[UrlDTO]:
        """
        **Description**: Creates a new URL in the system.

        **Parameters**:
        - `entity`: *UrlEntity* - Data for the new URL.

        **Returns**:
        - *Optional[UrlDTO]*: The created URL data, or None if creation failed.

        **Raises**:
        - `AlreadyExistError`: If the URL already exists in the system.

        **Usage**: Persists a new URL via the repository.
        """
        return await self.repository.create(entity)

    async def get(self, pk: int) -> Optional[UrlDTO]:
        """
        **Description**: Retrieves a URL by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the URL.

        **Returns**:
        - *Optional[UrlDTO]*: The URL data if found, otherwise None.

        **Usage**: Fetches a specific URL from the repository.
        """
        return await self.repository.get(pk)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[UrlDTO]:
        """
        **Description**: Retrieves a list of all URLs with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of URLs to return.
        - `offset`: *Optional[int]* - Number of URLs to skip for pagination.

        **Returns**:
        - *List[UrlDTO]*: List of URL details.

        **Raises**:
        - `PaginationError`: If limit or offset is negative.

        **Usage**: Fetches a paginated list of URLs from the repository.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError(f"Limit({limit}) or offset({offset}) is invalid (must be positive)")
        return await self.repository.get_list(limit, offset)

    async def filter(self, dto: FilterUrlsDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[UrlDTO]:
        """
        **Description**: Filters URLs based on criteria with optional pagination.

        **Parameters**:
        - `dto`: *FilterUrlsDTO* - Search criteria for filtering URLs.
        - `limit`: *Optional[int]* - Maximum number of URLs to return.
        - `offset`: *Optional[int]* - Number of URLs to skip for pagination.

        **Returns**:
        - *List[UrlDTO]*: List of matching URLs.

        **Raises**:
        - `PaginationError`: If limit or offset is negative.

        **Usage**: Retrieves a filtered list of URLs from the repository.
        """
        if limit is not None and offset is not None and (limit < 0 or offset < 0):
            raise PaginationError(f"Limit({limit}) or offset({offset}) is invalid (must be positive)")
        return await self.repository.filter(dto, limit, offset)

    async def update(self, dto: UpdateUrlDTO, pk: int) -> Optional[UrlDTO]:
        """
        **Description**: Updates an existing URL by its ID.

        **Parameters**:
        - `dto`: *UpdateUrlDTO* - New details for the URL.
        - `pk`: *int* - Unique identifier of the URL.

        **Returns**:
        - *Optional[UrlDTO]*: The updated URL data.

        **Raises**:
        - `NoResultFound`: If no URL with the given ID is found.
        - `MultipleResultsFound`: If multiple URLs match the ID (unlikely due to unique constraint).

        **Usage**: Modifies a URL’s details via the repository.
        """
        return await self.repository.update(dto, pk)

    async def delete(self, pk: int):
        """
        **Description**: Deletes a URL by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the URL.

        **Returns**:
        - None

        **Usage**: Removes a URL from the system via the repository.
        """
        return await self.repository.delete(pk)