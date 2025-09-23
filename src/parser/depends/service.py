from fastapi import Depends
from typing import Annotated

from src.parser.service import ParserService

IParserService = Annotated[ParserService, Depends()]
"""
**Description**: Dependency injection type hint for `ParserService`.

**Usage**: Used in API routes or other services to inject an instance of `ParserService` automatically.
"""