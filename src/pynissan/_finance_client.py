from __future__ import annotations

from datetime import date, datetime

from . import operations
from ._client_base import _NissanClientBase
from .common_inputs import AddressInput
from .finance_inputs import (
    NCFNotificationPreferencesInput,
    account_number_variables,
    contract_number_variables,
    finance_document_variables,
    invoice_pdf_variables,
    ncf_account_statement_variables,
    ncf_connect_account_variables,
    ncf_notification_preferences_variables,
    ncf_payout_quote_variables,
    ncf_update_account_variables,
    payment_history_variables,
)
from .finance_models import (
    FinancialVehicle,
    NCFAccountContractType,
    NCFAccountStatementPDF,
    NCFAccountStatementSummary,
    NCFAccountStatementVehicle,
    NCFConnectAccountResult,
    NCFCustomerType,
    NCFDisconnectAccountResult,
    NCFInvoicePDF,
    NCFInvoiceSummary,
    NCFNotificationPreferences,
    NCFPaymentHistoryEntry,
    NCFPayoutQuote,
    NCFUpdateAccountResult,
    NCFUpdateNotificationPreferencesResult,
    VehicleCreditInfo,
)
from .finance_parsing import (
    parse_account_statement_pdf,
    parse_account_statements,
    parse_financial_vehicles,
    parse_invoice_pdf,
    parse_invoices,
    parse_ncf_account_statement,
    parse_ncf_connect_account,
    parse_ncf_disconnect_account,
    parse_ncf_payout_quote,
    parse_ncf_preferences,
    parse_ncf_terms_and_conditions,
    parse_ncf_update_account,
    parse_ncf_update_notification_preferences,
    parse_payment_history,
    parse_vehicle_credit,
)
from .graphql_input import UNSET, UnsetType


