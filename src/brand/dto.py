from pydantic import BaseModel, constr, model_validator
from typing import Optional

class BrandDTO(BaseModel):
    """
    **Description**: Represents a brand’s data for transfer and display.

    **Fields**:
    - `id`: *int* - Unique identifier of the brand.
    - `name`: *str* - Name of the brand (1 to 10 characters).

    **Usage**: Used to serialize brand data for API responses.
    """
    id: int
    name: constr(max_length=10, min_length=1)

class UpdateBrandDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for updating a brand’s name.

    **Fields**:
    - `name`: *str* - New name for the brand (1 to 10 characters).

    **Usage**: Passed to the update endpoint to modify a brand’s name.
    """
    name: constr(max_length=10, min_length=1)

class FindBrandDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for finding or filtering brands.

    **Fields**:
    - `id`: *Optional[int]* - Optional brand ID for filtering.
    - `name`: *Optional[str]* - Optional brand name for filtering (1 to 10 characters).

    **Validation**:
    - At least one field (`id` or `name`) must be provided.

    **Usage**: Used in `find` and `filter` operations to specify search criteria.
    """
    id: Optional[int] = None
    name: Optional[constr(max_length=10, min_length=1)] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided.')
        return self