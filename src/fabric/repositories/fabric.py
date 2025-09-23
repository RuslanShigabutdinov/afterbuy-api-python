from typing import List, Optional
from sqlalchemy import select, update, delete, asc
from sqlalchemy.exc import IntegrityError, MultipleResultsFound

from src.config.database.session import ISession
from src.libs.exceptions import AlreadyExistError

from src.fabric.exceptions import FabricNotFound, FabricIsNotUnique
from src.fabric.models.fabric import FabricsModel
from src.fabric.entity import FabricEntity
from src.fabric.dto import UpdateFabricDTO, FabricDTO, FindFabricDTO

class FabricRepository:
    """
    **Description**: Repository class handling database operations for fabrics.

    **Attributes**:
    - `Model`: *FabricsModel* - The SQLAlchemy model for fabrics.
    - `session`: *ISession* - SQLAlchemy session for database interactions.

    **Methods**:
    - `create`: Creates a new fabric in the database.
    - `get_list`: Retrieves a list of fabrics with optional pagination.
    - `get`: Retrieves a fabric by its ID.
    - `find`: Finds a single fabric by criteria.
    - `filter`: Filters fabrics by criteria with pagination.
    - `update`: Updates a fabric by its ID.
    - `delete`: Deletes a fabric by its ID.
    - `_get_dto`: Converts a database row to a FabricDTO (static helper).

    **Usage**: Provides CRUD functionality for fabrics in the database.
    """
    Model = FabricsModel

    def __init__(self, session: ISession):
        """
        **Description**: Initializes the FabricRepository with a database session.

        **Parameters**:
        - `session`: *ISession* - SQLAlchemy session for database operations.
        """
        self.session = session

    async def create(self, fabric_entity: FabricEntity) -> FabricDTO:
        """
        **Description**: Creates a new fabric in the database.

        **Parameters**:
        - `fabric_entity`: *FabricEntity* - Data for the new fabric.

        **Returns**:
        - *FabricDTO*: Details of the created fabric.

        **Raises**:
        - `AlreadyExistError`: If a fabric with the same `afterbuy_id` already exists.

        **Usage**: Persists a new fabric and returns its DTO.
        """
        instance = self.Model(**fabric_entity.__dict__)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistError(f'Instance is already exist, {fabric_entity.name}')
        await self.session.refresh(instance)
        return self._get_dto(instance)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[FabricDTO]:
        """
        **Description**: Retrieves a list of fabrics with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of fabrics to return.
        - `offset`: *Optional[int]* - Starting index for pagination.

        **Returns**:
        - *List[FabricDTO]*: List of fabric details.

        **Usage**: Fetches all fabrics with optional pagination from the database.
        """
        stmt = select(self.Model).order_by(asc(self.Model.id)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_dto(instance) for instance in instances]

    async def get(self, pk: int) -> FabricDTO:
        """
        **Description**: Retrieves a fabric by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the fabric.

        **Returns**:
        - *FabricDTO*: Details of the fabric.

        **Raises**:
        - `FabricNotFound`: If no fabric exists with the given ID.

        **Usage**: Fetches a specific fabric from the database.
        """
        stmt = select(self.Model).filter_by(id=pk)
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one_or_none()
        if instance is None:
            raise FabricNotFound(f"Fabric with {pk} id is not found.")
        return self._get_dto(instance)

    async def find(self, dto: FindFabricDTO) -> FabricDTO:
        """
        **Description**: Finds a single fabric based on search criteria.

        **Parameters**:
        - `dto`: *FindFabricDTO* - Search criteria for the fabric.

        **Returns**:
        - *FabricDTO*: Details of the found fabric.

        **Raises**:
        - `FabricNotFound`: If no fabric matches the criteria.
        - `FabricIsNotUnique`: If multiple fabrics match the criteria.

        **Usage**: Locates a unique fabric in the database.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True))
        raw = await self.session.execute(stmt)
        try:
            instance = raw.scalar_one_or_none()
        except MultipleResultsFound:
            raise FabricIsNotUnique("Multiple fabric record found, try `/filter`")
        if instance is None:
            raise FabricNotFound("Fabric with this criteria not found")
        return self._get_dto(instance)

    async def filter(self, dto: FindFabricDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[FabricDTO]:
        """
        **Description**: Filters fabrics based on criteria with optional pagination.

        **Parameters**:
        - `dto`: *FindFabricDTO* - Search criteria for filtering fabrics.
        - `limit`: *Optional[int]* - Maximum number of fabrics to return.
        - `offset`: *Optional[int]* - Starting index for pagination.

        **Returns**:
        - *List[FabricDTO]*: List of matching fabrics.

        **Usage**: Retrieves a filtered list of fabrics from the database.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_dto(instance) for instance in instances]

    async def update(self, dto: UpdateFabricDTO, pk: int) -> FabricDTO:
        """
        **Description**: Updates a fabric’s details by its ID.

        **Parameters**:
        - `dto`: *UpdateFabricDTO* - New details for the fabric.
        - `pk`: *int* - Unique identifier of the fabric.

        **Returns**:
        - *FabricDTO*: Updated fabric details.

        **Raises**:
        - `FabricNotFound`: If no fabric exists with the given ID.

        **Usage**: Modifies an existing fabric in the database.
        """
        stmt = (
            update(self.Model)
            .values(**dto.model_dump())
            .filter_by(id=pk)
            .returning(self.Model)
        )
        raw = await self.session.execute(stmt)
        await self.session.commit()
        instance = raw.scalar_one()
        if instance is None:
            raise FabricNotFound(f"Fabric with {pk} id is not found.")
        return self._get_dto(instance)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a fabric by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the fabric.

        **Returns**:
        - None

        **Usage**: Removes a fabric from the database.
        """
        stmt = delete(self.Model).filter_by(id=pk)
        await self.session.execute(stmt)
        await self.session.commit()

    @staticmethod
    def _get_dto(row: FabricsModel) -> FabricDTO:
        """
        **Description**: Converts a database row to a FabricDTO.

        **Parameters**:
        - `row`: *FabricsModel* - Database row representing a fabric.

        **Returns**:
        - *FabricDTO*: Serialized fabric data.

        **Usage**: Helper method to transform database records into DTOs.
        """
        return FabricDTO(
            id=row.id,
            name=row.name,
            afterbuy_id=row.afterbuy_id,
            brand_id=row.brand_id,
            total_count=row.total_count,
            parsed_count=row.parsed_count,
            done=row.done
        )