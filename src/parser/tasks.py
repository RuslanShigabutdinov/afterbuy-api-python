from asgiref.sync import async_to_sync

from src.parser.container import ParserServiceContainer
from src.fabric.dto import FindFabricDTO
from src.brand.dto import FindBrandDTO
from src.libs.celery_app import celery_app

@celery_app.task
def parse_fabric_task(find_fabric_dto_dict: dict, find_brand_dto_dict: dict) -> None:
    """
    Asynchronously parses products for a specific fabric and brand.

    This Celery task takes dictionary representations of FindFabricDTO and
    FindBrandDTO, reconstructs them, and then uses the ParserService
    to perform the parsing operation.
    """
    async def run_task():
        """Helper coroutine to execute the async parsing logic."""
        async with ParserServiceContainer.get_parser_service_context() as parser_service:
            find_fabric_dto = FindFabricDTO(**find_fabric_dto_dict)
            find_brand_dto = FindBrandDTO(**find_brand_dto_dict)
            await parser_service.interface_for_fabric_parse(find_fabric_dto, find_brand_dto)
    async_to_sync(run_task)()

@celery_app.task
def parse_brand_task(find_brand_dto_dict: dict) -> None:
    """
    Asynchronously parses all fabrics and products for a specific brand.

    This Celery task takes a dictionary representation of FindBrandDTO,
    reconstructs it, and then uses the ParserService to perform the
    parsing operation for the entire brand.
    """
    async def run_task():
        """Helper coroutine to execute the async parsing logic."""
        async with ParserServiceContainer.get_parser_service_context() as parser_service:
            find_brand_dto = FindBrandDTO(**find_brand_dto_dict)
            await parser_service.interface_for_brand_parse(find_brand_dto)
    async_to_sync(run_task)()

@celery_app.task
def parse_all_task() -> None:
    """
    Asynchronously parses all fabrics and products for all configured brands.

    This Celery task uses the ParserService to initiate a comprehensive
    parsing operation across all known brands and their fabrics.
    """
    async def run_task():
        """Helper coroutine to execute the async parsing logic."""
        async with ParserServiceContainer.get_parser_service_context() as parser_service:
            await parser_service.interface_for_parse_all()
    async_to_sync(run_task)()

@celery_app.task
def complete_brand_task(dto_dict: dict) -> None:
    """
    Asynchronously completes the parsing process for a specific brand.

    This Celery task takes a dictionary representation of FindBrandDTO,
    reconstructs it, and then uses the ParserService to finalize
    or mark the parsing process as complete for that brand.
    """
    async def run_task():
        """Helper coroutine to execute the async parsing logic."""
        async with ParserServiceContainer.get_parser_service_context() as parser_service:
            dto = FindBrandDTO(**dto_dict)
            await parser_service.complete_parse(dto)
    async_to_sync(run_task)()