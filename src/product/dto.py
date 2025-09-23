from typing import Optional
from pydantic import BaseModel, model_validator, Field

class ProductPreviewDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) representing a part of product for transfer and display purposes.

    **Fields**:
    - `id`: *Optional[int]* - Unique identifier of the product.
    - `brand_id`: *Optional[int]* - Identifier of the brand.
    - `fabric_id`: *Optional[int]* - Identifier of the fabric.
    - `url_id`: *Optional[int]* - Identifier of the URL.
    - `collection`: *Optional[str]* - Collection name.
    - `product_num`: *Optional[str]* - Product number.
    - `price`: *Optional[float]* - Price of the product, must be greater than 0 and less than or equal to 100,000.
    - `properties`: *Optional[str]* - Product properties.
    - `article`: *Optional[str]* - Article number.
    - `pic_main`: *Optional[str]* - Main picture URL.
    - `pics`: *Optional[str]* - Additional pictures URLs.
    - `category`: *Optional[str]* - Product category.
    - `link`: *Optional[str]* - Product link.
    - `ean`: *Optional[str]* - EAN code.

    **Usage**: Used to serialize product data for API responses or input validation.
    """
    id: Optional[int] = None
    brand_id: Optional[int] = None
    fabric_id: Optional[int] = None
    url_id: Optional[int] = None
    collection: Optional[str] = None
    product_num: Optional[str] = None
    price: Optional[float] = None
    properties: Optional[str] = None
    article: Optional[str] = None
    pic_main: Optional[str] = None
    pics: Optional[str] = None
    category: Optional[str] = None
    link: Optional[str] = None
    ean: Optional[str] = None

class ProductDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) representing a product for transfer and display purposes.

    **Fields**:
    - `id`: *Optional[int]* - Unique identifier of the product.
    - `brand_id`: *Optional[int]* - Identifier of the brand.
    - `fabric_id`: *Optional[int]* - Identifier of the fabric.
    - `url_id`: *Optional[int]* - Identifier of the URL.
    - `collection`: *Optional[str]* - Collection name.
    - `product_num`: *Optional[str]* - Product number.
    - `price`: *Optional[float]* - Price of the product, must be greater than 0 and less than or equal to 100,000.
    - `properties`: *Optional[str]* - Product properties.
    - `article`: *Optional[str]* - Article number.
    - `pic_main`: *Optional[str]* - Main picture URL.
    - `pics`: *Optional[str]* - Additional pictures URLs.
    - `category`: *Optional[str]* - Product category.
    - `link`: *Optional[str]* - Product link.
    - `ean`: *Optional[str]* - EAN code.
    - `html_description`: *Optional[str]* - HTML description of the product.

    **Usage**: Used to serialize product data for API responses or input validation.
    """
    id: Optional[int] = None
    brand_id: Optional[int] = None
    fabric_id: Optional[int] = None
    url_id: Optional[int] = None
    collection: Optional[str] = None
    product_num: Optional[str] = None
    price: Optional[float] = Field(None, ge=0, le=100000)
    properties: Optional[str] = None
    article: Optional[str] = None
    pic_main: Optional[str] = None
    pics: Optional[str] = None
    category: Optional[str] = None
    link: Optional[str] = None
    ean: Optional[str] = None
    html_description: Optional[str] = None


class UpdateProductDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for updating existing product entries.

    **Fields**:
    - `brand_id`: *Optional[int]* - New brand identifier.
    - `fabric_id`: *Optional[int]* - New fabric identifier.
    - `url_id`: *Optional[int]* - New URL identifier.
    - `collection`: *Optional[str]* - New collection name.
    - `product_num`: *Optional[str]* - New product number.
    - `price`: *Optional[float]* - New price.
    - `properties`: *Optional[str]* - New properties.
    - `article`: *Optional[str]* - New article number.
    - `pic_main`: *Optional[str]* - New main picture URL.
    - `pics`: *Optional[str]* - New additional pictures URLs.
    - `category`: *Optional[str]* - New category.
    - `link`: *Optional[str]* - New product link.
    - `ean`: *Optional[str]* - New EAN code.
    - `html_description`: *Optional[str]* - New HTML description.

    **Validation**:
    - At least one field must be provided for the update operation.

    **Usage**: Passed to the update endpoint to modify product details.
    """
    brand_id: Optional[int] = None
    fabric_id: Optional[int] = None
    url_id: Optional[int] = None
    collection: Optional[str] = None
    product_num: Optional[str] = None
    price: Optional[float] = None
    properties: Optional[str] = None
    article: Optional[str] = None
    pic_main: Optional[str] = None
    pics: Optional[str] = None
    category: Optional[str] = None
    link: Optional[str] = None
    ean: Optional[str] = None
    html_description: Optional[str] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self


class FilterProductsDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for filtering product entries based on specified criteria.

    **Fields**:
    - `id`: *Optional[int]* - Filter by product identifier.
    - `url_id`: *Optional[int]* - Filter by URL identifier.
    - `product_num`: *Optional[str]* - Filter by product number.
    - `article`: *Optional[str]* - Filter by article number.
    - `link`: *Optional[str]* - Filter by product link.
    - `ean`: *Optional[str]* - Filter by EAN code.
    - `brand_id`: *Optional[int]* - Filter by brand identifier.
    - `fabric_id`: *Optional[int]* - Filter by fabric identifier.

    **Validation**:
    - At least one field must be provided for the filter operation.

    **Usage**: Used in `filter` operations to define search criteria for products.
    """
    id: Optional[int] = None
    url_id: Optional[int] = None
    product_num: Optional[str] = None
    article: Optional[str] = None
    link: Optional[str] = None
    ean: Optional[str] = None
    brand_id: Optional[int] = None
    fabric_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self


class FindProductDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for finding a specific product based on criteria.

    **Fields**:
    - `id`: *Optional[int]* - Product identifier.
    - `url_id`: *Optional[int]* - URL identifier.

    **Validation**:
    - At least one field must be provided for the find operation.

    **Usage**: Used in `find` operations to locate a unique product.
    """
    id: Optional[int] = None
    url_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self

