from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .common_inputs import AddressInput, address_input
from .finance_models import NCFAccountContractType, NCFCustomerType
from .graphql_input import (
    UNSET,
    UnsetType,
    optional_input_fields,
    serialize_datetime,
    serialize_enum,
)


@dataclass(frozen=True, slots=True)
class NCFNotificationPreferencesInput:
    """Required account and optional nullable NCF notification switches."""

    account_number: str
    is_payment_received: bool | UnsetType | None = UNSET
    is_statement_available: bool | UnsetType | None = UNSET
    is_payment_past_due: bool | UnsetType | None = UNSET
    is_payment_due_in_one_day: bool | UnsetType | None = UNSET


def ncf_connect_account_variables(
    vin: str,
    account_number: str,
    customer_type: NCFCustomerType | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize NCF account-link variables."""

    serialized_customer_type: object = (
        serialize_enum(customer_type)
        if isinstance(customer_type, NCFCustomerType)
        else customer_type
    )
    return optional_input_fields(
        vin=vin,
        customerType=serialized_customer_type,
        accountNumber=account_number,
    )


def account_number_variables(account_number: str) -> dict[str, object]:
    """Serialize a required finance account number."""

    return {"accountNumber": account_number}


def ncf_update_account_variables(
    account_number: str,
    address: AddressInput | UnsetType | None = UNSET,
    phone_number: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize independently optional NCF profile updates."""

    serialized_address: object = (
        address_input(address) if isinstance(address, AddressInput) else address
    )
    return optional_input_fields(
        accountNumber=account_number,
        address=serialized_address,
        phoneNumber=phone_number,
    )


def ncf_notification_preferences_variables(
    config: NCFNotificationPreferencesInput,
) -> dict[str, object]:
    """Serialize NCF notification-preference updates."""

    return {
        "input": optional_input_fields(
            accountNumber=config.account_number,
            isPaymentReceived=config.is_payment_received,
            isStatementAvailable=config.is_statement_available,
            isPaymentPastDue=config.is_payment_past_due,
            isPaymentDueInOneDay=config.is_payment_due_in_one_day,
        )
    }


def finance_document_variables(
    contract_number: str,
    document_number: str,
) -> dict[str, object]:
    """Serialize account-statement PDF variables."""

    return {"contractNumber": contract_number, "documentNumber": document_number}


def contract_number_variables(contract_number: str) -> dict[str, object]:
    """Serialize a required finance contract number."""

    return {"contractNumber": contract_number}


def invoice_pdf_variables(contract_number: str, uuid: str) -> dict[str, object]:
    """Serialize invoice PDF variables."""

    return {"contractNumber": contract_number, "uuid": uuid}


def ncf_account_statement_variables(
    start_date: date,
    end_date: date,
    contract_type: NCFAccountContractType,
) -> dict[str, object]:
    """Serialize an NCF statement period and contract type."""

    return {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "contractType": serialize_enum(contract_type),
    }


def ncf_payout_quote_variables(account_number: str, vin: str) -> dict[str, object]:
    """Serialize NCF payout-quote variables."""

    return {"accountNumber": account_number, "vin": vin}


def payment_history_variables(
    account_number: str,
    start_date: datetime,
    end_date: datetime,
) -> dict[str, object]:
    """Serialize an offset-aware payment-history period."""

    return {
        "accountNumber": account_number,
        "startDate": serialize_datetime(start_date),
        "endDate": serialize_datetime(end_date),
    }
