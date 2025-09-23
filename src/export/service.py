
import pandas as pd

from io import BytesIO

from typing import Optional

from src.product.depends.service import IProductService
from src.product.dto import FilterProductsDTO

class ExportService:
    def __init__(self, product_service: IProductService):
        self.product_service = product_service

    async def export_products(self, dto: FilterProductsDTO, limit: Optional[int] = None, offset: Optional[int] = None) -> BytesIO:
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
        products = await self.product_service.filter(dto, limit, offset)

        products_dict = [product.model_dump() for product in products]

        dataframe = pd.DataFrame(products_dict)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, sheet_name='Products', index=False)

        output.seek(0)

        return output