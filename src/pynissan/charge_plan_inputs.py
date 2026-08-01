from __future__ import annotations


def charge_product_variables(vin: str) -> dict[str, object]:
    """Serialize the required vehicle identity for ChargeProduct."""

    return {"vin": vin}


def pricing_details_variables(vin: str, location_id: str) -> dict[str, object]:
    """Serialize the required vehicle and charging-location identities."""

    return {"locationId": location_id, "vin": vin}


def enroll_charge_plan_variables(
    vin: str,
    product_sku: str,
    model: str,
    year: str,
) -> dict[str, object]:
    """Serialize the complete non-null EMP charge-plan enrollment input."""

    return {
        "config": {
            "vin": vin,
            "productSku": product_sku,
            "model": model,
            "year": year,
        }
    }


def cancel_charge_plan_variables(vin: str) -> dict[str, object]:
    """Serialize the required EMP charge-plan cancellation input."""

    return {"config": {"vin": vin}}
