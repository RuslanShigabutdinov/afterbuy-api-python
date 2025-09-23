from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.base_model import Base


class ProductsModel(Base):
    """
    **Description**: SQLAlchemy model representing the `products` database table.

    **Table**: `products`

    **Columns**:
    - `id`: *int* - Primary key, auto-incremented identifier (inherited from Base).
    - `brand_id`: *Optional[int]* - Foreign key to the `brands` table (nullable).
    - `fabric_id`: *Optional[int]* - Foreign key to the `fabrics` table (nullable).
    - `url_id`: *Optional[int]* - Foreign key to the `urls` table (nullable).
    - `collection`: *str* - Collection name (max length: 600).
    - `product_num`: *str* - Product number (max length: 100, nullable).
    - `price`: *float* - Product price (nullable).
    - `properties`: *str* - Product properties (text, nullable).
    - `article`: *str* - Article number (max length: 1000, nullable).
    - `pic_main`: *str* - Main picture URL (max length: 600, nullable).
    - `pics`: *str* - Additional pictures URLs (text, nullable).
    - `category`: *str* - Product category (max length: 600, nullable).
    - `link`: *str* - Product link (max length: 600, nullable, unique).
    - `ean`: *str* - EAN code (max length: 300, nullable).
    - `html_description`: *str* - HTML description (text, nullable).

    **Usage**: Defines the database schema for storing product data with relationships to brands, fabrics, and URLs.
    """
    __tablename__ = "products"

    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=True
    )
    fabric_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=True
    )
    url_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=True
    )
    collection: Mapped[str] = mapped_column(String(600))
    product_num: Mapped[str] = mapped_column(String(100), nullable=True)
    price: Mapped[float] = mapped_column(nullable=True)
    properties: Mapped[str] = mapped_column(Text, nullable=True)
    article: Mapped[str] = mapped_column(String(1000), nullable=True)
    pic_main: Mapped[str] = mapped_column(String(600), nullable=True)
    pics: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(600), nullable=True)
    link: Mapped[str] = mapped_column(String(600), nullable=True, unique=True)
    ean: Mapped[str] = mapped_column(String(300), nullable=True)
    html_description: Mapped[str] = mapped_column(Text, nullable=True)