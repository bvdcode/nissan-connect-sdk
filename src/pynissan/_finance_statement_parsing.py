from __future__ import annotations

from collections.abc import Mapping

from ._finance_value_parsing import (
    _nullable_list,
    _required_date,
    _required_nullable_date,
    _required_nullable_datetime,
    _required_nullable_float,
)
from .account_parsing import (
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _typename,
)
from .finance_models import (
    NCFAccountStatement,
    NCFAccountStatementAccount,
    NCFAccountStatementSummary,
    NCFAccountStatementVehicle,
    NCFBillingStatement,
    NCFInvoiceSummary,
    NCFLeaseBillingStatementDetails,
    NCFLeaseTransactionDetails,
    NCFPaymentHistoryEntry,
    NCFPaymentHistoryLoanDetails,
    NCFStatementTransaction,
    UnselectedFinanceResult,
    VehicleCredit,
    VehicleCreditInfo,
)


def _parse_statement_summary(
    value: Mapping[str, object],
    path: str,
) -> NCFAccountStatementSummary:
    return NCFAccountStatementSummary(
        date=_required_date(value, "date", f"{path}.date"),
        document_number=_required_string(value, "documentNumber", f"{path}.documentNumber"),
    )


def _parse_vehicle_credit_info(value: Mapping[str, object], path: str) -> VehicleCreditInfo:
    credit_path = f"{path}.credit"
    credit = _required_optional_typed_object(value, "credit", credit_path)
    return VehicleCreditInfo(
        vin=_required_string(value, "vin", f"{path}.vin"),
        credit=_parse_credit(credit, credit_path),
    )


def _parse_credit(value: Mapping[str, object] | None, path: str) -> VehicleCredit | None:
    if value is None:
        return None
    return VehicleCredit(
        current_quota=_required_nullable_int(value, "currentQuota", f"{path}.currentQuota"),
        credit_type=_required_nullable_string(value, "creditType", f"{path}.creditType"),
        credit_status=_required_nullable_string(value, "creditStatus", f"{path}.creditStatus"),
        status_text=_required_nullable_string(value, "statusText", f"{path}.statusText"),
        next_payment_amount=_required_nullable_float(
            value, "nextPaymentAmount", f"{path}.nextPaymentAmount"
        ),
        next_payment_date=_required_nullable_date(
            value, "nextPaymentDate", f"{path}.nextPaymentDate"
        ),
        contract_number=_required_nullable_string(
            value, "contractNumber", f"{path}.contractNumber"
        ),
        term=_required_nullable_int(value, "term", f"{path}.term"),
        overdue_quotas=_required_nullable_string(value, "overdueQuotas", f"{path}.overdueQuotas"),
        id=_required_nullable_string(value, "id", f"{path}.id"),
        balance=_required_nullable_float(value, "balance", f"{path}.balance"),
        account_domiciliation=_required_nullable_string(
            value,
            "accountDomiciliation",
            f"{path}.accountDomiciliation",
        ),
        last_update=_required_nullable_date(value, "lastUpdate", f"{path}.lastUpdate"),
        overdue_amount=_required_nullable_float(value, "overdueAmount", f"{path}.overdueAmount"),
        start_date=_required_nullable_date(value, "startDate", f"{path}.startDate"),
        end_date=_required_nullable_date(value, "endDate", f"{path}.endDate"),
        total_overdue_amount=_required_nullable_float(
            value,
            "totalOverdueAmount",
            f"{path}.totalOverdueAmount",
        ),
        extended_rent=_required_nullable_float(value, "extendedRent", f"{path}.extendedRent"),
        support_email=_required_nullable_string(value, "supportEmail", f"{path}.supportEmail"),
        support_phone_number=_required_nullable_string(
            value,
            "supportPhoneNumber",
            f"{path}.supportPhoneNumber",
        ),
        terms_and_conditions=_required_nullable_string(
            value,
            "termsAndConditions",
            f"{path}.termsAndConditions",
        ),
        end_contract_email=_required_nullable_string(
            value,
            "endContractEmail",
            f"{path}.endContractEmail",
        ),
        credits_portal=_required_nullable_string(value, "creditsPortal", f"{path}.creditsPortal"),
    )


def _parse_invoice_summary(value: Mapping[str, object], path: str) -> NCFInvoiceSummary:
    return NCFInvoiceSummary(
        date=_required_date(value, "date", f"{path}.date"),
        uuid=_required_string(value, "uuid", f"{path}.uuid"),
    )


def _parse_account_statement_vehicle(
    value: Mapping[str, object],
    path: str,
) -> NCFAccountStatementVehicle:
    typename = _typename(value, path)
    if typename != "NCFFinancialVehicle":
        return UnselectedFinanceResult(typename)
    account_path = f"{path}.account"
    account = _required_optional_typed_object(value, "account", account_path)
    if account is None:
        return NCFAccountStatementAccount(None, None)
    statement_path = f"{account_path}.statement"
    statement = _required_optional_typed_object(account, "statement", statement_path)
    return NCFAccountStatementAccount(
        account_number=_required_nullable_string(
            account,
            "accountNumber",
            f"{account_path}.accountNumber",
        ),
        statement=_parse_account_statement(statement, statement_path),
    )


