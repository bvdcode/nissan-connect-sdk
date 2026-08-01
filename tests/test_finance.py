from __future__ import annotations

import hashlib
from collections.abc import Awaitable, Mapping
from datetime import UTC, date, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    AddressInput,
    NCFAccountContractType,
    NCFConnectAccountSuccess,
    NCFCustomerType,
    NCFDisconnectAccountFailure,
    NCFNotificationPreferences,
    NCFNotificationPreferencesInput,
    NCFPaymentHistoryEntry,
    NCFPaymentHistoryLoanDetails,
    NCFPayoutQuote,
    NissanClient,
    ReadOnlyError,
    Tokens,
    UnselectedFinanceResult,
    UnselectedFinancialVehicle,
    VehicleCreditInfo,
    operations,
)
from pynissan.finance_inputs import (
    account_number_variables,
    finance_document_variables,
    invoice_pdf_variables,
    ncf_account_statement_variables,
    ncf_connect_account_variables,
    ncf_notification_preferences_variables,
    ncf_payout_quote_variables,
    ncf_update_account_variables,
    payment_history_variables,
)
from pynissan.finance_parsing import (
    parse_financial_vehicles,
    parse_ncf_account_statement,
    parse_ncf_connect_account,
    parse_ncf_disconnect_account,
    parse_ncf_payout_quote,
    parse_ncf_preferences,
    parse_ncf_update_notification_preferences,
    parse_payment_history,
    parse_vehicle_credit,
)

EXPECTED_OPERATIONS = {
    "NCF_CONNECT_ACCOUNT": "eb64b6703fe148c55e26a59b0dc29e2d28e67267a3f064cb48a59064a77b896c",
    "NCF_DISCONNECT_ACCOUNT": "c0e92d64f6cc319f2c804299427bcbf2de2a094f82dd022d515e8bb0d96332d0",
    "NCF_UPDATE_ACCOUNT": "512e60cf7ad47cd898ced786aef9ab42fe1023fa8a8f09fae4f07b0a91eef316",
    "NCF_UPDATE_NOTIFICATION_PREFERENCES": (
        "8ff2643cb091a5b5dfddd33452c8d2d124783dfc6f5955d453cbf1b66ec0e417"
    ),
    "FINANCIAL_VEHICLES": "0c26aa2fb725bcc6da1c91b0dfe3eee90657faaca9419810dafca51466b2e68b",
    "GET_ACCOUNT_STATEMENT_PDF": (
        "d0d9a460125763f1a1852344d1c30980d1c8c58b7032a30cfe4926bbd9c3f75a"
    ),
    "GET_ACCOUNT_STATEMENTS": "e6f8bbd7df344e1429f53bc161765b7f69f0da026ddf15ea0d4b6ce65a1d8a7d",
    "GET_CREDIT": "94266501084837bf2d4ef0dca3326b9f2147b9a88902b5e7218e284d19b014c8",
    "GET_INVOICE_PDF": "0f581c8c6fc0e1f6b5ed701196184afff1b5bb161d89d7a1ffbfe301fbb3824d",
    "GET_INVOICES": "e4b0e0348ae8cd5963e937d776663a762b14a449293976bda828735374cd840b",
    "NCF_ACCOUNT_STATEMENT": "2a82edfc8dbacadf95e6c82b52ce0180b67f5e9baacbf5ef392ebdac36e285b8",
    "NCF_PAYOUT_QUOTE": "6bf94c15258881030f6ec40d2054288401edf79f617d945e7b27bf8e552ab3e9",
    "NCF_PREFERENCES": "4484a489220beb655e170a914b0a35ca8255f164809e8e15f3b29a298a5eebe1",
    "NCF_TERMS_AND_CONDITIONS": (
        "f16189ddf5a2c23f7ee3766aa043656a33a302bffe6657759ecc8d8b9b4116a8"
    ),
    "PAYMENT_HISTORY": "e269c3294ba09c2c42850aeb06a57ed0681b1f97d492a1424f360b636319bb07",
}


class FakeResponse:
    def __init__(self, field: str, value: object) -> None:
        self.status = 200
        self._payload = {"data": {field: value}}

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


