from src.libs.exceptions import NotFoundException, SeveralAnswersFoundException

class BrandNotFound(NotFoundException):
    """
    **Description**: Raised when a brand is not found.

    **Cause**: Triggered if no brand matches the provided ID or search criteria.

    **Usage**: Used in `get`, `update`, `find`, and `delete` operations.
    """
    pass

class BrandIsNotUnique(SeveralAnswersFoundException):
    """
    **Description**: Raised when multiple brands match the search criteria.

    **Cause**: Occurs if the `find` operation returns more than one result.

    **Usage**: Thrown in the `find` operation to enforce uniqueness.
    """
    pass