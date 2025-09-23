from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.base_model import Base

class UrlsModel(Base):
    """
    **Description**: SQLAlchemy model representing the `urls` database table.

    **Table**: `urls`

    **Columns**:
    - `id`: *int* - Primary key, auto-incremented identifier (inherited from Base).
    - `url`: *str* - The URL string (max length: 600, unique, non-nullable).
    - `brand_id`: *Optional[int]* - Foreign key to the `brands` table (nullable).
    - `fab_id`: *Optional[int]* - Foreign key to the `fabrics` table (nullable).

    **Usage**: Defines the database schema for storing URL data with relationships to brands and fabrics.
    """
    __tablename__ = "urls"

    url: Mapped[str] = mapped_column(String(600), nullable=False, unique=True)

    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=True
    )
    fab_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=True
    )