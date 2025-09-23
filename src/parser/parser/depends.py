from fastapi import Depends
from typing import Annotated

from src.parser.parser.fabrics import FabricParserService
from src.parser.parser.product import ProductParserService

IFabricParserService = Annotated[FabricParserService, Depends()]
IProductParserService = Annotated[ProductParserService, Depends()]