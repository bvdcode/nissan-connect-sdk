from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

from .account_models import (
    CreatePinError,
    CreatePinResult,
    DeleteAccountResult,
    MarketingNotificationPreferences,
    MarketingPreferencesResult,
    MarketingPreferenceType,
    MobileCarrierCode,
    MobileNetworkOperator,
    NCIMarketingPreferences,
    NissanIdDoesNotExist,
    NissanIdExists,
    NissanIdRequiresNmacPasswordReset,
    NissanIdRequiresOwnerPortalPasswordReset,
    NissanIdRequiresOwnerPortalProfileCompletion,
    NissanIdValidationResult,
    NNAMarketingPreferences,
    PinOperationSuccess,
    PinValidationError,
    SecurityQuestion,
    UnselectedAccountResult,
    UpdateAccountAddressError,
    UpdateAccountFirstNameError,
    UpdateAccountGeneralError,
    UpdateAccountLandlineNumberError,
    UpdateAccountLastNameError,
    UpdateAccountMobileNumberError,
    UpdateAccountPostalCodeError,
    UpdateAccountResult,
    UpdateAccountSuccess,
    UpdatedAccountAddress,
    UpdatePinResult,
    UserInfo,
)
from .exceptions import ResponseError


def parse_validate_nissan_id(
    data: Mapping[str, object],
) -> NissanIdValidationResult | None:
    """Parse every generated Nissan ID validation union branch."""

    root_field = "validateNissanID"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "NissanIdExists":
        return NissanIdExists(_required_string(root, "nissanId", f"{root_field}.nissanId"))
    if typename == "NissanIdDoesNotExist":
        return NissanIdDoesNotExist(_required_string(root, "nissanId", f"{root_field}.nissanId"))
    if typename == "NissanIdRequiresOwnerPortalPWReset":
        return NissanIdRequiresOwnerPortalPasswordReset(
            _required_string(root, "nissanId", f"{root_field}.nissanId"),
            _required_string(root, "link", f"{root_field}.link"),
        )
    if typename == "NissanIdRequiresOwnerPortalProfileCompletion":
        return NissanIdRequiresOwnerPortalProfileCompletion(
            _required_string(root, "nissanId", f"{root_field}.nissanId"),
            _required_string(root, "link", f"{root_field}.link"),
        )
    if typename == "NissanIdRequiresNMACPWReset":
        return NissanIdRequiresNmacPasswordReset(
            _required_string(root, "nissanId", f"{root_field}.nissanId"),
            _required_string(root, "link", f"{root_field}.link"),
        )
    return UnselectedAccountResult(typename)


def parse_security_questions(
    data: Mapping[str, object],
) -> tuple[SecurityQuestion | None, ...] | None:
    """Parse nullable security questions and nullable list items."""

    field = "securityQuestions"
    value = _required_field(data, field, field)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{field} is not a list")
    questions: list[SecurityQuestion | None] = []
    for index, item in enumerate(value):
        if item is None:
            questions.append(None)
            continue
        path = f"{field}[{index}]"
        question = _typed_object(item, path)
        questions.append(
            SecurityQuestion(
                _required_nullable_string(question, "id", f"{path}.id"),
                _required_nullable_string(question, "question", f"{path}.question"),
            )
        )
    return tuple(questions)


def parse_user_info(data: Mapping[str, object]) -> UserInfo | None:
    """Parse nullable signed-in user security flags."""

    root = _root(data, "user")
    if root is None:
        return None
    return UserInfo(
        pin_configured=_required_nullable_bool(root, "pinConfigured", "user.pinConfigured"),
        security_question_id=_required_nullable_string(
            root,
            "securityQuestionId",
            "user.securityQuestionId",
        ),
        is_lite_account=_required_nullable_bool(root, "isLiteAccount", "user.isLiteAccount"),
    )


def parse_terms_and_conditions(data: Mapping[str, object]) -> str | None:
    """Parse the nullable account terms scalar."""

    return _required_nullable_string(
        data,
        "termsAndConditions",
        "termsAndConditions",
    )


def parse_marketing_preferences(
    data: Mapping[str, object],
) -> MarketingPreferencesResult | None:
    """Parse the signed-in user's country-specific marketing preferences."""

    user = _root(data, "user")
    if user is None:
        return None
    preferences = _required_optional_typed_object(
        user,
        "countryMarketingPreferences",
        "user.countryMarketingPreferences",
    )
    if preferences is None:
        return None
    return _parse_country_marketing_preferences(
        preferences,
        "user.countryMarketingPreferences",
    )


