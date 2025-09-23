from typing import Optional
from pydantic import BaseModel, model_validator

class ProductsMappingDTO(BaseModel):
    """
    **Description**: Represents a product mapping’s data for transfer and display.

    **Fields**:
    - `id`: *int* - Unique identifier of the mapping.
    - `fabric_mapping_id`: *Optional[int]* - ID referencing a fabric mapping.
    - `jv_product_id`: *Optional[int]* - ID referencing a JV product.
    - `xl_product_id`: *Optional[int]* - ID referencing an XL product.

    **Usage**: Used to serialize product mapping data for API responses.
    """
    id: int
    fabric_mapping_id: Optional[int] = None
    jv_product_id: Optional[int] = None
    xl_product_id: Optional[int] = None


class CreateProductsMappingDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for creating a new product mapping.

    **Fields**:
    - `fabric_mapping_id`: *Optional[int]* - ID referencing a fabric mapping.
    - `jv_product_id`: *Optional[int]* - ID referencing a JV product.
    - `xl_product_id`: *Optional[int]* - ID referencing an XL product.

    **Validation**:
    - At least one field (`fabric_mapping_id`, `jv_product_id`, or `xl_product_id`) must be provided.

    **Usage**: Passed to the create endpoint to add a new product mapping.
    """
    fabric_mapping_id: Optional[int] = None
    jv_product_id: Optional[int] = None
    xl_product_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one mapping field (fabric_mapping_id, jv_product_id, or xl_product_id) must be provided.')
        return self


class UpdateProductsMappingDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for updating an existing product mapping record.

    **Fields**:
    - `fabric_mapping_id`: *Optional[int]* - New fabric mapping ID.
    - `jv_product_id`: *Optional[int]* - New JV product ID.
    - `xl_product_id`: *Optional[int]* - New XL product ID.

    **Validation**:
    - At least one field (`fabric_mapping_id`, `jv_product_id`, or `xl_product_id`) must be provided for update.

    **Usage**: Passed to the update endpoint to modify a product mapping.
    """
    fabric_mapping_id: Optional[int] = None
    jv_product_id: Optional[int] = None
    xl_product_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided for update.')
        return self

class FindProductsMappingDTO(BaseModel):
    """
    **Description**: Data Transfer Object (DTO) for finding or filtering product mappings.

    **Fields**:
    - `id`: *Optional[int]* - Optional mapping ID for filtering.
    - `fabric_mapping_id`: *Optional[int]* - Optional fabric mapping ID for filtering.
    - `jv_product_id`: *Optional[int]* - Optional JV product ID for filtering.
    - `xl_product_id`: *Optional[int]* - Optional XL product ID for filtering.

    **Validation**:
    - At least one field (`id`, `fabric_mapping_id`, `jv_product_id`, or `xl_product_id`) must be provided.

    **Usage**: Used in `find` and `filter` operations to specify search criteria.
    """
    id: Optional[int] = None
    fabric_mapping_id: Optional[int] = None
    jv_product_id: Optional[int] = None
    xl_product_id: Optional[int] = None

    @model_validator(mode='after')
    def check_at_least_one_value(self):
        """Ensure at least one field is not None."""
        if not any(v is not None for v in self.__dict__.values()):
            raise ValueError('At least one field must be provided for filtering.')
        return self