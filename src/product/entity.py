from dataclasses import dataclass


@dataclass
class ProductEntity:
    """
    **Description**: Represents a product entity for creation or internal processing.

    **Fields**:
    - `brand_id`: *int* - Identifier of the brand.
    - `fabric_id`: *int* - Identifier of the fabric.
    - `url_id`: *int* - Identifier of the URL.
    - `collection`: *str* - Collection name.
    - `product_num`: *str* - Product number.
    - `price`: *float* - Price of the product.
    - `properties`: *str* - Product properties.
    - `article`: *str* - Article number.
    - `pic_main`: *str* - Main picture URL.
    - `pics`: *str* - Additional pictures URLs.
    - `category`: *str* - Product category.
    - `link`: *str* - Product link.
    - `ean`: *str* - EAN code.
    - `html_description`: *str* - HTML description of the product.

    **Usage**: Used as input for creating or processing products in the service layer.
    """
    brand_id: int
    fabric_id: int
    url_id: int
    collection: str
    product_num: str
    price: float
    properties: str
    article: str
    pic_main: str
    pics: str
    category: str
    link: str
    ean: str
    html_description: str