def parse_create_pin(data: Mapping[str, object]) -> CreatePinResult | None:
    """Parse every generated CreatePin union branch."""

    root_field = "createPin"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "ResponseStatus":
        return PinOperationSuccess(
            _required_nullable_bool(root, "success", f"{root_field}.success")
        )
    if typename == "CreatePINError":
        return CreatePinError(_required_string(root, "message", f"{root_field}.message"))
    return UnselectedAccountResult(typename)


def parse_update_pin(data: Mapping[str, object]) -> UpdatePinResult | None:
    """Parse every generated UpdatePin union branch."""

    root_field = "updatePin"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "ResponseStatus":
        return PinOperationSuccess(
            _required_nullable_bool(root, "success", f"{root_field}.success")
        )
    if typename == "ValidationError":
        return PinValidationError(
            _required_nullable_string(root, "message", f"{root_field}.message")
        )
    return UnselectedAccountResult(typename)


def parse_update_account(data: Mapping[str, object]) -> UpdateAccountResult | None:
    """Parse every generated account-update union branch."""

    root_field = "updateAccount"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    message_path = f"{root_field}.message"
    if typename == "UpdateAccountFirstNameError":
        return UpdateAccountFirstNameError(_required_string(root, "message", message_path))
    if typename == "UpdateAccountLastNameError":
        return UpdateAccountLastNameError(_required_string(root, "message", message_path))
    if typename == "UpdateAccountAddressError":
        return UpdateAccountAddressError(_required_string(root, "message", message_path))
    if typename == "UpdateAccountPostalCodeError":
        return UpdateAccountPostalCodeError(_required_string(root, "message", message_path))
    if typename == "UpdateAccountMobileNumberError":
        return UpdateAccountMobileNumberError(_required_string(root, "message", message_path))
    if typename == "UpdateAccountLandlineNumberError":
        return UpdateAccountLandlineNumberError(_required_string(root, "message", message_path))
    if typename == "UpdateAccountGeneralError":
        return UpdateAccountGeneralError(_required_string(root, "message", message_path))
    if typename != "User":
        return UnselectedAccountResult(typename)
    address = _required_optional_typed_object(root, "address", f"{root_field}.address")
    carrier = _required_optional_typed_object(
        root,
        "mobileNetworkOperator",
        f"{root_field}.mobileNetworkOperator",
    )
    return UpdateAccountSuccess(
        first_name=_required_string(root, "firstName", f"{root_field}.firstName"),
        last_name=_required_string(root, "lastName", f"{root_field}.lastName"),
        email=_required_string(root, "email", f"{root_field}.email"),
        mobile_number=_required_nullable_string(
            root,
            "mobileNumber",
            f"{root_field}.mobileNumber",
        ),
        address=_parse_updated_address(address, f"{root_field}.address"),
        mobile_network_operator=_parse_mobile_network_operator(
            carrier,
            f"{root_field}.mobileNetworkOperator",
        ),
    )


def parse_delete_account(data: Mapping[str, object]) -> DeleteAccountResult | None:
    """Parse the nullable account-deletion status."""

    root_field = "deleteAccount"
    root = _root(data, root_field)
    if root is None:
        return None
    return DeleteAccountResult(_required_nullable_bool(root, "success", f"{root_field}.success"))


def parse_update_nci_marketing_preferences(
    data: Mapping[str, object],
) -> MarketingPreferencesResult | None:
    """Parse country preferences returned after an NCI update."""

    return _parse_updated_marketing_preferences(data, "updateNCIAccountPreferences")


def parse_update_nna_marketing_preferences(
    data: Mapping[str, object],
) -> MarketingPreferencesResult | None:
    """Parse country preferences returned after an NNA update."""

    return _parse_updated_marketing_preferences(data, "updateAccountPreferences")


def _parse_updated_marketing_preferences(
    data: Mapping[str, object],
    root_field: str,
) -> MarketingPreferencesResult | None:
    root = _root(data, root_field)
    if root is None:
        return None
    path = f"{root_field}.countryMarketingPreferences"
    preferences = _required_optional_typed_object(root, "countryMarketingPreferences", path)
    if preferences is None:
        return None
    return _parse_country_marketing_preferences(preferences, path)


