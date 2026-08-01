from __future__ import annotations

from collections.abc import Mapping

from .account_parsing import (
    _enum,
    _required_field,
    _required_nullable_bool,
    _required_nullable_string,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .collision_report_models import (
    CollisionCenter,
    CollisionCenterAddress,
    CollisionCenterDistance,
    CollisionCenterPhone,
    CollisionCenterProperties,
    CollisionReportCreated,
    CollisionReportError,
    CollisionReportPdfCreated,
    CollisionReportPhotoDeleted,
    CollisionReportPhotoDeleteError,
    CollisionReportPhotoUploaded,
    CreateCollisionReportPdfResult,
    CreateCollisionReportResult,
    DeleteCollisionReportPhotoResult,
    UnselectedCollisionReportResult,
    UploadCollisionReportPhotoResult,
)
from .exceptions import ResponseError
from .models import DistanceUnit


def parse_collision_centers(
    data: Mapping[str, object],
) -> tuple[CollisionCenter | None, ...] | None:
    """Parse the nullable collision-center list and nullable entries."""

    field = "collisionCenters"
    value = _required_field(data, field, field)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{field} is not a list")
    centers: list[CollisionCenter | None] = []
    for index, item in enumerate(value):
        if item is None:
            centers.append(None)
            continue
        path = f"{field}[{index}]"
        centers.append(_parse_collision_center(_typed_object(item, path), path))
    return tuple(centers)


def parse_create_collision_report(
    data: Mapping[str, object],
) -> CreateCollisionReportResult | None:
    """Parse every generated collision-report creation branch."""

    field = "createCollisionReport"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "CreateCollisionReportSuccess":
        return CollisionReportCreated(_required_string(root, "collisionId", f"{field}.collisionId"))
    if typename == "CreateCollisionReportError":
        return CollisionReportError(_required_string(root, "message", f"{field}.message"))
    return UnselectedCollisionReportResult(typename)


def parse_create_collision_report_pdf(
    data: Mapping[str, object],
) -> CreateCollisionReportPdfResult | None:
    """Parse every generated collision-report PDF branch."""

    field = "createCollisionReportPDF"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "CreateCollisionReportPDFSuccess":
        return CollisionReportPdfCreated(_required_string(root, "pdfUrl", f"{field}.pdfUrl"))
    if typename == "CreateCollisionReportPDFError":
        return CollisionReportError(_required_string(root, "message", f"{field}.message"))
    return UnselectedCollisionReportResult(typename)


def parse_delete_collision_report_photo(
    data: Mapping[str, object],
) -> DeleteCollisionReportPhotoResult | None:
    """Parse every generated collision-report photo deletion branch."""

    field = "deletePhotoForCollisionReport"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "DeletePhotoForCollisionReportSuccess":
        return CollisionReportPhotoDeleted(
            _required_nullable_bool(root, "success", f"{field}.success")
        )
    if typename == "DeletePhotoForCollisionReportError":
        return CollisionReportPhotoDeleteError(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    return UnselectedCollisionReportResult(typename)


def parse_upload_collision_report_photo(
    data: Mapping[str, object],
) -> UploadCollisionReportPhotoResult | None:
    """Parse every generated collision-report photo upload branch."""

    field = "uploadPhotoForCollisionReport"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "UploadPhotoForCollisionReportSuccess":
        return CollisionReportPhotoUploaded(
            _required_nullable_bool(root, "success", f"{field}.success")
        )
    if typename == "UploadPhotoForCollisionReportError":
        return CollisionReportError(_required_string(root, "message", f"{field}.message"))
    return UnselectedCollisionReportResult(typename)


def _parse_collision_center(value: Mapping[str, object], path: str) -> CollisionCenter:
    _typename(value, path)
    address_path = f"{path}.address"
    distance_path = f"{path}.distance"
    address = _typed_object(
        _required_field(value, "address", address_path),
        address_path,
    )
    distance = _typed_object(
        _required_field(value, "distance", distance_path),
        distance_path,
    )
    properties_value = _required_field(value, "properties", f"{path}.properties")
    properties = (
        None
        if properties_value is None
        else _parse_properties(
            _typed_object(properties_value, f"{path}.properties"),
            f"{path}.properties",
        )
    )
    return CollisionCenter(
        id=_required_string(value, "id", f"{path}.id"),
        name=_required_string(value, "name", f"{path}.name"),
        address=_parse_address(address, address_path),
        distance=_parse_distance(distance, distance_path),
        phones=_parse_nullable_phones(value, path),
        emails=_parse_nullable_strings(value, "emails", f"{path}.emails"),
        website=_required_nullable_string(value, "website", f"{path}.website"),
        properties=properties,
    )


def _parse_address(value: Mapping[str, object], path: str) -> CollisionCenterAddress:
    _typename(value, path)
    return CollisionCenterAddress(
        address1=_required_nullable_string(value, "address1", f"{path}.address1"),
        address2=_required_nullable_string(value, "address2", f"{path}.address2"),
        city=_required_nullable_string(value, "city", f"{path}.city"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
        postal_code=_required_nullable_string(value, "postalCode", f"{path}.postalCode"),
        country=_required_nullable_string(value, "country", f"{path}.country"),
    )


def _parse_distance(value: Mapping[str, object], path: str) -> CollisionCenterDistance:
    _typename(value, path)
    raw_unit = _required_field(value, "unit", f"{path}.unit")
    return CollisionCenterDistance(
        value=_required_nullable_float(value, "value", f"{path}.value"),
        unit=None if raw_unit is None else _enum(raw_unit, DistanceUnit, f"{path}.unit"),
        drive_time=_required_nullable_float(value, "driveTime", f"{path}.driveTime"),
    )


def _parse_nullable_phones(
    value: Mapping[str, object],
    path: str,
) -> tuple[CollisionCenterPhone | None, ...]:
    field_path = f"{path}.phones"
    phones_value = _required_field(value, "phones", field_path)
    if not isinstance(phones_value, list):
        raise ResponseError(f"{field_path} is not a list")
    phones: list[CollisionCenterPhone | None] = []
    for index, item in enumerate(phones_value):
        if item is None:
            phones.append(None)
            continue
        item_path = f"{field_path}[{index}]"
        phone = _typed_object(item, item_path)
        _typename(phone, item_path)
        phones.append(
            CollisionCenterPhone(
                _required_nullable_bool(phone, "isPrimary", f"{item_path}.isPrimary"),
                _required_nullable_string(phone, "number", f"{item_path}.number"),
            )
        )
    return tuple(phones)


def _parse_nullable_strings(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> tuple[str | None, ...]:
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    items: list[str | None] = []
    for index, item in enumerate(value):
        if item is not None and not isinstance(item, str):
            raise ResponseError(f"{path}[{index}] is not a string")
        items.append(item)
    return tuple(items)


def _parse_properties(
    value: Mapping[str, object],
    path: str,
) -> CollisionCenterProperties:
    _typename(value, path)
    return CollisionCenterProperties(
        nissan_certified=_required_nullable_bool(
            value,
            "nissanCertified",
            f"{path}.nissanCertified",
        ),
        ev_certified=_required_nullable_bool(value, "evCertified", f"{path}.evCertified"),
        p1669718_status=_required_nullable_bool(
            value,
            "p1669718Status",
            f"{path}.p1669718Status",
        ),
        relevance_score=_required_nullable_float(
            value,
            "relevanceScore",
            f"{path}.relevanceScore",
        ),
        smart_filter_qualified=_required_nullable_bool(
            value,
            "smartFilterQualified",
            f"{path}.smartFilterQualified",
        ),
        participant_profile_status=_required_nullable_bool(
            value,
            "participantProfileStatus",
            f"{path}.participantProfileStatus",
        ),
        nissan_gtr=_required_nullable_bool(value, "nissanGTR", f"{path}.nissanGTR"),
        type_facility=_required_nullable_string(
            value,
            "typeFacility",
            f"{path}.typeFacility",
        ),
    )


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ResponseError(f"{path} is not a number")
    return float(value)