def make_client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def test_finance_operations_match_service_documents() -> None:
    for constant, expected_id in EXPECTED_OPERATIONS.items():
        document = getattr(operations, constant)
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_finance_inputs_preserve_omitted_and_explicit_null_fields() -> None:
    assert ncf_connect_account_variables("VIN", "ACCOUNT") == {
        "vin": "VIN",
        "accountNumber": "ACCOUNT",
    }
    assert ncf_connect_account_variables(
        "VIN",
        "ACCOUNT",
        NCFCustomerType.CO_SIGNER,
    ) == {"vin": "VIN", "customerType": "CO_SIGNER", "accountNumber": "ACCOUNT"}
    assert ncf_update_account_variables(
        "ACCOUNT",
        AddressInput(city="Franklin", state=None),
        None,
    ) == {
        "accountNumber": "ACCOUNT",
        "address": {"city": "Franklin", "state": None},
        "phoneNumber": None,
    }
    preferences = NCFNotificationPreferencesInput(
        "ACCOUNT",
        is_payment_received=True,
        is_statement_available=None,
    )
    assert ncf_notification_preferences_variables(preferences) == {
        "input": {
            "accountNumber": "ACCOUNT",
            "isPaymentReceived": True,
            "isStatementAvailable": None,
        }
    }
    assert ncf_account_statement_variables(
        date(2026, 1, 1),
        date(2026, 1, 31),
        NCFAccountContractType.LEASE,
    ) == {"startDate": "2026-01-01", "endDate": "2026-01-31", "contractType": "LEASE"}
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2026, 2, 1, tzinfo=UTC)
    assert payment_history_variables("ACCOUNT", start, end) == {
        "accountNumber": "ACCOUNT",
        "startDate": "2026-01-01T00:00:00+00:00",
        "endDate": "2026-02-01T00:00:00+00:00",
    }
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        ncf_connect_account_variables("VIN", "ACCOUNT", NCFCustomerType.UNKNOWN_VALUE)


def test_parse_finance_unions_and_future_branches() -> None:
    assert parse_ncf_connect_account(
        {
            "ncfConnectAccount": {
                "__typename": "NCFConnectAccountSuccessResponse",
                "success": None,
            }
        }
    ) == NCFConnectAccountSuccess(None)
    assert parse_ncf_disconnect_account(
        {
            "ncfDisconnectAccount": {
                "__typename": "NCFDisconnectAccountFailureResponse",
                "message": "Unable to disconnect",
            }
        }
    ) == NCFDisconnectAccountFailure("Unable to disconnect")
    assert parse_ncf_update_notification_preferences(
        {"ncfUpdateNotificationPreferences": {"__typename": "FutureResult"}}
    ) == UnselectedFinanceResult("FutureResult")
    assert parse_financial_vehicles(
        {"financialVehicles": [None, {"__typename": "FutureVehicle", "vin": "VIN"}]}
    ) == (None, UnselectedFinancialVehicle("FutureVehicle", "VIN"))
    assert parse_ncf_account_statement(
        {"financialVehicles": [{"__typename": "FutureVehicle"}]}
    ) == (UnselectedFinanceResult("FutureVehicle"),)


def test_parse_credit_quote_preferences_and_payment_history() -> None:
    assert parse_vehicle_credit(
        {"vehicles": [{"__typename": "Vehicle", "vin": "VIN", "credit": None}]}
    ) == (VehicleCreditInfo("VIN", None),)
    assert parse_ncf_payout_quote(
        {
            "ncfPayoutQuote": {
                "__typename": "NCFPayoutQuoteLease",
                "amount": 12500,
                "goodThroughDate": "2026-08-15",
                "earlyTerminationAmount": 250.5,
            }
        }
    ) == NCFPayoutQuote(12500.0, date(2026, 8, 15), 250.5)
    assert parse_ncf_preferences(
        {
            "ncfPreferences": {
                "__typename": "NCFPreferences",
                "notificationPreferences": {
                    "__typename": "NCFNotificationPreferences",
                    "isPaperlessStatement": True,
                    "isPaymentDueInOneDay": False,
                    "isPaymentReceived": True,
                    "isPaymentPastDue": False,
                    "isStatementAvailable": True,
                },
            }
        }
    ) == NCFNotificationPreferences(True, False, True, False, True)
    assert parse_payment_history(
        {
            "paymentHistory": [
                None,
                {
                    "__typename": "NCFPaymentHistoryTransactionLoan",
                    "type": "PAYMENT",
                    "description": None,
                    "effectiveDate": "2026-07-01T12:00:00Z",
                    "processDate": None,
                    "totalPaymentAmount": 500,
                    "miscellaneousFees": None,
                    "baseRentAmount": None,
                    "taxAmount": 10,
                    "lateFees": 0,
                    "adminFees": None,
                    "registrationFees": None,
                    "principleAmount": 400,
                    "interestAmount": 90,
                },
            ]
        }
    ) == (
        None,
        NCFPaymentHistoryEntry(
            "NCFPaymentHistoryTransactionLoan",
            "PAYMENT",
            None,
            datetime(2026, 7, 1, 12, tzinfo=UTC),
            None,
            500.0,
            None,
            None,
            10.0,
            0.0,
            None,
            None,
            NCFPaymentHistoryLoanDetails(400.0, 90.0),
        ),
    )