def _parse_country_marketing_preferences(
    value: Mapping[str, object],
    path: str,
) -> MarketingPreferencesResult:
    typename = _typename(value, path)
    if typename == "NCIMarketingPreferences":
        return NCIMarketingPreferences(
            email=_required_nullable_bool(value, "email", f"{path}.email"),
            product_updates=_parse_notification_preferences(
                value,
                "productUpdates",
                f"{path}.productUpdates",
            ),
            news_events=_parse_notification_preferences(
                value,
                "newsEvents",
                f"{path}.newsEvents",
            ),
            offers_promotion=_parse_notification_preferences(
                value,
                "offersPromotion",
                f"{path}.offersPromotion",
            ),
        )
    if typename == "NNAMarketingPreferences":
        return NNAMarketingPreferences(
            newsletter=_marketing_preference_list(value, "newsletter", path),
            product_offers=_marketing_preference_list(value, "productOffers", path),
            service_offers=_marketing_preference_list(value, "serviceOffers", path),
            scheduled_maintenance=_marketing_preference_list(
                value,
                "scheduledMaintenance",
                path,
            ),
            feedback=_marketing_preference_list(value, "feedback", path),
        )
    return UnselectedAccountResult(typename)


def _parse_notification_preferences(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> MarketingNotificationPreferences | None:
    value = _required_optional_typed_object(container, field, path)
    if value is None:
        return None
    return MarketingNotificationPreferences(
        email=_required_nullable_bool(value, "email", f"{path}.email"),
        text_message=_required_nullable_bool(value, "textMessage", f"{path}.textMessage"),
        direct_mail=_required_nullable_bool(value, "directMail", f"{path}.directMail"),
        in_app=_required_nullable_bool(value, "inApp", f"{path}.inApp"),
        in_vehicle=_required_nullable_bool(value, "inVehicle", f"{path}.inVehicle"),
    )


def _marketing_preference_list(
    container: Mapping[str, object],
    field: str,
    parent_path: str,
) -> tuple[MarketingPreferenceType | None, ...] | None:
    path = f"{parent_path}.{field}"
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    result: list[MarketingPreferenceType | None] = []
    for index, item in enumerate(value):
        if item is None:
            result.append(None)
            continue
        result.append(_enum(item, MarketingPreferenceType, f"{path}[{index}]"))
    return tuple(result)


def _parse_updated_address(
    value: Mapping[str, object] | None,
    path: str,
) -> UpdatedAccountAddress | None:
    if value is None:
        return None
    return UpdatedAccountAddress(
        address_1=_required_nullable_string(value, "address1", f"{path}.address1"),
        address_2=_required_nullable_string(value, "address2", f"{path}.address2"),
        city=_required_nullable_string(value, "city", f"{path}.city"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
        country=_required_nullable_string(value, "country", f"{path}.country"),
        postal_code=_required_nullable_string(value, "postalCode", f"{path}.postalCode"),
        district=_required_nullable_string(value, "district", f"{path}.district"),
        street_number=_required_nullable_string(
            value,
            "streetNumber",
            f"{path}.streetNumber",
        ),
    )


def _parse_mobile_network_operator(
    value: Mapping[str, object] | None,
    path: str,
) -> MobileNetworkOperator | None:
    if value is None:
        return None
    return MobileNetworkOperator(
        code=_required_enum(value, "code", MobileCarrierCode, f"{path}.code"),
        id=_required_int(value, "id", f"{path}.id"),
        name=_required_string(value, "name", f"{path}.name"),
    )


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    value = data[root_field]
    if value is None:
        return None
    return _typed_object(value, root_field)


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _typename(value, path)
    return value


def _required_optional_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _typed_object(value, path)


def _typename(container: Mapping[str, object], path: str) -> str:
    return _required_string(container, "__typename", f"{path}.__typename")


def _required_field(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _required_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str:
    value = _required_field(container, field, path)
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _required_nullable_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _required_nullable_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_int(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> int:
    value = _required_field(container, field, path)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _required_nullable_int(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> int | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _required_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    return _enum(_required_field(container, field, path), enum_type, path)


def _enum[EnumT: StrEnum](value: object, enum_type: type[EnumT], path: str) -> EnumT:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    try:
        return enum_type(value)
    except ValueError:
        try:
            return enum_type("UNKNOWN__")
        except ValueError:
            raise ResponseError(f"{path} has an unsupported value: {value}") from None
