from src.libs.exceptions import NotFoundException, AlreadyExistError


class ProductNotFoundException(NotFoundException):
    """
    **Description**: Raised when a product is not found.

    **Cause**: Triggered if no product matches the provided ID or search criteria.

    **Usage**: Used in `get`, `update`, `find` operations.
    """
    pass

class ProductAlreadyExists(AlreadyExistError):
    """
    **Description**: Raised when a product is already registered.

    **Cause**: Triggered if product not founded.

    **Usage**: Used in `create` operations.
    """

