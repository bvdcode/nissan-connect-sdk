from __future__ import annotations

from collections.abc import Mapping

from ._finance_account_parsing import _parse_financial_vehicle
from ._finance_statement_parsing import (
    _parse_account_statement_vehicle,
    _parse_invoice_summary,
    _parse_payment_history_entry,
    _parse_statement_summary,
    _parse_vehicle_credit_info,
)
from ._finance_value_parsing import (
    _nullable_list,
    _required_bool,
    _required_nullable_date,
    _required_nullable_float,
)
from .account_parsing import (
    _required_field,
    _required_nullable_bool,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typename,
)
from .exceptions import ResponseError
from .finance_models import (
    FinancialVehicle,
    NCFAccountStatementPDF,
    NCFAccountStatementSummary,
    NCFAccountStatementVehicle,
    NCFConnectAccountCoSignerAlreadyRegistered,
    NCFConnectAccountInternalError,
    NCFConnectAccountInvalidCombination,
    NCFConnectAccountPrimaryAlreadyRegistered,
    NCFConnectAccountResult,
    NCFConnectAccountSuccess,
    NCFDisconnectAccountFailure,
    NCFDisconnectAccountResult,
    NCFDisconnectAccountSuccess,
    NCFInvoicePDF,
    NCFInvoiceSummary,
    NCFNotificationPreferences,
    NCFPaymentHistoryEntry,
    NCFPayoutQuote,
    NCFUpdateAccountResult,
    NCFUpdateNotificationPreferencesError,
    NCFUpdateNotificationPreferencesResult,
    NCFUpdateNotificationPreferencesSuccess,
    UnselectedFinanceResult,
    VehicleCreditInfo,
)


