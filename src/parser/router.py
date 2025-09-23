# router.py
from fastapi import APIRouter, status, Body, Depends
from typing import Dict, Any

from src.brand.dto import FindBrandDTO
from src.fabric.dto import FindFabricDTO
from src.protection import RequireAdminToken
from src.parser.tasks import (
    parse_fabric_task,
    parse_brand_task,
    parse_all_task,
    complete_brand_task,
)
from src.parser.depends.service import IParserService

from src.mapping.depends.service import IMappingService

router = APIRouter(
    prefix="/parser",
    tags=["Parser"],
    dependencies=[RequireAdminToken]
)


@router.post("/do_all")
async def do_all(parsing_service: IParserService, mapping_service: IMappingService):
    await parsing_service.complete_parse(FindBrandDTO(id=1))
    await parsing_service.complete_parse(FindBrandDTO(id=2))
    await mapping_service.map_all()

@router.post(
    "/parse-specific-brands",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger parsing for JV and XL brands",
    description=(
        "Initiates background parsing for all products under the 'JV' and 'XL' brands. "
        "This operation is asynchronous."
    )
)
async def parse_jv_and_xl_brands() -> Dict[str, str]:
    """
    Dispatches Celery tasks to parse products for the 'JV' and 'XL' brands.
    """
    jv_brand_dto = FindBrandDTO(name="JV")
    xl_brand_dto = FindBrandDTO(name="XL")
    parse_brand_task.delay(jv_brand_dto.model_dump())
    parse_brand_task.delay(xl_brand_dto.model_dump())
    return {"message": "Parsing process initiated for JV and XL brands."}

@router.post(
    "/parse-fabric",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger parsing for a specific fabric and brand",
    description="Dispatches a Celery task to parse products associated with a given fabric and brand."
)
async def parse_specific_fabric(
    find_fabric_dto: FindFabricDTO = Body(...),
    find_brand_dto: FindBrandDTO = Body(...),
) -> Dict[str, str]:
    """
    Dispatches a Celery task to parse products for a specific fabric within a specific brand.
    """
    parse_fabric_task.delay(find_fabric_dto.model_dump(), find_brand_dto.model_dump())
    return {"message": f"Parsing task initiated for fabric '{find_fabric_dto.name}' of brand '{find_brand_dto.name}'."}

@router.post(
    "/parse-brand",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger parsing for a specific brand",
    description="Dispatches a Celery task to parse all fabrics and products for a given brand."
)
async def parse_specific_brand(
    find_brand_dto: FindBrandDTO = Body(...),
) -> Dict[str, str]:
    """
    Dispatches a Celery task to parse all fabrics and products for the specified brand.
    """
    parse_brand_task.delay(find_brand_dto.model_dump())
    return {"message": f"Parsing process initiated for brand: {find_brand_dto.name}."}

@router.post(
    "/parse-all",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger parsing for all brands and fabrics",
    description="Dispatches a Celery task to parse all fabrics and products for all configured brands."
)
async def parse_everything() -> Dict[str, str]:
    """
    Dispatches a Celery task to parse all items for all configured brands.
    """
    parse_all_task.delay()
    return {"message": "Full parsing process initiated for all brands and fabrics."}

@router.post(
    "/prepare",
    status_code=status.HTTP_200_OK,
    summary="Prepare system for parsing",
    description="Executes synchronous preparation steps required for parsing, such as ensuring base data exists."
)
async def prepare_parsing_data(parser_service: IParserService) -> Dict[str, str]:
    """
    Synchronously prepares the system for parsing operations.
    This might involve setting up initial data for brands or fabrics.
    """
    await parser_service.prepare()
    return {"message": "Preparation completed successfully."}

@router.post(
    "/complete-brand",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger completion process for a brand's parsing",
    description="Dispatches a Celery task to finalize or mark parsing as complete for a given brand."
)
async def complete_brand_parsing(find_brand_dto: FindBrandDTO = Body(...)) -> Dict[str, str]:
    """
    Dispatches a Celery task to mark the parsing process for the specified brand as complete.
    """
    complete_brand_task.delay(find_brand_dto.model_dump())
    return {"message": f"Completion task initiated for brand: {find_brand_dto.name}."}
