# C:\Users\office\Desktop\AfterbuyBot\src\parser\parser\fabrics.py
from typing import List

from src.fabric.dto import FindFabricDTO
from src.parser.http_utils.search import SearchUtil
from src.parser.http_utils.login import LoginClient
from src.parser.exceptions import LoginFailedError # Assuming LoginFailedError exists

class FabricParserService:
    """
    **Description**: Sub-service responsible for parsing fabric information from the external source.

    **Methods**:
    - `get_fabrics`: Fetches a list of available fabrics for a given brand by interacting with the search interface.

    **Usage**: Used by the main ParserService to retrieve fabric data.
    """
    @staticmethod
    async def get_fabrics(brand_id: int) -> List[FindFabricDTO]:
        """
        **Description**: Fetches a list of fabrics for a specific brand from the external service's search page.

        **Input**:
        - `brand_id`: *int* - The ID of the brand to fetch fabrics for.

        **Output**:
        - *List[FindFabricDTO]* - A list of FindFabricDTOs representing the available fabrics.

        **Exceptions**:
        - `LoginFailedError`: If authentication with the external service fails.
        - Exceptions from `SearchUtil.get_fabrics` or underlying HTTP/parsing operations will bubble up.

        **How It Works**:
        - Initializes a `LoginClient` for the specified brand using an async context manager.
        - Initializes a `SearchUtil` with the authenticated client.
        - Calls `search_util.get_fabrics` to retrieve fabric data from the search page HTML.
        - Returns the list of fabric DTOs.
        """
        async with LoginClient(brand_id) as client:
            search_util = SearchUtil(client)
            return await search_util.get_fabrics()