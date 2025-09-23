from fastapi import Depends
from typing import Annotated

from src.product_mapping.service import ProductMappingService

IProductMappingService = Annotated[ProductMappingService, Depends()]
"""
**Description**: Dependency injection type hint for `ProductMappingService`.

**Usage**: Used in API routes to inject an instance of `ProductMappingService` automatically.
"""