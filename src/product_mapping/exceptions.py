from src.libs.exceptions import NotFoundException, SeveralAnswersFoundException, AlreadyExistError as LibAlreadyExistError

class ProductMappingNotFound(NotFoundException):
    """
    **Description**: Raised when a product mapping is not found.

    **Cause**: Triggered if no mapping matches the provided ID or search criteria.

    **Usage**: Used in `get`, `update`, `find`, and `delete` operations.
    """
    pass

class ProductMappingIsNotUnique(SeveralAnswersFoundException):
    """
    **Description**: Raised when multiple product mappings match the search criteria for a single result.

    **Cause**: Occurs if the `find` operation returns more than one result.

    **Usage**: Thrown in the `find` operation to enforce uniqueness.
    """
    pass

class ProductMappingAlreadyExists(LibAlreadyExistError):
    """
    **Description**: Raised when a product mapping with the same unique constraints already exists.

    **Cause**: Occurs during creation if a mapping with the same product IDs or fabric mapping ID already exists.

    **Usage**: Used in `create` and potentially `update` operations.
    """
    pass