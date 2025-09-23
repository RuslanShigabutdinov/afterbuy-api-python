from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.export.depends.service import IExportService, ExportService
from src.fabric.dto import FabricDTO
from src.product.dto import FilterProductsDTO
from src.protection import RequireUserToken

from datetime import datetime

router = APIRouter(prefix="/export", tags=["Export"], dependencies=[RequireUserToken])

@router.post("/products")
async def export_products(
    service: IExportService,
    dto: FilterProductsDTO,
    limit: Optional[int] = Query(100, ge=0, le=10_000),
    offset: Optional[int] = Query(None, ge=0),
):
    """
    **Description**: Filters products based on criteria with optional pagination and returns Excel file.

    **Parameters**:
    - `dto`: *FilterProductsDTO* - Search criteria for filtering products.
    - `limit`: *Optional[int]* - Maximum number of products to return.
    - `offset`: *Optional[int]* - Number of products to skip for pagination.

    **Returns**:
    - *Excel file*: List of matching products.

    **Raises**:
    - `PaginationError`: If limit or offset is negative.

    **Usage**: Retrieves a filtered list of products from the repository in Excel.
    """
    service: ExportService
    file: BytesIO = await service.export_products(dto, limit, offset)
    filename = f"products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"
    return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={filename}"})