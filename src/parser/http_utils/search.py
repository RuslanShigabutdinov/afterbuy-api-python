import asyncio
import logging
from typing import Any, Awaitable, List, Dict, Optional

from src.parser.http_utils.login import LoginClient
from src.parser.html_utils.search_util import SearchHtmlUtil
from src.fabric.dto import FindFabricDTO, FabricDTO


class SearchUtil:
    """
    **Description**: Utility class for interacting with the Afterbuy search interface
    to find fabrics and retrieve product links, handling pagination.

    **Attributes**:
    - `login_client`: *LoginClient* - An authenticated HTTP client instance.
    - `search_html_util`: *SearchHtmlUtil* - Utility for parsing search results HTML.
    - `ebay_url`: *str* - Base URL for eBay listings search.
    - `pagination_url`: *str* - URL pattern for accessing specific pages of search results.
    - `pagination_params`: *Dict[str, Any]* - Base parameters for search requests.
    - `search_batch_size`: *int* - Number of search pages to fetch concurrently.

    **Methods**:
    - `get_fabrics`: Fetches the list of available fabrics from the search page.
    - `set_pagination`: Configures search parameters for a specific fabric and determines pagination offsets.
    - `get_products_links`: Fetches HTML content for all pages of search results for a fabric and extracts product links.

    **Usage**: Used by the FabricParserService and ProductParserService to interact with search results.
    """

    # Base parameters for search requests
    pagination_params: Dict[str, Any] = {
        "art": "SetAuswahl",
        "lAWSuchwort": "",
        "lAWFilter": 0,
        "lAWFilter2": 0,
        "I_Stammartikel": "",
        "siteIDsuche": -1,
        "lAWartikelnummer": "",
        "lAWKollektion": "COLLECTION_VALUE", # Placeholder for fabric Afterbuy ID
        "lAWKollektion1": -1,
        "lAWKollektion2": -1,
        "lAWKollektion3": -1,
        "lAWKollektion4": -1,
        "lAWKollektion5": -1,
        "lAWean": "",
        "Vorlage": "",
        "Vorlageart": 0,
        "lAWebaykat": "",
        "lAWshopcat1": -1,
        "lAWshopcat2": -1,
        "lawmaxart": 500, # Max items per page
        "maxgesamt": 0, # Total items found (set after first request)
        "BlockingReason": "",
        "DispatchTimeMax": -1,
        "listerId": "",
        "ebayLister_DynamicPriceRules": -100,
        "lAWSellerPaymentProfile": 0,
        "lAWSellerReturnPolicyProfile": 0,
        "lAWSellerShippingProfile": 0
    }

    search_batch_size: int = 5 # Default number of pages to fetch concurrently

    def __init__(
        self,
        login_client: LoginClient,
        search_html_util: Optional[SearchHtmlUtil] = None # Use Optional with None default
    ) -> None:
        """
        **Description**: Initializes a SearchUtil instance.

        **Input**:
        - `login_client`: *LoginClient* - A LoginClient instance for authenticated requests.
        - `search_html_util`: *Optional[SearchHtmlUtil]* - An optional SearchHtmlUtil for parsing search results; defaults to a new instance if None.

        **How It Works**:
        - Stores the provided LoginClient.
        - Initializes the SearchHtmlUtil (using provided instance or creating a new one).
        - Constructs the base URLs for search and pagination.
        """
        self.login_client: LoginClient = login_client
        # Create a new instance if None is explicitly passed or if no argument is given
        self.search_html_util: SearchHtmlUtil = search_html_util if search_html_util is not None else SearchHtmlUtil()
        # Base Afterbuy eBay-lister endpoint
        self.ebay_url: str = f"{self.login_client.base_url}/afterbuy/ebayliste2.aspx"
        # URL for paginated listings - format string for offset
        self.pagination_url: str = self.ebay_url + "?jump=2&rsposition={offset}"


    async def get_fabrics(self) -> List[FindFabricDTO]:
        """
        **Description**: Fetch a list of available fabrics from the main search page's dropdown.

        **Output**:
        - *List[FindFabricDTO]* - A list of FindFabricDTO objects retrieved from the HTML.
                                 Returns an empty list if the fabric dropdown is not found or empty.

        **Exceptions**:
        - Exceptions from delegated HTTP requests (`HttpClient.html_request`) or HTML parsing (`SearchHtmlUtil.fetch_fabrics`)
          will bubble up.

        **How It Works**:
        - Fetches the initial search page HTML.
        - Uses `search_html_util.fetch_fabrics` to parse the HTML and extract fabric data.
        - Returns the list of fabric DTOs.
        """
        # Exceptions from html_request or fetch_fabrics will bubble up
        search_page: str = await self.login_client.html_request("GET", self.ebay_url)
        search_collections: List[FindFabricDTO] = self.search_html_util.fetch_fabrics(search_page)
        return search_collections

    async def set_pagination(self, fabric: FabricDTO) -> list[int]:
        """
        **Description**: Configures search parameters for a given fabric, sends an initial
        search request to determine total items and pagination offsets.

        **Input**:
        - `fabric`: *FabricDTO* - A FabricDTO instance, containing the Afterbuy ID (`afterbuy_id`).

        **Output**:
        - *list[int]* - A list of integer offsets (start positions) for iterating through paginated search results for this fabric.

        **Exceptions**:
        - `ParsingError`: If the total items count cannot be extracted from the search page HTML.
        - Exceptions from delegated HTTP requests (`HttpClient.html_request`) will bubble up.

        **How It Works**:
        - Creates a copy of the base `pagination_params`.
        - Sets the `lAWKollektion` parameter to the fabric's `afterbuy_id`.
        - Sends a GET request to the search URL with the fabric-specific parameters.
        - Uses `search_html_util.fetch_page_count` to parse the response and get offsets and total item count.
        - Sets the `maxgesamt` parameter in the search parameters to the total item count (this might be a requirement of the external service's pagination).
        - Sends another GET request with the updated `maxgesamt` parameter to likely finalize the pagination setup on the server side.
        - Returns the list of calculated offsets.
        """
        logging.info("Setting search parameters for fabric: %s", fabric.name)

        params: Dict[str, Any] = self.pagination_params.copy()
        params["lAWKollektion"] = fabric.afterbuy_id

        # Step 1: First request to discover how many items there are and get offsets
        search_page_initial: str = await self.login_client.html_request("GET", self.ebay_url, params=params)
        # ParsingError is raised by fetch_page_count if parsing fails
        offsets, total_items = self.search_html_util.fetch_page_count(search_page_initial)

        logging.info("Fabric '%s' (Afterbuy ID: %s) has %d total items across %d pages.",
                     fabric.name, fabric.afterbuy_id, total_items, len(offsets))

        # Step 2: Set max items in parameters and potentially send another request
        # This second request might be necessary for the external system to correctly
        # handle subsequent paginated requests.
        params["maxgesamt"] = total_items
        await self.login_client.html_request("GET", self.ebay_url, params=params)

        return offsets

    async def get_products_links(self, fabric: FabricDTO) -> list[str]:
        """
        **Description**: Retrieves product links for a specific fabric by fetching HTML content
        from all paginated search results pages.

        **Input**:
        - `fabric`: *FabricDTO* - A FabricDTO instance representing the fabric to look up.

        **Output**:
        - *list[str]* - A list of relative URL strings, each corresponding to a product's detail page.

        **Exceptions**:
        - Exceptions from `set_pagination`, delegated HTTP requests (`HttpClient.html_request`),
          or HTML parsing (`SearchHtmlUtil.fetch_product_links`) will bubble up.

        **How It Works**:
        - Calls `set_pagination` to configure search parameters and get the list of page offsets.
        - Creates a list of asynchronous tasks to fetch the HTML content for each page offset.
        - Fetches the pages concurrently in batches.
        - Iterates through the fetched HTML content for each page.
        - Uses `search_html_util.fetch_product_links` to extract all product links from each page's HTML.
        - Returns a flattened list of all extracted product links.
        """
        # Exceptions from set_pagination will bubble up
        offsets: list[int] = await self.set_pagination(fabric)

        # If no offsets (0 total items), return empty list immediately
        if not offsets:
             logging.info("No offsets found for fabric %s, returning empty product links list.", fabric.name)
             return []

        logging.info("Gathering search pages for fabric: %s", fabric.name)

        tasks: list[Awaitable[str]] = []
        # Prepare requests for each page offset
        for offset in offsets:
            url: str = self.pagination_url.format(offset=offset)
            tasks.append(self.login_client.html_request("GET", url))

        # Fetch pages concurrently in batches
        search_pages: list[str] = []
        # Exceptions from asyncio.gather (e.g., HTTP errors) will bubble up
        for i in range(0, len(tasks), self.search_batch_size):
            batch: list[Awaitable[str]] = tasks[i : i + self.search_batch_size]
            batch_results = await asyncio.gather(*batch)
            search_pages.extend(batch_results)

        logging.info("Extracting product links from collected pages for fabric %s.", fabric.name)

        products_links: list[str] = []
        # Exceptions from fetch_product_links will bubble up
        for html_content in search_pages:
            products_links.extend(self.search_html_util.fetch_product_links(html_content))

        logging.info("Found %d product links total for fabric %s.", len(products_links), fabric.name)

        return products_links