def parse_ncf_connect_account(
    data: Mapping[str, object],
) -> NCFConnectAccountResult | None:
    """Parse every generated NCF account-link union branch."""

    field = "ncfConnectAccount"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "NCFConnectAccountSuccessResponse":
        return NCFConnectAccountSuccess(
            _required_nullable_bool(root, "success", f"{field}.success")
        )
    if typename == "NCFConnectAccountCoSignerAlreadyRegisteredErrorResponse":
        return NCFConnectAccountCoSignerAlreadyRegistered(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    if typename == "NCFConnectAccountInvalidVinAndAccountCombinationErrorResponse":
        return NCFConnectAccountInvalidCombination(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    if typename == "NCFConnectAccountInternalErrorResponse":
        return NCFConnectAccountInternalError(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    if typename == "NCFConnectAccountPrimaryAlreadyRegisteredErrorResponse":
        return NCFConnectAccountPrimaryAlreadyRegistered(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    return UnselectedFinanceResult(typename)


def parse_ncf_disconnect_account(
    data: Mapping[str, object],
) -> NCFDisconnectAccountResult | None:
    """Parse every generated NCF account-disconnection union branch."""

    field = "ncfDisconnectAccount"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "NCFDisconnectAccountSuccessResponse":
        return NCFDisconnectAccountSuccess(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    if typename == "NCFDisconnectAccountFailureResponse":
        return NCFDisconnectAccountFailure(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    return UnselectedFinanceResult(typename)


def parse_ncf_update_account(
    data: Mapping[str, object],
) -> NCFUpdateAccountResult | None:
    """Parse the nullable NCF profile-update status."""

    field = "ncfUpdateAccount"
    root = _root(data, field)
    if root is None:
        return None
    return NCFUpdateAccountResult(_required_nullable_bool(root, "success", f"{field}.success"))


def parse_ncf_update_notification_preferences(
    data: Mapping[str, object],
) -> NCFUpdateNotificationPreferencesResult | None:
    """Parse every generated NCF notification-update union branch."""

    field = "ncfUpdateNotificationPreferences"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == "NCFUpdateNotificationPreferencesSuccessResponse":
        success = _required_field(root, "success", f"{field}.success")
        if not isinstance(success, bool):
            raise ResponseError(f"{field}.success is not a boolean")
        return NCFUpdateNotificationPreferencesSuccess(success)
    if typename == "NCFUpdateNotificationPreferencesErrorResponse":
        return NCFUpdateNotificationPreferencesError(
            _required_nullable_string(root, "message", f"{field}.message")
        )
    return UnselectedFinanceResult(typename)


def parse_financial_vehicles(
    data: Mapping[str, object],
) -> tuple[FinancialVehicle | None, ...] | None:
    """Parse nullable NCF vehicles."""

    return _nullable_list(data, "financialVehicles", "financialVehicles", _parse_financial_vehicle)


def parse_account_statement_pdf(
    data: Mapping[str, object],
) -> NCFAccountStatementPDF | None:
    """Parse a nullable account-statement PDF payload."""

    field = "accountStatementPDF"
    root = _root(data, field)
    if root is None:
        return None
    return NCFAccountStatementPDF(
        document=_required_string(root, "document", f"{field}.document"),
        document_url=_required_string(root, "documentUrl", f"{field}.documentUrl"),
    )


def parse_account_statements(
    data: Mapping[str, object],
) -> tuple[NCFAccountStatementSummary | None, ...] | None:
    """Parse nullable account-statement summaries."""

    return _nullable_list(data, "accountStatements", "accountStatements", _parse_statement_summary)


def parse_vehicle_credit(
    data: Mapping[str, object],
) -> tuple[VehicleCreditInfo | None, ...] | None:
    """Parse nullable vehicle credit details."""

    return _nullable_list(data, "vehicles", "vehicles", _parse_vehicle_credit_info)


def parse_invoice_pdf(data: Mapping[str, object]) -> NCFInvoicePDF | None:
    """Parse a nullable invoice PDF payload."""

    field = "invoicePDF"
    root = _root(data, field)
    if root is None:
        return None
    return NCFInvoicePDF(
        uuid=_required_string(root, "uuid", f"{field}.uuid"),
        file=_required_string(root, "file", f"{field}.file"),
    )


def parse_invoices(
    data: Mapping[str, object],
) -> tuple[NCFInvoiceSummary | None, ...] | None:
    """Parse nullable invoice summaries."""

    return _nullable_list(data, "invoices", "invoices", _parse_invoice_summary)


def parse_ncf_account_statement(
    data: Mapping[str, object],
) -> tuple[NCFAccountStatementVehicle | None, ...] | None:
    """Parse nullable per-vehicle NCF billing statements."""

    return _nullable_list(
        data,
        "financialVehicles",
        "financialVehicles",
        _parse_account_statement_vehicle,
    )


def parse_ncf_payout_quote(data: Mapping[str, object]) -> NCFPayoutQuote | None:
    """Parse a nullable NCF loan or lease payout quote."""

    field = "ncfPayoutQuote"
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    early_termination_amount = None
    if typename == "NCFPayoutQuoteLease":
        early_termination_amount = _required_nullable_float(
            root,
            "earlyTerminationAmount",
            f"{field}.earlyTerminationAmount",
        )
    return NCFPayoutQuote(
        amount=_required_nullable_float(root, "amount", f"{field}.amount"),
        good_through_date=_required_nullable_date(
            root,
            "goodThroughDate",
            f"{field}.goodThroughDate",
        ),
        early_termination_amount=early_termination_amount,
    )


def parse_ncf_preferences(
    data: Mapping[str, object],
) -> NCFNotificationPreferences | None:
    """Parse nullable NCF notification preferences."""

    root = _root(data, "ncfPreferences")
    if root is None:
        return None
    field = "ncfPreferences.notificationPreferences"
    preferences = _required_optional_typed_object(root, "notificationPreferences", field)
    if preferences is None:
        return None
    return NCFNotificationPreferences(
        paperless_statement=_required_bool(
            preferences,
            "isPaperlessStatement",
            f"{field}.isPaperlessStatement",
        ),
        payment_due_in_one_day=_required_bool(
            preferences,
            "isPaymentDueInOneDay",
            f"{field}.isPaymentDueInOneDay",
        ),
        payment_received=_required_bool(
            preferences,
            "isPaymentReceived",
            f"{field}.isPaymentReceived",
        ),
        payment_past_due=_required_bool(
            preferences,
            "isPaymentPastDue",
            f"{field}.isPaymentPastDue",
        ),
        statement_available=_required_bool(
            preferences,
            "isStatementAvailable",
            f"{field}.isStatementAvailable",
        ),
    )


def parse_ncf_terms_and_conditions(data: Mapping[str, object]) -> str | None:
    """Parse nullable NCF terms."""

    return _required_nullable_string(
        data,
        "ncfTermsAndConditions",
        "ncfTermsAndConditions",
    )


def parse_payment_history(
    data: Mapping[str, object],
) -> tuple[NCFPaymentHistoryEntry | None, ...] | None:
    """Parse nullable NCF payment history."""

    return _nullable_list(data, "paymentHistory", "paymentHistory", _parse_payment_history_entry)