class _FinanceClientMixin(_NissanClientBase):
    async def async_ncf_connect_account(
        self,
        vin: str,
        account_number: str,
        *,
        customer_type: NCFCustomerType | UnsetType | None = UNSET,
    ) -> NCFConnectAccountResult | None:
        """Link an NCF account to a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NCFConnectAccount",
            operations.NCF_CONNECT_ACCOUNT,
            ncf_connect_account_variables(vin, account_number, customer_type),
        )
        return parse_ncf_connect_account(data)

    async def async_ncf_disconnect_account(
        self,
        account_number: str,
    ) -> NCFDisconnectAccountResult | None:
        """Disconnect an NCF account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NCFDisconnectAccount",
            operations.NCF_DISCONNECT_ACCOUNT,
            account_number_variables(account_number),
        )
        return parse_ncf_disconnect_account(data)

    async def async_ncf_update_account(
        self,
        account_number: str,
        *,
        address: AddressInput | UnsetType | None = UNSET,
        phone_number: str | UnsetType | None = UNSET,
    ) -> NCFUpdateAccountResult | None:
        """Patch optional NCF contact fields."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NCFUpdateAccount",
            operations.NCF_UPDATE_ACCOUNT,
            ncf_update_account_variables(
                account_number,
                address,
                phone_number,
            ),
        )
        return parse_ncf_update_account(data)

    async def async_ncf_update_notification_preferences(
        self,
        config: NCFNotificationPreferencesInput,
    ) -> NCFUpdateNotificationPreferencesResult | None:
        """Patch NCF notification preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NCFUpdateNotificationPreferences",
            operations.NCF_UPDATE_NOTIFICATION_PREFERENCES,
            ncf_notification_preferences_variables(config),
        )
        return parse_ncf_update_notification_preferences(data)

    async def async_get_financial_vehicles(
        self,
    ) -> tuple[FinancialVehicle | None, ...] | None:
        """Return vehicles and contracts linked through financial services."""

        data = await self._transport.async_graphql(
            "FinancialVehicles",
            operations.FINANCIAL_VEHICLES,
            {},
        )
        return parse_financial_vehicles(data)

    async def async_get_account_statement_pdf(
        self,
        contract_number: str,
        document_number: str,
    ) -> NCFAccountStatementPDF | None:
        """Return one Nissan finance account-statement document."""

        data = await self._transport.async_graphql(
            "GetAccountStatementPDF",
            operations.GET_ACCOUNT_STATEMENT_PDF,
            finance_document_variables(contract_number, document_number),
        )
        return parse_account_statement_pdf(data)

    async def async_get_account_statements(
        self,
        contract_number: str,
    ) -> tuple[NCFAccountStatementSummary | None, ...] | None:
        """Return Nissan finance account-statement summaries."""

        data = await self._transport.async_graphql(
            "GetAccountStatements",
            operations.GET_ACCOUNT_STATEMENTS,
            contract_number_variables(contract_number),
        )
        return parse_account_statements(data)

    async def async_get_vehicle_credit(
        self,
    ) -> tuple[VehicleCreditInfo | None, ...] | None:
        """Return vehicle credit data exposed by the signed-in account."""

        data = await self._transport.async_graphql(
            "GetCredit",
            operations.GET_CREDIT,
            {},
        )
        return parse_vehicle_credit(data)

    async def async_get_invoice_pdf(
        self,
        contract_number: str,
        uuid: str,
    ) -> NCFInvoicePDF | None:
        """Return one Nissan finance invoice document."""

        data = await self._transport.async_graphql(
            "GetInvoicePDF",
            operations.GET_INVOICE_PDF,
            invoice_pdf_variables(contract_number, uuid),
        )
        return parse_invoice_pdf(data)

    async def async_get_invoices(
        self,
        contract_number: str,
    ) -> tuple[NCFInvoiceSummary | None, ...] | None:
        """Return Nissan finance invoice summaries."""

        data = await self._transport.async_graphql(
            "GetInvoices",
            operations.GET_INVOICES,
            contract_number_variables(contract_number),
        )
        return parse_invoices(data)

    async def async_get_ncf_account_statement(
        self,
        start_date: date,
        end_date: date,
        contract_type: NCFAccountContractType,
    ) -> tuple[NCFAccountStatementVehicle | None, ...] | None:
        """Return detailed NCF statements for a date range."""

        data = await self._transport.async_graphql(
            "NCFAccountStatement",
            operations.NCF_ACCOUNT_STATEMENT,
            ncf_account_statement_variables(start_date, end_date, contract_type),
        )
        return parse_ncf_account_statement(data)

    async def async_get_ncf_payout_quote(
        self,
        account_number: str,
        vin: str,
    ) -> NCFPayoutQuote | None:
        """Return the current payout quote for a finance account and vehicle."""

        data = await self._transport.async_graphql(
            "NCFPayoutQuote",
            operations.NCF_PAYOUT_QUOTE,
            ncf_payout_quote_variables(account_number, vin),
        )
        return parse_ncf_payout_quote(data)

    async def async_get_ncf_preferences(
        self,
        account_number: str,
    ) -> NCFNotificationPreferences | None:
        """Return NCF notification preferences."""

        data = await self._transport.async_graphql(
            "NCFPreferences",
            operations.NCF_PREFERENCES,
            account_number_variables(account_number),
        )
        return parse_ncf_preferences(data)

    async def async_get_ncf_terms_and_conditions(self) -> str | None:
        """Return NCF terms and conditions."""

        data = await self._transport.async_graphql(
            "NCFTermsAndConditions",
            operations.NCF_TERMS_AND_CONDITIONS,
            {},
        )
        return parse_ncf_terms_and_conditions(data)

    async def async_get_payment_history(
        self,
        account_number: str,
        start_date: datetime,
        end_date: datetime,
    ) -> tuple[NCFPaymentHistoryEntry | None, ...] | None:
        """Return NCF payment history for a date-time range."""

        data = await self._transport.async_graphql(
            "PaymentHistory",
            operations.PAYMENT_HISTORY,
            payment_history_variables(account_number, start_date, end_date),
        )
        return parse_payment_history(data)
