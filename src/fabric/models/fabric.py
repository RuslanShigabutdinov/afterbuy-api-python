from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.base_model import Base

class FabricsModel(Base):
    """
    **Description**: SQLAlchemy model representing the `fabrics` database table.

    **Table**: `fabrics`

    **Columns**:
    - `id`: *int* - Primary key, auto-incremented identifier.
    - `name`: *str* - Name of the fabric (max length: 600, non-nullable).
    - `afterbuy_id`: *str* - Unique Afterbuy identifier (max length: 300, non-nullable).
    - `brand_id`: *Optional[int]* - Foreign key to `brands` table (nullable, on delete cascade).
    - `items_count`: *int* - Number of items associated with the fabric (nullable).
    - `done`: *bool* - Completion status of the fabric (nullable).

    **Usage**: Defines the database schema for storing fabric data.
    """
    __tablename__ = "fabrics"

    name: Mapped[str] = mapped_column(String(600), nullable=False)
    afterbuy_id: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE")
    )
    total_count: Mapped[int] = mapped_column(nullable=True)
    parsed_count: Mapped[int] = mapped_column(nullable=True)
    done: Mapped[bool] = mapped_column(nullable=True)