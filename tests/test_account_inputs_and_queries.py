from __future__ import annotations

import hashlib

import pytest

from pynissan import (
    UNSET,
    AddressInput,
    MarketingNotificationPreferences,
    MarketingPreferenceInput,
    MarketingPreferenceType,
    NCIMarketingPreferenceInput,
    NCIMarketingPreferences,
    NissanIdExists,
    NissanIdRequiresOwnerPortalPasswordReset,
    NNAMarketingPreferences,
    NotificationPreferenceTogglesInput,
    RegisterAccountAddressInput,
    RegisterAccountInput,
    SecurityQuestion,
    UnselectedAccountResult,
    UpdateAccountInput,
    UserInfo,
    operations,
)
from pynissan.account_inputs import (
    register_account_variables,
    update_account_variables,
    update_nci_marketing_preferences_variables,
    update_nna_marketing_preferences_variables,
)
from pynissan.account_parsing import (
    parse_marketing_preferences,
    parse_security_questions,
    parse_terms_and_conditions,
    parse_user_info,
    parse_validate_nissan_id,
)
from pynissan.exceptions import ResponseError

EXPECTED_OPERATIONS = {
    "VALIDATE_NISSAN_ID": "b5f146397db98fabeae691a05a8f2105d5f0467f6249d8d9aa2e3cbf2f78b496",
    "SECURITY_QUESTIONS": "0f4e903f6e7aaab9f1d395f63389b5e851a620b7aae75fb0f2c2590c832eb3ee",
    "USER_INFO": "e90c04b6e66bda2df2f3017a3ddfae4c3ca8780c1f883d199c74390acc786287",
    "TERMS_AND_CONDITIONS": "7ce8d6e19ea35543909809c8eb0c221a29dab74eb312b4a54ca251964bd70c17",
    "MARKETING_PREFERENCES": "281cf505506de3bb2011c410413cad23f6e12baae9097c4089aa0d55c6461a7d",
    "REGISTER_ACCOUNT": "f3306b7a7b99ae529b4bf40cf2d4dc89aff592ffa27d71950bdda418a138a76a",
    "NCAR_ICAR_REGISTER_ACCOUNT": (
        "75e5b49f52d986ba013048f306a24dfb97bbaf72fb5f5ca3573d2f27b93a76d2"
    ),
    "NCAR_ICAR_VERIFY_ACCOUNT": (
        "7e26704ab9c5bf1cb164adb26e2173cb00e2c936a378648c1034f33d5fe34c3c"
    ),
    "NCAR_ICAR_CUSTOMER_ENROLLMENT": (
        "d857de7c920940fa00b5cf4dfedf51805a55c1156954b5016144a7f1ba54cbf9"
    ),
    "NCAR_ICAR_GENERATE_OTP": ("50f54a2e7c81b43e91dcf0f223c9f962d34f93bdeda9a4b7021d975dc6370625"),
    "NCAR_ICAR_VERIFY_OTP": ("9efcc780691e03a32ee58344f4017a28008c8e2735ff4e0c67ed756f05ab5eb2"),
    "GENERATE_OTP": "c6c7a86861f37af8adb5376d3d73cc42e2ec045fe064c6d39d7c0de07ec9c612",
    "VERIFY_OTP": "7d165e2df809afaf6ba02224431b4d829cb1938d09487574643814ec99980f64",
    "CREATE_PIN": "181d5a83c7afa1cbae2b5b778b722fbc37c76f971ca572dbba1e395dd306c98a",
    "UPDATE_PIN": "b99a8380729759799933da39704f52703b4cab6131cf45ed9211d3730fd218a8",
    "UPDATE_ACCOUNT": "aad3256b184b448f93a68f725ba963908f532d6f381e1e5fa2a99851b3d81d14",
    "DELETE_ACCOUNT": "c82dce2ce140e41c131860bc25d3c2c67b91d3c8f4cb7cae0fdb9e0d3e70597e",
    "UPDATE_NCI_MARKETING_PREFERENCES": (
        "fcb00c4f6a74e8e25da1764e2fcc61866b924f9bf8b18bd317e866e2757568d2"
    ),
    "UPDATE_NNA_MARKETING_PREFERENCES": (
        "b1e334a1e2b9a92e58ad12d0ad10a967ea17d3c7dc7c4de73a88bb74607c3cf8"
    ),
}


@pytest.mark.parametrize(("constant", "expected_id"), EXPECTED_OPERATIONS.items())
def test_account_operations_match_service_documents(constant: str, expected_id: str) -> None:
    document = getattr(operations, constant)
    operation_id = getattr(operations, f"{constant}_OPERATION_ID")

    assert operation_id == expected_id
    assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_register_account_variables_preserve_nested_apollo_optionality() -> None:
    config = RegisterAccountInput(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.test",
        phone_number="+15555550100",
        password="secret",
        address=RegisterAccountAddressInput(
            address_1="1 Main St",
            city="Franklin",
            state="TN",
            postal_code="37064",
            country="US",
            address_2=None,
        ),
        second_last_name=None,
        mobile_carrier_id=7,
        marketing_preferences=MarketingPreferenceInput(
            newsletter=(MarketingPreferenceType.EMAIL,),
            product_offers=(),
            service_offers=(MarketingPreferenceType.SMS,),
            scheduled_maintenance=(MarketingPreferenceType.IAM,),
            feedback=(MarketingPreferenceType.TELEPHONE,),
        ),
    )

    assert register_account_variables(config) == {
        "config": {
            "firstName": "Ada",
            "lastName": "Lovelace",
            "secondLastName": None,
            "email": "ada@example.test",
            "phoneNumber": "+15555550100",
            "mobileCarrierId": 7,
            "password": "secret",
            "address": {
                "address1": "1 Main St",
                "address2": None,
                "city": "Franklin",
                "state": "TN",
                "postalCode": "37064",
                "country": "US",
            },
            "marketingPreferences": {
                "newsletter": ["EMAIL"],
                "productOffers": [],
                "serviceOffers": ["SMS"],
                "scheduledMaintenance": ["IAM"],
                "feedback": ["TELEPHONE"],
            },
        }
    }


