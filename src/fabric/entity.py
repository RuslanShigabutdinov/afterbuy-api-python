from typing import Optional
from pydantic import BaseModel

class FabricEntity(BaseModel):
    """
    **Description**: Represents the data required to create a new fabric.

    **Fields**:
    - `name`: *str* - Name of the fabric.
    - `afterbuy_id`: *str* - Afterbuy identifier for the fabric.
    - `brand_id`: *int* - Identifier of the brand associated with the fabric.
    - `total_count`: *int* - Number of items (defaults to 0).
    - `done`: *bool* - Completion status (defaults to False).

    **Usage**: Used as input data for creating a new fabric in the system.
    """
    name: str
    afterbuy_id: str
    brand_id: int
    total_count: int = 0
    parsed_count: int = 0
    done: bool = False