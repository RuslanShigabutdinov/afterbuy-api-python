from typing import Annotated
from fastapi import Depends

from src.product.repositories.product import ProductsRepository


IProductsRepository = Annotated[ProductsRepository, Depends()]
"""
**Description**: Type hint for dependency injection of the ProductsRepository.

**Usage**: Provides an instance of `ProductsRepository` to dependent components (e.g., ProductService).
"""