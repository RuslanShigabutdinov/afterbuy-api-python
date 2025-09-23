from typing import Annotated
from fastapi import Depends

from src.url.repositories.url import UrlsRepository

IUrlsRepository = Annotated[UrlsRepository, Depends()]
"""
**Description**: Type hint for dependency injection of the UrlsRepository.

**Usage**: Provides an instance of `UrlsRepository` to dependent components (e.g., UrlService).
"""