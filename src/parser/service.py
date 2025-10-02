import logging

from src.brand.depends.service import IBrandService
from src.brand.dto import FindBrandDTO, BrandDTO
from src.brand.entity import BrandEntity

from src.fabric.depends.service import IFabricService
from src.fabric.dto import FabricDTO, UpdateFabricDTO, FindFabricDTO
from src.fabric.entity import FabricEntity
from src.libs.exceptions import AlreadyExistError

from src.product.depends.service import IProductService
from src.product.entity import ProductEntity
from src.product.dto import ProductDTO, UpdateProductDTO, FindProductDTO
from src.product.exceptions import ProductAlreadyExists
from typing import List

from src.url.depends.service import IUrlService
from src.url.dto import FilterUrlsDTO, UrlDTO
from src.url.entity import UrlEntity

from src.parser.parser.depends import IFabricParserService, IProductParserService

class ParserService:
    """
    **Description**: High-level service orchestrating the parsing process for
    brand fabrics and related products from an external source (Afterbuy).

    **Dependencies**:
    - `brand_service`: *IBrandService* - Service for brand operations.
    - `product_service`: *IProductService* - Service for product operations.
    - `url_service`: *IUrlService* - Service for URL operations.
    - `fabric_service`: *IFabricService* - Service for fabric operations.
    - `fabric_parser_service`: *IFabricParserService* - Parser for fabrics.
    - `product_parser_service`: *IProductParserService* - Parser for products.

    **Methods**:
    - `map_all`: Orchestrates the full parsing and mapping process.
    - `parse_fabric`: Parses products for a specific fabric and updates fabric status.
    - `prepare`: Ensures necessary brands and fabrics exist by creating them if not found.
    - `interface_for_fabric_parse`: External interface to trigger parsing for a specific fabric.
    - `interface_for_brand_parse`: External interface to trigger parsing for all fabrics of a brand.

    **Usage**: Provides the main entry points for initiating parsing tasks.
    """
    def __init__(
        self,
        brand_service: IBrandService,
        product_service: IProductService,
        url_service: IUrlService,
        fabric_service: IFabricService,
        fabric_parser_service: IFabricParserService,
        product_parser_service: IProductParserService,
    ):
        self.brand_service = brand_service
        self.product_service = product_service
        self.url_service = url_service
        self.fabric_service = fabric_service
        self.fabric_parser_service = fabric_parser_service
        self.product_parser_service = product_parser_service

    async def parse_fabric(self, fabric: FabricDTO, brand: BrandDTO):
        """
        **Description**: Parses product links and product data for a given fabric and brand,
        then updates the fabric's status based on parsing results.

        **Input**:
        - `fabric`: *FabricDTO* - The fabric to parse products for.
        - `brand`: *BrandDTO* - The brand associated with the fabric.

        **Output**:
        - None

        **Exceptions**:
        - Exceptions from delegated service calls (e.g., `ParsingError`, `ProductAlreadyExists`)
          will bubble up to be handled by the global exception handler.
        - `Exception`: Catches generic exceptions during product creation logging a warning,
          allowing parsing to continue for other products within the fabric.

        **How It Works**:
        - Parses product links associated with the fabric and brand.
        - Creates URL entities for the discovered links.
        - Parses product data from the links.
        - Creates product entities in the database for the parsed products,
          catching exceptions during creation to avoid stopping the whole process.
        - Updates the fabric entity with the count of links found and parsing completion status.
        """
        try:
            links = await self.product_parser_service.parse_links(fabric=fabric, brand=brand)
        except Exception as e:
            logging.warning(f"Can't parse search info from: {fabric.name} {brand.name}")
            return

        for link in links:
            entity = UrlEntity(url=link, brand_id=brand.id, fab_id=fabric.id)
            try:
                await self.url_service.create(entity)
            except AlreadyExistError as e:
                logging.info(f"Url already exists: {link}. Skipping creation: {e}")
        links_count = len(links)

        logging.info(f"Parsed {links_count} urls.")

        products: List[ProductDTO] = await self.product_parser_service.parse_products(links=links, brand=brand)

        products_count = len(products)

        print(links_count)
        print(products_count)

        for product_dto in products:
            if not isinstance(product_dto, ProductDTO):
                logging.warning(f"Skipping unexpected product payload type: {type(product_dto).__name__}")
                continue

            product_dto.fabric_id = fabric.id
            product_dto.brand_id = brand.id

            if not getattr(product_dto, "link", None):
                logging.warning(f"Parsed product missing link. Skipping product_num={product_dto.product_num}")
                continue

            try:
                url_candidates = await self.url_service.filter(FilterUrlsDTO(url=product_dto.link))
            except Exception as e:
                logging.warning(f"Failed to fetch URL entry for product {product_dto.product_num}: {e}")
                continue

            if not url_candidates:
                logging.warning(f"No URL entry found for parsed product link: {product_dto.link}")
                continue

            url_dto: UrlDTO = url_candidates[0]

            product_dto.url_id = url_dto.id
            try:
                product_entity = ProductEntity(**product_dto.model_dump(exclude={"id"}))
                await self.product_service.create(product_entity)
            except AlreadyExistError:
                logging.warning(f"Product already exists: {product_dto.product_num}. Updating.")

                old_product_dto = await self.product_service.find(FindProductDTO(url_id=url_dto.id))

                product_update_dto = UpdateProductDTO(**product_dto.model_dump(exclude={"id"}))

                await self.product_service.update(product_update_dto, old_product_dto.id)
            except Exception as e:
                logging.warning(f"Failed to create product {product_dto.product_num}: {e}")

        update_dto = UpdateFabricDTO(
            brand_id=fabric.brand_id,
            total_count=links_count,
            parsed_count=products_count,
            afterbuy_id=fabric.afterbuy_id,
            name=fabric.name,
            done=(links_count == products_count)
        )

        await self.fabric_service.update(update_dto, fabric.id)

    async def prepare(self):
        """
        **Description**: Prepares the environment by ensuring essential brands ("JV", "XL")
        and their associated fabrics are present in the database.

        **Input**:
        - None

        **Output**:
        - None

        **Exceptions**:
        - `AlreadyExistError`: Catches exceptions during brand or fabric creation, logging a warning
          and allowing preparation to continue for other entities.
        - Exceptions from delegated service calls (e.g., `ParsingError`) will bubble up.

        **How It Works**:
        - Attempts to create "JV" and "XL" brands. If they exist, the AlreadyExistError is caught.
        - Retrieves fabrics for each brand using the fabric parser service.
        - Attempts to create each fetched fabric. If they exist, the AlreadyExistError is caught.
        - Continues processing even if specific brands or fabrics fail to be created due to existence or other errors.
        """
        brands_to_prepare = ["JV", "XL"]
        prepared_brands = []

        for brand_name in brands_to_prepare:
            try:
                brand = await self.brand_service.create(BrandEntity(name=brand_name))
                prepared_brands.append(brand)
            except AlreadyExistError:
                 try:
                    brand = await self.brand_service.find(FindBrandDTO(name=brand_name))
                    prepared_brands.append(brand)
                 except Exception as e:
                    logging.warning(f"Failed to find existing brand {brand_name}: {e}")
            except Exception as e:
                logging.warning(f"Failed to create brand {brand_name}: {e}")


        for brand in prepared_brands:
            try:
                fabrics = await self.fabric_parser_service.get_fabrics(brand.id)
            except Exception as e:
                logging.warning(f"Failed to get fabrics for brand {brand.name}: {e}")
                continue

            for fabric_dto in fabrics:
                try:
                    fabric_entity = FabricEntity(
                         name=fabric_dto.name,
                         afterbuy_id=fabric_dto.afterbuy_id,
                         brand_id=brand.id,
                         total_count=0,
                         parsed_count=0,
                         done=False
                     )
                    await self.fabric_service.create(fabric_entity)
                except AlreadyExistError:
                    logging.warning(f"Fabric already exists for brand {brand.name}: {fabric_dto.name}. Skipping creation.")
                except Exception as e:
                    logging.warning(f"Failed to create fabric {fabric_dto.name} for brand {brand.name}: {e}")

    async def complete_parse(self, dto: FindBrandDTO):
        """
        **Description**: Initiates a comprehensive parsing process for all relevant fabrics associated with a specific brand.

        This method first prepares the system, then finds the specified brand,
        retrieves all its associated fabrics, and finally processes each fabric
        that meets certain criteria (not done and has a valid afterbuy_id).

        **Input**:
        - `dto`: *FindBrandDTO* - Data Transfer Object containing criteria to find the target brand.

        **Output**:
        - None

        **Exceptions**:
        - `BrandNotFound`: If the brand matching the `dto` criteria is not found (raised by `self.brand_service.find`).
        - Any exceptions raised by `self.prepare()` will bubble up.
        - Any exceptions raised by `self.fabric_service.filter()` (e.g., database connection issues) will bubble up.
        - Any exceptions raised by `self.parse_fabric()` during individual fabric parsing will bubble up.

        **How It Works**:
        1. Calls `self.prepare()` to perform any necessary setup or prerequisite actions.
        2. Finds the brand using the criteria provided in the `dto` by calling `self.brand_service.find()`.
        3. Retrieves all fabrics associated with the found brand's ID by calling `self.fabric_service.filter()`.
        4. Iterates through the list of retrieved fabrics.
        5. For each `fabric` in the list:
           - It checks if the fabric is not yet marked as done (`fabric.done == False`).
           - It also checks if the `fabric.afterbuy_id` is not a placeholder value like "-1" or "0", indicating it's a valid item to parse.
           - If both conditions are met, it calls `self.parse_fabric()` with the current fabric and the found brand to process that specific fabric.
        """
        await self.prepare()

        brand = await self.brand_service.find(dto)

        fabrics = await self.fabric_service.filter(FindFabricDTO(brand_id=brand.id))

        for fabric in fabrics:
            fabric: FabricDTO
            if fabric.done == False and fabric.afterbuy_id not in ["-1", "0"]:
                await self.parse_fabric(fabric, brand)

        return {"Maybe all good": "I think..."}




    async def interface_for_fabric_parse(self, find_fabric: FindFabricDTO, find_brand: FindBrandDTO):
        """
        **Description**: Triggers the parsing process for a specific fabric identified by criteria.

        **Input**:
        - `find_fabric`: *FindFabricDTO* - Criteria to find the target fabric.
        - `find_brand`: *FindBrandDTO* - Criteria to find the associated brand.

        **Output**:
        - None

        **Exceptions**:
        - `BrandNotFound`: If the brand matching the criteria is not found (handled by brand_service.find).
        - `FabricNotFound`: If the fabric matching the criteria is not found (handled by fabric_service.find).
        - Any exceptions raised by `parse_fabric` will bubble up.

        **How It Works**:
        - Finds the brand using the provided criteria.
        - Finds the fabric using the provided criteria and the found brand's ID.
        - Delegates the parsing task to `parse_fabric`.
        """

        await self.prepare()

        brand = await self.brand_service.find(find_brand)

        find_fabric.brand_id = brand.id

        fabric = await self.fabric_service.find(find_fabric)

        await self.parse_fabric(fabric, brand)


    async def interface_for_brand_parse(self, find_brand: FindBrandDTO):
        """
        **Description**: Triggers the parsing process for all fabrics associated with a brand.

        **Input**:
        - `find_brand`: *FindBrandDTO* - Criteria to find the target brand.

        **Output**:
        - None

        **Exceptions**:
        - `BrandNotFound`: If the brand matching the criteria is not found (handled by brand_service.find).
        - `FabricNotFound`: If fabrics for the brand are not found (handled by fabric_service.filter).
        - `Exception`: Catches generic exceptions during fabric parsing, logging a warning and continuing.

        **How It Works**:
        - Finds the brand using the provided criteria.
        - Filters all fabrics belonging to that brand.
        - Iterates through the fabrics and triggers parsing for each one, skipping those with specific afterbuy_id values.
        - Catches exceptions during parsing of a single fabric to avoid stopping the entire brand parsing process.
        """

        await self.prepare()

        brand = await self.brand_service.find(find_brand)

        fabrics = await self.fabric_service.filter(FindFabricDTO(brand_id=brand.id))

        for fabric in fabrics:
            if fabric.afterbuy_id in ["-1", "0"]:
                continue
            try:
                await self.parse_fabric(fabric, brand)
            except Exception as e:
                logging.warning(f"Failed to parse fabric {fabric.name} (ID: {fabric.id}) for brand {brand.name}: {e}")

    async def interface_for_parse_all(self):
        await self.prepare()
        jv = FindBrandDTO(name="JV")
        xl = FindBrandDTO(name="XL")

        await self.interface_for_brand_parse(jv)
        await self.interface_for_brand_parse(xl)
