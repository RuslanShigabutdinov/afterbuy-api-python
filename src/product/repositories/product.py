from typing import List, Optional
from sqlalchemy import select, update, delete, asc
from sqlalchemy.exc import IntegrityError

from src.libs.exceptions import AlreadyExistError
from src.config.database.session import ISession
from src.product.exceptions import ProductNotFoundException
from src.product.models.product import ProductsModel
from src.product.entity import ProductEntity
from src.product.dto import ProductDTO, FilterProductsDTO, UpdateProductDTO, FindProductDTO, ProductPreviewDTO


class ProductsRepository:
    """
    **Description**: Repository class for handling database operations related to products.

    **Attributes**:
    - `Model`: *ProductsModel* - SQLAlchemy model for the products table.
    - `session`: *ISession* - SQLAlchemy session for database interactions.

    **Methods**:
    - `create`: Creates a new product in the database.
    - `get_list`: Retrieves a list of products with pagination.
    - `get`: Retrieves a product by ID.
    - `find`: Finds a single product by criteria.
    - `filter`: Filters products by criteria with pagination.
    - `update`: Updates a product’s details.
    - `delete`: Deletes a product by ID.
    - `_get_dto`: Converts a database row to a ProductDTO (static helper).

    **Usage**: Provides CRUD functionality for product data in the database.
    """
    Model = ProductsModel

    def __init__(self, session: ISession):
        """
        **Description**: Initializes the ProductsRepository with a database session.

        **Parameters**:
        - `session`: *ISession* - SQLAlchemy session for database operations.
        """
        self.session = session

    async def create(self, entity: ProductEntity) -> Optional[ProductDTO]:
        """
        **Description**: Creates a new product in the database.

        **Parameters**:
        - `entity`: *ProductEntity* - Data for the new product.

        **Returns**:
        - *Optional[ProductDTO]*: The created product data.

        **Raises**:
        - `AlreadyExistError`: If the product already exists (e.g., duplicate product_num or link).

        **Usage**: Persists a new product and returns its DTO representation.
        """
        instance = self.Model(**entity.__dict__)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistError(f'Instance is already exist, {entity.product_num}')
        await self.session.refresh(instance)
        return self._get_dto(instance)

    async def get_list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductPreviewDTO]:
        """
        **Description**: Retrieves a list of all products with optional pagination.

        **Parameters**:
        - `limit`: *Optional[int]* - Maximum number of products to return.
        - `offset`: *Optional[int]* - Number of products to skip for pagination.

        **Returns**:
        - *List[ProductDTO]*: List of product details.

        **Usage**: Fetches a paginated list of products from the database, ordered by ID.
        """
        stmt = select(self.Model).order_by(asc(self.Model.id)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_preview_dto(instance) for instance in instances]

    async def get(self, pk: int) -> Optional[ProductDTO]:
        """
        **Description**: Retrieves a product by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the product.

        **Returns**:
        - *Optional[ProductDTO]*: The product data if found, otherwise None.

        **Usage**: Fetches a specific product from the database.
        """
        stmt = select(self.Model).filter_by(id=pk)
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one_or_none()

        if instance is None:
            raise ProductNotFoundException(f"Product with {pk} id is not found.")

        return self._get_dto(instance)

    async def find(self, dto: FindProductDTO) -> Optional[ProductDTO]:
        """
        **Description**: Finds a single product based on specified criteria.

        **Parameters**:
        - `dto`: *FindProductDTO* - Criteria for finding the product.

        **Returns**:
        - *Optional[ProductDTO]*: The product data if found, otherwise None.

        **Usage**: Locates a unique product in the database.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True))
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one_or_none()

        if instance is None:
            raise ProductNotFoundException(f"Product with this criteria is not found. {dto}")

        return self._get_dto(instance)

    async def filter(self, dto: FilterProductsDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ProductPreviewDTO]:
        """
        **Description**: Filters products based on criteria with optional pagination.

        **Parameters**:
        - `dto`: *FilterProductsDTO* - Search criteria for filtering products.
        - `limit`: *Optional[int]* - Maximum number of products to return.
        - `offset`: *Optional[int]* - Number of products to skip for pagination.

        **Returns**:
        - *List[ProductDTO]*: List of matching products.

        **Usage**: Retrieves a filtered list of products from the database.
        """
        stmt = select(self.Model).filter_by(**dto.model_dump(exclude_none=True)).offset(offset).limit(limit)
        raw = await self.session.execute(stmt)
        instances = raw.scalars().all()
        return [self._get_preview_dto(instance) for instance in instances]

    async def update(self, dto: UpdateProductDTO, pk: int) -> ProductDTO:
        """
        **Description**: Updates a product’s details by its ID.

        **Parameters**:
        - `dto`: *UpdateProductDTO* - New details for the product.
        - `pk`: *int* - Unique identifier of the product.

        **Returns**:
        - *ProductDTO*: The updated product data.

        **Raises**:
        - `NoResultFound`: If no product with the given ID is found.

        **Usage**: Modifies a product’s details in the database and returns the updated DTO.
        """
        stmt = (
            update(self.Model)
            .values(**dto.model_dump())
            .filter_by(id=pk)
            .returning(self.Model)
        )
        raw = await self.session.execute(stmt)
        instance = raw.scalar_one_or_none()
        await self.session.commit()

        if instance is None:
            raise ProductNotFoundException(f"Product with this {pk} id is not found.")

        return self._get_dto(instance)

    async def delete(self, pk: int) -> None:
        """
        **Description**: Deletes a product by its ID.

        **Parameters**:
        - `pk`: *int* - Unique identifier of the product.

        **Returns**:
        - None

        **Usage**: Removes a product from the database.
        """
        stmt = delete(self.Model).filter_by(id=pk)
        await self.session.execute(stmt)
        await self.session.commit()

    @staticmethod
    def _get_dto(row: ProductsModel) -> ProductDTO:
        """
        **Description**: Converts a database row to a ProductDTO.

        **Parameters**:
        - `row`: *ProductsModel* - Database row representing a product.

        **Returns**:
        - *ProductDTO*: Serialized product data.

        **Usage**: Helper method to transform database records into DTOs for API responses.
        """
        return ProductDTO(
            id=row.id,
            brand_id=row.brand_id,
            fabric_id=row.fabric_id,
            url_id=row.url_id,
            collection=row.collection,
            product_num=row.product_num,
            price=row.price,
            properties=row.properties,
            article=row.article,
            pic_main=row.pic_main,
            pics=row.pics,
            category=row.category,
            link=row.link,
            ean=row.ean,
            html_description=row.html_description
        )

    @staticmethod
    def _get_preview_dto(row: ProductsModel) -> ProductPreviewDTO:
        """
        **Description**: Converts a database row to a ProductPreviewDTO.

        **Parameters**:
        - `row`: *ProductsModel* - Database row representing a product.

        **Returns**:
        - *ProductPreviewDTO*: Serialized product data.

        **Usage**: Helper method to transform database records into DTOs for API responses.
        """
        return ProductPreviewDTO(
            id=row.id,
            brand_id=row.brand_id,
            fabric_id=row.fabric_id,
            url_id=row.url_id,
            collection=row.collection,
            product_num=row.product_num,
            price=row.price,
            properties=row.properties,
            article=row.article,
            pic_main=row.pic_main,
            pics=row.pics,
            category=row.category,
            link=row.link,
            ean=row.ean
        )