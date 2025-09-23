from typing import Annotated
from fastapi import Depends

from src.product.service import ProductService


IProductService = Annotated[ProductService, Depends()]
"""
**Description**: Type hint for dependency injection of the ProductService.

**Usage**: Provides an instance of `ProductService` to dependent components (e.g., API routes).
"""
