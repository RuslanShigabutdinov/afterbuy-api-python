from dataclasses import dataclass

@dataclass
class BrandEntity:
    """
    **Description**: Represents a brand entity for creation.

    **Fields**:
    - `name`: *str* - Name of the brand (must be unique and 1 to 10 characters).

    **Usage**: Used as input for creating a new brand.
    """
    name: str