from __future__ import annotations

from collections.abc import Mapping

from ._commerce_value_parsing import _parse_nullable_object_list, _required_nullable_float
from .account_parsing import (
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
)
from .commerce_models import (
    NissanStoreCatalogChildProduct,
    NissanStoreCatalogPackage,
    NissanStoreCatalogPromotion,
    NissanStoreCatalogSellingModel,
)


def _parse_catalog_package(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogPackage:
    return NissanStoreCatalogPackage(
        short_description=_required_nullable_string(
            value,
            "shortDescription",
            f"{path}.shortDescription",
        ),
        trial_duration=_required_nullable_int(
            value,
            "npTrialDuration",
            f"{path}.npTrialDuration",
        ),
        product_image_url=_required_nullable_string(
            value,
            "productImageUrl",
            f"{path}.productImageUrl",
        ),
        long_description=_required_nullable_string(
            value,
            "longDescription",
            f"{path}.longDescription",
        ),
        selling_models=_parse_nullable_object_list(
            value,
            "sellingModels",
            path,
            _parse_catalog_selling_model,
        ),
        product_id=_required_nullable_string(value, "productId", f"{path}.productId"),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        child_products=_parse_nullable_object_list(
            value,
            "childProducts",
            path,
            _parse_catalog_child_product,
        ),
        is_feature_on_demand=_required_nullable_bool(value, "isFoD", f"{path}.isFoD"),
        promotions=_parse_nullable_object_list(
            value,
            "promotions",
            path,
            _parse_catalog_promotion,
        ),
    )


def _parse_catalog_selling_model(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogSellingModel:
    return NissanStoreCatalogSellingModel(
        pricing_term_unit=_required_nullable_string(
            value,
            "sellingModelPricingTermUnit",
            f"{path}.sellingModelPricingTermUnit",
        ),
        retail_price=_required_nullable_float(value, "retailPrice", f"{path}.retailPrice"),
        discounted_price=_required_nullable_float(
            value,
            "discountedPrice",
            f"{path}.discountedPrice",
        ),
        selling_model_type=_required_nullable_string(
            value,
            "sellingModelType",
            f"{path}.sellingModelType",
        ),
        selling_model_id=_required_nullable_string(
            value,
            "sellingModelId",
            f"{path}.sellingModelId",
        ),
    )


def _parse_catalog_child_product(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogChildProduct:
    return NissanStoreCatalogChildProduct(
        name=_required_nullable_string(value, "name", f"{path}.name"),
        customer_facing=_required_nullable_bool(
            value,
            "npCustomerFacing",
            f"{path}.npCustomerFacing",
        ),
    )


def _parse_catalog_promotion(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogPromotion:
    return NissanStoreCatalogPromotion(
        promotion_id=_required_nullable_string(
            value,
            "promotionId",
            f"{path}.promotionId",
        ),
        priority=_required_nullable_int(value, "priority", f"{path}.priority"),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        monthly_price=_required_nullable_float(
            value,
            "monthlyPromotionPrice",
            f"{path}.monthlyPromotionPrice",
        ),
        annual_price=_required_nullable_float(
            value,
            "annualPromotionPrice",
            f"{path}.annualPromotionPrice",
        ),
        end_date=_required_nullable_string(value, "endDate", f"{path}.endDate"),
        description=_required_nullable_string(
            value,
            "description",
            f"{path}.description",
        ),
    )
