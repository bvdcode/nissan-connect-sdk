from __future__ import annotations

from dataclasses import dataclass

from .graphql_input import UNSET, UnsetType, optional_input_fields


@dataclass(frozen=True, slots=True)
class AddressInput:
    """Optional postal address fields accepted by Nissan input objects."""

    address1: str | UnsetType | None = UNSET
    address2: str | UnsetType | None = UNSET
    city: str | UnsetType | None = UNSET
    state: str | UnsetType | None = UNSET
    postal_code: str | UnsetType | None = UNSET
    country: str | UnsetType | None = UNSET
    neighbourhood: str | UnsetType | None = UNSET
    district: str | UnsetType | None = UNSET
    street_number: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CoordinateInput:
    """Required latitude and longitude accepted by Nissan input objects."""

    latitude: float
    longitude: float


def address_input(value: AddressInput) -> dict[str, object]:
    return optional_input_fields(
        address1=value.address1,
        address2=value.address2,
        city=value.city,
        state=value.state,
        postalCode=value.postal_code,
        country=value.country,
        neighbourhood=value.neighbourhood,
        district=value.district,
        streetNumber=value.street_number,
    )


def coordinate_input(value: CoordinateInput) -> dict[str, object]:
    return {"latitude": value.latitude, "longitude": value.longitude}
