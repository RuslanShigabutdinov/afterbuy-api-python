from typing import Annotated
from fastapi import Depends

from src.url.service import UrlService

IUrlService = Annotated[UrlService, Depends()]
"""
**Description**: Type hint for dependency injection of the UrlService.

**Usage**: Provides an instance of `UrlService` to dependent components (e.g., API routes).
"""