def test_account_update_variables_distinguish_omission_and_null() -> None:
    assert update_account_variables() == {}
    assert update_account_variables(None) == {"config": None}
    assert update_account_variables(
        UpdateAccountInput(first_name="Ada", email=None, address=AddressInput(city="Franklin"))
    ) == {
        "config": {
            "firstName": "Ada",
            "email": None,
            "address": {"city": "Franklin"},
        }
    }


def test_marketing_input_variables_preserve_every_schema_shape() -> None:
    nci = NCIMarketingPreferenceInput(
        email=True,
        offers_promotion=NotificationPreferenceTogglesInput(
            email=False,
            text_message=None,
            in_app=True,
        ),
        news_events=None,
    )
    assert update_nci_marketing_preferences_variables(nci) == {
        "marketingPreferences": {
            "email": True,
            "offersPromotion": {
                "email": False,
                "textMessage": None,
                "inApp": True,
            },
            "newsEvents": None,
        }
    }
    assert update_nna_marketing_preferences_variables() == {}
    assert update_nna_marketing_preferences_variables(None) == {"marketingPreferences": None}


def test_marketing_inputs_reject_unknown_enum_values() -> None:
    config = MarketingPreferenceInput(
        newsletter=(MarketingPreferenceType.UNKNOWN_VALUE,),
        product_offers=(),
        service_offers=(),
        scheduled_maintenance=(),
        feedback=(),
        promotion_offers=UNSET,
    )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        update_nna_marketing_preferences_variables(config)


def test_parse_nissan_id_validation_known_reset_and_future_results() -> None:
    assert parse_validate_nissan_id(
        {"validateNissanID": {"__typename": "NissanIdExists", "nissanId": "ada"}}
    ) == NissanIdExists("ada")
    assert parse_validate_nissan_id(
        {
            "validateNissanID": {
                "__typename": "NissanIdRequiresOwnerPortalPWReset",
                "nissanId": "ada",
                "link": "https://example.test/reset",
            }
        }
    ) == NissanIdRequiresOwnerPortalPasswordReset(
        "ada",
        "https://example.test/reset",
    )
    assert parse_validate_nissan_id(
        {"validateNissanID": {"__typename": "FutureValidationResult"}}
    ) == UnselectedAccountResult("FutureValidationResult")


def test_parse_security_questions_preserves_nullable_list_and_items() -> None:
    assert parse_security_questions({"securityQuestions": None}) is None
    assert parse_security_questions(
        {
            "securityQuestions": [
                None,
                {
                    "__typename": "SecurityQuestion",
                    "id": None,
                    "question": "First car?",
                },
            ]
        }
    ) == (None, SecurityQuestion(None, "First car?"))


def test_parse_user_info_and_terms_preserve_nullability() -> None:
    assert parse_user_info(
        {
            "user": {
                "__typename": "User",
                "pinConfigured": None,
                "securityQuestionId": "42",
                "isLiteAccount": False,
            }
        }
    ) == UserInfo(None, "42", False)
    assert parse_user_info({"user": None}) is None
    assert parse_terms_and_conditions({"termsAndConditions": None}) is None
    assert parse_terms_and_conditions({"termsAndConditions": "Terms"}) == "Terms"


def test_parse_nci_marketing_preferences_preserves_nullable_toggles() -> None:
    assert parse_marketing_preferences(
        {
            "user": {
                "__typename": "User",
                "countryMarketingPreferences": {
                    "__typename": "NCIMarketingPreferences",
                    "email": True,
                    "productUpdates": {
                        "__typename": "NCIMarketingPreferenceProductUpdates",
                        "email": True,
                        "textMessage": None,
                        "directMail": False,
                        "inApp": True,
                        "inVehicle": None,
                    },
                    "newsEvents": None,
                    "offersPromotion": None,
                },
            }
        }
    ) == NCIMarketingPreferences(
        True,
        MarketingNotificationPreferences(True, None, False, True, None),
        None,
        None,
    )


def test_parse_nna_marketing_preferences_preserves_nullable_lists_and_items() -> None:
    assert parse_marketing_preferences(
        {
            "user": {
                "__typename": "User",
                "countryMarketingPreferences": {
                    "__typename": "NNAMarketingPreferences",
                    "newsletter": ["EMAIL", None, "FUTURE"],
                    "productOffers": None,
                    "serviceOffers": [],
                    "scheduledMaintenance": ["SMS"],
                    "feedback": ["IAM"],
                },
            }
        }
    ) == NNAMarketingPreferences(
        (MarketingPreferenceType.EMAIL, None, MarketingPreferenceType.UNKNOWN_VALUE),
        None,
        (),
        (MarketingPreferenceType.SMS,),
        (MarketingPreferenceType.IAM,),
    )


def test_account_query_parsers_reject_missing_or_malformed_fields() -> None:
    with pytest.raises(ResponseError, match="securityQuestions is missing"):
        parse_security_questions({})
    with pytest.raises(ResponseError, match=r"user\.pinConfigured is not a boolean"):
        parse_user_info(
            {
                "user": {
                    "__typename": "User",
                    "pinConfigured": "yes",
                    "securityQuestionId": None,
                    "isLiteAccount": None,
                }
            }
        )
