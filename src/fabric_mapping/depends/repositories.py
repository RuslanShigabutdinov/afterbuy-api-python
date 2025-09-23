from fastapi import Depends
from typing import Annotated

from src.fabric_mapping.repositories.fabric_mapping import FabricMappingRepository

IFabricMappingsRepository = Annotated[FabricMappingRepository, Depends()]
"""
**Description**: Type Alias for dependency injection of the Fabric Mapping Repository.

**Usage**: Use this type hint in function signatures (e.g., in services or routers)
           where an instance of `FabricMappingRepository` is required. FastAPI will handle
           the instantiation and injection.

           Example:
           ```python
           from fastapi import APIRouter
           from .repositories import IFabricMappingsRepository

           router = APIRouter()

           @router.get("/")
           async def get_mappings(repo: IFabricMappingsRepository):
               return await repo.get_list()
           ```
"""