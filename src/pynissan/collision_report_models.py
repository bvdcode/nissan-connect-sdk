from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import DistanceUnit


class PhotoSection(StrEnum):
    """Known collision-report photo slots."""

    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"
    EIGHT = "EIGHT"
    NINE = "NINE"
    TEN = "TEN"
    ELEVEN = "ELEVEN"
    TWELVE = "TWELVE"
    THIRTEEN = "THIRTEEN"
    FOURTEEN = "FOURTEEN"
    FIFTEEN = "FIFTEEN"
    SIXTEEN = "SIXTEEN"
    SEVENTEEN = "SEVENTEEN"
    EIGHTEEN = "EIGHTEEN"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class CollisionCenterAddress:
    """Nullable postal address fields for a collision center."""

    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None


@dataclass(frozen=True, slots=True)
class CollisionCenterDistance:
    """Nullable distance and driving-time details."""

    value: float | None
    unit: DistanceUnit | None
    drive_time: float | None


@dataclass(frozen=True, slots=True)
class CollisionCenterPhone:
    """Nullable collision-center phone fields."""

    is_primary: bool | None
    number: str | None


@dataclass(frozen=True, slots=True)
class CollisionCenterProperties:
    """Nullable Nissan certification and search metadata."""

    nissan_certified: bool | None
    ev_certified: bool | None
    p1669718_status: bool | None
    relevance_score: float | None
    smart_filter_qualified: bool | None
    participant_profile_status: bool | None
    nissan_gtr: bool | None
    type_facility: str | None


@dataclass(frozen=True, slots=True)
class CollisionCenter:
    """Collision center returned by Nissan's location search."""

    id: str
    name: str
    address: CollisionCenterAddress
    distance: CollisionCenterDistance
    phones: tuple[CollisionCenterPhone | None, ...]
    emails: tuple[str | None, ...]
    website: str | None
    properties: CollisionCenterProperties | None


@dataclass(frozen=True, slots=True)
class CollisionReportCreated:
    """Successful collision-report creation."""

    collision_id: str


@dataclass(frozen=True, slots=True)
class CollisionReportPdfCreated:
    """Successful collision-report PDF generation."""

    pdf_url: str


@dataclass(frozen=True, slots=True)
class CollisionReportPhotoDeleted:
    """Nullable status returned after deleting a report photo."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class CollisionReportPhotoUploaded:
    """Nullable status returned after uploading a report photo."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class CollisionReportError:
    """Required collision-report mutation error message."""

    message: str


@dataclass(frozen=True, slots=True)
class CollisionReportPhotoDeleteError:
    """Nullable collision-report photo deletion error message."""

    message: str | None


@dataclass(frozen=True, slots=True)
class UnselectedCollisionReportResult:
    """Future collision-report union branch selected only by type name."""

    typename: str


type CreateCollisionReportResult = (
    CollisionReportCreated | CollisionReportError | UnselectedCollisionReportResult
)
type CreateCollisionReportPdfResult = (
    CollisionReportPdfCreated | CollisionReportError | UnselectedCollisionReportResult
)
type DeleteCollisionReportPhotoResult = (
    CollisionReportPhotoDeleted | CollisionReportPhotoDeleteError | UnselectedCollisionReportResult
)
type UploadCollisionReportPhotoResult = (
    CollisionReportPhotoUploaded | CollisionReportError | UnselectedCollisionReportResult
)
