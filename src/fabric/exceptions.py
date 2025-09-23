from src.libs.exceptions import NotFoundException, SeveralAnswersFoundException

class FabricNotFound(NotFoundException):
    """
    **Description**: Exception raised when a fabric is not found in the system.

    **Cause**: Triggered when a fabric cannot be located by ID or search criteria.

    **Usage**: Used in operations like `get`, `update`, `find`, and `delete`.
    """
    pass

class FabricIsNotUnique(SeveralAnswersFoundException):
    """
    **Description**: Exception raised when multiple fabrics match the search criteria.

    **Cause**: Triggered when the `find` operation returns more than one result.

    **Usage**: Used in the `find` operation to enforce uniqueness of results.
    """
    pass