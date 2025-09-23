from typing import Optional, List

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound

from src.brand.exceptions import BrandNotFound, BrandIsNotUnique
from src.config.database.session import ISession

from src.brand.models.brand import BrandsModel
from src.brand.entity import BrandEntity
from src.brand.dto import UpdateBrandDTO, BrandDTO, FindBrandDTO

from src.libs.exceptions import AlreadyExistError

class BrandRepository:
    """
    **Description**: Repository class for brand database operations.

    **Model**: `BrandsModel`

    **Dependencies**:
    - `session`: *ISession* - SQLAlchemy session for database interactions.

    **Methods**:
    - `create`: Creates a new brand.
    - `get_list`: Retrieves a list of brands with optional pagination.
    - `get`: Retrieves a brand by ID.
    - `update`: Updates a brand’s name by ID.
    - `find`: Finds a single brand based on criteria.
    - `filter`: Filters brands based on criteria with pagination.
    - `delete`: Deletes a brand by ID.

    **Usage**: Handles CRUD operations for brands in the database.
    """
    Model = BrandsModel

    def __init__(self, session: ISession):
        self.session = session

    async def create(self, entity: BrandEntity) -> Optional[BrandDTO]:
        """
        **Description**: Creates a new brand in the database.

        **Input**:
        - `entity`: *BrandEntity* - Brand data (name).

        **Output**:
        - *Optional[BrandDTO]* - Created brand details if successful.

        **Exceptions**:
        - `AlreadyExistError`: If a brand with the same name exists.

        **How It Works**:
        - Inserts a new brand into the database.
        - Commits the transaction and refreshes the instance.
        - Returns the brand’s DTO.
        """
        instance = self.Model(**entity.__dict__)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistError(f'Instance is already exist, {entity.name}')
        await self.session.refresh(instance)
        return self._get_dto(instance)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[BrandDTO]:
        """
        **Description**: Retrieves a list of brands with optional pagination.

        **Input**:
        - `limit`: *Optional[int]* - Maximum number of brands to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[BrandDTO]* - List of brand details.

        **How It Works**:
        - Executes a SELECT query with optional LIMIT and OFFSET.
        - Returns a list of brand DTOs.
        """
        stmt = select(self.Model).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_dto(instance) for instance in instances]

    async def get(self, pk: int) -> BrandDTO:
        """
        **Description**: Retrieves a brand by its ID.

        **Input**:
        - `pk`: *int* - Brand ID.

        **Output**:
        - *BrandDTO* - Brand details.

        **Exceptions**:
        - `BrandNotFound`: If the brand doesn’t exist.

        **How It Works**:
        - Executes a SELECT query filtered by ID.
        - Raises an exception if not found.
        """
        stmt = select(self.Model).filter_by(id=pk)
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one_or_none()
        if instance is None:
            raise BrandNotFound(f"Brand with {pk} id is not found.")
        return self._get_dto(instance)

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
        - Executes an UPDATE query with the new name.
        - Commits the transaction and returns the updated brand.
        """
        stmt = update(self.Model).values(**dto.model_dump()).filter_by(id=pk).returning(self.Model)
        raw = await self.session.execute(stmt)
        await self.session.commit()
        try:
            instance = raw.scalar_one()
        except NoResultFound:
            raise BrandNotFound(f"Brand with this {pk} id is not found.")
        return self._get_dto(instance)

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
        - Executes a SELECT query with filters.
        - Ensures exactly one result is returned.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True))
        raw = await self.session.execute(stmt)
        try:
            instance = raw.scalar_one_or_none()
        except MultipleResultsFound:
            raise BrandIsNotUnique("Multiple brand record found")
        if instance is None:
            raise BrandNotFound("Brand not found")
        return self._get_dto(instance)

    async def filter(self, dto: FindBrandDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[BrandDTO]:
        """
        **Description**: Filters brands based on criteria with optional pagination.

        **Input**:
        - `dto`: *FindBrandDTO* - Search criteria (ID or name).
        - `limit`: *Optional[int]* - Maximum number of brands to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[BrandDTO]* - List of matching brands.

        **How It Works**:
        - Executes a SELECT query with filters and pagination.
        - Returns a list of brand DTOs.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_dto(instance) for instance in instances]

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a brand by its ID.

        **Input**:
        - `pk`: *int* - Brand ID.

        **Output**:
        - None

        **Exceptions**:
        - `BrandNotFound`: If the brand doesn’t exist (handled by repository logic).

        **How It Works**:
        - Executes a DELETE query filtered by ID.
        - Commits the transaction.
        """
        stmt = delete(self.Model).filter_by(id=pk)
        await self.session.execute(stmt)
        await self.session.commit()

    @staticmethod
    def _get_dto(row: BrandsModel) -> BrandDTO:
        """
        **Description**: Converts a SQLAlchemy model instance to a BrandDTO.

        **Input**:
        - `row`: *BrandsModel* - Database row.

        **Output**:
        - *BrandDTO* - Serialized brand data.

        **Usage**: Internal helper method for repository operations.
        """
        return BrandDTO(id=row.id, name=row.name)