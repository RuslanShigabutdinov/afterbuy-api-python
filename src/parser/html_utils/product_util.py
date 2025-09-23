import logging
from typing import Dict, List, Optional

from json import dumps

from lxml import html, etree
from lxml.etree import _Element as Element, XPath as CompiledXPath

from src.product.dto import ProductDTO
from src.parser.exceptions import ParsingError


logger = logging.getLogger(__name__)


class ProductHtmlUtil:
    """
    Utility class for parsing HTML content of product detail pages.
    It extracts product data into a ProductDTO, handling missing elements
    gracefully by defaulting fields to None or appropriate empty values.
    """
    # Compiled XPath expressions for performance and clarity
    _main_table_xpath: CompiledXPath = etree.XPath("//table[@class='mainTable']")
    _collection_select_xpath: CompiledXPath = etree.XPath(".//select[@name='Kollektion']//option[@selected]")
    _product_num_input_xpath: CompiledXPath = etree.XPath(".//input[@id='I_Stammartikelfield']")
    _price_input_xpath: CompiledXPath = etree.XPath(".//input[@name='Startpreis']")
    _properties_outer_div_xpath: CompiledXPath = etree.XPath(".//div[@id='id_CustomItemSpecifics']")
    _properties_inner_table_xpath: CompiledXPath = etree.XPath(".//table[@class='cbadonknow']")
    _properties_row_xpath: CompiledXPath = etree.XPath(".//tr")
    _prop_row_name_xpath: CompiledXPath = etree.XPath(".//input[starts-with(@name, 'cis_ItemSpecificName_')]")
    _prop_row_value_xpath: CompiledXPath = etree.XPath(".//input[starts-with(@name, 'cis_ItemSpecificValue_')]")
    _article_input_xpath: CompiledXPath = etree.XPath(".//input[@id='Artikelbeschreibung']")
    _main_pic_input_xpath: CompiledXPath = etree.XPath(".//input[@id='PictureURL']")
    _category_id_input_xpath: CompiledXPath = etree.XPath(".//input[@id='CategoryId']")

    def _get_first_element(self, elements: List[Element], description: str, log_prefix: str) -> Optional[Element]:
        """Safely retrieves the first element from a list, logging if empty or multiple found."""
        if not elements:
            logger.debug(f"{log_prefix}No elements found for '{description}'.")
            return None
        if len(elements) > 1:
            logger.warning(
                f"{log_prefix}Expected 1 element for '{description}', found {len(elements)}. Using the first.")
        return elements[0]

    def _extract_text(self, parent: Element, xpath: CompiledXPath, field_name: str, log_prefix: str) -> Optional[str]:
        """Extracts stripped text content from the first element found by XPath."""
        try:
            nodes: List[Element] = xpath(parent)
            node = self._get_first_element(nodes, f"text for {field_name}", log_prefix)
            if node is not None and node.text is not None:
                value = node.text.strip()
                return value if value else None
            return None
        except Exception as e:
            logger.error(f"{log_prefix}Error extracting text for {field_name}: {e}", exc_info=True)
            return None

    def _extract_attribute(self, parent: Element, xpath: CompiledXPath, attr: str, field_name: str, log_prefix: str) -> \
    Optional[str]:
        """Extracts a stripped attribute value from the first element found by XPath."""
        try:
            nodes: List[Element] = xpath(parent)
            node = self._get_first_element(nodes, f"attribute '{attr}' for {field_name}", log_prefix)
            if node is not None:
                attr_value = node.get(attr)
                if attr_value is not None:
                    value = attr_value.strip()
                    return value if value else None
            return None
        except Exception as e:
            logger.error(f"{log_prefix}Error extracting attribute '{attr}' for {field_name}: {e}", exc_info=True)
            return None

    def _extract_collection(self, main_table: Element, log_prefix: str) -> Optional[str]:
        return self._extract_text(main_table, self._collection_select_xpath, "collection", log_prefix)

    def _extract_product_num(self, main_table: Element, log_prefix: str) -> Optional[str]:
        return self._extract_attribute(main_table, self._product_num_input_xpath, "value", "product_num", log_prefix)

    def _extract_price(self, main_table: Element, log_prefix: str) -> Optional[float]:
        price_str = self._extract_attribute(main_table, self._price_input_xpath, "value", "price", log_prefix)
        if price_str:
            try:
                return float(price_str.replace(",", "."))
            except ValueError:
                logger.warning(f"{log_prefix}Failed to convert price string '{price_str}' to float.")
        return None

    def _extract_article(self, main_table: Element, log_prefix: str) -> Optional[str]:
        return self._extract_attribute(main_table, self._article_input_xpath, "value", "article", log_prefix)

    def _extract_main_pic_url(self, main_table: Element, log_prefix: str) -> Optional[str]:
        return self._extract_attribute(main_table, self._main_pic_input_xpath, "value", "main_pic_url", log_prefix)

    def _extract_category_id(self, main_table: Element, log_prefix: str) -> Optional[str]:
        return self._extract_attribute(main_table, self._category_id_input_xpath, "value", "category_id", log_prefix)

    def _extract_properties_json(self, main_table: Element, log_prefix: str) -> str:
        """Extracts product properties as a JSON string. Returns '{}' on failure or if not found."""
        properties_dict: Dict[str, List[str]] = {}
        try:
            outer_div_nodes: List[Element] = self._properties_outer_div_xpath(main_table)
            outer_div = self._get_first_element(outer_div_nodes, "properties outer div", log_prefix)
            if outer_div is None:
                return dumps({})

            inner_tables: List[Element] = self._properties_inner_table_xpath(outer_div)
            if not inner_tables:
                return dumps({})

            for inner_table in inner_tables:
                rows: List[Element] = self._properties_row_xpath(inner_table)
                for row in rows:
                    name = self._extract_attribute(row, self._prop_row_name_xpath, "value", "property name", log_prefix)
                    if not name:
                        continue

                    value_nodes: List[Element] = self._prop_row_value_xpath(row)
                    values: List[str] = []
                    for v_node in value_nodes:
                        val_attr = v_node.get("value")
                        if val_attr is not None:
                            stripped_val = val_attr.strip()
                            if stripped_val:
                                values.append(stripped_val)

                    if values:
                        properties_dict[name] = properties_dict.get(name, []) + values
            return dumps(properties_dict, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"{log_prefix}Error during properties extraction: {e}", exc_info=True)
            return dumps({})  # Default to empty JSON object string

    def _extract_all_pics_str(self, main_table: Element, main_pic_url: Optional[str], log_prefix: str) -> Optional[str]:
        """Extracts all picture URLs. Returns space-separated string or None."""
        pic_urls: List[str] = []
        try:
            for i in range(23):  # EPS_0 to EPS_22
                eps_id = f'EPS_{i}'
                eps_xpath_expr = etree.XPath(f".//input[@id='{eps_id}']")  # Dynamic XPath
                url = self._extract_attribute(main_table, eps_xpath_expr, "value", f"EPS pic {eps_id}", log_prefix)
                if url:
                    pic_urls.append(url)

            if main_pic_url and main_pic_url not in pic_urls:
                pic_urls.append(main_pic_url)

            return " ".join(sorted(list(set(pic_urls)))) if pic_urls else None
        except Exception as e:
            logger.error(f"{log_prefix}Error during all_pics extraction: {e}", exc_info=True)
            return None

    def parse_item_html(self, html_content: str, source_url: Optional[str] = None) -> ProductDTO:
        """
        Parses HTML content to extract product data into a ProductDTO.

        Args:
            html_content: The HTML string to parse.
            source_url: Optional URL for logging context.

        Returns:
            A ProductDTO instance with extracted data.

        Raises:
            ParsingError: If HTML is empty, malformed, or the main product table is missing.
        """
        log_prefix_base = "ProductHTMLParser"
        if source_url:
            log_prefix_base += f"({source_url})"

        # Using a portion of the content's hash for a more unique log prefix per call if needed
        # parse_id = hashlib.md5(html_content.encode('utf-8')).hexdigest()[:8] if html_content else "no_content"
        # log_prefix = f"[{log_prefix_base}-{parse_id}] "
        log_prefix = f"[{log_prefix_base}] "  # Simpler prefix

        logger.info(f"{log_prefix}Parsing process started.")

        if not html_content:
            logger.error(f"{log_prefix}HTML content is empty.")
            raise ParsingError("HTML content is empty.")

        try:
            tree: Element = html.fromstring(html_content.encode('utf-8'))
        except (etree.ParserError, etree.XMLSyntaxError) as e:
            logger.error(f"{log_prefix}Malformed HTML: {e}", exc_info=True)
            raise ParsingError(f"Malformed HTML content: {e}") from e
        except Exception as e:
            logger.error(f"{log_prefix}Unexpected error parsing HTML: {e}", exc_info=True)
            raise ParsingError(f"Unexpected error parsing HTML: {e}") from e

        main_table_nodes: List[Element] = self._main_table_xpath(tree)
        main_table = self._get_first_element(main_table_nodes, "main product table", log_prefix)

        if main_table is None:
            logger.error(f"{log_prefix}Main product table ('.mainTable') not found. Cannot proceed.")
            raise ParsingError("Main product table not found in HTML content.")

        logger.debug(f"{log_prefix}Main product table found.")

        try:
            main_pic_val = self._extract_main_pic_url(main_table, log_prefix)

            dto = ProductDTO(
                collection=self._extract_collection(main_table, log_prefix),
                product_num=self._extract_product_num(main_table, log_prefix),
                price=self._extract_price(main_table, log_prefix),
                properties=self._extract_properties_json(main_table, log_prefix),
                article=self._extract_article(main_table, log_prefix),
                pic_main=main_pic_val,
                pics=self._extract_all_pics_str(main_table, main_pic_val, log_prefix),
                category=self._extract_category_id(main_table, log_prefix)
            )
            logger.info(f"{log_prefix}Parsing successful. Product Num: {dto.product_num or 'N/A'}")
            logger.debug(f"{log_prefix}Result DTO: {dto}")
            return dto
        except Exception as e:
            logger.error(f"{log_prefix}Unexpected error during data extraction or DTO creation: {e}", exc_info=True)
            raise ParsingError(f"Unexpected error during data extraction: {e}") from e
