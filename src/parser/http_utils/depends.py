from fastapi import Depends
from typing import Annotated

from src.parser.parser.fabrics import FabricParserService
from src.parser.parser.product import ProductParserService

IFabricParserService = Annotated[FabricParserService, Depends()]
IProductParserService = Annotated[ProductParserService, Depends()]
"""
**Description**: Dependency injection type hints for parser sub-services.

**Usage**: Used to inject instances of FabricParserService and ProductParserService.
"""