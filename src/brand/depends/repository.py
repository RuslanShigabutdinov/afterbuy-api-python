from typing import Annotated
from fastapi import Depends

from src.brand.repositories.brand import BrandRepository

IBrandRepository = Annotated[BrandRepository, Depends()]
"""
**Description**: Dependency injection type hint for `BrandRepository`.

**Usage**: Used in `BrandService` to inject an instance of `BrandRepository` automatically.
"""