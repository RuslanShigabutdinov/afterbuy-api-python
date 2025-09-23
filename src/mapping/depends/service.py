from fastapi import Depends
from typing import Annotated

from src.mapping.service import MappingService

IMappingService = Annotated[MappingService, Depends()]