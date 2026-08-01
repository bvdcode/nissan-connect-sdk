from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime

from .account_parsing import (
    _enum,
    _required_field,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .exceptions import ResponseError
from .finance_models import (
    FinancialVehicle,
    NCFAccountStatement,
    NCFAccountStatementAccount,
    NCFAccountStatementPDF,
    NCFAccountStatementSummary,
    NCFAccountStatementVehicle,
    NCFBillingAddress,
    NCFBillingStatement,
    NCFConnectAccountCoSignerAlreadyRegistered,
    NCFConnectAccountInternalError,
    NCFConnectAccountInvalidCombination,
    NCFConnectAccountPrimaryAlreadyRegistered,
    NCFConnectAccountResult,
    NCFConnectAccountSuccess,
    NCFCustomerType,
    NCFDisconnectAccountFailure,
    NCFDisconnectAccountResult,
    NCFDisconnectAccountSuccess,
    NCFFinancialAccount,
    NCFFinancialContract,
    NCFFinancialCustomer,
    NCFFinancialDealer,
    NCFFinancialRules,
    NCFFinancialVehicle,
    NCFInvoicePDF,
    NCFInvoiceSummary,
    NCFLeaseBillingStatementDetails,
    NCFLeaseDetails,
    NCFLeaseTransactionDetails,
    NCFLoanDetails,
    NCFNotificationPreferences,
    NCFPaymentHistoryEntry,
    NCFPaymentHistoryLoanDetails,
    NCFPayoutQuote,
    NCFStatementTransaction,
    NCFUpcomingPayment,
    NCFUpdateAccountResult,
    NCFUpdateNotificationPreferencesError,
    NCFUpdateNotificationPreferencesResult,
    NCFUpdateNotificationPreferencesSuccess,
    UnselectedFinanceResult,
    UnselectedFinancialVehicle,
    VehicleCredit,
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


def _parse_financial_vehicle(value: Mapping[str, object], path: str) -> FinancialVehicle:
    typename = _typename(value, path)
    vin = _required_string(value, "vin", f"{path}.vin")
    if typename != "NCFFinancialVehicle":
        return UnselectedFinancialVehicle(typename, vin)
    account_path = f"{path}.account"
    account = _required_optional_typed_object(value, "account", account_path)
    return NCFFinancialVehicle(
        vin=vin,
        model=_required_nullable_string(value, "model", f"{path}.model"),
        year=_required_nullable_string(value, "year", f"{path}.year"),
        image=_required_nullable_string(value, "image", f"{path}.image"),
        account=_parse_financial_account(account, account_path),
    )


def _parse_financial_account(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFFinancialAccount | None:
    if value is None:
        return None
    payment_path = f"{path}.upcomingPayment"
    payment = _required_optional_typed_object(value, "upcomingPayment", payment_path)
    contract_path = f"{path}.contract"
    contract = _required_optional_typed_object(value, "contract", contract_path)
    rules_path = f"{path}.rules"
    rules = _required_optional_typed_object(value, "rules", rules_path)
    customer_type = _required_field(value, "customerType", f"{path}.customerType")
    return NCFFinancialAccount(
        account_number=_required_nullable_string(value, "accountNumber", f"{path}.accountNumber"),
        upcoming_payment=_parse_upcoming_payment(payment, payment_path),
        customer_type=(
            None
            if customer_type is None
            else _enum(customer_type, NCFCustomerType, f"{path}.customerType")
        ),
        contract=_parse_financial_contract(contract, contract_path),
        rules=_parse_financial_rules(rules, rules_path),
    )


def _parse_upcoming_payment(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFUpcomingPayment | None:
    if value is None:
        return None
    return NCFUpcomingPayment(
        amount_due=_required_nullable_float(
            value, "upcomingPaymentDue", f"{path}.upcomingPaymentDue"
        ),
        due_date=_required_nullable_datetime(value, "dueDate", f"{path}.dueDate"),
        recent_payment=_required_nullable_float(value, "recentPayment", f"{path}.recentPayment"),
        recent_payment_date=_required_nullable_datetime(
            value,
            "recentPaymentDate",
            f"{path}.recentPaymentDate",
        ),
        overdue_balance=_required_nullable_float(value, "overdueBalance", f"{path}.overdueBalance"),
    )


def _parse_financial_contract(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFFinancialContract | None:
    if value is None:
        return None
    typename = _typename(value, path)
    customers = _nullable_list(value, "customers", f"{path}.customers", _parse_financial_customer)
    dealer_path = f"{path}.dealer"
    dealer = _required_optional_typed_object(value, "dealer", dealer_path)
    loan_details = None
    lease_details = None
    if typename == "NCFContractLoan":
        loan_details = NCFLoanDetails(
            original_balance=_required_nullable_float(
                value, "originalBalance", f"{path}.originalBalance"
            ),
            remaining_balance=_required_nullable_float(
                value, "remainingBalance", f"{path}.remainingBalance"
            ),
            apr=_required_nullable_float(value, "apr", f"{path}.apr"),
            principle_paid_amount=_required_nullable_float(
                value,
                "principlePaidAmount",
                f"{path}.principlePaidAmount",
            ),
            interest_paid_amount=_required_nullable_float(
                value,
                "interestPaidAmount",
                f"{path}.interestPaidAmount",
            ),
            payment_progress_percentage=_required_nullable_int(
                value,
                "paymentProgressPercentage",
                f"{path}.paymentProgressPercentage",
            ),
        )
    if typename == "NCFContractLease":
        lease_details = _parse_lease_details(value, path)
    return NCFFinancialContract(
        typename=typename,
        maturity_date=_required_nullable_datetime(value, "maturityDate", f"{path}.maturityDate"),
        start_date=_required_nullable_datetime(value, "startDate", f"{path}.startDate"),
        number_of_payments_made=_required_nullable_int(
            value,
            "numberOfPaymentsMade",
            f"{path}.numberOfPaymentsMade",
        ),
        customers=customers,
        dealer=_parse_financial_dealer(dealer, dealer_path),
        loan_details=loan_details,
        lease_details=lease_details,
    )


def _parse_financial_customer(value: Mapping[str, object], path: str) -> NCFFinancialCustomer:
    address_path = f"{path}.billingAddress"
    address = _required_optional_typed_object(value, "billingAddress", address_path)
    buyer_type = _required_field(value, "buyerType", f"{path}.buyerType")
    return NCFFinancialCustomer(
        first_name=_required_nullable_string(value, "firstName", f"{path}.firstName"),
        last_name=_required_nullable_string(value, "lastName", f"{path}.lastName"),
        buyer_type=(
            None if buyer_type is None else _enum(buyer_type, NCFCustomerType, f"{path}.buyerType")
        ),
        phone_number=_required_nullable_string(value, "phoneNumber", f"{path}.phoneNumber"),
        billing_address=_parse_billing_address(address, address_path),
    )


def _parse_billing_address(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFBillingAddress | None:
    if value is None:
        return None
    return NCFBillingAddress(
        address=_required_nullable_string(value, "address", f"{path}.address"),
        city=_required_nullable_string(value, "city", f"{path}.city"),
        zip_code=_required_nullable_string(value, "zipCode", f"{path}.zipCode"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
    )


def _parse_financial_dealer(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFFinancialDealer | None:
    if value is None:
        return None
    return NCFFinancialDealer(
        name=_required_nullable_string(value, "name", f"{path}.name"),
        phone_number=_required_nullable_string(value, "phoneNumber", f"{path}.phoneNumber"),
    )


def _parse_financial_rules(
    value: Mapping[str, object] | None,
    path: str,
) -> NCFFinancialRules | None:
    if value is None:
        return None
    return NCFFinancialRules(
        static_text=_required_nullable_string(value, "staticText", f"{path}.staticText"),
        get_payoff_quote=_required_nullable_bool(value, "getPayoffQuote", f"{path}.getPayoffQuote"),
        payment_history=_required_nullable_bool(value, "paymentHistory", f"{path}.paymentHistory"),
        contract_details=_required_nullable_bool(
            value, "contractDetails", f"{path}.contractDetails"
        ),
        progress_bar_maturity=_required_nullable_bool(
            value,
            "progressBarMaturity",
            f"{path}.progressBarMaturity",
        ),
    )


def _parse_lease_details(value: Mapping[str, object], path: str) -> NCFLeaseDetails:
    return NCFLeaseDetails(
        term=_required_nullable_float(value, "term", f"{path}.term"),
        payments_remaining=_required_nullable_float(
            value, "paymentsRemaining", f"{path}.paymentsRemaining"
        ),
        original_mileage=_required_nullable_float(
            value, "originalMileage", f"{path}.originalMileage"
        ),
        contracted_mileage=_required_nullable_float(
            value, "contractedMileage", f"{path}.contractedMileage"
        ),
        total_mileage_allowance=_required_nullable_float(
            value,
            "totalMileageAllowance",
            f"{path}.totalMileageAllowance",
        ),
        excess_mileage_charge_amount=_required_nullable_float(
            value,
            "excessMileageChargeAmount",
            f"{path}.excessMileageChargeAmount",
        ),
        disposition_fee_amount=_required_nullable_float(
            value,
            "dispositionFeeAmount",
            f"{path}.dispositionFeeAmount",
        ),
        residual_value=_required_nullable_float(value, "residualValue", f"{path}.residualValue"),
        adjusted_payment_amount=_required_nullable_float(
            value,
            "adjustedPaymentAmount",
            f"{path}.adjustedPaymentAmount",
        ),
        total_payment_amount=_required_nullable_float(
            value,
            "totalPaymentAmount",
            f"{path}.totalPaymentAmount",
        ),
        payment_tax_amount=_required_nullable_float(
            value, "paymentTaxAmount", f"{path}.paymentTaxAmount"
        ),
        payment_tax_rate=_required_nullable_float(
            value, "paymentTaxRate", f"{path}.paymentTaxRate"
        ),
        payment_progress_percentage=_required_nullable_int(
            value,
            "paymentProgressPercentage",
            f"{path}.paymentProgressPercentage",
        ),
        security_deposit_amount=_required_nullable_float(
            value,
            "securityDepositAmount",
            f"{path}.securityDepositAmount",
        ),
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


def _nullable_list[ItemT](
    container: Mapping[str, object],
    field: str,
    path: str,
    parser: Callable[[Mapping[str, object], str], ItemT],
) -> tuple[ItemT | None, ...] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    items: list[ItemT | None] = []
    for index, item in enumerate(value):
        if item is None:
            items.append(None)
            continue
        item_path = f"{path}[{index}]"
        items.append(parser(_typed_object(item, item_path), item_path))
    return tuple(items)


def _required_bool(container: Mapping[str, object], field: str, path: str) -> bool:
    value = _required_field(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


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


def _required_date(container: Mapping[str, object], field: str, path: str) -> date:
    value = _required_string(container, field, path)
    return _parse_date(value, path)


def _required_nullable_date(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> date | None:
    value = _required_nullable_string(container, field, path)
    return None if value is None else _parse_date(value, path)


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_nullable_string(container, field, path)
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date-time") from None


def _parse_date(value: str, path: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date") from None
