from fastapi import Depends
from typing import Annotated

from src.export.service import ExportService


IExportService = Annotated[ExportService, Depends()]