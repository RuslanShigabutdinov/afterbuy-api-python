from typing import Optional, List, Sequence
from sqlalchemy import select, update, delete, or_, and_

from src.fabric_mapping.exceptions import FabricMappingNotFoundException
from src.fabric_mapping.models.fabric_mapping import FabricMappingModel
from src.fabric_mapping.dto import UpdateFabricMappingDTO, FabricMappingDTO, CreateFabricMappingDTO

from src.config.database.session import ISession

class FabricMappingRepository:
    """
    **Description**: Repository layer for handling data access operations for Fabric Mappings.
                     It interacts directly with the database via SQLAlchemy.

    **Attributes**:
    - `Model`: *FabricMappingModel* - The SQLAlchemy ORM model class associated with this repository.
    - `session`: *AsyncSession* - The asynchronous database session instance used for executing queries.

    **Methods**:
    - `create`: Creates a new mapping or returns an existing one if the pair already exists.
    - `get_list`: Retrieves a list of mappings with pagination.
    - `get`: Retrieves a single mapping by its primary key.
    - `find_pairs`: Finds mappings containing a specific fabric ID (either JV or XL).
    - `update`: Updates a mapping by its primary key.
    - `delete`: Deletes a mapping by its primary key.
    - `delete_all`: Deletes all mapping records.
    - `_get_dto`: Helper to convert a model instance to a DTO.

    **Usage**: Provides an abstraction over raw database queries related to fabric mappings.
               Used by the `FabricMappingService` to perform CRUD and custom query operations.
    """
    Model = FabricMappingModel

    def __init__(self, session: ISession):
        """
        **Description**: Initializes the FabricMappingRepository with an async database session.

        **Parameters**:
        - `session`: *AsyncSession* - The SQLAlchemy async session instance.
        """
        self.session = session

    async def create(self, dto: CreateFabricMappingDTO) -> FabricMappingDTO:
        """
        **Description**: Creates a new Fabric Mapping record in the database.
                         First checks if an identical mapping pair (JV ID, XL ID) already exists.
                         If it exists, returns the existing record's DTO. Otherwise, creates and returns the new one.

        **Parameters**:
        - `dto`: *CreateFabricMappingDTO* - DTO containing the `fabric_id_JV` and `fabric_id_XL` for the new mapping.

        **Returns**:
        - *FabricMappingDTO*: The DTO representation of the created or found mapping record.

        **Usage**: Persists a new mapping pair, ensuring uniqueness of the pair combination.
        """
        stmt_select = select(self.Model).where(
            and_(
                self.Model.fabric_id_XL == dto.fabric_id_XL,
                self.Model.fabric_id_JV == dto.fabric_id_JV
            )
        )
        result = await self.session.execute(stmt_select)
        existing_instance = result.scalar_one_or_none()

        if existing_instance is not None:
            return self._get_dto(existing_instance)

        instance = self.Model(**dto.model_dump())

        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return self._get_dto(instance)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[FabricMappingDTO]:
        """
        **Description**: Retrieves a list of Fabric Mapping records from the database with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - The maximum number of records to retrieve.
        - `offset`: *Optional[int]* - The number of records to skip (for pagination).

        **Returns**:
        - *List[FabricMappingDTO]*: A list of DTOs representing the fetched mapping records.
                                      Returns an empty list if no records match the criteria.

        **Usage**: Fetches multiple records, commonly used for displaying lists with pagination support.
        """
        stmt = select(self.Model).order_by(self.Model.id)

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        instances: Sequence[FabricMappingModel] = result.scalars().all()
        return [self._get_dto(obj) for obj in instances]

    async def get(self, pk: int) -> FabricMappingDTO:
        """
        **Description**: Retrieves a single Fabric Mapping record by its primary key (`id`).

        **Parameters**:
        - `pk`: *int* - The unique identifier of the mapping record to retrieve.

        **Returns**:
        - *FabricMappingDTO*: The DTO representation of the found mapping record.

        **Raises**:
        - `FabricMappingNotFoundException`: If no record with the specified `pk` is found in the database.

        **Usage**: Fetches a specific record when its primary key is known.
        """
        stmt = select(self.Model).filter_by(id=pk)
        result = await self.session.execute(stmt)
        instance: Optional[FabricMappingModel] = result.scalar_one_or_none()

        if instance is None:
            raise FabricMappingNotFoundException(f"Fabric mapping with id '{pk}' not found.")

        return self._get_dto(instance)

    async def find_pairs(self, fabric_id: int) -> List[FabricMappingDTO]:
        """
        **Description**: Finds and retrieves all mapping records where the provided `fabric_id`
                         matches either the `fabric_id_JV` or `fabric_id_XL` field.

        **Parameters**:
        - `fabric_id`: *int* - The fabric identifier to search for within the mapping pairs.

        **Returns**:
        - *List[FabricMappingDTO]*: A list of DTOs for all matching mapping records.
                                      Returns an empty list if no matches are found.

        **Usage**: Used to find related fabric IDs across the JV and XL systems based on one known ID.
        """
        stmt = select(self.Model).where(
            or_(
                self.Model.fabric_id_XL == fabric_id,
                self.Model.fabric_id_JV == fabric_id
            )
        ).order_by(self.Model.id)

        result = await self.session.execute(stmt)
        instances: Sequence[FabricMappingModel] = result.scalars().all()
        return [self._get_dto(obj) for obj in instances]

    async def update(self, pk: int, dto: UpdateFabricMappingDTO) -> FabricMappingDTO:
        """
        **Description**: Updates an existing Fabric Mapping record identified by its primary key (`pk`)
                         with the data provided in the DTO. Only non-null fields in the DTO are updated.

        **Parameters**:
        - `pk`: *int* - The primary key of the record to update.
        - `dto`: *UpdateFabricMappingDTO* - DTO containing the new values for the fields to be updated.

        **Returns**:
        - *FabricMappingDTO*: The DTO representation of the record *after* the update.

        **Raises**:
        - `FabricMappingNotFoundException`: If no record with the specified `pk` exists.

        **Usage**: Modifies specific fields of an existing mapping record.
        """

        stmt = (
            update(self.Model)
            .values(**dto.model_dump(exclude_none=True))
            .filter_by(id=pk)
            .returning(self.Model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        instance: Optional[FabricMappingModel] = result.scalar_one_or_none()

        if instance is None:
            raise FabricMappingNotFoundException(f"Fabric mapping with id '{pk}' not found during update.")

        return self._get_dto(instance)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a Fabric Mapping record from the database based on its primary key (`pk`).

        **Parameters**:
        - `pk`: *int* - The primary key of the record to delete.

        **Returns**:
        - *None*

        **Usage**: Permanently removes a single mapping record.
        """
        stmt = delete(self.Model).filter_by(id=pk)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all(self) -> None:
        """
        **Description**: Deletes **ALL** records from the `fabric_mappings` table. Use with extreme caution.

        **Parameters**:
        - None

        **Returns**:
        - *None*

        **Usage**: Primarily for test environment resets or controlled data clearing operations.
                   Not typically exposed directly in production APIs without safeguards.
        """
        stmt = delete(self.Model)
        await self.session.execute(stmt)
        await self.session.commit()

    @staticmethod
    def _get_dto(instance: FabricMappingModel) -> FabricMappingDTO:
        """
        **Description**: Static helper method to convert a `FabricMappingModel` ORM instance
                         into a `FabricMappingDTO` data transfer object.

        **Parameters**:
        - `instance`: *FabricMappingModel* - The SQLAlchemy model instance.

        **Returns**:
        - *FabricMappingDTO*: The corresponding DTO populated with data from the model instance.

        **Usage**: Internal helper to ensure consistent DTO creation from model objects.
        """
        return FabricMappingDTO(
            id=instance.id,
            fabric_id_JV=instance.fabric_id_JV,
            fabric_id_XL=instance.fabric_id_XL
        )