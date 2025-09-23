from typing import Annotated
from fastapi import Depends

from src.fabric.repositories.fabric import FabricRepository

IFabricRepository = Annotated[FabricRepository, Depends()]
"""
**Description**: Type hint for dependency injection of the FabricRepository.

**Usage**: Provides an instance of `FabricRepository` to dependent components (e.g., `FabricService`).
"""