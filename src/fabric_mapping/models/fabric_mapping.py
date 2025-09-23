from typing import Optional
from sqlalchemy import Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.base_model import Base # Assuming Base provides an 'id: Mapped[int] = mapped_column(primary_key=True)'

class FabricMappingModel(Base):
    """
    **Description**: SQLAlchemy ORM Model representing the `fabric_mappings` table.
                     This table stores associations between fabric identifiers from two different
                     systems or sources, referred to as 'JV' and 'XL'.

    **Attributes**: (Inherited `id` from `Base` is assumed)
    - `id`: *Mapped[int]* - Primary key for the mapping record.
    - `fabric_id_JV`: *Mapped[Optional[int]]* - Foreign key referencing the `fabrics.id` table,
                                                representing the fabric ID from the 'JV' source. Nullable.
    - `fabric_id_XL`: *Mapped[Optional[int]]* - Foreign key referencing the `fabrics.id` table,
                                                representing the fabric ID from the 'XL' source. Nullable.

    **Table Arguments**:
    - `UniqueConstraint('fabric_id_JV', 'fabric_id_XL', name='uq_fabric_mapping_pair')`:
        Ensures that each pair of (JV ID, XL ID) is unique within the table. Note: handles nulls differently across DBs.
        Consider if nulls should be part of the uniqueness or if a check constraint is needed.
    - `Index('ix_fabric_mapping_jv_id', 'fabric_id_JV')`: Index on the JV fabric ID for faster lookups.
    - `Index('ix_fabric_mapping_xl_id', 'fabric_id_XL')`: Index on the XL fabric ID for faster lookups.

    **Relationships**:
    - Defines foreign keys to the `fabrics` table (assuming it exists).
    - `ondelete="CASCADE"` means if a referenced Fabric is deleted, the corresponding mapping rows are also deleted.

    **Usage**: Defines the database schema structure for fabric mappings and is used by the repository
               layer (via SQLAlchemy) to interact with the `fabric_mappings` table.
    """
    __tablename__ = "fabric_mappings"

    # Foreign key referencing the 'fabrics' table for the JV system ID
    fabric_id_JV: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("fabrics.id", name="fk_fabric_mapping_jv_id", ondelete="CASCADE"),
        nullable=True,
        comment="Fabric ID from the JV source system, references fabrics.id"
    )

    # Foreign key referencing the 'fabrics' table for the XL system ID
    fabric_id_XL : Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("fabrics.id", name="fk_fabric_mapping_xl_id", ondelete="CASCADE"),
        nullable=True,
        comment="Fabric ID from the XL source system, references fabrics.id"
    )

    __table_args__ = (
        UniqueConstraint('fabric_id_JV', 'fabric_id_XL', name='uq_fabric_mapping_pair'),

        # Add indexes for faster lookups based on individual fabric IDs
        Index('ix_fabric_mapping_jv_id', 'fabric_id_JV'),
        Index('ix_fabric_mapping_xl_id', 'fabric_id_XL'),

        {'comment': 'Stores mappings between fabric IDs from JV and XL systems'}
    )

    def __repr__(self) -> str:
        return f"<FabricMappingModel(id={self.id}, jv_id={self.fabric_id_JV}, xl_id={self.fabric_id_XL})>"

