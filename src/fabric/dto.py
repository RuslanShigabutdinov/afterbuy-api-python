from typing import Optional
from pydantic import BaseModel, model_validator, constr, Field

class FabricDTO(BaseModel):
    """
    **Description**: Represents a fabric's data for transfer and display purposes.

    **Fields**:
    - `id`: *int* - Unique identifier of the fabric.
    - `name`: *str* - Name of the fabric.
    - `afterbuy_id`: *str* - Afterbuy identifier for the fabric.
    - `brand_id`: *int* - Identifier of the brand associated with the fabric.
    - `items_count`: *int* - Number of items associated with the fabric.
    - `done`: *bool* - Indicates whether the fabric processing is complete.

    **Usage**: Used to serialize fabric data for API responses or data transfer.
    """
    id: int
    name: str
    afterbuy_id: str
    brand_id: int
    total_count: int
    parsed_count: int
    done: bool

class UpdateFabricDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for updating fabric details.

    **Fields**:
    - `name`: *Optional[str]* - Updated name of the fabric (optional).
    - `afterbuy_id`: *Optional[str]* - Updated Afterbuy identifier (optional).
    - `brand_id`: *Optional[int]* - Updated brand identifier (optional).
    - `items_count`: *Optional[int]* - Updated items count (optional).
    - `done`: *Optional[bool]* - Updated completion status (optional).

    **Validation**:
    - At least one field must be provided for the update operation.

    **Usage**: Used in API endpoints to partially update fabric details.
    """
    name: Optional[str] = None
    afterbuy_id: Optional[str] = None
    brand_id: Optional[int] = None
    total_count: Optional[int] = None
    parsed_count: Optional[int] = None
    done: Optional[bool] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """
        **Description**: Validates that at least one field is provided.

        **Raises**:
        - `ValueError`: If all fields are None.

        **Returns**:
        - *self*: The validated instance.
        """
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self

class FindFabricDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for finding or filtering fabrics based on criteria.

    **Fields**:
    - `id`: *Optional[int]* - Fabric ID to filter by (optional).
    - `name`: *Optional[str]* - Fabric name to filter by (optional).
    - `brand_id`: *Optional[int]* - Brand ID to filter by (optional).
    - `afterbuy_id`: *Optional[str]* - Afterbuy ID to filter by (optional).

    **Validation**:
    - At least one field must be provided for the search operation.

    **Usage**: Used in `find` and `filter` operations to specify search criteria.
    """
    id: Optional[int] = None
    name: Optional[str] = None
    brand_id: Optional[int] = None
    afterbuy_id: Optional[str] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """
        **Description**: Validates that at least one field is provided.

        **Raises**:
        - `ValueError`: If all fields are None.

        **Returns**:
        - *self*: The validated instance.
        """
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self