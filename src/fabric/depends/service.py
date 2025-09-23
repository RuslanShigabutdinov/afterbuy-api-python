from typing import Annotated
from fastapi import Depends

from src.fabric.service import FabricService

IFabricService = Annotated[FabricService, Depends()]
"""
**Description**: Type hint for dependency injection of the FabricService.

**Usage**: Provides an instance of `FabricService` to dependent components (e.g., API routes).
"""