async def test_client_wires_all_finance_operations() -> None:
    session = FakeSession(
        FakeResponse("ncfConnectAccount", None),
        FakeResponse("ncfDisconnectAccount", None),
        FakeResponse("ncfUpdateAccount", None),
        FakeResponse("ncfUpdateNotificationPreferences", None),
        FakeResponse("financialVehicles", None),
        FakeResponse("accountStatementPDF", None),
        FakeResponse("accountStatements", None),
        FakeResponse("vehicles", None),
        FakeResponse("invoicePDF", None),
        FakeResponse("invoices", None),
        FakeResponse("financialVehicles", None),
        FakeResponse("ncfPayoutQuote", None),
        FakeResponse("ncfPreferences", None),
        FakeResponse("ncfTermsAndConditions", None),
        FakeResponse("paymentHistory", None),
    )
    sdk = make_client(session, read_only=False)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 31)
    start_time = datetime(2026, 1, 1, tzinfo=UTC)
    end_time = datetime(2026, 2, 1, tzinfo=UTC)
    preferences = NCFNotificationPreferencesInput("ACCOUNT")

    assert await sdk.async_ncf_connect_account("VIN", "ACCOUNT") is None
    assert await sdk.async_ncf_disconnect_account("ACCOUNT") is None
    assert await sdk.async_ncf_update_account("ACCOUNT") is None
    assert await sdk.async_ncf_update_notification_preferences(preferences) is None
    assert await sdk.async_get_financial_vehicles() is None
    assert await sdk.async_get_account_statement_pdf("CONTRACT", "DOCUMENT") is None
    assert await sdk.async_get_account_statements("CONTRACT") is None
    assert await sdk.async_get_vehicle_credit() is None
    assert await sdk.async_get_invoice_pdf("CONTRACT", "UUID") is None
    assert await sdk.async_get_invoices("CONTRACT") is None
    assert (
        await sdk.async_get_ncf_account_statement(
            start_date,
            end_date,
            NCFAccountContractType.LEASE,
        )
        is None
    )
    assert await sdk.async_get_ncf_payout_quote("ACCOUNT", "VIN") is None
    assert await sdk.async_get_ncf_preferences("ACCOUNT") is None
    assert await sdk.async_get_ncf_terms_and_conditions() is None
    assert await sdk.async_get_payment_history("ACCOUNT", start_time, end_time) is None

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "NCFConnectAccount",
        "NCFDisconnectAccount",
        "NCFUpdateAccount",
        "NCFUpdateNotificationPreferences",
        "FinancialVehicles",
        "GetAccountStatementPDF",
        "GetAccountStatements",
        "GetCredit",
        "GetInvoicePDF",
        "GetInvoices",
        "NCFAccountStatement",
        "NCFPayoutQuote",
        "NCFPreferences",
        "NCFTermsAndConditions",
        "PaymentHistory",
    ]
    assert [payload["variables"] for payload in payloads] == [
        ncf_connect_account_variables("VIN", "ACCOUNT"),
        account_number_variables("ACCOUNT"),
        ncf_update_account_variables("ACCOUNT"),
        ncf_notification_preferences_variables(preferences),
        {},
        finance_document_variables("CONTRACT", "DOCUMENT"),
        {"contractNumber": "CONTRACT"},
        {},
        invoice_pdf_variables("CONTRACT", "UUID"),
        {"contractNumber": "CONTRACT"},
        ncf_account_statement_variables(start_date, end_date, NCFAccountContractType.LEASE),
        ncf_payout_quote_variables("ACCOUNT", "VIN"),
        account_number_variables("ACCOUNT"),
        {},
        payment_history_variables("ACCOUNT", start_time, end_time),
    ]


async def test_read_only_mode_blocks_every_finance_mutation_before_network() -> None:
    session = FakeSession()
    sdk = make_client(session, read_only=True)
    calls: tuple[Awaitable[object], ...] = (
        sdk.async_ncf_connect_account("VIN", "ACCOUNT"),
        sdk.async_ncf_disconnect_account("ACCOUNT"),
        sdk.async_ncf_update_account("ACCOUNT"),
        sdk.async_ncf_update_notification_preferences(NCFNotificationPreferencesInput("ACCOUNT")),
    )

    for call in calls:
        with pytest.raises(ReadOnlyError):
            await call

    assert session.calls == []
