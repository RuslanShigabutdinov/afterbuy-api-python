from src.libs.exceptions import NotFoundException


class FabricMappingNotFoundException(NotFoundException):
    """
    **Description**: Custom exception raised when a specific Fabric Mapping record cannot be found.

    **Inheritance**:
    - `NotFoundException`: Base exception for 'not found' scenarios.

    **Usage**: Raised by the repository or service layer when an operation targets
               a non-existent Fabric Mapping primary key (`id`).
    """
    pass