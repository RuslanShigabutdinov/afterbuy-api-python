import asyncio
import logging
from typing import List, Optional

from celery import group
from celery.result import GroupResult, AsyncResult

from src.brand.dto import BrandDTO
from src.fabric.dto import FabricDTO
from src.parser.http_utils import ProductUtil
from src.product.dto import ProductDTO

from src.parser.http_utils.login import LoginClient
from src.parser.http_utils.search import SearchUtil


class ProductParserService:
    """Parses product information using Celery for parallelism.

    This service handles fetching product links and then distributing the parsing
    of these links across multiple Celery tasks.

    Attributes:
        CHUNK_SIZE (int): Number of links to process in a single Celery task.
    """

    CHUNK_SIZE: int = 50

    @staticmethod
    async def parse_links(fabric: FabricDTO, brand: BrandDTO) -> List[str]:
        """Fetches all product detail page links for a given fabric and brand.

        Args:
            fabric: The FabricDTO entity.
            brand: The BrandDTO entity.

        Returns:
            A list of full URLs to product detail pages.
        """
        async with LoginClient(brand.id) as client:
            search_util = SearchUtil(client)
            links = await search_util.get_products_links(fabric)
            full_links = []
            for link in links:
                if link.startswith(('http://', 'https://')):
                    full_links.append(link)
                else:
                    base = client.base_url.rstrip('/')
                    relative = link.lstrip('/')
                    full_links.append(f"{base}/{relative}")
            return full_links

    async def parse_products(self, links: List[str], brand: BrandDTO) -> List[ProductDTO]:
        """Parses a list of product links concurrently using Celery tasks.

        This method divides the list of links into chunks and dispatches
        a Celery task for each chunk. It then collects results from all tasks.
        Individual task failures are logged, and successful results are aggregated.

        Args:
            links: A list of product URL strings to parse.
            brand: The BrandDTO to which these products belong.

        Returns:
            A list of successfully parsed ProductDTO objects. Returns an empty
            list if no links are provided, if critical errors occur during
            task group processing, or if all tasks fail.
        """

        async def parse_links_chunks(links_chunk: list[str]):
            async with LoginClient(brand.id) as client:
                util = ProductUtil(client)
                tasks_l = [util.parse_item(link) for link in links_chunk]
                results_l = await asyncio.gather(*tasks_l, return_exceptions=True)

            filtered_results: list[ProductDTO] = []

            for link, result in zip(links_chunk, results_l):
                if isinstance(result, BaseException):
                    logging.warning(
                        "Skipping product link %s due to background task error: %s (%s)",
                        link,
                        type(result).__name__,
                        result,
                    )
                    continue

                if not isinstance(result, ProductDTO):
                    logging.warning(
                        "Unexpected result from product parsing task for link %s. Dropping entry: %s",
                        link,
                        type(result).__name__,
                    )
                    continue

                filtered_results.append(result)

            return filtered_results

        if not links:
            logging.info("No links provided to parse_products. Returning empty list.")
            return []

        links_chunks = [
            links[i:i + self.CHUNK_SIZE]
            for i in range(0, len(links), self.CHUNK_SIZE)
        ]

        if not links_chunks:
            logging.info("No link chunks to process. Returning empty list.")
            return []

        logging.info(f"Divided {len(links)} links into {len(links_chunks)} chunks for Celery processing.")

        tasks = [parse_links_chunks(links) for links in links_chunks]
        results = await asyncio.gather(*tasks)

        return [item for sub in results or [] for item in sub or []]
