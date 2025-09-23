from typing import Optional, List

from sqlalchemy import select, update, delete, or_, asc, and_
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound

from src.config.database.session import ISession
from src.product_mapping.models.product_mapping import ProductsMappingModel
from src.product_mapping.dto import (
    ProductsMappingDTO,
    CreateProductsMappingDTO,
    UpdateProductsMappingDTO,
    FindProductsMappingDTO
)
from src.product_mapping.exceptions import (
    ProductMappingNotFound,
    ProductMappingIsNotUnique,
    ProductMappingAlreadyExists
)

class ProductsMappingRepository:
    """
    **Description**: Repository class for product mapping database operations.

    **Model**: `ProductsMappingModel`

    **Dependencies**:
    - `session`: *ISession* - SQLAlchemy session for database interactions.

    **Methods**:
    - `create`: Creates a new product mapping.
    - `get_list`: Retrieves a list of product mappings with optional pagination.
    - `get`: Retrieves a product mapping by ID.
    - `find`: Finds a single product mapping based on criteria.
    - `filter`: Filters product mappings based on criteria with pagination.
    - `update`: Updates a product mapping by ID.
    - `delete`: Deletes a product mapping by ID.

    **Usage**: Handles CRUD operations for product mappings in the database.
    """
    Model = ProductsMappingModel

    def __init__(self, session: ISession):
        self.session = session

    async def create(self, dto: CreateProductsMappingDTO) -> ProductsMappingDTO:
        """
        **Description**: Creates a new product mapping in the database.

        **Input**:
        - `dto`: *CreateProductsMappingDTO* - Product mapping data.

        **Output**:
        - *ProductsMappingDTO* - Created mapping details.

        **Exceptions**:
        - `ProductMappingAlreadyExists`: If a mapping with the same unique constraints already exists.

        **How It Works**:
        - Inserts a new mapping into the database.
        - Commits the transaction and refreshes the instance.
        - Raises an exception if a unique constraint is violated.
        """
        instance = self.Model(**dto.model_dump(exclude_none=True))
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ProductMappingAlreadyExists("Product mapping with the provided details already exists.")
        await self.session.refresh(instance)
        return self._get_dto(instance)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductsMappingDTO]:
        """
        **Description**: Retrieves a list of ProductsMapping records with optional pagination.

        **Input**:
        - `limit`: *Optional[int]* - Maximum number of records to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[ProductsMappingDTO]* - List of mapping details.

        **How It Works**:
        - Executes a SELECT query with optional LIMIT and OFFSET, ordered by ID.
        - Returns a list of mapping DTOs.
        """
        stmt = select(self.Model).offset(offset).limit(limit).order_by(asc(self.Model.id))
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        return [self._get_dto(obj) for obj in instances]

    async def get(self, pk: int) -> ProductsMappingDTO:
        """
        **Description**: Retrieves a ProductsMapping record by its primary key (id).

        **Input**:
        - `pk`: *int* - Mapping ID.

        **Output**:
        - *ProductsMappingDTO* - Mapping details.

        **Exceptions**:
        - `ProductMappingNotFound`: If the record doesn’t exist.

        **How It Works**:
        - Executes a SELECT query filtered by ID.
        - Raises an exception if not found.
        """
        stmt = select(self.Model).filter_by(id=pk)
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            raise ProductMappingNotFound(f"Product mapping with id {pk} is not found.")
        return self._get_dto(instance)

    async def find(self, dto: FindProductsMappingDTO) -> ProductsMappingDTO:
        """
        **Description**: Finds a single product mapping based on criteria.

        **Input**:
        - `dto`: *FindProductsMappingDTO* - Search criteria.

        **Output**:
        - *ProductsMappingDTO* - Mapping details if found and unique.

        **Exceptions**:
        - `ProductMappingNotFound`: If no mapping matches.
        - `ProductMappingIsNotUnique`: If multiple mappings match.

        **How It Works**:
        - Executes a SELECT query with filters from the DTO.
        - Ensures exactly one result is returned.
        """
        filters = [getattr(self.Model, k) == v for k, v in dto.model_dump(exclude_none=True).items()]
        stmt = select(self.Model).filter(and_(*filters))

        try:
            result = await self.session.execute(stmt)
            instance = result.scalar_one_or_none()
        except MultipleResultsFound:
             raise ProductMappingIsNotUnique("Multiple product mapping records found for the given criteria.")

        if instance is None:
            raise ProductMappingNotFound("Product mapping not found for the given criteria.")

        return self._get_dto(instance)

    async def filter(self, dto: FindProductsMappingDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductsMappingDTO]:
        """
        **Description**: Filters product mappings based on criteria with optional pagination.

        **Input**:
        - `dto`: *FindProductsMappingDTO* - Search criteria.
        - `limit`: *Optional[int]* - Maximum number of records to return.
        - `offset`: *Optional[int]* - Starting index for the list.

        **Output**:
        - *List[ProductsMappingDTO]* - List of matching mappings.

        **How It Works**:
        - Executes a SELECT query with filters and pagination.
        - Returns a list of mapping DTOs.
        """
        filters = [getattr(self.Model, k) == v for k, v in dto.model_dump(exclude_none=True).items()]
        stmt = select(self.Model).filter(and_(*filters)).offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        return [self._get_dto(obj) for obj in instances]


    async def update(self, pk: int, dto: UpdateProductsMappingDTO) -> ProductsMappingDTO:
        """
        **Description**: Update an existing ProductsMapping record identified by pk.

        **Input**:
        - `pk`: *int* - Mapping ID.
        - `dto`: *UpdateProductsMappingDTO* - New mapping data.

        **Output**:
        - *ProductsMappingDTO* - Updated mapping details.

        **Exceptions**:
        - `ProductMappingNotFound`: If the record doesn’t exist.
        - `ProductMappingAlreadyExists`: If the update violates unique constraints.

        **How It Works**:
        - Executes an UPDATE query with the new data.
        - Commits the transaction and returns the updated mapping.
        """
        update_data = dto.model_dump(exclude_unset=True)
        if not update_data:
            # This case should ideally be caught by DTO validation
            raise ValueError("No fields provided for update.")

        stmt = (
            update(self.Model)
            .values(**update_data)
            .filter_by(id=pk)
            .returning(self.Model)
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            instance = result.scalar_one()
        except NoResultFound:
            await self.session.rollback()
            raise ProductMappingNotFound(f"Product mapping with id {pk} is not found.")
        except IntegrityError:
             raise ProductMappingAlreadyExists("Update violates unique constraint.")

        return self._get_dto(instance)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Delete a ProductsMapping record by its primary key.

        **Input**:
        - `pk`: *int* - Mapping ID.

        **Output**:
        - None

        **Exceptions**:
        - `ProductMappingNotFound`: If the record doesn’t exist.

        **How It Works**:
        - Executes a DELETE query filtered by ID.
        - Commits the transaction.
        - Raises ProductMappingNotFound if no row was deleted.
        """
        stmt = delete(self.Model).filter_by(id=pk)
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount == 0:
             raise ProductMappingNotFound(f"Product mapping with id {pk} is not found.")


    def _get_dto(self, instance: ProductsMappingModel) -> Optional[ProductsMappingDTO]:
        """
        **Description**: Transform a ProductsMappingModel instance into a ProductsMappingDTO.

        **Input**:
        - `instance`: *ProductsMappingModel* - Database record.

        **Output**:
        - *ProductsMappingDTO* - Serialized mapping data.

        **Usage**: Internal helper method for repository operations.
        """
        if instance is None:
            return None
        return ProductsMappingDTO(
            id=instance.id,
            fabric_mapping_id=instance.fabric_mapping_id,
            jv_product_id=instance.jv_product_id,
            xl_product_id=instance.xl_product_id,
        )