from typing import Annotated
from fastapi import Depends

from src.brand.service import BrandService

IBrandService = Annotated[BrandService, Depends()]
"""
**Description**: Dependency injection type hint for `BrandService`.

**Usage**: Used in API routes to inject an instance of `BrandService` automatically.
"""