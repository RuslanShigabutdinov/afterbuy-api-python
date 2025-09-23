import asyncio
import logging
from typing import Optional, Dict, Any

from src.parser.html_utils.product_util import ProductHtmlUtil
from src.parser.http_utils.login import LoginClient
from src.product.dto import ProductDTO
from src.parser.exceptions import ParsingError, LoginFailedError

class ProductUtil:
    """
    **Description**: Utility class for fetching and parsing product data from individual
    product detail pages using an authenticated HTTP client.

    **Attributes**:
    - `http_client`: *LoginClient* - An authenticated HTTP client instance.
    - `product_html_util`: *ProductHtmlUtil* - Utility for parsing product HTML.
    - `ebay_url`: *str* - Base URL for eBay listings.
    - `pagination_url`: *str* - URL pattern for paginated listings.
    - `logger`: *logging.Logger* - Logger instance for this utility.

    **Methods**:
    - `fetch_add_data`: Fetches additional product data via an API endpoint.
    - `parse_main_data`: Fetches and parses main product data from an HTML link.
    - `parse_item`: Orchestrates fetching and parsing both main and additional product data.

    **Usage**: Used by the ProductParserService to get detailed product information.
    """
    def __init__(self, http_client: LoginClient, product_html_util: Optional[ProductHtmlUtil] = None) -> None:
        """
        **Description**: Initialize the ProductUtil with an HTTP client and optional HTML utility.

        **Input**:
        - `http_client`: *LoginClient* - The LoginClient instance for HTTP requests.
        - `product_html_util`: *Optional[ProductHtmlUtil]* - Optional ProductHtmlUtil instance; defaults to a new instance if None.

        **How It Works**:
        - Stores the provided HTTP client and HTML utility (creating a default one if not provided).
        - Constructs base URLs for eBay listings and pagination.
        - Initializes a logger.
        """
        self.http_client: LoginClient = http_client
        # Create a new instance if None is explicitly passed or if no argument is given
        self.product_html_util: ProductHtmlUtil = product_html_util if product_html_util is not None else ProductHtmlUtil()
        self.ebay_url: str = self.http_client.base_url + "/afterbuy/ebayliste2.aspx"
        self.pagination_url: str = self.ebay_url + "?jump=2&rsposition={offset}" # This seems unused here, but keep as it was in original
        self.logger: logging.Logger = logging.getLogger(__name__)

    async def fetch_add_data(self, product: ProductDTO) -> ProductDTO:
        """
        **Description**: Fetch additional product data from a JSON API endpoint and update the ProductDTO.

        **Input**:
        - `product`: *ProductDTO* - The ProductDTO to enrich with additional data.

        **Output**:
        - *ProductDTO* - The updated ProductDTO.

        **Exceptions**:
        - Exceptions from delegated HTTP requests (`HttpClient.json_request`) will bubble up.
        - `KeyError`, `TypeError`, `IndexError`, `AttributeError`: If the JSON response structure is unexpected. These will bubble up.

        **How It Works**:
        - Constructs the URL and parameters for the product details API endpoint using the product's `product_num`.
        - Sends a JSON GET request to the API.
        - Attempts to extract relevant data (EAN, HTML description) from the nested JSON structure.
        - Updates the provided ProductDTO instance with the fetched data.
        - Returns the updated ProductDTO.
        """
        if not product.product_num:
             self.logger.warning("Cannot fetch additional data: product_num is missing.")
             return product # Return product as is if no product_num

        details_url: str = self.http_client.base_url + "/afterbuy/Services/Products/index.aspx"
        # Ensure product_num is an integer for the parameter if required by the API
        try:
            product_num_int = int(product.product_num.strip())
        except (ValueError, AttributeError):
             self.logger.warning(f"Invalid product_num for fetching additional data: {product.product_num}")
             return product # Return product as is if product_num is not a valid integer

        params: Dict[str, int] = {"ProductId": product_num_int, "pac": 0}

        # Exceptions from json_request (like connection errors, bad response status) will bubble up
        data: Dict[str, Any] = await self.http_client.json_request(
            "GET", details_url, params=params
        )

        # Access nested data safely; exceptions like KeyError, IndexError will bubble up
        product_data: Dict[str, Any] = data.get("ReadAllResponse", {}).get("ProductDetails", [{}])[0]

        # Assuming ProductDTO has these attributes and they accept str | None
        # Use .get() with a default of None for robustness against missing keys
        product.ean = product_data.get("ManufacturerPartNumber")
        product.html_description = product_data.get("Beschreibung")

        return product

    async def parse_main_data(self, link: str) -> ProductDTO:
        """
        **Description**: Fetches and parses the main product data from an HTML page link.
        Includes a retry mechanism with relogin if initial parsing fails critically.

        **Input**:
        - `link`: *str* - The relative or full URL to the product detail page.

        **Output**:
        - *ProductDTO* - A ProductDTO with parsed main data, including the original link.

        **Exceptions**:
        - `ParsingError`: If the initial HTML parsing fails critically (e.g., main table not found).
        - `LoginFailedError`: If the relogin attempt fails.
        - Exceptions from delegated HTTP requests (`HttpClient.html_request`) will bubble up.
        - Any exception raised by `self.product_html_util.parse_item_html`.

        **How It Works**:
        - Fetches the HTML content of the product link.
        - Parses the HTML using `product_html_util.parse_item_html`.
        - If `parse_item_html` raises `ParsingError` related to critical missing data (like main table),
          it attempts to relogin and retry the HTML fetch and parsing once.
        - Appends the original link to the parsed ProductDTO.
        - Returns the parsed ProductDTO.
        """
        url: str = link

        html_content: str = await self.http_client.html_request("GET", url)

        try:
            product: ProductDTO = await asyncio.to_thread(self.product_html_util.parse_item_html, html_content)
        except ParsingError as e:
             self.logger.warning(f"Parsing failed for {url}: {e}. Attempting relogin and retry.")
             try:
                 await self.http_client.login()
                 html_content = await self.http_client.html_request("GET", url)
                 product = await asyncio.to_thread(self.product_html_util.parse_item_html, html_content)
             except (LoginFailedError, ParsingError, Exception) as retry_e:
                  self.logger.error(f"Retry parsing failed for {url} after relogin: {retry_e}")
                  raise retry_e


        product.link = link
        return product

    async def parse_item(self, link: str) -> ProductDTO:
        """
        **Description**: Parses a product item from its link, including main HTML data
        and additional data fetched via API.

        **Input**:
        - `link`: *str* - The relative URL path to the product page.

        **Output**:
        - *ProductDTO* - A fully parsed ProductDTO.

        **Exceptions**:
        - Exceptions from `parse_main_data` or `fetch_add_data` will bubble up.

        **How It Works**:
        - Calls `parse_main_data` to get initial product information from HTML.
        - Calls `fetch_add_data` to enrich the ProductDTO with additional details from an API.
        - Logs completion for the item.
        - Returns the complete ProductDTO.
        """
        product: ProductDTO = await self.parse_main_data(link)
        self.logger.info(f"Successfully parsed main data for {link}!")
        # fetch_add_data handles cases where product.product_num might be None
        product = await self.fetch_add_data(product)
        self.logger.info(f"Successfully parsed all data for {link}!")
        return product