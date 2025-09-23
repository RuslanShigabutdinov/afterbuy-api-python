from typing import Optional
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.base_model import Base

class ProductsMappingModel(Base):
    """
    **Description**: SQLAlchemy model for the `products_mappings` table.

    **Table**: `products_mappings`

    **Columns**:
    - `id`: *int* - Primary key, auto-incremented.
    - `fabric_mapping_id`: *Optional[int]* - Foreign key to the `fabric_mappings` table (nullable).
    - `jv_product_id`: *Optional[int]* - Foreign key to the `products` table for JV product (nullable).
    - `xl_product_id`: *Optional[int]* - Foreign key to the `products` table for XL product (nullable).

    **Constraints**:
    - Unique constraint on (`jv_product_id`, `xl_product_id`) pair, allowing NULLs.
    - Unique constraint on `fabric_mapping_id`, allowing NULLs.

    **Relationships**:
    - `jv_product`: Links to `ProductsModel` via `jv_product_id`.
    - `xl_product`: Links to `ProductsModel` via `xl_product_id`.
    - `fabric_mapping`: Links to `FabricMappingModel` via `fabric_mapping_id`.

    **Usage**: Represents the database schema for product mappings.
    """
    __tablename__ = "products_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    fabric_mapping_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("fabric_mappings.id", ondelete="CASCADE"),
        nullable=True
    )

    jv_product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True
    )

    xl_product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True
    )
