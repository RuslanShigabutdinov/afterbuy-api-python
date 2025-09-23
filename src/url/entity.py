from typing import Optional
from pydantic import BaseModel

class UrlEntity(BaseModel):
    """
    **Description**: Represents a URL entity for creation or internal processing.

    **Fields**:
    - `url`: *str* - The URL string.
    - `brand_id`: *Optional[int]* - Identifier of the brand, if applicable.
    - `fab_id`: *Optional[int]* - Identifier of the fabric, if applicable.

    **Usage**: Used as input for creating or processing URLs in the service layer.
    """
    url: str
    brand_id: Optional[int] = None
    fab_id: Optional[int] = None