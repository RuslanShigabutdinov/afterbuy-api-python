from typing import Optional
from pydantic import BaseModel, model_validator

class UrlDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) representing a URL entry for transfer and display purposes.

    **Fields**:
    - `id`: *int* - Unique identifier of the URL.
    - `url`: *str* - The URL string, validated as a proper HTTP/HTTPS URL.
    - `brand_id`: *int* - Identifier of the brand associated with the URL.
    - `fabric_id`: *int* - Identifier of the fabric associated with the URL.

    **Usage**: Used to serialize URL data for API responses or input validation.
    """
    id: int
    url: str
    brand_id: int
    fabric_id: int

class UpdateUrlDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for updating existing URL entries.

    **Fields**:
    - `url`: *Optional[str]* - New URL string, if updating (validated as HTTP/HTTPS).
    - `brand_id`: *Optional[int]* - New brand identifier, if updating.
    - `fabric_id`: *Optional[int]* - New fabric identifier, if updating.

    **Validation**:
    - At least one field must be provided for the update operation.

    **Usage**: Passed to the update endpoint to modify URL details.
    """
    url: Optional[str] = None
    brand_id: Optional[int] = None
    fabric_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self

class FilterUrlsDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for filtering URL entries based on specified criteria.

    **Fields**:
    - `id`: *Optional[int]* - Filter by URL identifier.
    - `url`: *Optional[str]* - Filter by URL string (validated as HTTP/HTTPS).
    - `brand_id`: *Optional[int]* - Filter by brand identifier.
    - `fabric_id`: *Optional[int]* - Filter by fabric identifier.

    **Validation**:
    - At least one field must be provided for the filter operation.

    **Usage**: Used in `filter` operations to define search criteria for URLs.
    """
    id: Optional[int] = None
    url: Optional[str] = None
    brand_id: Optional[int] = None
    fabric_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self