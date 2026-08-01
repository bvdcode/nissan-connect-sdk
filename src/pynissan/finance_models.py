from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class NCFCustomerType(StrEnum):
    """Known NCF customer roles."""

    PRIMARY = "PRIMARY"
    CO_SIGNER = "CO_SIGNER"
    UNKNOWN_VALUE = "UNKNOWN__"


class NCFAccountContractType(StrEnum):
    """Known NCF statement contract types."""

    RETAIL = "RETAIL"
    LEASE = "LEASE"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class UnselectedFinanceResult:
    """Future finance union branch selected only by type name."""

    typename: str


@dataclass(frozen=True, slots=True)
class NCFConnectAccountSuccess:
    """Nullable status returned after linking an NCF account."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class NCFFinanceMessageResult:
    """Base for finance union branches with nullable messages."""

    message: str | None


@dataclass(frozen=True, slots=True)
class NCFConnectAccountCoSignerAlreadyRegistered(NCFFinanceMessageResult):
    """The co-signer is already registered."""


@dataclass(frozen=True, slots=True)
class NCFConnectAccountInvalidCombination(NCFFinanceMessageResult):
    """VIN and account number do not form a valid combination."""


@dataclass(frozen=True, slots=True)
class NCFConnectAccountInternalError(NCFFinanceMessageResult):
    """Internal account-link failure."""


@dataclass(frozen=True, slots=True)
class NCFConnectAccountPrimaryAlreadyRegistered(NCFFinanceMessageResult):
    """The primary borrower is already registered."""


type NCFConnectAccountResult = (
    NCFConnectAccountSuccess
    | NCFConnectAccountCoSignerAlreadyRegistered
    | NCFConnectAccountInvalidCombination
    | NCFConnectAccountInternalError
    | NCFConnectAccountPrimaryAlreadyRegistered
    | UnselectedFinanceResult
)


@dataclass(frozen=True, slots=True)
class NCFDisconnectAccountSuccess(NCFFinanceMessageResult):
    """Successful NCF account disconnection."""


@dataclass(frozen=True, slots=True)
class NCFDisconnectAccountFailure(NCFFinanceMessageResult):
    """Failed NCF account disconnection."""


type NCFDisconnectAccountResult = (
    NCFDisconnectAccountSuccess | NCFDisconnectAccountFailure | UnselectedFinanceResult
)


@dataclass(frozen=True, slots=True)
class NCFUpdateAccountResult:
    """Nullable status returned after updating an NCF account."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class NCFUpdateNotificationPreferencesSuccess:
    """Successful NCF notification-preference update."""

    success: bool


@dataclass(frozen=True, slots=True)
class NCFUpdateNotificationPreferencesError(NCFFinanceMessageResult):
    """Failed NCF notification-preference update."""


type NCFUpdateNotificationPreferencesResult = (
    NCFUpdateNotificationPreferencesSuccess
    | NCFUpdateNotificationPreferencesError
    | UnselectedFinanceResult
)


@dataclass(frozen=True, slots=True)
class NCFUpcomingPayment:
    """Nullable upcoming, recent, and overdue payment amounts."""

    amount_due: float | None
    due_date: datetime | None
    recent_payment: float | None
    recent_payment_date: datetime | None
    overdue_balance: float | None


@dataclass(frozen=True, slots=True)
class NCFBillingAddress:
    """Nullable billing-address fields for an NCF customer."""

    address: str | None
    city: str | None
    zip_code: str | None
    state: str | None


@dataclass(frozen=True, slots=True)
class NCFFinancialCustomer:
    """Nullable customer fields attached to a finance contract."""

    first_name: str | None
    last_name: str | None
    buyer_type: NCFCustomerType | None
    phone_number: str | None
    billing_address: NCFBillingAddress | None


@dataclass(frozen=True, slots=True)
class NCFFinancialDealer:
    """Nullable originating dealer details."""

    name: str | None
    phone_number: str | None


@dataclass(frozen=True, slots=True)
class NCFLoanDetails:
    """Nullable values selected for a retail loan contract."""

    original_balance: float | None
    remaining_balance: float | None
    apr: float | None
    principle_paid_amount: float | None
    interest_paid_amount: float | None
    payment_progress_percentage: int | None


@dataclass(frozen=True, slots=True)
class NCFLeaseDetails:
    """Nullable values selected for a lease contract."""

    term: float | None
    payments_remaining: float | None
    original_mileage: float | None
    contracted_mileage: float | None
    total_mileage_allowance: float | None
    excess_mileage_charge_amount: float | None
    disposition_fee_amount: float | None
    residual_value: float | None
    adjusted_payment_amount: float | None
    total_payment_amount: float | None
    payment_tax_amount: float | None
    payment_tax_rate: float | None
    payment_progress_percentage: int | None
    security_deposit_amount: float | None


@dataclass(frozen=True, slots=True)
class NCFFinancialContract:
    """Common contract fields and type-specific loan or lease values."""

    typename: str
    maturity_date: datetime | None
    start_date: datetime | None
    number_of_payments_made: int | None
    customers: tuple[NCFFinancialCustomer | None, ...] | None
    dealer: NCFFinancialDealer | None
    loan_details: NCFLoanDetails | None
    lease_details: NCFLeaseDetails | None


