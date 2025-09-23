import glob
import os
from typing import List, Optional, Any, Dict, Set, Tuple
import functools

import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError
from thefuzz import fuzz

from src.fabric.dto import FindFabricDTO
from src.fabric_mapping.dto import CreateFabricMappingDTO, FabricMappingDTO
from src.product.dto import ProductPreviewDTO, FilterProductsDTO

from src.product_mapping.depends.services import IProductMappingService
from src.fabric_mapping.depends.services import IFabricMappingService

from src.fabric.depends.service import IFabricService
from src.product.depends.service import IProductService
from src.product_mapping.dto import CreateProductsMappingDTO


class ProductMatcherConfig:
    """
    Configuration for the product matching logic.

    Attributes:
        FIELD_WEIGHTS: A dictionary where keys are ProductPreviewDTO field names
            and values are their corresponding weights (float) used in similarity
            scoring. Higher weights mean more importance.
        MATCHING_FIELDS: A list of ProductPreviewDTO field names that will be
            used for comparison. Derived from the keys of FIELD_WEIGHTS.
        MAX_DIFFERENCE_THRESHOLD: The maximum acceptable weighted sum of
            differences for two products to be considered a match. A lower
            threshold means stricter matching (0.0 is a perfect match).
    """
    FIELD_WEIGHTS: Dict[str, float] = {
        "properties": 0.40,
        "pic_main": 0.25,
        "article": 0.20,
        "category": 0.10,
        "pics": 0.05,
    }
    MATCHING_FIELDS: List[str] = list(FIELD_WEIGHTS.keys())
    MAX_DIFFERENCE_THRESHOLD: float = 0.4





@functools.lru_cache(maxsize=2048)  # Cache results for performance
def calculate_string_difference(s1: Optional[str], s2: Optional[str]) -> float:
    """
    Calculates a normalized difference score (0.0 to 1.0) between two strings.

    The score is based on `thefuzz.fuzz.ratio`.
    - 0.0 means strings are identical (case-insensitive) or both are None/empty.
    - 1.0 means strings are completely different.
    Comparison is case-insensitive. None or empty strings are treated as empty
    strings for comparison.

    Args:
        s1: The first string.
        s2: The second string.

    Returns:
        A float between 0.0 and 1.0 representing the difference.
    """
    str1 = (s1 or "").lower()
    str2 = (s2 or "").lower()

    if str1 == str2:
        return 0.0

    similarity_ratio = fuzz.ratio(str1, str2)
    difference_score = 1.0 - (similarity_ratio / 100.0)
    return difference_score


def _calculate_dto_pair_weighted_difference(
        dto1: ProductPreviewDTO,
        dto2: ProductPreviewDTO,
        matcher_config: ProductMatcherConfig
) -> float:
    """
    Calculates the total weighted difference score between two DTOs.

    Iterates through `matcher_config.MATCHING_FIELDS`, calculates the string
    difference for each field pair using `calculate_string_difference`,
    applies the field-specific weight, and sums these weighted differences.

    Args:
        dto1: The first ProductPreviewDTO.
        dto2: The second ProductPreviewDTO.
        matcher_config: Configuration for matching, including field weights.

    Returns:
        The total weighted difference score. Lower scores indicate more similarity.
    """
    total_weighted_difference = 0.0
    for field_name in matcher_config.MATCHING_FIELDS:
        val1 = getattr(dto1, field_name, None)
        val2 = getattr(dto2, field_name, None)

        field_difference = calculate_string_difference(val1, val2)
        weighted_field_diff = field_difference * matcher_config.FIELD_WEIGHTS[field_name]
        total_weighted_difference += weighted_field_diff

    return total_weighted_difference



class MappingService:
    def __init__(self,
                 product_service: IProductService,
                 fabric_service: IFabricService,
                 product_mapping_service: IProductMappingService,
                 fabric_mapping_service: IFabricMappingService):
        self.product_service = product_service
        self.fabric_service = fabric_service
        self.product_mapping_service = product_mapping_service
        self.fabric_mapping_service = fabric_mapping_service

    async def map_fabrics(self):
        j_fabrics = await self.fabric_service.filter(FindFabricDTO(brand_id=1))
        x_fabrics = await self.fabric_service.filter(FindFabricDTO(brand_id=2))

        for fabric in j_fabrics:
            for x_fabric in x_fabrics:
                if str(fabric.name).strip().lower() == str(x_fabric.name).strip().lower() and fabric.total_count > 0 and x_fabric.total_count > 0:
                    await self.fabric_mapping_service.create(CreateFabricMappingDTO(fabric_id_JV=fabric.id, fabric_id_XL=x_fabric.id))

    async def map_products(self):

        fabric_mappings = await self.fabric_mapping_service.get_list()
        print(fabric_mappings)
        matcher_config = ProductMatcherConfig()

        for mapping in fabric_mappings:
            mapping: FabricMappingDTO
            print("\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA")
            j_fabric = await self.fabric_service.get(mapping.fabric_id_JV)
            x_fabric = await self.fabric_service.get(mapping.fabric_id_XL)

            j_products = await self.product_service.filter(FilterProductsDTO(fabric_id=j_fabric.id))
            x_products = await self.product_service.filter(FilterProductsDTO(fabric_id=x_fabric.id))
            print(j_products)
            print(x_products)
            for i, dto1 in enumerate(j_products):
                best_target_dto: Optional[ProductPreviewDTO] = None
                lowest_weighted_diff = float('inf')

                for dto2 in x_products:
                    current_diff = _calculate_dto_pair_weighted_difference(dto1, dto2, matcher_config)

                    if current_diff < lowest_weighted_diff:
                        lowest_weighted_diff = current_diff
                        best_target_dto = dto2

                if best_target_dto and lowest_weighted_diff <= matcher_config.MAX_DIFFERENCE_THRESHOLD:
                    await self.product_mapping_service.create(CreateProductsMappingDTO(
                        fabric_mapping_id=mapping.id,
                        xl_product_id=best_target_dto.id,
                        jv_product_id=dto1.id
                    ))

                if (i + 1) % 10 == 0 or (i + 1) == len(j_products):
                    print(f"Processed {i + 1}/{len(j_products)} source DTOs...")

        return "All done i think"

    async def map_all(self):
        await self.fabric_mapping_service.delete_all()
        await self.map_fabrics()
        await self.map_products()