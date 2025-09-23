from fastapi import APIRouter

from src.user.router import router as user_router
from src.auth.router import router as auth_router
from src.brand.router import router as brand_router
from src.fabric.router import router as fabric_router
from src.product.router import router as product_router
from src.url.router import router as url_router
from src.fabric_mapping.router import router as fabric_mapping_router
from src.product_mapping.router import router as product_mapping_router
from src.mapping.router import router as mapping_router
from src.parser.router import router as parser_router
from src.export.router import router as export_router


router = APIRouter(prefix="/v1", tags=["API"])

router.include_router(user_router)
router.include_router(auth_router)

router.include_router(brand_router)
router.include_router(fabric_router)
router.include_router(product_router)
router.include_router(url_router)

router.include_router(fabric_mapping_router)
router.include_router(product_mapping_router)
router.include_router(mapping_router)

router.include_router(parser_router)

router.include_router(export_router)