def _parse_account_statement(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFAccountStatement | None:
    if value is None:
        return None
    return NCFAccountStatement(
        billing_statements=_nullable_list(
            value,
            "billingStatements",
            f"{path}.billingStatements",
            _parse_billing_statement,
        ),
        transactions=_nullable_list(
            value,
            "transactions",
            f"{path}.transactions",
            _parse_statement_transaction,
        ),
    )


def _parse_billing_statement(value: Mapping[str, object], path: str) -> NCFBillingStatement:
    typename = _typename(value, path)
    lease_details = None
    if typename == "NCFAccountBillingStatementLease":
        lease_details = NCFLeaseBillingStatementDetails(
            prior_balance_amount=_required_nullable_float(
                value,
                "priorBalanceAmount",
                f"{path}.priorBalanceAmount",
            ),
            vehicle_year=_required_nullable_string(value, "vehicleYear", f"{path}.vehicleYear"),
            vehicle_model=_required_nullable_string(value, "vehicleModel", f"{path}.vehicleModel"),
            vehicle_make=_required_nullable_string(value, "vehicleMake", f"{path}.vehicleMake"),
        )
    return NCFBillingStatement(
        typename=typename,
        current_balance_amount=_required_nullable_float(
            value,
            "currentBalanceAmount",
            f"{path}.currentBalanceAmount",
        ),
        payment_due_date=_required_nullable_date(value, "paymentDueDate", f"{path}.paymentDueDate"),
        financial_account_id=_required_nullable_string(
            value,
            "financialAccountId",
            f"{path}.financialAccountId",
        ),
        statement_date=_required_nullable_date(value, "statementDate", f"{path}.statementDate"),
        total_amount_due=_required_nullable_float(
            value, "totalAmountDue", f"{path}.totalAmountDue"
        ),
        lease_details=lease_details,
    )


def _parse_statement_transaction(
    value: Mapping[str, object],
    path: str,
) -> NCFStatementTransaction:
    typename = _typename(value, path)
    lease_details = None
    if typename == "NCFAccountTransactionLease":
        lease_details = NCFLeaseTransactionDetails(
            payment_total_amount=_required_nullable_float(
                value,
                "paymentTotalAmount",
                f"{path}.paymentTotalAmount",
            ),
            payment_tax_amount=_required_nullable_float(
                value,
                "paymentTaxAmount",
                f"{path}.paymentTaxAmount",
            ),
            payment_description=_required_nullable_string(
                value,
                "paymentDescription",
                f"{path}.paymentDescription",
            ),
        )
    return NCFStatementTransaction(
        typename=typename,
        payment_amount=_required_nullable_float(value, "paymentAmount", f"{path}.paymentAmount"),
        financial_account_id=_required_nullable_string(
            value,
            "financialAccountId",
            f"{path}.financialAccountId",
        ),
        statement_date=_required_nullable_date(value, "statementDate", f"{path}.statementDate"),
        sequence_number=_required_nullable_string(value, "sequenceNo", f"{path}.sequenceNo"),
        lease_details=lease_details,
    )


def _parse_payment_history_entry(
    value: Mapping[str, object],
    path: str,
) -> NCFPaymentHistoryEntry:
    typename = _typename(value, path)
    loan_details = None
    if typename == "NCFPaymentHistoryTransactionLoan":
        loan_details = NCFPaymentHistoryLoanDetails(
            principle_amount=_required_nullable_float(
                value,
                "principleAmount",
                f"{path}.principleAmount",
            ),
            interest_amount=_required_nullable_float(
                value, "interestAmount", f"{path}.interestAmount"
            ),
        )
    return NCFPaymentHistoryEntry(
        typename=typename,
        type=_required_nullable_string(value, "type", f"{path}.type"),
        description=_required_nullable_string(value, "description", f"{path}.description"),
        effective_date=_required_nullable_datetime(value, "effectiveDate", f"{path}.effectiveDate"),
        process_date=_required_nullable_datetime(value, "processDate", f"{path}.processDate"),
        total_payment_amount=_required_nullable_float(
            value,
            "totalPaymentAmount",
            f"{path}.totalPaymentAmount",
        ),
        miscellaneous_fees=_required_nullable_float(
            value,
            "miscellaneousFees",
            f"{path}.miscellaneousFees",
        ),
        base_rent_amount=_required_nullable_float(
            value, "baseRentAmount", f"{path}.baseRentAmount"
        ),
        tax_amount=_required_nullable_float(value, "taxAmount", f"{path}.taxAmount"),
        late_fees=_required_nullable_float(value, "lateFees", f"{path}.lateFees"),
        admin_fees=_required_nullable_float(value, "adminFees", f"{path}.adminFees"),
        registration_fees=_required_nullable_float(
            value,
            "registrationFees",
            f"{path}.registrationFees",
        ),
        loan_details=loan_details,
    )
