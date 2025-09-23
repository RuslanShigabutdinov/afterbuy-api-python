from fastapi import Depends
from typing import Annotated

from src.product_mapping.repositories.product_mapping import ProductsMappingRepository

IProductMappingRepository = Annotated[ProductsMappingRepository, Depends()]
"""
**Description**: Dependency injection type hint for `ProductsMappingRepository`.

**Usage**: Used in `ProductMappingService` to inject an instance of `ProductsMappingRepository` automatically.
"""