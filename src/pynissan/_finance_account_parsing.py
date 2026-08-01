from __future__ import annotations

from collections.abc import Mapping

from ._finance_value_parsing import (
    _nullable_list,
    _required_nullable_datetime,
    _required_nullable_float,
)
from .account_parsing import (
    _enum,
    _required_field,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _typename,
)
from .finance_models import (
    FinancialVehicle,
    NCFBillingAddress,
    NCFCustomerType,
    NCFFinancialAccount,
    NCFFinancialContract,
    NCFFinancialCustomer,
    NCFFinancialDealer,
    NCFFinancialRules,
    NCFFinancialVehicle,
    NCFLeaseDetails,
    NCFLoanDetails,
    NCFUpcomingPayment,
    UnselectedFinancialVehicle,
)


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