@dataclass(frozen=True, slots=True)
class NCFFinancialRules:
    """Nullable presentation and feature rules for a finance account."""

    static_text: str | None
    get_payoff_quote: bool | None
    payment_history: bool | None
    contract_details: bool | None
    progress_bar_maturity: bool | None


@dataclass(frozen=True, slots=True)
class NCFFinancialAccount:
    """Finance account, payment, contract, and rule details."""

    account_number: str | None
    upcoming_payment: NCFUpcomingPayment | None
    customer_type: NCFCustomerType | None
    contract: NCFFinancialContract | None
    rules: NCFFinancialRules | None


@dataclass(frozen=True, slots=True)
class NCFFinancialVehicle:
    """Vehicle data linked to an NCF account."""

    vin: str
    model: str | None
    year: str | None
    image: str | None
    account: NCFFinancialAccount | None


@dataclass(frozen=True, slots=True)
class UnselectedFinancialVehicle:
    """Future financial-vehicle type with its universally selected VIN."""

    typename: str
    vin: str


type FinancialVehicle = NCFFinancialVehicle | UnselectedFinancialVehicle


@dataclass(frozen=True, slots=True)
class NCFAccountStatementPDF:
    """Required account-statement document and URL."""

    document: str
    document_url: str


@dataclass(frozen=True, slots=True)
class NCFAccountStatementSummary:
    """Account-statement date and document number."""

    date: date
    document_number: str


@dataclass(frozen=True, slots=True)
class VehicleCredit:
    """Nullable credit fields attached to a vehicle."""

    current_quota: int | None
    credit_type: str | None
    credit_status: str | None
    status_text: str | None
    next_payment_amount: float | None
    next_payment_date: date | None
    contract_number: str | None
    term: int | None
    overdue_quotas: str | None
    id: str | None
    balance: float | None
    account_domiciliation: str | None
    last_update: date | None
    overdue_amount: float | None
    start_date: date | None
    end_date: date | None
    total_overdue_amount: float | None
    extended_rent: float | None
    support_email: str | None
    support_phone_number: str | None
    terms_and_conditions: str | None
    end_contract_email: str | None
    credits_portal: str | None


@dataclass(frozen=True, slots=True)
class VehicleCreditInfo:
    """Vehicle VIN and its nullable credit details."""

    vin: str
    credit: VehicleCredit | None


@dataclass(frozen=True, slots=True)
class NCFInvoicePDF:
    """Required invoice UUID and file content."""

    uuid: str
    file: str


@dataclass(frozen=True, slots=True)
class NCFInvoiceSummary:
    """Invoice date and UUID."""

    date: date
    uuid: str


@dataclass(frozen=True, slots=True)
class NCFLeaseBillingStatementDetails:
    """Nullable lease-only billing-statement details."""

    prior_balance_amount: float | None
    vehicle_year: str | None
    vehicle_model: str | None
    vehicle_make: str | None


@dataclass(frozen=True, slots=True)
class NCFBillingStatement:
    """Common statement fields and optional lease details."""

    typename: str
    current_balance_amount: float | None
    payment_due_date: date | None
    financial_account_id: str | None
    statement_date: date | None
    total_amount_due: float | None
    lease_details: NCFLeaseBillingStatementDetails | None


@dataclass(frozen=True, slots=True)
class NCFLeaseTransactionDetails:
    """Nullable lease-only transaction values."""

    payment_total_amount: float | None
    payment_tax_amount: float | None
    payment_description: str | None


@dataclass(frozen=True, slots=True)
class NCFStatementTransaction:
    """Common statement transaction fields and optional lease details."""

    typename: str
    payment_amount: float | None
    financial_account_id: str | None
    statement_date: date | None
    sequence_number: str | None
    lease_details: NCFLeaseTransactionDetails | None


@dataclass(frozen=True, slots=True)
class NCFAccountStatement:
    """Nullable billing statement and transaction lists."""

    billing_statements: tuple[NCFBillingStatement | None, ...] | None
    transactions: tuple[NCFStatementTransaction | None, ...] | None


@dataclass(frozen=True, slots=True)
class NCFAccountStatementAccount:
    """Account number and nullable generated statement."""

    account_number: str | None
    statement: NCFAccountStatement | None


type NCFAccountStatementVehicle = NCFAccountStatementAccount | UnselectedFinanceResult


@dataclass(frozen=True, slots=True)
class NCFPayoutQuote:
    """Nullable payout amount, date, and lease termination amount."""

    amount: float | None
    good_through_date: date | None
    early_termination_amount: float | None


@dataclass(frozen=True, slots=True)
class NCFNotificationPreferences:
    """Required finance notification switches."""

    paperless_statement: bool
    payment_due_in_one_day: bool
    payment_received: bool
    payment_past_due: bool
    statement_available: bool


@dataclass(frozen=True, slots=True)
class NCFPaymentHistoryLoanDetails:
    """Nullable loan-only payment allocation."""

    principle_amount: float | None
    interest_amount: float | None


@dataclass(frozen=True, slots=True)
class NCFPaymentHistoryEntry:
    """Common payment-history fields and optional loan details."""

    typename: str
    type: str | None
    description: str | None
    effective_date: datetime | None
    process_date: datetime | None
    total_payment_amount: float | None
    miscellaneous_fees: float | None
    base_rent_amount: float | None
    tax_amount: float | None
    late_fees: float | None
    admin_fees: float | None
    registration_fees: float | None
    loan_details: NCFPaymentHistoryLoanDetails | None
