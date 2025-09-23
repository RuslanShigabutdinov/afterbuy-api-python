# Refactored Code:

# C:\Users\office\Desktop\AfterbuyBot\src\fabric_mapping\dto.py
from typing import Optional
from pydantic import BaseModel, Field

class FabricMappingDTO(BaseModel):
    """
    **Description**: Data Transfer Object for representing a Fabric Mapping record.

    **Attributes**:
    - `id`: *Optional[int]* - The unique identifier of the mapping record. Usually auto-generated.
    - `fabric_id_JV`: *Optional[int]* - The identifier for the fabric from the 'JV' system/source.
    - `fabric_id_XL`: *Optional[int]* - The identifier for the fabric from the 'XL' system/source.

    **Usage**: Used for returning fabric mapping data from the service/repository layers.
    """
    id: Optional[int] = Field(None, description="Unique identifier for the fabric mapping")
    fabric_id_JV: Optional[int] = Field(None, description="Fabric ID from the JV source")
    fabric_id_XL: Optional[int] = Field(None, description="Fabric ID from the XL source")


class CreateFabricMappingDTO(BaseModel):
    """
    **Description**: Data Transfer Object for creating a new Fabric Mapping record.

    **Attributes**:
    - `fabric_id_JV`: *Optional[int]* - The identifier for the fabric from the 'JV' system/source.
    - `fabric_id_XL`: *Optional[int]* - The identifier for the fabric from the 'XL' system/source.

    **Usage**: Used as input data when creating a new fabric mapping entry.
               At least one ID should typically be provided.
    """
    fabric_id_JV: Optional[int] = Field(None, description="Fabric ID from the JV source")
    fabric_id_XL: Optional[int] = Field(None, description="Fabric ID from the XL source")


class UpdateFabricMappingDTO(BaseModel):
    """
    **Description**: Data Transfer Object for updating an existing Fabric Mapping record.
                 All fields are optional, allowing partial updates.

    **Attributes**:
    - `fabric_id_JV`: *Optional[int]* - The new identifier for the fabric from the 'JV' system/source.
    - `fabric_id_XL`: *Optional[int]* - The new identifier for the fabric from the 'XL' system/source.

    **Usage**: Used as input data when updating an existing fabric mapping entry.
               Only fields that need changing should be provided.
    """
    fabric_id_JV: Optional[int] = Field(None, description="Updated Fabric ID from the JV source")
    fabric_id_XL: Optional[int] = Field(None, description="Updated Fabric ID from the XL source")
