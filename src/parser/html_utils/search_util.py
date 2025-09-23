from math import ceil
from typing import List, Tuple
from lxml import html

from src.fabric.dto import FindFabricDTO
from src.parser.exceptions import ParsingError
from src.config.afterbuy import settings

class SearchHtmlUtil:
    """
    **Description**: Utility class for parsing HTML content of search results pages.

    **Attributes**:
    - `per_page`: *int* - The number of items displayed per page in search results.

    **Methods**:
    - `fetch_title`: Extracts the page title.
    - `fetch_page_count`: Extracts pagination information (offsets and total item count).
    - `fetch_fabrics`: Extracts fabric information from a dropdown.
    - `fetch_product_links`: Extracts product detail page links.

    **Usage**: Used by the SearchUtil (http_utils) to parse fetched search pages.
    """
    per_page: int = settings.parsing_per_page

    @staticmethod
    def fetch_title(html_content: str) -> str:
        """
        **Description**: Extracts the page title from HTML content.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *str* - The stripped title text.

        **Exceptions**:
        - `ParsingError`: If no title element is found.

        **How It Works**:
        - Parses the HTML to find the `<title>` element.
        - Extracts and returns the text content, stripped of whitespace.
        - Raises ParsingError if no title is found.
        """
        tree = html.fromstring(html_content)
        title_elements = tree.xpath("//title/text()")
        if not title_elements:
            raise ParsingError("No <title> element found in HTML content")
        return title_elements[0].strip()


    @staticmethod
    def fetch_page_count(html_content: str) -> Tuple[List[int], int]:
        """
        **Description**: Extract the offset (pages start positions) and total items count
        from search page HTML.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *Tuple[List[int], int]* - A tuple containing:
            - A list of integer offsets (start positions for each page).
            - The total number of items found.

        **Exceptions**:
        - `ParsingError`: If the total items count element or its value cannot be found or parsed.

        **How It Works**:
        - Parses the HTML to find the element containing the total item count text.
        - Extracts the total count from the text.
        - Calculates the number of pages and generates a list of offsets based on items per page.
        - Raises ParsingError if the count cannot be found or parsed.
        """
        tree = html.fromstring(html_content)
        total_items_text_list = tree.xpath("//*[@id='totalItemsCount']/text()")
        total_items_text = total_items_text_list[0] if total_items_text_list else None

        if total_items_text is None:
            raise ParsingError("Total items count element not found on the search page.")

        try:
            total_items: int = int(total_items_text.split()[1])
        except (IndexError, ValueError):
            raise ParsingError(f"Could not parse integer total items count from text: '{total_items_text}'")

        # Calculate offsets: 0, per_page, 2*per_page, ... up to total_items
        offsets: List[int] = [i * SearchHtmlUtil.per_page for i in range(ceil(total_items / SearchHtmlUtil.per_page))]
        return offsets, total_items

    @staticmethod
    def fetch_fabrics(html_content: str) -> List[FindFabricDTO]:
        """
        **Description**: Extracts fabric information from a dropdown list on the search page HTML.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *List[FindFabricDTO]* - A list of FindFabricDTOs, each representing a fabric.
                                 Returns an empty list if the dropdown is not found or has no options.

        **How It Works**:
        - Parses the HTML to find the select element with `name='lAWKollektion'`.
        - Iterates through the option elements within the select.
        - Extracts the 'value' (afterbuy_id) and text (name) for each option.
        - Creates a FindFabricDTO for each valid option and adds it to a list.
        - Returns the list of fabric DTOs.
        """
        fabric_list: List[FindFabricDTO] = []
        tree = html.fromstring(html_content)
        select_list = tree.xpath("//select[@name='lAWKollektion']")
        select = select_list[0] if select_list else None

        if select is None:
            return fabric_list

        options = select.xpath(".//option")
        for option in options:
            idx = option.get("value")
            text = option.text
            # Only include options with both value and text
            if idx is not None and text is not None and text.strip():
                fabric_list.append(FindFabricDTO(
                    name=text.strip(),
                    afterbuy_id=idx,
                ))

        return fabric_list

    @staticmethod
    def fetch_product_links(html_content: str) -> List[str]:
        """
        **Description**: Extracts product links from search results HTML.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *List[str]* - A list of relative URL strings for product detail pages.

        **How It Works**:
        - Parses the HTML to find elements with `title='Artikel bearbeiten'` (edit article).
        - Assumes the parent element of these is an anchor (`<a>`) tag containing the link.
        - Extracts the 'href' attribute from the parent element.
        - Returns a list of the extracted hrefs.
        """
        tree = html.fromstring(html_content)
        elements = tree.xpath("//*[@title='Artikel bearbeiten']")
        product_links = []

        for element in elements:
            parent = element.getparent()
            if parent is not None:
                href = parent.get("href")
                if href is not None:
                    product_links.append(href)

        return product_links