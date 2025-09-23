from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.base_model import Base

class BrandsModel(Base):
    """
    **Description**: SQLAlchemy model for the `brands` table.

    **Table**: `brands`

    **Columns**:
    - `id`: *int* - Primary key, auto-incremented.
    - `name`: *str* - Brand name (unique, non-null, max length: 10).

    **Usage**: Represents the database schema for brands.
    """
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)