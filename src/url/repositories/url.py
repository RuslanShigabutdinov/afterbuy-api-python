from typing import List, Optional
from sqlalchemy import select, update, delete, asc
from sqlalchemy.exc import IntegrityError

from src.libs.exceptions import AlreadyExistError
from src.config.database.session import ISession
from src.url.models.url import UrlsModel
from src.url.entity import UrlEntity
from src.url.dto import UpdateUrlDTO, UrlDTO, FilterUrlsDTO

class UrlsRepository:
    """
    **Description**: Repository class for handling database operations related to URLs.

    **Attributes**:
    - `Model`: *UrlsModel* - SQLAlchemy model for the URLs table.
    - `session`: *ISession* - SQLAlchemy session for database interactions.

    **Methods**:
    - `create`: Creates a new URL in the database.
    - `get_list`: Retrieves a list of URLs with pagination.
    - `get`: Retrieves a URL by ID.
    - `filter`: Filters URLs by criteria with pagination.
    - `update`: Updates a URL’s details.
    - `delete`: Deletes a URL by ID.
    - `_get_dto`: Converts a database row to a UrlDTO (static helper).

    **Usage**: Provides CRUD functionality for URL data in the database.
    """
    Model = UrlsModel

    def __init__(self, session: ISession):
        """
        **Description**: Initializes the UrlsRepository with a database session.

        **Parameters**:
        - `session`: *ISession* - SQLAlchemy session for database operations.
        """
        self.session = session

    async def create(self, entity: UrlEntity) -> Optional[UrlDTO]:
        """
        **Description**: Creates a new URL in the database.

        **Parameters**:
        - `entity`: *UrlEntity* - Data for the new URL.

        **Returns**:
        - *Optional[UrlDTO]*: The created URL data.

        **Raises**:
        - `AlreadyExistError`: If the URL already exists (due to unique constraint).

        **Usage**: Persists a new URL and returns its DTO representation.
        """
        instance = self.Model(**entity.__dict__)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistError(f'Instance is already exist, {entity.url}')
        await self.session.refresh(instance)
        return self._get_dto(instance)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[UrlDTO]:
        """
        **Description**: Retrieves a list of all URLs with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of URLs to return.
        - `offset`: *Optional[int]* - Number of URLs to skip for pagination.

        **Returns**:
        - *List[UrlDTO]*: List of URL details.

        **Usage**: Fetches a paginated list of URLs from the database, ordered by ID.
        """
        stmt = select(self.Model).order_by(asc(self.Model.id)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_dto(instance) for instance in instances]

    async def get(self, pk: int) -> Optional[UrlDTO]:
        """
        **Description**: Retrieves a URL by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the URL.

        **Returns**:
        - *Optional[UrlDTO]*: The URL data if found, otherwise None.

        **Usage**: Fetches a specific URL from the database.
        """
        stmt = select(self.Model).filter_by(id=pk)
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one_or_none()
        return self._get_dto(instance) if instance else None

    async def filter(self, dto: FilterUrlsDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[UrlDTO]:
        """
        **Description**: Filters URLs based on criteria with optional pagination.

        **Parameters**:
        - `dto`: *FilterUrlsDTO* - Search criteria for filtering URLs.
        - `limit`: *Optional[int]* - Maximum number of URLs to return.
        - `offset`: *Optional[int]* - Number of URLs to skip for pagination.

        **Returns**:
        - *List[UrlDTO]*: List of matching URLs.

        **Usage**: Retrieves a filtered list of URLs from the database.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_dto(instance) for instance in instances]

    async def update(self, dto: UpdateUrlDTO, pk: int) -> UrlDTO:
        """
        **Description**: Updates a URL’s details by its ID.

        **Parameters**:
        - `dto`: *UpdateUrlDTO* - New details for the URL.
        - `pk`: *int* - Unique identifier of the URL.

        **Returns**:
        - *UrlDTO*: The updated URL data.

        **Raises**:
        - `NoResultFound`: If no URL with the given ID is found.
        - `MultipleResultsFound`: If multiple URLs match the ID (unlikely due to unique constraint).

        **Usage**: Modifies a URL’s details in the database and returns the updated DTO.
        """
        stmt = (
            update(self.Model)
            .values(**dto.model_dump())
            .filter_by(id=pk)
            .returning(self.Model)
        )
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one()
        await self.session.commit()
        return self._get_dto(instance)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a URL by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the URL.

        **Returns**:
        - None

        **Usage**: Removes a URL from the database.
        """
        stmt = delete(self.Model).filter_by(id=pk)
        await self.session.execute(stmt)
        await self.session.commit()

    @staticmethod
    def _get_dto(row: UrlsModel) -> UrlDTO:
        """
        **Description**: Converts a database row to a UrlDTO.

        **Parameters**:
        - `row`: *UrlsModel* - Database row representing a URL.

        **Returns**:
        - *UrlDTO*: Serialized URL data.

        **Usage**: Helper method to transform database records into DTOs for API responses.
        """
        return UrlDTO(
            id=row.id,
            url=row.url,
            brand_id=row.brand_id,
            fabric_id=row.fab_id
        )