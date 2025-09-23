from contextlib import asynccontextmanager # Keep this for the original intent if you revert
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession # Assuming SQLAlchemy

from src.brand.repositories.brand import BrandRepository
from src.brand.service import BrandService
from src.config.database.engine import db_helper # Assuming db_helper.get_db_session() is the correct name
from src.fabric.repositories.fabric import FabricRepository
from src.fabric.service import FabricService
from src.parser.parser.fabrics import FabricParserService # Assuming this is the http_utils one
from src.parser.parser.product import ProductParserService # Assuming this is the http_utils one
from src.parser.service import ParserService
from src.product.repositories.product import ProductsRepository
from src.product.service import ProductService
from src.url.repositories.url import UrlsRepository
from src.url.service import UrlService

class ParserServiceContainer:
    """
    Provides a dependency injection container for creating ParserService instances
    within a single database session scope.
    """

    @staticmethod
    @asynccontextmanager # Use this decorator for the context manager pattern
    async def get_parser_service_context() -> AsyncGenerator[ParserService, None]: # Yield ParserService
        """
        Provides a ParserService instance with all its dependencies initialized
        within a single, managed database session.

        Yields:
            ParserService: An instance of ParserService.
        """
        # All services will share this single session for the duration of the 'with' block
        async with db_helper.get_db_session() as session: # type: AsyncSession
            brand_repository = BrandRepository(session)
            brand_service = BrandService(brand_repository)

            product_repository = ProductsRepository(session)
            product_service = ProductService(product_repository)

            url_repository = UrlsRepository(session)
            url_service = UrlService(url_repository)

            fabric_repository = FabricRepository(session)
            fabric_service = FabricService(fabric_repository)

            # These parser sub-services likely don't need DB sessions directly
            # but might be passed to ParserService.
            # If they do need DB access, they should also take the session.
            fabric_parser_service_http = FabricParserService() # Renamed to avoid confusion if there's another one
            product_parser_service_http = ProductParserService() # Renamed for clarity

            parser_service_instance = ParserService(
                brand_service=brand_service,
                product_service=product_service,
                url_service=url_service,
                fabric_service=fabric_service,
                fabric_parser_service=fabric_parser_service_http, # Use the correct instance
                product_parser_service=product_parser_service_http, # Use the correct instance
            )
            yield parser_service_instance # Yield the instance

__all__ = ("ParserServiceContainer",)