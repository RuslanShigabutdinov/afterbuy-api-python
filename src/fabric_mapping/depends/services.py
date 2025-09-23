from fastapi import Depends
from typing import Annotated

from src.fabric_mapping.service import FabricMappingService

IFabricMappingService = Annotated[FabricMappingService, Depends()]
"""
**Description**: Type Alias for dependency injection of the Fabric Mapping Service.

**Usage**: Use this type hint in function signatures (e.g., in API routers)
           where an instance of `FabricMappingService` is required. FastAPI takes care
           of creating the service instance and injecting its required dependencies (like the repository).

           Example:
           ```python
           from fastapi import APIRouter, status
           from .services import IFabricMappingService
           from ..dto import CreateFabricMappingDTO

           router = APIRouter()

           @router.post("/", status_code=status.HTTP_201_CREATED)
           async def create_mapping(
               dto: CreateFabricMappingDTO,
               service: IFabricMappingService
           ):
               return await service.create(dto)
           ```
"""