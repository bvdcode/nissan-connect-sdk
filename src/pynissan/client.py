from __future__ import annotations

import asyncio
import math
from collections.abc import Mapping
from datetime import date, datetime
from typing import assert_never

from aiohttp import ClientSession

from . import operations
from ._profile import profile_for
from .account_enrollment_parsing import (
    parse_generate_otp,
    parse_ncar_icar_customer_enrollment,
    parse_ncar_icar_generate_otp,
    parse_ncar_icar_register_account,
    parse_ncar_icar_verify_account,
    parse_ncar_icar_verify_otp,
    parse_register_account,
    parse_verify_otp,
)
from .account_inputs import (
    MarketingPreferenceInput,
    NCIMarketingPreferenceInput,
    RegisterAccountInput,
    UpdateAccountInput,
    generate_otp_variables,
    ncar_icar_generate_otp_variables,
    ncar_icar_verify_account_variables,
    ncar_icar_verify_otp_variables,
    pin_variables,
    register_account_variables,
    update_account_variables,
    update_nci_marketing_preferences_variables,
    update_nna_marketing_preferences_variables,
    validate_nissan_id_variables,
    verify_otp_variables,
)
from .account_models import (
    CreatePinResult,
    DeleteAccountResult,
    GenerateOtpResult,
    MarketingPreferencesResult,
    NcarIcarCustomerEnrollmentResult,
    NcarIcarGenerateOtpResult,
    NcarIcarVerifyAccountResult,
    NcarIcarVerifyOtpResult,
    NissanIdValidationResult,
    RegisterAccountResult,
    SecurityQuestion,
    UpdateAccountResult,
    UpdatePinResult,
    UserInfo,
    VerifyOtpResult,
)
from .account_parsing import (
    parse_create_pin,
    parse_delete_account,
    parse_marketing_preferences,
    parse_security_questions,
    parse_terms_and_conditions,
    parse_update_account,
    parse_update_nci_marketing_preferences,
    parse_update_nna_marketing_preferences,
    parse_update_pin,
    parse_user_info,
    parse_validate_nissan_id,
)
from .alert_inputs import (
    BoundaryAlertInput,
    BoundaryAlertUpdate,
    CurfewAlertInput,
    SpeedAlertInput,
    ValetRadiusInput,
    boundary_alert_input,
    boundary_alert_update_input,
    curfew_alert_input,
    optional_coordinate_input,
    optional_valet_radius_input,
    speed_alert_input,
)
from .charge_plan_inputs import (
    cancel_charge_plan_variables,
    charge_product_variables,
    enroll_charge_plan_variables,
    pricing_details_variables,
)
from .charge_plan_models import (
    ChargePlanCancellationResult,
    ChargePlanEnrollmentResult,
    ChargePlanPricingDetails,
    ChargeProductResult,
)
from .charge_plan_parsing import (
    parse_cancel_charge_plan,
    parse_charge_product,
    parse_enroll_charge_plan,
    parse_pricing_details,
)
from .collision_report_inputs import (
    CollisionCenterSearchInput,
    CollisionReportPhotoInput,
    CreateCollisionReportInput,
    collision_center_variables,
    collision_report_pdf_variables,
    collision_report_photo_variables,
    create_collision_report_variables,
    delete_collision_report_photo_variables,
)
from .collision_report_models import (
    CollisionCenter,
    CreateCollisionReportPdfResult,
    CreateCollisionReportResult,
    DeleteCollisionReportPhotoResult,
    PhotoSection,
    UploadCollisionReportPhotoResult,
)
from .collision_report_parsing import (
    parse_collision_centers,
    parse_create_collision_report,
    parse_create_collision_report_pdf,
    parse_delete_collision_report_photo,
    parse_upload_collision_report_photo,
)
from .commerce_inputs import (
    AddProductToCartInput,
    CancelSubscriptionInput,
    ProductCatalogInput,
    add_product_to_cart_variables,
    cancel_pending_subscription_variables,
    cancel_subscription_variables,
    nissan_pay_order_history_variables,
    nissan_store_link_variables,
    product_catalog_variables,
)
from .commerce_models import (
    AddProductToCartResult,
    CancelPendingSubscriptionResult,
    CancelSubscriptionResult,
    NissanPayAccount,
    NissanPayOrderHistory,
    NissanStoreClientOrigin,
    ProductCatalogResult,
    UnselectedCommerceResult,
    UpsertNissanPayAccountResult,
)
from .commerce_parsing import (
    parse_add_product_to_cart,
    parse_cancel_pending_subscription,
    parse_cancel_subscription,
    parse_digital_wallet_url,
    parse_nissan_pay,
    parse_nissan_pay_order_history,
    parse_nissan_store_checkout_url,
    parse_product_catalog,
    parse_trial_checkout_link,
    parse_upsert_nissan_pay_account,
)
from .common_inputs import AddressInput, CoordinateInput, address_input
from .content_inputs import contact_us_variables, faq_variables, live_chat_hours_variables
from .content_models import (
    CertifiedPreOwnedDetails,
    ClientType,
    ContactUsInfo,
    FrequentlyAskedQuestionCategory,
    LiveChatHours,
    MobileCarrier,
)
from .content_parsing import (
    parse_contact_us,
    parse_cpo_details,
    parse_faq,
    parse_live_chat_hours,
    parse_mobile_carriers,
)
from .countries import Country
from .dealer_inputs import (
    MaintenanceMileageInput,
    ServiceAppointmentInput,
    ServiceCode,
    ServiceLocationType,
    all_dealers_variables,
    cancel_service_appointment_variables,
    dealers_by_search_variables,
    maintenance_visits_variables,
    service_advisors_variables,
    service_appointment_variables,
    service_appointments_variables,
    service_time_slots_variables,
    update_service_appointment_variables,
)
from .dealer_models import (
    CancelServiceAppointmentResult,
    Dealer,
    DealerDealsAndImages,
    DealerServiceOperation,
    DealerSummary,
    MaintenanceVisits,
    PreferredDealerUpdateResult,
    ServiceAdvisor,
    ServiceAppointment,
    ServiceAppointmentCreateResult,
    ServiceAppointmentTimeSlot,
    ServiceAppointmentUpdateResult,
    ServiceCategory,
    ServiceOperationsAtInterval,
    ServiceTransportationOption,
)
from .dealer_parsing import (
    parse_all_dealers,
    parse_cancel_service_appointment,
    parse_create_service_appointment,
    parse_dealer,
    parse_dealer_deals_and_images,
    parse_dealers,
    parse_maintenance_visits,
    parse_service_advisors,
    parse_service_appointment_time_slots,
    parse_service_appointments,
    parse_service_categories,
    parse_service_operations,
    parse_service_operations_by_mileage,
    parse_transportation_options,
    parse_update_service_appointment,
    parse_update_vehicle_preferred_dealer,
)
from .device_notification_inputs import (
    MobileInfoInput,
    in_vehicle_message_variables,
    in_vehicle_messages_variables,
    register_device_for_push_notifications_variables,
    register_push_notifications_variables,
    unregister_device_for_push_notifications_variables,
    unregister_push_notifications_variables,
)
from .device_notification_models import (
    DeviceOS,
    InVehicleMessage,
    InVehicleMessageSummary,
    PushNotificationResult,
)
from .device_notification_parsing import (
    parse_in_vehicle_message,
    parse_in_vehicle_messages,
    parse_register_device_for_push_notifications,
    parse_register_push_notifications,
    parse_unregister_device_for_push_notifications,
    parse_unregister_push_notifications,
)
from .driver_inputs import (
    CreateEmergencyContactInput,
    DriverInviteActionInput,
    DriverInviteInput,
    OwnerInviteActionInput,
    UpdateDriverInput,
    UpdateEmergencyContactInput,
    create_emergency_contact_variables,
    create_rsa_link_variables,
    delete_driver_variables,
    delete_emergency_contact_variables,
    driver_invite_action_variables,
    driver_invites_variables,
    emergency_contacts_variables,
    invite_driver_variables,
    owner_invite_action_variables,
    update_driver_variables,
    update_emergency_contact_variables,
)
from .driver_models import (
    CreateEmergencyContactResult,
    CreateRSALinkResult,
    DeleteDriverResult,
    DeleteEmergencyContactResult,
    DriverInviteActionResult,
    DriverInvitesResult,
    EmergencyContactsResult,
    InviteDriverResult,
    OwnerInviteActionResult,
    UpdateDriverResult,
    UpdateEmergencyContactResult,
)
from .driver_parsing import (
    parse_create_emergency_contact,
    parse_create_rsa_link,
    parse_delete_driver,
    parse_delete_emergency_contact,
    parse_driver_invite_action,
    parse_driver_invites,
    parse_emergency_contacts,
    parse_invite_driver,
    parse_owner_invite_action,
    parse_update_driver,
    parse_update_emergency_contact,
)
from .energy_account_models import (
    ACCOUNT_STATUS_POLL_INTERVAL_SECONDS,
    ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS,
    EnergyAccountPollingOutcome,
    EnergyAccountStatusResult,
    account_status_polling_outcome,
)
from .energy_account_parsing import parse_account_status
from .exceptions import ReadOnlyError, ResponseError
from .extended_vehicle_inputs import (
    EmpConnectorLevelInput,
    EmpEvseStatusInput,
    driving_history_variables,
    e_vehicle_eligibility_variables,
    ev_charge_stations_variables,
    last_known_camera_usage_counter_variables,
    location_details_variables,
    parking_chargeable_variables,
    shareable_capabilities_variables,
    tariff_pricing_variables,
)
from .extended_vehicle_models import (
    DrivingHistory,
    DrivingHistoryAggregator,
    EVChargeStation,
    EVehicleEligibility,
    LastKnownCameraUsageCounter,
    LocationDetails,
    ParkingChargeable,
    ShareableCapabilities,
    TariffPricing,
    WeightUnit,
)
from .extended_vehicle_parsing import (
    parse_driving_history,
    parse_e_vehicle_eligibility,
    parse_ev_charge_stations,
    parse_last_known_camera_usage_counter,
    parse_location_details,
    parse_parking_chargeable,
    parse_shareable_capabilities,
    parse_tariff_pricing,
)
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
from .garage_inputs import (
    NcarIcarRegisterAccountInput,
    add_vehicle_variables,
    apc_agreement_variables,
    apc_document_url_variables,
    connected_terms_and_conditions_by_vin_variables,
    create_apc_agreement_variables,
    delete_vehicle_variables,
    ncar_icar_add_vehicle_variables,
    onboarding_features_variables,
    ownership_status_variables,
    pending_vehicles_variables,
    update_apc_agreement_variables,
    update_vehicle_manual_mileage_variables,
    update_vehicle_nickname_variables,
    update_vehicle_variables,
    upload_ownership_verification_variables,
)
from .garage_models import (
    AddVehicleResult,
    APCAgreement,
    APCAgreementMutationResult,
    APCDocument,
    ConnectedTermsAndConditionsResult,
    DeleteVehicleResult,
    NcarIcarAddVehicleResult,
    OnboardingFeature,
    OwnershipStatus,
    PendingVehicle,
    UpdateVehicleManualMileageResult,
    UpdateVehicleNicknameResult,
    UpdateVehicleResult,
    UploadOwnershipVerificationResult,
    VehicleHologram,
)
from .garage_parsing import (
    parse_add_vehicle,
    parse_apc_agreement,
    parse_apc_document_url,
    parse_connected_terms_and_conditions_by_vin,
    parse_create_apc_agreement,
    parse_delete_vehicle,
    parse_ncar_icar_add_vehicle,
    parse_onboarding_features,
    parse_ownership_status,
    parse_pending_vehicles,
    parse_update_apc_agreement,
    parse_update_vehicle,
    parse_update_vehicle_manual_mileage,
    parse_update_vehicle_nickname,
    parse_upload_ownership_verification,
)
from .graphql_input import UNSET, UnsetType, optional_input_fields
from .insurance_inputs import VehicleInsuranceInput, vehicle_insurance_variables
from .insurance_models import (
    VehicleInsurance,
    VehicleInsuranceMutationResult,
    VehicleInsurer,
)
from .insurance_parsing import (
    parse_add_vehicle_insurance,
    parse_insurers,
    parse_update_vehicle_insurance,
    parse_vehicle_insurance,
)
from .maintenance_inputs import (
    CreatePartsReminderInput,
    PastServiceInput,
    ResetPartsReminderInput,
    UpdatePartsReminderInput,
    UpdatePastServiceInput,
    add_past_service_variables,
    collision_history_variables,
    collision_probe_data_variables,
    create_parts_reminder_variables,
    delete_parts_reminder_variables,
    get_maintenance_timeline_variables,
    get_service_contracts_variables,
    parts_reminders_variables,
    reset_parts_reminder_variables,
    update_parts_reminder_variables,
    update_past_service_variables,
)
from .maintenance_models import (
    CollisionHistoryEntry,
    CollisionProbeReading,
    MaintenanceTimeline,
    PartsReminderMutationResult,
    PastServiceResult,
    ServiceContract,
    VehiclePartsReminders,
)
from .maintenance_parsing import (
    parse_add_past_service,
    parse_collision_history,
    parse_collision_probe_data,
    parse_create_parts_reminder,
    parse_delete_parts_reminder,
    parse_maintenance_timeline,
    parse_parts_reminders,
    parse_reset_parts_reminder,
    parse_service_contracts,
    parse_update_parts_reminder,
    parse_update_past_service,
)
from .models import (
    BatteryStatus,
    BoundaryAlert,
    BreachAlerts,
    ChargeConfig,
    ChargeHistoryAggregator,
    ChargeSchedule,
    ChargeScheduleInput,
    ClimateDefaults,
    ClimateParameters,
    ClimateScheduleInput,
    ClimateSettings,
    ClimateStatus,
    CurfewAlert,
    DataPrivacyMode,
    DistanceUnit,
    DoorsStatus,
    ReminderNotificationsAfterLeavingVehicle,
    RemoteServiceHistory,
    ServiceRequest,
    ServiceRequestKind,
    ServiceRequestResult,
    ServiceRequestStatus,
    SpeedAlert,
    SpeedUnit,
    TemperatureUnit,
    Tokens,
    V2LStatus,
    ValetAlert,
    Vehicle,
    VehicleAlertKind,
    VehicleAlertRequest,
    VehicleAlerts,
    VehicleCapabilities,
    VehicleChargeHistory,
    VehicleClimateSchedules,
    VehicleLocation,
    VehiclePhotos,
    VehiclePreferences,
    VehicleStatus,
    VehicleSubscriptions,
    VehicleWifiConsumption,
)
from .navigation_inputs import (
    DestinationInput,
    NavigationDataSource,
    PlannedRouteInput,
    PlannedRouteUpdate,
    PlugConnectorType,
    PointOfInterestFolder,
    PointOfInterestFolderFilter,
    RouteCalculationCondition,
    RouteStatus,
    RouteWaypointInput,
    TJunctionLocationInput,
    delete_saved_t_junction_locations_input,
    delete_unsaved_t_junction_locations_input,
    destination_input,
    navigation_enum_input,
    nullable_plug_connector_types_input,
    nullable_route_waypoints_input,
    optional_battery_level_string,
    optional_destination_time,
    optional_navigation_enum,
    planned_route_input,
    planned_route_update_input,
    save_t_junction_locations_input,
    update_saved_t_junction_location_input,
)
from .navigation_models import (
    EVWaypointResult,
    TJunctionLocations,
    VehicleJourneys,
    VehiclePlannedRoutes,
    VehiclePointOfInterestDestinations,
    VehicleRoutesHistory,
)
from .navigation_parsing import (
    parse_t_junction_locations,
    parse_vehicle_ev_waypoints,
    parse_vehicle_journeys,
    parse_vehicle_planned_routes,
    parse_vehicle_point_of_interest_destinations,
    parse_vehicle_routes_history,
)
from .notification_inputs import (
    NotificationPreferenceInput,
    notification_preferences_input,
    update_nissan_energy_notification_preferences_variables,
)
from .notification_models import (
    NissanEnergyNotificationPreferences,
    NissanEnergyNotificationPreferencesUpdate,
    NotificationPreference,
)
from .notification_parsing import (
    parse_nissan_energy_notification_preferences,
    parse_notification_preferences,
    parse_update_nissan_energy_notification_preferences,
)
from .ota_inputs import (
    data_wipe_type_input,
    download_ota_update_input,
    ota_activation_schedule_input,
)
from .ota_models import DataWipeType, OtaUpdate, OtaUpdateProgress
from .ota_parsing import parse_ota_update, parse_ota_update_progress
from .parsing import (
    parse_alert_request_status,
    parse_breach_alerts,
    parse_charge_config,
    parse_charge_schedules,
    parse_climate_defaults,
    parse_climate_schedules,
    parse_photos_around_vehicle,
    parse_reminder_notifications_after_leaving_vehicle,
    parse_remote_service_history,
    parse_service_request,
    parse_service_request_result,
    parse_toggle_reminder_notifications_after_leaving_vehicle,
    parse_v2l_status,
    parse_vehicle_alert_request,
    parse_vehicle_alerts,
    parse_vehicle_capabilities,
    parse_vehicle_charge_history,
    parse_vehicle_data_privacy_mode,
    parse_vehicle_location,
    parse_vehicle_preferences,
    parse_vehicle_status,
    parse_vehicle_subscriptions,
    parse_vehicle_wifi_consumption,
    parse_vehicles,
)
from .pnc_inputs import (
    retry_certificate_install_variables,
    start_charge_session_variables,
    stop_charge_session_variables,
    update_pnc_service_status_variables,
)
from .pnc_models import (
    PlugAndChargeCertificateRetryResult,
    PlugAndChargeServiceState,
    PlugAndChargeServiceStatus,
    PlugAndChargeStatusInput,
    PublicChargeSessionStartResult,
    PublicChargeSessionState,
    PublicChargeSessionStatus,
    PublicChargeSessionStopResult,
)
from .pnc_parsing import (
    parse_charge_session_status,
    parse_pnc_service_status,
    parse_retry_certificate_install,
    parse_start_charge_session,
    parse_stop_charge_session,
    parse_update_pnc_service_status,
)
from .second_delivery_inputs import (
    SecondDeliveryAppointmentInput,
    second_delivery_appointment_variables,
    second_delivery_home_slots_variables,
    second_delivery_location_slots_variables,
    second_delivery_send_auth_code_variables,
    second_delivery_verify_auth_code_variables,
    update_second_delivery_appointment_variables,
)
from .second_delivery_models import (
    SecondDeliveryAddressValidationResult,
    SecondDeliveryAppointmentResult,
    SecondDeliveryEligibility,
    SecondDeliveryOperationResult,
    SecondDeliveryTimeSlotsResult,
)
from .second_delivery_parsing import (
    parse_cancel_second_delivery_appointment,
    parse_create_second_delivery_appointment,
    parse_second_delivery_address_validation,
    parse_second_delivery_appointment,
    parse_second_delivery_eligibility,
    parse_second_delivery_home_time_slots,
    parse_second_delivery_hub_time_slots,
    parse_second_delivery_send_auth_code,
    parse_second_delivery_verify_auth_code,
    parse_second_delivery_virtual_time_slots,
    parse_update_second_delivery_appointment,
)
from .service_inputs import (
    vehicle_preferred_dealer_variables,
    vehicle_recalls_variables,
    vehicle_roadside_assistance_variables,
    vehicle_service_history_variables,
    warranty_info_variables,
)
from .service_models import (
    VehiclePreferredDealer,
    VehicleRecall,
    VehicleRoadsideAssistance,
    VehicleServiceHistoryEntry,
    VehicleWarranty,
)
from .service_parsing import (
    parse_vehicle_preferred_dealer,
    parse_vehicle_recalls,
    parse_vehicle_roadside_assistance,
    parse_vehicle_service_history,
    parse_warranty_info,
)
from .transport import NissanTransport, TokenListener
from .v1g_inputs import (
    V1GNotificationPreferenceInput,
    v1g_cancel_monitored_charging_plan_variables,
    v1g_enroll_monitored_charging_plan_variables,
    v1g_monitored_charging_account_status_variables,
    v1g_tokenized_url_variables,
    v1g_update_notification_preferences_variables,
)
from .v1g_models import (
    V1GMonitoredChargingAccountStatusResult,
    V1GMonitoredChargingPlanCancellationResult,
    V1GMonitoredChargingPlanEnrollmentResult,
    V1GNotificationPreferencesUpdateResult,
    V1GTokenizedUrlResult,
)
from .v1g_parsing import (
    parse_v1g_cancel_monitored_charging_plan,
    parse_v1g_enroll_monitored_charging_plan,
    parse_v1g_monitored_charging_account_status,
    parse_v1g_tokenized_url,
    parse_v1g_update_notification_preferences,
)
from .vehicle_detail_inputs import (
    vehicle_battery_status_variables,
    vehicle_boundary_alerts_variables,
    vehicle_climate_status_variables,
    vehicle_curfew_alerts_variables,
    vehicle_doors_status_variables,
    vehicle_model_year_variables,
    vehicle_nickname_variables,
    vehicle_speed_alerts_variables,
    vehicle_status_and_recalls_variables,
    vehicle_status_variables,
    vehicle_valet_alerts_variables,
)
from .vehicle_detail_models import (
    VehicleModelYear,
    VehicleNickname,
    VehicleStatusAndRecalls,
)
from .vehicle_detail_parsing import (
    parse_vehicle_battery_status,
    parse_vehicle_boundary_alerts,
    parse_vehicle_climate_status,
    parse_vehicle_core_status,
    parse_vehicle_curfew_alerts,
    parse_vehicle_doors_status,
    parse_vehicle_model_year,
    parse_vehicle_nickname,
    parse_vehicle_speed_alerts,
    parse_vehicle_status_and_recalls,
    parse_vehicle_valet_alert,
)
from .wearable_models import VehicleWithCapabilities
from .wearable_parsing import parse_vehicles_with_capabilities


class NissanClient:
    """Async client for MyNISSAN connected vehicles."""

    def __init__(
        self,
        session: ClientSession,
        *,
        country: Country = Country.US,
        tokens: Tokens | None = None,
        token_listener: TokenListener | None = None,
        read_only: bool = True,
        oauth_device_id: str | None = None,
    ) -> None:
        self._transport = NissanTransport(
            session,
            profile=profile_for(country),
            tokens=tokens,
            token_listener=token_listener,
            oauth_device_id=oauth_device_id,
        )
        self._country = country
        self._read_only = read_only

    @property
    def country(self) -> Country:
        """Return the country selected for this client."""

        return self._country

    @property
    def read_only(self) -> bool:
        """Return whether state-changing operations are blocked."""

        return self._read_only

    @property
    def tokens(self) -> Tokens | None:
        """Return the currently active OAuth tokens."""

        return self._transport.tokens

    @property
    def oauth_device_id(self) -> str:
        """Return the identifier used for a mobile OAuth authorization scope."""

        return self._transport.oauth_device_id

    async def async_authenticate(self, email: str, password: str) -> Tokens:
        """Authenticate with MyNISSAN credentials."""

        return await self._transport.async_authenticate(email, password)

    async def async_refresh_tokens(self) -> Tokens:
        """Refresh and publish the active OAuth token set."""

        return await self._transport.async_refresh_tokens()

    async def async_validate_nissan_id(
        self,
        nissan_id: str,
    ) -> NissanIdValidationResult | None:
        """Return the account state associated with a Nissan ID."""

        data = await self._transport.async_graphql(
            "ValidateNissanID",
            operations.VALIDATE_NISSAN_ID,
            validate_nissan_id_variables(nissan_id),
        )
        return parse_validate_nissan_id(data)

    async def async_get_security_questions(
        self,
    ) -> tuple[SecurityQuestion | None, ...] | None:
        """Return the account security-question catalog."""

        data = await self._transport.async_graphql(
            "SecurityQuestions",
            operations.SECURITY_QUESTIONS,
            {},
        )
        return parse_security_questions(data)

    async def async_get_user_info(self) -> UserInfo | None:
        """Return the signed-in user's PIN and account-kind flags."""

        data = await self._transport.async_graphql(
            "UserInfo",
            operations.USER_INFO,
            {},
        )
        return parse_user_info(data)

    async def async_get_terms_and_conditions(self) -> str | None:
        """Return the nullable account terms content."""

        data = await self._transport.async_graphql(
            "TermsAndConditions",
            operations.TERMS_AND_CONDITIONS,
            {},
        )
        return parse_terms_and_conditions(data)

    async def async_get_marketing_preferences(
        self,
    ) -> MarketingPreferencesResult | None:
        """Return country-specific marketing preferences."""

        data = await self._transport.async_graphql(
            "MarketingPreferences",
            operations.MARKETING_PREFERENCES,
            {},
        )
        return parse_marketing_preferences(data)

    async def async_register_account(
        self,
        config: RegisterAccountInput,
    ) -> RegisterAccountResult | None:
        """Register a MyNISSAN account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RegisterAccount",
            operations.REGISTER_ACCOUNT,
            register_account_variables(config),
        )
        return parse_register_account(data)

    async def async_register_ncar_icar_account(
        self,
        config: RegisterAccountInput,
    ) -> RegisterAccountResult | None:
        """Register an account through the NCAR/ICAR flow."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarRegisterAccount",
            operations.NCAR_ICAR_REGISTER_ACCOUNT,
            register_account_variables(config),
        )
        return parse_ncar_icar_register_account(data)

    async def async_verify_ncar_icar_account(
        self,
        guid: str,
    ) -> NcarIcarVerifyAccountResult | None:
        """Check account availability for an NCAR/ICAR enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarVerifyAccount",
            operations.NCAR_ICAR_VERIFY_ACCOUNT,
            ncar_icar_verify_account_variables(guid),
        )
        return parse_ncar_icar_verify_account(data)

    async def async_get_ncar_icar_customer_enrollment(
        self,
        guid: str,
    ) -> NcarIcarCustomerEnrollmentResult | None:
        """Recover customer details from an NCAR/ICAR enrollment link."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarCustomerEnrollment",
            operations.NCAR_ICAR_CUSTOMER_ENROLLMENT,
            ncar_icar_verify_account_variables(guid),
        )
        return parse_ncar_icar_customer_enrollment(data)

    async def async_generate_ncar_icar_otp(
        self,
        guid: str,
        phone_number: str,
    ) -> NcarIcarGenerateOtpResult | None:
        """Generate a one-time password for NCAR/ICAR enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarGenerateOTP",
            operations.NCAR_ICAR_GENERATE_OTP,
            ncar_icar_generate_otp_variables(guid, phone_number),
        )
        return parse_ncar_icar_generate_otp(data)

    async def async_verify_ncar_icar_otp(
        self,
        guid: str,
        phone_number: str,
        reference_id: str,
        otp: str,
    ) -> NcarIcarVerifyOtpResult | None:
        """Verify an NCAR/ICAR enrollment one-time password."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarVerifyOTP",
            operations.NCAR_ICAR_VERIFY_OTP,
            ncar_icar_verify_otp_variables(guid, phone_number, reference_id, otp),
        )
        return parse_ncar_icar_verify_otp(data)

    async def async_generate_otp(self, phone_number: str) -> GenerateOtpResult | None:
        """Generate a one-time password for direct account verification."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "GenerateOTP",
            operations.GENERATE_OTP,
            generate_otp_variables(phone_number),
        )
        return parse_generate_otp(data)

    async def async_verify_otp(
        self,
        phone_number: str,
        otp: str,
        reference_id: str,
    ) -> VerifyOtpResult | None:
        """Verify a direct account one-time password."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "VerifyOTP",
            operations.VERIFY_OTP,
            verify_otp_variables(phone_number, otp, reference_id),
        )
        return parse_verify_otp(data)

    async def async_create_pin(
        self,
        question_id: str,
        answer: str,
        new_pin: str,
    ) -> CreatePinResult | None:
        """Create the account PIN and security answer."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreatePin",
            operations.CREATE_PIN,
            pin_variables(question_id, answer, new_pin),
        )
        return parse_create_pin(data)

    async def async_update_pin(
        self,
        question_id: str,
        answer: str,
        new_pin: str,
    ) -> UpdatePinResult | None:
        """Replace the account PIN and security answer."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePin",
            operations.UPDATE_PIN,
            pin_variables(question_id, answer, new_pin),
        )
        return parse_update_pin(data)

    async def async_update_account(
        self,
        config: UpdateAccountInput | UnsetType | None = UNSET,
    ) -> UpdateAccountResult | None:
        """Update independently optional account profile fields."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateAccount",
            operations.UPDATE_ACCOUNT,
            update_account_variables(config),
        )
        return parse_update_account(data)

    async def async_delete_account(self) -> DeleteAccountResult | None:
        """Permanently delete the signed-in MyNISSAN account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteAccount",
            operations.DELETE_ACCOUNT,
            {},
        )
        return parse_delete_account(data)

    async def async_update_nci_marketing_preferences(
        self,
        marketing_preferences: NCIMarketingPreferenceInput,
    ) -> MarketingPreferencesResult | None:
        """Replace NCI account preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateNCIMarketingPreferences",
            operations.UPDATE_NCI_MARKETING_PREFERENCES,
            update_nci_marketing_preferences_variables(marketing_preferences),
        )
        return parse_update_nci_marketing_preferences(data)

    async def async_update_nna_marketing_preferences(
        self,
        marketing_preferences: MarketingPreferenceInput | UnsetType | None = UNSET,
    ) -> MarketingPreferencesResult | None:
        """Replace NNA account preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateNNAMarketingPreferences",
            operations.UPDATE_NNA_MARKETING_PREFERENCES,
            update_nna_marketing_preferences_variables(marketing_preferences),
        )
        return parse_update_nna_marketing_preferences(data)

    async def async_get_contact_us(
        self,
        client_type: ClientType = ClientType.ANDROID,
    ) -> ContactUsInfo:
        """Return account, ownership, and support contact information."""

        data = await self._transport.async_graphql(
            "ContactUs",
            operations.CONTACT_US,
            contact_us_variables(client_type),
        )
        return parse_contact_us(data)

    async def async_get_cpo_details(self) -> CertifiedPreOwnedDetails | None:
        """Return certified-pre-owned provider details."""

        data = await self._transport.async_graphql(
            "CpoDetails",
            operations.CPO_DETAILS,
            {},
        )
        return parse_cpo_details(data)

    async def async_get_faq(
        self,
        categories: tuple[str | None, ...] | UnsetType | None = UNSET,
    ) -> tuple[FrequentlyAskedQuestionCategory, ...]:
        """Return FAQ categories, optionally filtered by category name."""

        data = await self._transport.async_graphql(
            "FAQ",
            operations.FAQ,
            faq_variables(categories),
        )
        return parse_faq(data)

    async def async_get_live_chat_hours(
        self,
        departments: tuple[str | None, ...] | UnsetType | None = UNSET,
        enhanced_chat: bool | UnsetType | None = UNSET,
    ) -> tuple[LiveChatHours | None, ...] | None:
        """Return nullable live-chat hours for selected departments."""

        data = await self._transport.async_graphql(
            "LiveChatHours",
            operations.LIVE_CHAT_HOURS,
            live_chat_hours_variables(departments, enhanced_chat),
        )
        return parse_live_chat_hours(data)

    async def async_get_mobile_carriers(self) -> tuple[MobileCarrier, ...]:
        """Return the mobile-carrier catalog used by account profiles."""

        data = await self._transport.async_graphql(
            "MobileCarriers",
            operations.MOBILE_CARRIERS,
            {},
        )
        return parse_mobile_carriers(data)

    async def async_add_product_to_nissan_store_cart(
        self,
        config: AddProductToCartInput,
    ) -> AddProductToCartResult | None:
        """Add a selected product and selling model to Nissan Store cart."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddProductToNissanStoreCart",
            operations.ADD_PRODUCT_TO_NISSAN_STORE_CART,
            add_product_to_cart_variables(config),
        )
        return parse_add_product_to_cart(data)

    async def async_cancel_pending_subscription(
        self,
        pending_order_id: str,
    ) -> CancelPendingSubscriptionResult | UnselectedCommerceResult:
        """Cancel a pending subscription order."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelPendingSubscription",
            operations.CANCEL_PENDING_SUBSCRIPTION,
            cancel_pending_subscription_variables(pending_order_id),
        )
        return parse_cancel_pending_subscription(data)

    async def async_cancel_subscription(
        self,
        config: CancelSubscriptionInput,
    ) -> CancelSubscriptionResult | None:
        """Cancel an active Nissan Store subscription."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelSubscription",
            operations.CANCEL_SUBSCRIPTION,
            cancel_subscription_variables(config),
        )
        return parse_cancel_subscription(data)

    async def async_create_nissan_store_fod_trial_checkout_link(
        self,
        vin: str,
        client_origin: NissanStoreClientOrigin = NissanStoreClientOrigin.ONE_APP,
    ) -> str | None:
        """Create a feature-on-demand trial checkout link."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateNissanStoreFODTrialCheckoutLink",
            operations.CREATE_NISSAN_STORE_FOD_TRIAL_CHECKOUT_LINK,
            nissan_store_link_variables(vin, client_origin),
        )
        return parse_trial_checkout_link(data)

    async def async_get_digital_wallet_url(self) -> str | None:
        """Return the nullable Nissan Pay digital-wallet URL."""

        data = await self._transport.async_graphql(
            "DigitalWalletURL",
            operations.DIGITAL_WALLET_URL,
            {},
        )
        return parse_digital_wallet_url(data)

    async def async_get_nissan_pay(self) -> NissanPayAccount | None:
        """Return Nissan Pay methods and digital-wallet information."""

        data = await self._transport.async_graphql(
            "NissanPay",
            operations.NISSAN_PAY,
            {},
        )
        return parse_nissan_pay(data)

    async def async_get_nissan_pay_order_history(
        self,
        vin: str,
        page_cursor: str | UnsetType | None = UNSET,
    ) -> NissanPayOrderHistory | None:
        """Return paginated Nissan Pay energy order history."""

        data = await self._transport.async_graphql(
            "NissanPayOrderHistory",
            operations.NISSAN_PAY_ORDER_HISTORY,
            nissan_pay_order_history_variables(vin, page_cursor),
        )
        return parse_nissan_pay_order_history(data)

    async def async_get_nissan_store_checkout_url(
        self,
        vin: str,
        client_origin: NissanStoreClientOrigin = NissanStoreClientOrigin.ONE_APP,
    ) -> str | None:
        """Return the nullable checkout URL for a vehicle."""

        data = await self._transport.async_graphql(
            "NissanStoreCheckoutURL",
            operations.NISSAN_STORE_CHECKOUT_URL,
            nissan_store_link_variables(vin, client_origin),
        )
        return parse_nissan_store_checkout_url(data)

    async def async_get_product_catalog(
        self,
        config: ProductCatalogInput,
    ) -> ProductCatalogResult | None:
        """Return Nissan Store product packages for an optional vehicle."""

        data = await self._transport.async_graphql(
            "ProductCatalog",
            operations.PRODUCT_CATALOG,
            product_catalog_variables(config),
        )
        return parse_product_catalog(data)

    async def async_upsert_nissan_pay_account(
        self,
    ) -> UpsertNissanPayAccountResult | None:
        """Create or synchronize the signed-in Nissan Pay account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpsertNissanPayAccount",
            operations.UPSERT_NISSAN_PAY_ACCOUNT,
            {},
        )
        return parse_upsert_nissan_pay_account(data)

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

    async def async_get_all_dealers(
        self,
        *,
        vin: str | UnsetType | None = UNSET,
        page_size: int | UnsetType | None = UNSET,
    ) -> tuple[DealerSummary | None, ...] | None:
        """Return the compact dealer list with optional vehicle and page filters."""

        data = await self._transport.async_graphql(
            "AllDealers",
            operations.ALL_DEALERS,
            all_dealers_variables(vin, page_size),
        )
        return parse_all_dealers(data)

    async def async_get_dealers(
        self,
        postal_code: str,
    ) -> tuple[Dealer | None, ...] | None:
        """Return dealers matching a postal code."""

        data = await self._transport.async_graphql(
            "Dealers",
            operations.DEALERS,
            {"zip": postal_code},
        )
        return parse_dealers(data)

    async def async_search_dealers(
        self,
        *,
        vin: str | UnsetType | None = UNSET,
        service_code: ServiceCode | UnsetType | None = UNSET,
        radius: int | UnsetType | None = UNSET,
        latitude: float | UnsetType | None = UNSET,
        longitude: float | UnsetType | None = UNSET,
    ) -> tuple[Dealer | None, ...] | None:
        """Search dealers with independently optional vehicle and location filters."""

        data = await self._transport.async_graphql(
            "DealersBySearch",
            operations.DEALERS_BY_SEARCH,
            dealers_by_search_variables(
                vin=vin,
                service_code=service_code,
                radius=radius,
                latitude=latitude,
                longitude=longitude,
            ),
        )
        return parse_dealers(data)

    async def async_get_dealer_deals_and_images(
        self,
        dealer_id: str,
    ) -> DealerDealsAndImages:
        """Return coupons and coupon images for a dealer."""

        data = await self._transport.async_graphql(
            "DealsAndImagesByDealerId",
            operations.DEALS_AND_IMAGES_BY_DEALER_ID,
            {"dealerId": dealer_id},
        )
        return parse_dealer_deals_and_images(data)

    async def async_get_dealer(self, dealer_id: str) -> Dealer | None:
        """Return one dealer by identifier."""

        data = await self._transport.async_graphql(
            "GetDealerById",
            operations.GET_DEALER_BY_ID,
            {"dealerId": dealer_id},
        )
        return parse_dealer(data)

    async def async_generate_all_maintenance_visits(
        self,
        vin: str,
        mileage: MaintenanceMileageInput,
        severity_id: str,
        past_visits: int,
        future_visits: int,
    ) -> MaintenanceVisits | None:
        """Generate the requested past and future maintenance visits."""

        data = await self._transport.async_graphql(
            "GenerateAllVisits",
            operations.GENERATE_ALL_VISITS,
            maintenance_visits_variables(
                vin,
                mileage,
                severity_id,
                past_visits,
                future_visits,
            ),
        )
        return parse_maintenance_visits(data)

    async def async_generate_next_maintenance_visit(
        self,
        vin: str,
        mileage: MaintenanceMileageInput,
        severity_id: str,
        past_visits: int,
        future_visits: int,
    ) -> MaintenanceVisits | None:
        """Generate the next maintenance visit with a severity identifier."""

        data = await self._transport.async_graphql(
            "GenerateNextVisit",
            operations.GENERATE_NEXT_VISIT,
            maintenance_visits_variables(
                vin,
                mileage,
                severity_id,
                past_visits,
                future_visits,
            ),
        )
        return parse_maintenance_visits(data)

    async def async_generate_next_maintenance_visit_no_severity(
        self,
        vin: str,
        mileage: MaintenanceMileageInput,
        severity_id: str,
        past_visits: int,
        future_visits: int,
    ) -> MaintenanceVisits | None:
        """Call Nissan's separately named no-severity maintenance operation."""

        data = await self._transport.async_graphql(
            "GenerateNextVisitNoSeverity",
            operations.GENERATE_NEXT_VISIT_NO_SEVERITY,
            maintenance_visits_variables(
                vin,
                mileage,
                severity_id,
                past_visits,
                future_visits,
            ),
        )
        return parse_maintenance_visits(data)

    async def async_get_service_advisors(
        self,
        dealer_id: str,
        service_operation_ids: tuple[str, ...],
        *,
        vin: str | UnsetType | None = UNSET,
    ) -> tuple[ServiceAdvisor | None, ...] | None:
        """Return service advisors for selected dealer operations."""

        data = await self._transport.async_graphql(
            "ServiceAdvisors",
            operations.SERVICE_ADVISORS,
            service_advisors_variables(dealer_id, service_operation_ids, vin),
        )
        return parse_service_advisors(data)

    async def async_get_service_appointment_time_slots(
        self,
        dealer_id: str,
        service_operation_ids: tuple[str, ...],
        start_date: datetime,
        *,
        advisor_id: str | UnsetType | None = UNSET,
        transportation_code: str | UnsetType | None = UNSET,
        location_type: ServiceLocationType | UnsetType | None = UNSET,
        vin: str | UnsetType | None = UNSET,
    ) -> tuple[ServiceAppointmentTimeSlot | None, ...]:
        """Return available service appointment time slots."""

        data = await self._transport.async_graphql(
            "ServiceAppointmentTimeSlots",
            operations.SERVICE_APPOINTMENT_TIME_SLOTS,
            service_time_slots_variables(
                dealer_id,
                service_operation_ids,
                start_date,
                advisor_id=advisor_id,
                transportation_code=transportation_code,
                location_type=location_type,
                vin=vin,
            ),
        )
        return parse_service_appointment_time_slots(data)

    async def async_get_service_appointments(
        self,
        vin: str,
        *,
        start_date: datetime | UnsetType | None = UNSET,
        end_date: datetime | UnsetType | None = UNSET,
    ) -> tuple[ServiceAppointment | None, ...] | None:
        """Return service appointments for a vehicle and optional date-time range."""

        data = await self._transport.async_graphql(
            "ServiceAppointments",
            operations.SERVICE_APPOINTMENTS,
            service_appointments_variables(vin, start_date, end_date),
        )
        return parse_service_appointments(data)

    async def async_get_service_categories(
        self,
    ) -> tuple[ServiceCategory | None, ...] | None:
        """Return service categories and their operations."""

        data = await self._transport.async_graphql(
            "ServiceCategories",
            operations.SERVICE_CATEGORIES,
            {},
        )
        return parse_service_categories(data)

    async def async_get_service_operations(
        self,
        vin: str,
        dealer_id: str,
    ) -> tuple[DealerServiceOperation | None, ...] | None:
        """Return the service operations available for a vehicle and dealer."""

        data = await self._transport.async_graphql(
            "ServiceOperations",
            operations.SERVICE_OPERATIONS,
            {"vin": vin, "dealerId": dealer_id},
        )
        return parse_service_operations(data)

    async def async_get_service_operations_by_mileage(
        self,
        vin: str,
        dealer_id: str,
        mileage: int,
    ) -> tuple[ServiceOperationsAtInterval | None, ...] | None:
        """Return service operations grouped around the supplied mileage."""

        data = await self._transport.async_graphql(
            "ServiceOperationsByMileage",
            operations.SERVICE_OPERATIONS_BY_MILEAGE,
            {"vin": vin, "dealerId": dealer_id, "mileage": mileage},
        )
        return parse_service_operations_by_mileage(data)

    async def async_get_transportation_options(
        self,
        dealer_id: str,
        service_operation_ids: tuple[str, ...],
        *,
        vin: str | UnsetType | None = UNSET,
    ) -> tuple[ServiceTransportationOption | None, ...] | None:
        """Return transportation options for selected dealer operations."""

        data = await self._transport.async_graphql(
            "TransportationOptions",
            operations.TRANSPORTATION_OPTIONS,
            service_advisors_variables(dealer_id, service_operation_ids, vin),
        )
        return parse_transportation_options(data)

    async def async_cancel_service_appointment(
        self,
        appointment_id: str,
        dealer_id: str,
        *,
        vin: str | UnsetType | None = UNSET,
    ) -> CancelServiceAppointmentResult | None:
        """Cancel a service appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelServiceAppointment",
            operations.CANCEL_SERVICE_APPOINTMENT,
            cancel_service_appointment_variables(appointment_id, dealer_id, vin),
        )
        return parse_cancel_service_appointment(data)

    async def async_create_service_appointment(
        self,
        appointment: ServiceAppointmentInput,
    ) -> ServiceAppointmentCreateResult | None:
        """Create a service appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateServiceAppointment",
            operations.CREATE_SERVICE_APPOINTMENT,
            service_appointment_variables(appointment),
        )
        return parse_create_service_appointment(data)

    async def async_update_service_appointment(
        self,
        appointment_id: str,
        appointment: ServiceAppointmentInput,
    ) -> ServiceAppointmentUpdateResult | None:
        """Replace a service appointment's selected details."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateServiceAppointment",
            operations.UPDATE_SERVICE_APPOINTMENT,
            update_service_appointment_variables(appointment_id, appointment),
        )
        return parse_update_service_appointment(data)

    async def async_update_vehicle_preferred_dealer(
        self,
        vin: str,
        preferred_dealer_id: str,
    ) -> PreferredDealerUpdateResult | None:
        """Set the preferred dealer for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehiclePreferredDealer",
            operations.UPDATE_VEHICLE_PREFERRED_DEALER,
            {"vin": vin, "preferredDealerId": preferred_dealer_id},
        )
        return parse_update_vehicle_preferred_dealer(data)

    async def async_get_second_delivery_appointment(
        self,
        vin: str,
    ) -> SecondDeliveryAppointmentResult | None:
        """Return the existing second-delivery appointment state."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointment",
            operations.SECOND_DELIVERY_APPOINTMENT,
            {"vin": vin},
        )
        return parse_second_delivery_appointment(data)

    async def async_get_second_delivery_home_time_slots(
        self,
        vin: str,
        address: AddressInput,
        hub_id: str,
        start: datetime,
        end: datetime,
    ) -> SecondDeliveryTimeSlotsResult | None:
        """Return at-home second-delivery appointment time slots."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointmentsAtHome",
            operations.SECOND_DELIVERY_APPOINTMENTS_AT_HOME,
            second_delivery_home_slots_variables(vin, address, hub_id, start, end),
        )
        return parse_second_delivery_home_time_slots(data)

    async def async_get_second_delivery_hub_time_slots(
        self,
        hub_id: str,
        postal_code: str,
        start: datetime,
        end: datetime,
        vin: str,
    ) -> SecondDeliveryTimeSlotsResult | None:
        """Return in-hub second-delivery appointment time slots."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointmentsAtHub",
            operations.SECOND_DELIVERY_APPOINTMENTS_AT_HUB,
            second_delivery_location_slots_variables(
                hub_id,
                postal_code,
                start,
                end,
                vin,
            ),
        )
        return parse_second_delivery_hub_time_slots(data)

    async def async_get_second_delivery_virtual_time_slots(
        self,
        hub_id: str,
        postal_code: str,
        start: datetime,
        end: datetime,
        vin: str,
    ) -> SecondDeliveryTimeSlotsResult | None:
        """Return virtual second-delivery appointment time slots."""

        data = await self._transport.async_graphql(
            "SecondDeliveryAppointmentsAtVirtual",
            operations.SECOND_DELIVERY_APPOINTMENTS_AT_VIRTUAL,
            second_delivery_location_slots_variables(
                hub_id,
                postal_code,
                start,
                end,
                vin,
            ),
        )
        return parse_second_delivery_virtual_time_slots(data)

    async def async_get_second_delivery_eligibility(
        self,
        vin: str,
    ) -> SecondDeliveryEligibility | None:
        """Return second-delivery eligibility and CTA state."""

        data = await self._transport.async_graphql(
            "SecondDeliveryEligibility",
            operations.SECOND_DELIVERY_ELIGIBILITY,
            {"vin": vin},
        )
        return parse_second_delivery_eligibility(data)

    async def async_validate_second_delivery_address(
        self,
        vin: str,
        address: AddressInput,
    ) -> SecondDeliveryAddressValidationResult | None:
        """Validate an address for at-home second delivery."""

        data = await self._transport.async_graphql(
            "ValidateSecondDeliveryAddress",
            operations.VALIDATE_SECOND_DELIVERY_ADDRESS,
            {"vin": vin, "address": address_input(address)},
        )
        return parse_second_delivery_address_validation(data)

    async def async_cancel_second_delivery_appointment(
        self,
        activity_id: int,
    ) -> SecondDeliveryOperationResult | None:
        """Cancel a second-delivery appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelSecondDeliveryAppointment",
            operations.CANCEL_SECOND_DELIVERY_APPOINTMENT,
            {"activityId": activity_id},
        )
        return parse_cancel_second_delivery_appointment(data)

    async def async_create_second_delivery_appointment(
        self,
        appointment: SecondDeliveryAppointmentInput,
    ) -> SecondDeliveryOperationResult | None:
        """Create a second-delivery appointment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateSecondDeliveryAppointment",
            operations.CREATE_SECOND_DELIVERY_APPOINTMENT,
            second_delivery_appointment_variables(appointment),
        )
        return parse_create_second_delivery_appointment(data)

    async def async_second_delivery_send_auth_code(
        self,
        appointment_id: int,
        access_token: str,
        *,
        send_via_email: bool,
        send_via_sms: bool,
    ) -> SecondDeliveryOperationResult | None:
        """Send a second-delivery appointment authentication code."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SecondDeliverySendAuthCode",
            operations.SECOND_DELIVERY_SEND_AUTH_CODE,
            second_delivery_send_auth_code_variables(
                appointment_id,
                access_token,
                send_via_email,
                send_via_sms,
            ),
        )
        return parse_second_delivery_send_auth_code(data)

    async def async_second_delivery_verify_auth_code(
        self,
        appointment_id: int,
        access_token: str,
        auth_code: str,
    ) -> SecondDeliveryOperationResult | None:
        """Verify a second-delivery appointment authentication code."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SecondDeliveryVerifyAuthCode",
            operations.SECOND_DELIVERY_VERIFY_AUTH_CODE,
            second_delivery_verify_auth_code_variables(
                appointment_id,
                access_token,
                auth_code,
            ),
        )
        return parse_second_delivery_verify_auth_code(data)

    async def async_update_second_delivery_appointment(
        self,
        activity_id: int,
        appointment: SecondDeliveryAppointmentInput,
    ) -> SecondDeliveryOperationResult | None:
        """Replace a second-delivery appointment's selected details."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateSecondDeliveryAppointment",
            operations.UPDATE_SECOND_DELIVERY_APPOINTMENT,
            update_second_delivery_appointment_variables(activity_id, appointment),
        )
        return parse_update_second_delivery_appointment(data)

    async def async_get_insurers(
        self,
    ) -> tuple[VehicleInsurer | None, ...] | None:
        """Return the insurer catalog available to the signed-in account."""

        data = await self._transport.async_graphql(
            "Insurers",
            operations.INSURERS,
            {},
        )
        return parse_insurers(data)

    async def async_get_vehicle_insurance(
        self,
        vin: str,
    ) -> VehicleInsurance | None:
        """Return the insurance policy attached to a vehicle."""

        data = await self._transport.async_graphql(
            "GetVehicleInsurance",
            operations.GET_VEHICLE_INSURANCE,
            {"vin": vin},
        )
        return parse_vehicle_insurance(data)

    async def async_add_vehicle_insurance(
        self,
        config: VehicleInsuranceInput,
    ) -> VehicleInsuranceMutationResult | None:
        """Add insurance details to a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddVehicleInsurance",
            operations.ADD_VEHICLE_INSURANCE,
            vehicle_insurance_variables(config),
        )
        return parse_add_vehicle_insurance(data)

    async def async_update_vehicle_insurance(
        self,
        config: VehicleInsuranceInput,
    ) -> VehicleInsuranceMutationResult | None:
        """Replace insurance details for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicleInsurance",
            operations.UPDATE_VEHICLE_INSURANCE,
            vehicle_insurance_variables(config),
        )
        return parse_update_vehicle_insurance(data)

    async def async_get_collision_centers(
        self,
        config: CollisionCenterSearchInput,
    ) -> tuple[CollisionCenter | None, ...] | None:
        """Return collision centers matching vehicle and location filters."""

        data = await self._transport.async_graphql(
            "CollisionCenters",
            operations.COLLISION_CENTERS,
            collision_center_variables(config),
        )
        return parse_collision_centers(data)

    async def async_create_collision_report(
        self,
        config: CreateCollisionReportInput,
    ) -> CreateCollisionReportResult | None:
        """Create a collision report for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateCollisionReport",
            operations.CREATE_COLLISION_REPORT,
            create_collision_report_variables(config),
        )
        return parse_create_collision_report(data)

    async def async_create_collision_report_pdf(
        self,
        collision_id: str,
    ) -> CreateCollisionReportPdfResult | None:
        """Generate a PDF URL for a collision report."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateCollisionReportPDF",
            operations.CREATE_COLLISION_REPORT_PDF,
            collision_report_pdf_variables(collision_id),
        )
        return parse_create_collision_report_pdf(data)

    async def async_delete_photo_for_collision_report(
        self,
        vin: str,
        collision_id: str,
        photo_section: PhotoSection,
    ) -> DeleteCollisionReportPhotoResult | None:
        """Delete one photo slot from a collision report."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeletePhotoForCollisionReport",
            operations.DELETE_PHOTO_FOR_COLLISION_REPORT,
            delete_collision_report_photo_variables(
                vin,
                collision_id,
                photo_section,
            ),
        )
        return parse_delete_collision_report_photo(data)

    async def async_upload_photo_for_collision_report(
        self,
        vin: str,
        collision_id: str,
        photo: CollisionReportPhotoInput,
        photo_section: PhotoSection,
    ) -> UploadCollisionReportPhotoResult | None:
        """Upload a Base64 attachment to one collision-report photo slot."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UploadPhotoForCollisionReport",
            operations.UPLOAD_PHOTO_FOR_COLLISION_REPORT,
            collision_report_photo_variables(
                vin,
                collision_id,
                photo,
                photo_section,
            ),
        )
        return parse_upload_collision_report_photo(data)

    async def async_get_vehicles(self) -> tuple[Vehicle, ...]:
        """Return vehicles attached to the account."""

        data = await self._transport.async_graphql(
            "VehiclesStaticData",
            operations.VEHICLES_STATIC_DATA,
            {},
        )
        return parse_vehicles(data)

    async def async_get_vehicles_with_capabilities(
        self,
    ) -> tuple[VehicleWithCapabilities | None, ...] | None:
        """Return the wearable client's batch vehicle and capability summary."""

        data = await self._transport.async_graphql(
            "WearableVehicles",
            operations.WEARABLE_VEHICLES,
            {},
        )
        return parse_vehicles_with_capabilities(data)

    async def async_add_vehicle(
        self,
        vin: str,
        terms_and_conditions_accepted: bool,
    ) -> AddVehicleResult | None:
        """Register a vehicle in the signed-in account's garage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddVehicle",
            operations.ADD_VEHICLE,
            add_vehicle_variables(vin, terms_and_conditions_accepted),
        )
        return parse_add_vehicle(data)

    async def async_delete_vehicle(self, vin: str) -> DeleteVehicleResult | None:
        """Remove a vehicle from the signed-in account's garage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteVehicle",
            operations.DELETE_VEHICLE,
            delete_vehicle_variables(vin),
        )
        return parse_delete_vehicle(data)

    async def async_add_ncar_icar_vehicle(
        self,
        terms_and_conditions_accepted: bool,
        guid: str,
        *,
        account: NcarIcarRegisterAccountInput | UnsetType | None = UNSET,
    ) -> NcarIcarAddVehicleResult | None:
        """Register a vehicle through the NCAR/ICAR garage flow."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "NcarIcarAddVehicle",
            operations.NCAR_ICAR_ADD_VEHICLE,
            ncar_icar_add_vehicle_variables(
                terms_and_conditions_accepted,
                guid,
                account=account,
            ),
        )
        return parse_ncar_icar_add_vehicle(data)

    async def async_get_pending_vehicles(
        self,
    ) -> tuple[PendingVehicle | None, ...] | None:
        """Return garage registrations awaiting ownership verification."""

        data = await self._transport.async_graphql(
            "PendingVehicles",
            operations.PENDING_VEHICLES,
            pending_vehicles_variables(),
        )
        return parse_pending_vehicles(data)

    async def async_get_ownership_status(self, vin: str) -> OwnershipStatus | None:
        """Return the vehicle's account ownership sign-in state."""

        data = await self._transport.async_graphql(
            "OwnershipStatus",
            operations.OWNERSHIP_STATUS,
            ownership_status_variables(vin),
        )
        return parse_ownership_status(data)

    async def async_get_apc_agreement(self, vin: str) -> APCAgreement | None:
        """Return the vehicle's APC agreement state."""

        data = await self._transport.async_graphql(
            "APCAgreement",
            operations.APC_AGREEMENT,
            apc_agreement_variables(vin),
        )
        return parse_apc_agreement(data)

    async def async_get_apc_document_url(self, vin: str) -> APCDocument | None:
        """Return the vehicle's APC agreement document URL."""

        data = await self._transport.async_graphql(
            "APCDocumentURL",
            operations.APC_DOCUMENT_URL,
            apc_document_url_variables(vin),
        )
        return parse_apc_document_url(data)

    async def async_create_apc_agreement(
        self,
        vin: str,
        opt_in: bool,
    ) -> APCAgreementMutationResult | None:
        """Create the vehicle's APC agreement selection."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateAPCAgreement",
            operations.CREATE_APC_AGREEMENT,
            create_apc_agreement_variables(vin, opt_in),
        )
        return parse_create_apc_agreement(data)

    async def async_update_apc_agreement(
        self,
        vin: str,
        opt_in: bool,
    ) -> APCAgreementMutationResult | None:
        """Update the vehicle's APC agreement selection."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateAPCAgreement",
            operations.UPDATE_APC_AGREEMENT,
            update_apc_agreement_variables(vin, opt_in),
        )
        return parse_update_apc_agreement(data)

    async def async_get_connected_terms_and_conditions_by_vin(
        self,
        vin: str,
    ) -> ConnectedTermsAndConditionsResult | None:
        """Request connected-services terms for a VIN through Nissan's mutation."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "ConnectedTermsAndConditionsByVIN",
            operations.CONNECTED_TERMS_AND_CONDITIONS_BY_VIN,
            connected_terms_and_conditions_by_vin_variables(vin),
        )
        return parse_connected_terms_and_conditions_by_vin(data)

    async def async_get_onboarding_features(
        self,
        vin: str,
    ) -> tuple[OnboardingFeature | None, ...] | None:
        """Return feature cards used while onboarding a vehicle."""

        data = await self._transport.async_graphql(
            "OnboardingFeatures",
            operations.ONBOARDING_FEATURES,
            onboarding_features_variables(vin),
        )
        return parse_onboarding_features(data)

    async def async_update_vehicle(
        self,
        vin: str,
        *,
        license_plate: str | UnsetType | None = UNSET,
        hologram: VehicleHologram | UnsetType | None = UNSET,
    ) -> UpdateVehicleResult | None:
        """Update optional license-plate and hologram garage metadata."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicle",
            operations.UPDATE_VEHICLE,
            update_vehicle_variables(
                vin,
                license_plate=license_plate,
                hologram=hologram,
            ),
        )
        return parse_update_vehicle(data)

    async def async_update_vehicle_manual_mileage(
        self,
        vin: str,
        *,
        manual_mileage: int | UnsetType | None = UNSET,
    ) -> UpdateVehicleManualMileageResult | None:
        """Update or clear the vehicle's manually recorded mileage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicleManualMileage",
            operations.UPDATE_VEHICLE_MANUAL_MILEAGE,
            update_vehicle_manual_mileage_variables(
                vin,
                manual_mileage=manual_mileage,
            ),
        )
        return parse_update_vehicle_manual_mileage(data)

    async def async_update_vehicle_nickname(
        self,
        vin: str,
        nickname: str,
    ) -> UpdateVehicleNicknameResult | None:
        """Update the vehicle nickname shown in the account garage."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateVehicleNickname",
            operations.UPDATE_VEHICLE_NICKNAME,
            update_vehicle_nickname_variables(vin, nickname),
        )
        return parse_update_vehicle_nickname(data)

    async def async_upload_ownership_verification(
        self,
        vin: str,
        filename: str,
        attachment: str,
        opt_in_sms: bool,
    ) -> UploadOwnershipVerificationResult | None:
        """Upload an ownership-verification attachment for a pending vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UploadOwnershipVerification",
            operations.UPLOAD_OWNERSHIP_VERIFICATION,
            upload_ownership_verification_variables(
                vin,
                filename,
                attachment,
                opt_in_sms,
            ),
        )
        return parse_upload_ownership_verification(data)

    async def async_get_emergency_contacts(
        self,
        vin: str,
    ) -> EmergencyContactsResult | None:
        """Return emergency contacts configured for a vehicle."""

        data = await self._transport.async_graphql(
            "EmergencyContacts",
            operations.EMERGENCY_CONTACTS,
            emergency_contacts_variables(vin),
        )
        return parse_emergency_contacts(data)

    async def async_create_emergency_contact(
        self,
        vin: str,
        contact: CreateEmergencyContactInput,
    ) -> CreateEmergencyContactResult | None:
        """Create an emergency contact for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateEmergencyContact",
            operations.CREATE_EMERGENCY_CONTACT,
            create_emergency_contact_variables(vin, contact),
        )
        return parse_create_emergency_contact(data)

    async def async_update_emergency_contact(
        self,
        vin: str,
        contact: UpdateEmergencyContactInput,
    ) -> UpdateEmergencyContactResult | None:
        """Update an emergency contact configured for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateEmergencyContact",
            operations.UPDATE_EMERGENCY_CONTACT,
            update_emergency_contact_variables(vin, contact),
        )
        return parse_update_emergency_contact(data)

    async def async_delete_emergency_contact(
        self,
        vin: str,
        emergency_contact_id: str,
    ) -> DeleteEmergencyContactResult | None:
        """Delete an emergency contact configured for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteEmergencyContact",
            operations.DELETE_EMERGENCY_CONTACT,
            delete_emergency_contact_variables(vin, emergency_contact_id),
        )
        return parse_delete_emergency_contact(data)

    async def async_get_driver_invites(self, vin: str) -> DriverInvitesResult | None:
        """Return shared-driver invitations for a vehicle."""

        data = await self._transport.async_graphql(
            "DriverInvites",
            operations.DRIVER_INVITES,
            driver_invites_variables(vin),
        )
        return parse_driver_invites(data)

    async def async_invite_driver(
        self,
        config: DriverInviteInput | UnsetType | None = UNSET,
    ) -> InviteDriverResult | None:
        """Invite another account to drive a vehicle with selected permissions."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "InviteDriver",
            operations.INVITE_DRIVER,
            invite_driver_variables(config),
        )
        return parse_invite_driver(data)

    async def async_driver_invite_action(
        self,
        config: DriverInviteActionInput | UnsetType | None = UNSET,
    ) -> DriverInviteActionResult | None:
        """Accept, decline, or invalidate a received driver invitation."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DriverInviteAction",
            operations.DRIVER_INVITE_ACTION,
            driver_invite_action_variables(config),
        )
        return parse_driver_invite_action(data)

    async def async_delete_driver(self, invite_id: str) -> DeleteDriverResult | None:
        """Remove a shared driver or invitation from the account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteDriver",
            operations.DELETE_DRIVER,
            delete_driver_variables(invite_id),
        )
        return parse_delete_driver(data)

    async def async_update_driver(
        self,
        config: UpdateDriverInput,
    ) -> UpdateDriverResult | None:
        """Replace a shared driver's permissions and notification settings."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateDriver",
            operations.UPDATE_DRIVER,
            update_driver_variables(config),
        )
        return parse_update_driver(data)

    async def async_owner_invite_action(
        self,
        config: OwnerInviteActionInput | UnsetType | None = UNSET,
    ) -> OwnerInviteActionResult | None:
        """Resend or cancel a shared-driver invitation as the vehicle owner."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "OwnerInviteAction",
            operations.OWNER_INVITE_ACTION,
            owner_invite_action_variables(config),
        )
        return parse_owner_invite_action(data)

    async def async_create_rsa_link(self, vin: str) -> CreateRSALinkResult | None:
        """Create the roadside-assistance link associated with a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateRSALink",
            operations.CREATE_RSA_LINK,
            create_rsa_link_variables(vin),
        )
        return parse_create_rsa_link(data)

    async def async_get_vehicle_status(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit = DistanceUnit.MILE,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleStatus:
        """Return cached dynamic status without waking the vehicle."""

        data = await self._transport.async_graphql(
            "VehicleDynamicData",
            operations.VEHICLE_DYNAMIC_DATA,
            {
                "vin": vin,
                "unit": distance_unit.value,
                "temperatureUnit": temperature_unit.value,
            },
        )
        return parse_vehicle_status(data, vin)

    async def async_get_vehicle_battery_status(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> BatteryStatus | None:
        """Return the upstream service's standalone cached battery-status response."""

        data = await self._transport.async_graphql(
            "VehicleBatteryStatus",
            operations.VEHICLE_BATTERY_STATUS,
            vehicle_battery_status_variables(vin, unit=unit),
        )
        return parse_vehicle_battery_status(data, vin)

    async def async_get_vehicle_boundary_alerts(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> tuple[BoundaryAlert | None, ...] | None:
        """Return the upstream service's standalone boundary-alert collection."""

        data = await self._transport.async_graphql(
            "VehicleBoundaryAlerts",
            operations.VEHICLE_BOUNDARY_ALERTS,
            vehicle_boundary_alerts_variables(
                vin,
                distance_unit=distance_unit,
            ),
        )
        return parse_vehicle_boundary_alerts(data)

    async def async_get_vehicle_climate_status(
        self,
        vin: str,
        temperature_unit: TemperatureUnit,
    ) -> ClimateStatus | None:
        """Return the upstream service's standalone cached climate-status response."""

        data = await self._transport.async_graphql(
            "VehicleClimateStatus",
            operations.VEHICLE_CLIMATE_STATUS,
            vehicle_climate_status_variables(vin, temperature_unit),
        )
        return parse_vehicle_climate_status(data, vin)

    async def async_get_vehicle_curfew_alerts(
        self,
        vin: str,
    ) -> tuple[CurfewAlert | None, ...] | None:
        """Return the upstream service's standalone curfew-alert collection."""

        data = await self._transport.async_graphql(
            "VehicleCurfewAlerts",
            operations.VEHICLE_CURFEW_ALERTS,
            vehicle_curfew_alerts_variables(vin),
        )
        return parse_vehicle_curfew_alerts(data)

    async def async_get_vehicle_doors_status(
        self,
        vin: str,
    ) -> DoorsStatus | None:
        """Return the upstream service's standalone cached doors-status response."""

        data = await self._transport.async_graphql(
            "VehicleDoorsStatus",
            operations.VEHICLE_DOORS_STATUS,
            vehicle_doors_status_variables(vin),
        )
        return parse_vehicle_doors_status(data, vin)

    async def async_get_vehicle_model_year(
        self,
        vin: str,
    ) -> VehicleModelYear | None:
        """Return the standalone required model and year fields for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleModelYear",
            operations.VEHICLE_MODEL_YEAR,
            vehicle_model_year_variables(vin),
        )
        return parse_vehicle_model_year(data)

    async def async_get_vehicle_nickname(
        self,
        vin: str,
    ) -> VehicleNickname | None:
        """Return the standalone nullable nickname response for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleNickname",
            operations.VEHICLE_NICKNAME,
            vehicle_nickname_variables(vin),
        )
        return parse_vehicle_nickname(data)

    async def async_get_vehicle_speed_alerts(
        self,
        vin: str,
        *,
        speed_unit: SpeedUnit | UnsetType | None = UNSET,
    ) -> tuple[SpeedAlert | None, ...] | None:
        """Return the upstream service's standalone speed-alert collection."""

        data = await self._transport.async_graphql(
            "VehicleSpeedAlerts",
            operations.VEHICLE_SPEED_ALERTS,
            vehicle_speed_alerts_variables(vin, speed_unit=speed_unit),
        )
        return parse_vehicle_speed_alerts(data)

    async def async_get_vehicle_core_status(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> VehicleStatus | None:
        """Return the narrower non-EV VehicleStatus operation from the upstream service."""

        data = await self._transport.async_graphql(
            "VehicleStatus",
            operations.VEHICLE_STATUS,
            vehicle_status_variables(vin, unit=unit),
        )
        return parse_vehicle_core_status(data, vin)

    async def async_get_vehicle_status_and_recalls(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> VehicleStatusAndRecalls | None:
        """Return the upstream service's combined cached core status and recalls response."""

        data = await self._transport.async_graphql(
            "VehicleStatusAndRecalls",
            operations.VEHICLE_STATUS_AND_RECALLS,
            vehicle_status_and_recalls_variables(vin, unit=unit),
        )
        return parse_vehicle_status_and_recalls(data, vin)

    async def async_get_vehicle_valet_alert(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> ValetAlert | None:
        """Return the upstream service's standalone valet-alert response."""

        data = await self._transport.async_graphql(
            "VehicleValetAlerts",
            operations.VEHICLE_VALET_ALERTS,
            vehicle_valet_alerts_variables(vin, distance_unit=distance_unit),
        )
        return parse_vehicle_valet_alert(data)

    async def async_get_vehicle_location(self, vin: str) -> VehicleLocation:
        """Return the last cached location without requesting a new fix."""

        data = await self._transport.async_graphql(
            "VehicleLocation",
            operations.VEHICLE_LOCATION,
            {"vin": vin},
        )
        return parse_vehicle_location(data, vin)

    async def async_get_photos_around_vehicle(self, vin: str) -> VehiclePhotos | None:
        """Return cached vehicle photos and their temporary links when available."""

        data = await self._transport.async_graphql(
            "PhotosAroundVehicle",
            operations.PHOTOS_AROUND_VEHICLE,
            {"vin": vin},
        )
        return parse_photos_around_vehicle(data)

    async def async_get_vehicle_journeys(self, vin: str) -> VehicleJourneys | None:
        """Return journeys cached for a connected vehicle."""

        data = await self._transport.async_graphql(
            "VehicleJourneys",
            operations.VEHICLE_JOURNEYS,
            {"vin": vin},
        )
        return parse_vehicle_journeys(data)

    async def async_get_vehicle_planned_routes(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        temperature_unit: TemperatureUnit | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> VehiclePlannedRoutes | None:
        """Return saved planned routes for an electric vehicle."""

        data = await self._transport.async_graphql(
            "VehiclePlannedRoutes",
            operations.VEHICLE_PLANNED_ROUTES,
            optional_input_fields(
                vin=vin,
                distanceUnit=optional_navigation_enum(distance_unit),
                temperatureUnit=optional_navigation_enum(temperature_unit),
            ),
            extra_headers=_navigation_headers(data_source),
        )
        return parse_vehicle_planned_routes(data)

    async def async_get_vehicle_point_of_interest_destinations(
        self,
        vin: str,
        *,
        folder: PointOfInterestFolderFilter | UnsetType | None = (PointOfInterestFolderFilter.BOTH),
    ) -> VehiclePointOfInterestDestinations | None:
        """Return favorite and recent destinations stored for a vehicle."""

        data = await self._transport.async_graphql(
            "VehiclePOIDestinations",
            operations.VEHICLE_POINT_OF_INTEREST_DESTINATIONS,
            optional_input_fields(
                vin=vin,
                folderName=optional_navigation_enum(folder),
            ),
        )
        return parse_vehicle_point_of_interest_destinations(data)

    async def async_get_vehicle_routes_history(
        self,
        vin: str,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        temperature_unit: TemperatureUnit | UnsetType | None = UNSET,
        status: RouteStatus | UnsetType | None = UNSET,
    ) -> VehicleRoutesHistory | None:
        """Return route history for a compatible electric AVK2 vehicle."""

        data = await self._transport.async_graphql(
            "RoutesHistory",
            operations.ROUTES_HISTORY,
            optional_input_fields(
                vin=vin,
                distanceUnit=optional_navigation_enum(distance_unit),
                temperatureUnit=optional_navigation_enum(temperature_unit),
                status=optional_navigation_enum(status),
            ),
        )
        return parse_vehicle_routes_history(data)

    async def async_get_t_junction_locations(self, vin: str) -> TJunctionLocations | None:
        """Return saved and unsaved T-junction camera locations."""

        data = await self._transport.async_graphql(
            "TJunctionLocations",
            operations.T_JUNCTION_LOCATIONS,
            {"vin": vin},
        )
        return parse_t_junction_locations(data)

    async def async_get_vehicle_ev_waypoints(
        self,
        vin: str,
        routes: tuple[RouteWaypointInput | None, ...],
        plug_connector_types: tuple[PlugConnectorType | None, ...],
        *,
        depart_at: datetime | UnsetType | None = UNSET,
        arrived_by: datetime | UnsetType | None = UNSET,
        state_of_charge_at_destination: int | UnsetType | None = UNSET,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        estimated_battery_level_at_departure: int | UnsetType | None = UNSET,
        minimum_power: float | UnsetType | None = UNSET,
        state_of_charge_at_stop: int | UnsetType | None = UNSET,
        use_hvac: bool | UnsetType | None = UNSET,
        avoid_highway: bool | UnsetType | None = UNSET,
        avoid_tolls: bool | UnsetType | None = UNSET,
        avoid_ferries: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> EVWaypointResult | None:
        """Calculate electric route waypoints or return a typed route error."""

        effective_state_of_charge_at_stop = state_of_charge_at_stop
        if data_source is NavigationDataSource.KMR and isinstance(
            effective_state_of_charge_at_stop,
            UnsetType,
        ):
            effective_state_of_charge_at_stop = 20
        data = await self._transport.async_graphql(
            "VehicleEVWaypoints",
            operations.VEHICLE_EV_WAYPOINTS,
            optional_input_fields(
                vin=vin,
                departAt=optional_destination_time(depart_at),
                arrivedBy=optional_destination_time(arrived_by),
                socAtDestination=state_of_charge_at_destination,
                routes=nullable_route_waypoints_input(routes),
                distanceUnit=optional_navigation_enum(distance_unit),
                plugConnectorTypes=nullable_plug_connector_types_input(plug_connector_types),
                estimatedBatteryLevelAtDeparture=optional_battery_level_string(
                    estimated_battery_level_at_departure
                ),
                minPower=minimum_power,
                socAtStop=effective_state_of_charge_at_stop,
                useHvac=use_hvac,
                avoidHighway=avoid_highway,
                avoidTolls=avoid_tolls,
                avoidFerries=avoid_ferries,
            ),
            extra_headers=_navigation_headers(data_source),
        )
        return parse_vehicle_ev_waypoints(data)

    async def async_get_ota_update(self, vin: str) -> OtaUpdate | None:
        """Return the OTA campaign currently offered to a compatible vehicle."""

        data = await self._transport.async_graphql(
            "OtaUpdate",
            operations.OTA_UPDATE,
            {"vin": vin},
        )
        return parse_ota_update(data)

    async def async_get_ota_update_progress(
        self,
        vin: str,
        campaign_operation_id: str,
    ) -> OtaUpdateProgress | None:
        """Return download or activation progress for one OTA campaign."""

        data = await self._transport.async_graphql(
            "OtaUpdateProgress",
            operations.OTA_UPDATE_PROGRESS,
            {
                "campaignOperationId": campaign_operation_id,
                "vin": vin,
            },
        )
        return parse_ota_update_progress(data)

    async def async_get_notification_preferences(
        self,
        vin: str,
    ) -> tuple[NotificationPreference | None, ...] | None:
        """Return vehicle notification opt-ins grouped by category."""

        data = await self._transport.async_graphql(
            "NotificationPreferences",
            operations.NOTIFICATION_PREFERENCES,
            {"vin": vin},
        )
        return parse_notification_preferences(data)

    async def async_get_nissan_energy_notification_preferences(
        self,
        vin: str,
    ) -> NissanEnergyNotificationPreferences | None:
        """Return Nissan Energy Charge Network delivery preferences."""

        data = await self._transport.async_graphql(
            "NissanEnergyNotificationPreferences",
            operations.NISSAN_ENERGY_NOTIFICATION_PREFERENCES,
            {"vin": vin},
        )
        return parse_nissan_energy_notification_preferences(data)

    async def async_get_in_vehicle_messages(
        self,
        vin: str,
    ) -> tuple[InVehicleMessageSummary | None, ...] | None:
        """Return the vehicle's nullable in-vehicle message summaries."""

        data = await self._transport.async_graphql(
            "InVehicleMessages",
            operations.IN_VEHICLE_MESSAGES,
            in_vehicle_messages_variables(vin),
        )
        return parse_in_vehicle_messages(data)

    async def async_get_in_vehicle_message(
        self,
        vin: str,
        campaign_id: str,
        *,
        push: bool | UnsetType | None = False,
    ) -> InVehicleMessage | None:
        """Fetch one message, allowing Nissan to record the detail as viewed."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "InVehicleMessage",
            operations.IN_VEHICLE_MESSAGE,
            in_vehicle_message_variables(vin, campaign_id, push=push),
        )
        return parse_in_vehicle_message(data)

    async def async_get_vehicle_alerts(
        self,
        vin: str,
        *,
        speed_unit: SpeedUnit | None = None,
        distance_unit: DistanceUnit | None = None,
    ) -> VehicleAlerts | None:
        """Return all configured vehicle alerts in one cached read."""

        data = await self._transport.async_graphql(
            "VehicleAlerts",
            operations.VEHICLE_ALERTS,
            _optional_variables(
                vin=vin,
                speedUnit=_enum_value(speed_unit),
                distanceUnit=_enum_value(distance_unit),
            ),
        )
        return parse_vehicle_alerts(data)

    async def async_get_breach_alerts(
        self,
        vin: str,
        *,
        page_number: int = 1,
        items_per_page: int = 20,
    ) -> BreachAlerts | None:
        """Return one page of raw vehicle-alert breach events."""

        _validate_positive_integer(page_number, "page_number")
        _validate_positive_integer(items_per_page, "items_per_page")
        data = await self._transport.async_graphql(
            "BreachAlerts",
            operations.BREACH_ALERTS,
            {
                "vin": vin,
                "pageNumber": page_number,
                "itemsPerPage": items_per_page,
            },
        )
        return parse_breach_alerts(data)

    async def async_get_alert_request_status(
        self,
        vin: str,
        service_request_id: str,
        alert_kind: VehicleAlertKind,
    ) -> str | None:
        """Return the raw status of a vehicle-alert configuration request."""

        match alert_kind:
            case VehicleAlertKind.BOUNDARY:
                operation_name = "VehicleBoundaryAlert"
                document = operations.VEHICLE_BOUNDARY_ALERT
                root_field = "boundaryAlert"
                status_required = True
            case VehicleAlertKind.CURFEW:
                operation_name = "VehicleCurfewAlert"
                document = operations.VEHICLE_CURFEW_ALERT
                root_field = "curfewAlert"
                status_required = True
            case VehicleAlertKind.SPEED:
                operation_name = "VehicleSpeedAlert"
                document = operations.VEHICLE_SPEED_ALERT
                root_field = "speedAlert"
                status_required = True
            case VehicleAlertKind.VALET:
                operation_name = "VehicleValetAlert"
                document = operations.VEHICLE_VALET_ALERT
                root_field = "valetAlert"
                status_required = False
            case _:
                assert_never(alert_kind)

        data = await self._transport.async_graphql(
            operation_name,
            document,
            {"vin": vin, "serviceRequestId": service_request_id},
        )
        return parse_alert_request_status(
            data,
            root_field,
            status_required=status_required,
        )

    async def async_wait_for_alert_request(
        self,
        vin: str,
        request: VehicleAlertRequest,
        *,
        poll_interval_seconds: float = 1.0,
        timeout_seconds: float = 210.0,
    ) -> str:
        """Poll a vehicle-alert change until Nissan reports success or failure."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        async with asyncio.timeout(timeout_seconds):
            while True:
                status = await self.async_get_alert_request_status(
                    vin,
                    request.id,
                    request.kind,
                )
                if status in {
                    ServiceRequestStatus.SUCCESS.value,
                    ServiceRequestStatus.FAILED.value,
                }:
                    return status
                await asyncio.sleep(poll_interval_seconds)

    async def async_create_boundary_alert(
        self,
        vin: str,
        alert: BoundaryAlertInput,
    ) -> VehicleAlertRequest:
        """Create a vehicle entry or exit boundary alert."""

        return await self._async_vehicle_alert_request(
            "CreateBoundaryAlert",
            operations.CREATE_BOUNDARY_ALERT,
            "createBoundaryAlert",
            {"vin": vin, "alert": boundary_alert_input(alert)},
            VehicleAlertKind.BOUNDARY,
        )

    async def async_update_boundary_alert(
        self,
        vin: str,
        service_request_id: str,
        update: BoundaryAlertUpdate,
    ) -> VehicleAlertRequest:
        """Patch an existing boundary alert."""

        return await self._async_vehicle_alert_request(
            "SetBoundaryAlert",
            operations.UPDATE_BOUNDARY_ALERT,
            "setBoundaryAlert",
            {
                "vin": vin,
                "alert": boundary_alert_update_input(service_request_id, update),
            },
            VehicleAlertKind.BOUNDARY,
        )

    async def async_delete_boundary_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Delete an existing boundary alert."""

        return await self._async_vehicle_alert_request(
            "CancelBoundaryAlert",
            operations.DELETE_BOUNDARY_ALERT,
            "cancelBoundaryAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.BOUNDARY,
        )

    async def async_toggle_boundary_alert(
        self,
        vin: str,
        service_request_id: str,
        *,
        enabled: bool,
    ) -> VehicleAlertRequest:
        """Enable or disable an existing boundary alert."""

        return await self._async_vehicle_alert_request(
            "ToggleBoundaryAlert",
            operations.TOGGLE_BOUNDARY_ALERT,
            "toggleBoundaryAlert",
            {
                "vin": vin,
                "alert": {
                    "serviceRequestId": service_request_id,
                    "enable": enabled,
                },
            },
            VehicleAlertKind.BOUNDARY,
        )

    async def async_create_curfew_alert(
        self,
        vin: str,
        alert: CurfewAlertInput,
    ) -> VehicleAlertRequest:
        """Create a recurring vehicle curfew alert."""

        return await self._async_vehicle_alert_request(
            "CreateCurfewAlert",
            operations.CREATE_CURFEW_ALERT,
            "createCurfewAlert",
            {"vin": vin, "alert": curfew_alert_input(alert)},
            VehicleAlertKind.CURFEW,
        )

    async def async_update_curfew_alert(
        self,
        vin: str,
        service_request_id: str,
        alert: CurfewAlertInput,
    ) -> VehicleAlertRequest:
        """Replace an existing curfew alert."""

        return await self._async_vehicle_alert_request(
            "SetCurfewAlert",
            operations.UPDATE_CURFEW_ALERT,
            "setCurfewAlert",
            {
                "vin": vin,
                "serviceRequestId": service_request_id,
                "alert": curfew_alert_input(alert),
            },
            VehicleAlertKind.CURFEW,
        )

    async def async_delete_curfew_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Delete an existing curfew alert."""

        return await self._async_vehicle_alert_request(
            "CancelCurfewAlert",
            operations.DELETE_CURFEW_ALERT,
            "cancelCurfewAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.CURFEW,
        )

    async def async_toggle_curfew_alert(
        self,
        vin: str,
        service_request_id: str,
        *,
        enabled: bool,
    ) -> VehicleAlertRequest:
        """Enable or disable an existing curfew alert."""

        return await self._async_vehicle_alert_request(
            "ToggleCurfewAlert",
            operations.TOGGLE_CURFEW_ALERT,
            "toggleCurfewAlert",
            {
                "vin": vin,
                "alert": {
                    "serviceRequestId": service_request_id,
                    "enable": enabled,
                },
            },
            VehicleAlertKind.CURFEW,
        )

    async def async_create_speed_alert(
        self,
        vin: str,
        alert: SpeedAlertInput,
    ) -> VehicleAlertRequest:
        """Create a vehicle speed alert."""

        return await self._async_vehicle_alert_request(
            "CreateSpeedAlert",
            operations.CREATE_SPEED_ALERT,
            "createSpeedAlert",
            {"vin": vin, "alert": speed_alert_input(alert)},
            VehicleAlertKind.SPEED,
        )

    async def async_update_speed_alert(
        self,
        vin: str,
        service_request_id: str,
        alert: SpeedAlertInput,
    ) -> VehicleAlertRequest:
        """Replace an existing speed alert."""

        speed_update = {
            "serviceRequestId": service_request_id,
            **speed_alert_input(alert),
        }
        return await self._async_vehicle_alert_request(
            "SetSpeedAlert",
            operations.UPDATE_SPEED_ALERT,
            "setSpeedAlert",
            {"vin": vin, "alert": speed_update},
            VehicleAlertKind.SPEED,
        )

    async def async_delete_speed_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Delete an existing speed alert."""

        return await self._async_vehicle_alert_request(
            "CancelSpeedAlert",
            operations.DELETE_SPEED_ALERT,
            "cancelSpeedAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.SPEED,
        )

    async def async_toggle_speed_alert(
        self,
        vin: str,
        service_request_id: str,
        *,
        enabled: bool,
    ) -> VehicleAlertRequest:
        """Enable or disable an existing speed alert."""

        return await self._async_vehicle_alert_request(
            "ToggleSpeedAlert",
            operations.TOGGLE_SPEED_ALERT,
            "toggleSpeedAlert",
            {
                "vin": vin,
                "alert": {
                    "serviceRequestId": service_request_id,
                    "enable": enabled,
                },
            },
            VehicleAlertKind.SPEED,
        )

    async def async_activate_valet_alert(
        self,
        vin: str,
        *,
        radius: ValetRadiusInput | UnsetType | None = UNSET,
        location: CoordinateInput | UnsetType | None = UNSET,
    ) -> VehicleAlertRequest:
        """Activate a valet boundary alert around an optional location."""

        variables = optional_input_fields(
            vin=vin,
            radiusWithUnit=optional_valet_radius_input(radius),
            location=optional_coordinate_input(location),
        )
        return await self._async_vehicle_alert_request(
            "ActivateValetAlert",
            operations.ACTIVATE_VALET_ALERT,
            "activateValetAlert",
            variables,
            VehicleAlertKind.VALET,
        )

    async def async_deactivate_valet_alert(
        self,
        vin: str,
        service_request_id: str,
    ) -> VehicleAlertRequest:
        """Deactivate the current valet alert."""

        return await self._async_vehicle_alert_request(
            "DeactivateValetAlert",
            operations.DEACTIVATE_VALET_ALERT,
            "deactivateValetAlert",
            {"vin": vin, "serviceRequestId": service_request_id},
            VehicleAlertKind.VALET,
        )

    async def async_get_reminder_notifications_after_leaving_vehicle(
        self,
        vin: str,
    ) -> ReminderNotificationsAfterLeavingVehicle | None:
        """Return after-leaving reminder flags when supported by the vehicle."""

        data = await self._transport.async_graphql(
            "ReminderNotificationsAfterLeavingVehicle",
            operations.REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE,
            {"vin": vin},
        )
        return parse_reminder_notifications_after_leaving_vehicle(data)

    async def async_toggle_reminder_notifications_after_leaving_vehicle(
        self,
        vin: str,
        *,
        enable_lock: bool | None = None,
        enable_door: bool | None = None,
        enable_trunk: bool | None = None,
        enable_sunroof: bool | None = None,
        enable_window: bool | None = None,
    ) -> bool | None:
        """Patch one or more after-leaving reminder flags."""

        reminder_notifications = _optional_variables(
            enableLock=enable_lock,
            enableDoor=enable_door,
            enableTrunk=enable_trunk,
            enableSunroof=enable_sunroof,
            enableWindow=enable_window,
        )
        if not reminder_notifications:
            raise ValueError("At least one reminder notification setting is required")
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "ToggleReminderNotificationsAfterLeavingVehicle",
            operations.TOGGLE_REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE,
            {
                "vin": vin,
                "reminderNotifications": reminder_notifications,
            },
        )
        return parse_toggle_reminder_notifications_after_leaving_vehicle(data)

    async def async_get_vehicle_data_privacy_mode(
        self,
        vin: str,
    ) -> DataPrivacyMode | None:
        """Return the vehicle's current data privacy mode."""

        data = await self._transport.async_graphql(
            "VehicleDataPrivacyMode",
            operations.VEHICLE_DATA_PRIVACY_MODE,
            {"vin": vin},
        )
        return parse_vehicle_data_privacy_mode(data)

    async def async_get_vehicle_wifi_consumption(
        self,
        vin: str,
    ) -> VehicleWifiConsumption | None:
        """Return current in-vehicle Wi-Fi consumption when available."""

        data = await self._transport.async_graphql(
            "VehicleWifiConsumption",
            operations.VEHICLE_WIFI_CONSUMPTION,
            {"vin": vin},
        )
        return parse_vehicle_wifi_consumption(data)

    async def async_get_vehicle_preferences(
        self,
        vin: str,
    ) -> VehiclePreferences | None:
        """Return MIL/DTC maintenance-data sharing preferences when available."""

        data = await self._transport.async_graphql(
            "VehiclePreferences",
            operations.VEHICLE_PREFERENCES,
            {"vin": vin},
        )
        return parse_vehicle_preferences(data)

    async def async_get_vehicle_subscriptions(
        self,
        vin: str,
    ) -> VehicleSubscriptions | None:
        """Return the vehicle subscription capability without app-level filtering."""

        data = await self._transport.async_graphql(
            "VehicleSubscriptions",
            operations.VEHICLE_SUBSCRIPTIONS,
            {"vin": vin},
        )
        return parse_vehicle_subscriptions(data, vin)

    async def async_update_vehicle_preferences(
        self,
        vin: str,
        preferences: VehiclePreferences,
    ) -> bool:
        """Replace all MIL/DTC maintenance-data sharing preferences."""

        return await self._async_success_operation(
            "UpdateVehiclePreferences",
            operations.UPDATE_VEHICLE_PREFERENCES,
            "updateVehiclePreferences",
            {
                "vin": vin,
                "communication": {
                    "milDataSharing": {
                        "enabled": preferences.enabled,
                        "text": preferences.text,
                        "phone": preferences.phone,
                        "email": preferences.email,
                    }
                },
            },
        )

    async def async_get_remote_service_history(
        self,
        vin: str,
        *,
        page_number: int,
        items_per_page: int,
    ) -> RemoteServiceHistory | None:
        """Return one page of raw remote-service request history."""

        data = await self._transport.async_graphql(
            "RemoteServiceHistory",
            operations.REMOTE_SERVICE_HISTORY,
            {
                "vin": vin,
                "pageNumber": page_number,
                "itemsPerPage": items_per_page,
            },
        )
        return parse_remote_service_history(data)

    async def async_get_maintenance_timeline(
        self,
        vin: str,
        mileage_unit: DistanceUnit = DistanceUnit.MILE,
    ) -> MaintenanceTimeline | None:
        """Return the vehicle's current and projected maintenance milestones."""

        data = await self._transport.async_graphql(
            "GetMaintenanceTimeline",
            operations.GET_MAINTENANCE_TIMELINE,
            get_maintenance_timeline_variables(vin, mileage_unit),
        )
        return parse_maintenance_timeline(data)

    async def async_get_service_contracts(
        self,
        vin: str,
        mileage: int,
    ) -> tuple[ServiceContract | None, ...] | None:
        """Return warranty service contracts evaluated at the supplied mileage."""

        data = await self._transport.async_graphql(
            "GetServiceContracts",
            operations.GET_SERVICE_CONTRACTS,
            get_service_contracts_variables(vin, mileage),
        )
        return parse_service_contracts(data)

    async def async_add_past_service(
        self,
        service: PastServiceInput | UnsetType | None = UNSET,
    ) -> PastServiceResult | None:
        """Add a completed maintenance record to the account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddPastService",
            operations.ADD_PAST_SERVICE,
            add_past_service_variables(service),
        )
        return parse_add_past_service(data)

    async def async_update_past_service(
        self,
        service: UpdatePastServiceInput,
    ) -> PastServiceResult | None:
        """Replace a completed maintenance record."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePastService",
            operations.UPDATE_PAST_SERVICE,
            update_past_service_variables(service),
        )
        return parse_update_past_service(data)

    async def async_get_parts_reminders(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> VehiclePartsReminders | None:
        """Return the vehicle's service-part catalog and configured reminders."""

        data = await self._transport.async_graphql(
            "PartsReminders",
            operations.PARTS_REMINDERS,
            parts_reminders_variables(vin, unit=unit),
        )
        return parse_parts_reminders(data)

    async def async_create_parts_reminder(
        self,
        vin: str,
        reminder: CreatePartsReminderInput,
    ) -> PartsReminderMutationResult | None:
        """Create a service-parts reminder for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreatePartsReminder",
            operations.CREATE_PARTS_REMINDER,
            create_parts_reminder_variables(vin, reminder),
        )
        return parse_create_parts_reminder(data)

    async def async_update_parts_reminder(
        self,
        vin: str,
        reminder: UpdatePartsReminderInput,
    ) -> PartsReminderMutationResult | None:
        """Replace a service-parts reminder for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePartsReminder",
            operations.UPDATE_PARTS_REMINDER,
            update_parts_reminder_variables(vin, reminder),
        )
        return parse_update_parts_reminder(data)

    async def async_reset_parts_reminder(
        self,
        vin: str,
        reminder: ResetPartsReminderInput,
    ) -> PartsReminderMutationResult | None:
        """Reset a service-parts reminder schedule."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "ResetPartsReminder",
            operations.RESET_PARTS_REMINDER,
            reset_parts_reminder_variables(vin, reminder),
        )
        return parse_reset_parts_reminder(data)

    async def async_delete_parts_reminder(
        self,
        vin: str,
        reminder_id: str,
    ) -> PartsReminderMutationResult | None:
        """Delete a service-parts reminder from a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeletePartsReminder",
            operations.DELETE_PARTS_REMINDER,
            delete_parts_reminder_variables(vin, reminder_id),
        )
        return parse_delete_parts_reminder(data)

    async def async_get_collision_history(
        self,
        vin: str,
    ) -> tuple[CollisionHistoryEntry | None, ...] | None:
        """Return collision reports attached to the vehicle account."""

        data = await self._transport.async_graphql(
            "CollisionHistory",
            operations.COLLISION_HISTORY,
            collision_history_variables(vin),
        )
        return parse_collision_history(data)

    async def async_get_collision_probe_data(
        self,
        vin: str,
    ) -> tuple[CollisionProbeReading | None, ...] | None:
        """Return vehicle telemetry captured for a collision report."""

        data = await self._transport.async_graphql(
            "CollisionProbeData",
            operations.COLLISION_PROBE_DATA,
            collision_probe_data_variables(vin),
        )
        return parse_collision_probe_data(data)

    async def async_get_vehicle_capabilities(
        self,
        vin: str,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleCapabilities:
        """Return the connected services advertised for a vehicle."""

        data = await self._transport.async_graphql(
            "VehicleCapabilities",
            operations.VEHICLE_CAPABILITIES,
            {"vin": vin, "unit": temperature_unit.value},
        )
        return parse_vehicle_capabilities(data, vin)

    async def async_get_charge_schedules(self, vin: str) -> tuple[ChargeSchedule, ...]:
        """Return the vehicle's recurring charge schedules."""

        data = await self._transport.async_graphql(
            "VehicleChargeSchedules",
            operations.VEHICLE_CHARGE_SCHEDULES,
            {"vin": vin},
        )
        return parse_charge_schedules(data)

    async def async_get_charge_config(self, vin: str) -> ChargeConfig | None:
        """Return configured charging limits when supported by the vehicle."""

        data = await self._transport.async_graphql(
            "ChargeConfig",
            operations.CHARGE_CONFIG,
            {"vin": vin},
        )
        return parse_charge_config(data)

    async def async_get_v2l_status(self, vin: str) -> V2LStatus | None:
        """Return V2L state and battery reserve levels when supported."""

        data = await self._transport.async_graphql(
            "V2lStatus",
            operations.V2L_STATUS,
            {"vin": vin},
        )
        return parse_v2l_status(data)

    async def async_get_charge_history(
        self,
        vin: str,
        aggregator: ChargeHistoryAggregator,
    ) -> VehicleChargeHistory | None:
        """Return charging sessions and summaries for a requested aggregation."""

        data = await self._transport.async_graphql(
            "VehicleChargeHistory",
            operations.VEHICLE_CHARGE_HISTORY,
            {"vin": vin, "aggregator": aggregator.value},
        )
        return parse_vehicle_charge_history(data)

    async def async_get_energy_account_status(
        self,
        vin: str,
    ) -> EnergyAccountStatusResult | None:
        """Return Nissan Energy account, PnC, toggle, and NACS status."""

        data = await self._transport.async_graphql(
            "AccountStatus",
            operations.ACCOUNT_STATUS,
            {"vin": vin},
        )
        return parse_account_status(data)

    async def async_get_charge_product(
        self,
        vin: str,
    ) -> ChargeProductResult | None:
        """Return the EMP charge-plan product offered for the vehicle."""

        data = await self._transport.async_graphql(
            "ChargeProduct",
            operations.CHARGE_PRODUCT,
            charge_product_variables(vin),
        )
        return parse_charge_product(data)

    async def async_get_charge_plan_pricing_details(
        self,
        vin: str,
        location_id: str,
    ) -> ChargePlanPricingDetails | None:
        """Return EMP parking and connector tariffs for a charging location."""

        data = await self._transport.async_graphql(
            "PricingDetails",
            operations.PRICING_DETAILS,
            pricing_details_variables(vin, location_id),
        )
        return parse_pricing_details(data)

    async def async_get_driving_history(
        self,
        vin: str,
        aggregator: DrivingHistoryAggregator,
        *,
        distance_unit: DistanceUnit | UnsetType | None = UNSET,
        weight_unit: WeightUnit | UnsetType | None = UNSET,
        speed_unit: SpeedUnit | UnsetType | None = UNSET,
    ) -> DrivingHistory | None:
        """Return trip summaries and individual trips for an electric vehicle."""

        data = await self._transport.async_graphql(
            "DrivingHistory",
            operations.DRIVING_HISTORY,
            driving_history_variables(
                vin,
                aggregator,
                distance_unit=distance_unit,
                weight_unit=weight_unit,
                speed_unit=speed_unit,
            ),
        )
        return parse_driving_history(data)

    async def async_get_ev_charge_stations(
        self,
        vin: str,
        coordinate: CoordinateInput,
        *,
        plug_connector_types: (tuple[PlugConnectorType | None, ...] | UnsetType | None) = UNSET,
        enable_within_range_restriction: bool | UnsetType | None = UNSET,
    ) -> tuple[EVChargeStation | None, ...] | None:
        """Return charging stations near a coordinate for the vehicle."""

        data = await self._transport.async_graphql(
            "EVChargeStations",
            operations.EV_CHARGE_STATIONS,
            ev_charge_stations_variables(
                vin,
                coordinate,
                plug_connector_types=plug_connector_types,
                enable_within_range_restriction=enable_within_range_restriction,
            ),
        )
        return parse_ev_charge_stations(data)

    async def async_get_e_vehicle_eligibility(
        self,
        vin: str,
    ) -> EVehicleEligibility | None:
        """Return the Nissan Energy eligibility response for the vehicle."""

        data = await self._transport.async_graphql(
            "eVehicleEligibility",
            operations.E_VEHICLE_ELIGIBILITY,
            e_vehicle_eligibility_variables(vin),
        )
        return parse_e_vehicle_eligibility(data)

    async def async_get_last_known_camera_usage_counter(
        self,
        vin: str,
    ) -> LastKnownCameraUsageCounter | None:
        """Return the last known camera usage counter and update time."""

        data = await self._transport.async_graphql(
            "LastKnownCameraUsageCounter",
            operations.LAST_KNOWN_CAMERA_USAGE_COUNTER,
            last_known_camera_usage_counter_variables(vin),
        )
        return parse_last_known_camera_usage_counter(data)

    async def async_get_location_details(
        self,
        vin: str,
        latitude: str,
        longitude: str,
        in_network_only: bool,
        range_value: int,
        *,
        operator_names: tuple[str | None, ...] | UnsetType | None = UNSET,
        evse: EmpEvseStatusInput | UnsetType | None = UNSET,
        plug_types: tuple[str | None, ...] | UnsetType | None = UNSET,
        charge_level: EmpConnectorLevelInput | UnsetType | None = UNSET,
        pnc_stations_only: bool | UnsetType | None = UNSET,
    ) -> LocationDetails | None:
        """Return Nissan Energy charging-location details for a search area."""

        data = await self._transport.async_graphql(
            "LocationDetails",
            operations.LOCATION_DETAILS,
            location_details_variables(
                vin,
                latitude,
                longitude,
                in_network_only,
                range_value,
                operator_names=operator_names,
                evse=evse,
                plug_types=plug_types,
                charge_level=charge_level,
                pnc_stations_only=pnc_stations_only,
            ),
        )
        return parse_location_details(data)

    async def async_get_parking_chargeable(
        self,
        evse_id: str,
    ) -> ParkingChargeable | None:
        """Return whether parking fees can be charged for an EVSE."""

        data = await self._transport.async_graphql(
            "ParkingChargeable",
            operations.PARKING_CHARGEABLE,
            parking_chargeable_variables(evse_id),
        )
        return parse_parking_chargeable(data)

    async def async_get_shareable_capabilities(
        self,
        vin: str,
        *,
        driver_id: str | UnsetType | None = UNSET,
    ) -> ShareableCapabilities | None:
        """Return capabilities that can be shared with another driver."""

        data = await self._transport.async_graphql(
            "ShareableCapabilities",
            operations.SHAREABLE_CAPABILITIES,
            shareable_capabilities_variables(vin, driver_id=driver_id),
        )
        return parse_shareable_capabilities(data)

    async def async_get_tariff_pricing(
        self,
        vin: str,
        location_id: str,
    ) -> TariffPricing | None:
        """Return Nissan Energy tariff pricing for one charging location."""

        data = await self._transport.async_graphql(
            "TariffPricing",
            operations.TARIFF_PRICING,
            tariff_pricing_variables(vin, location_id),
        )
        return parse_tariff_pricing(data)

    async def async_get_pnc_service_status(
        self,
        vin: str,
    ) -> PlugAndChargeServiceStatus | None:
        """Return the vehicle's Nissan Energy Plug & Charge enrollment state."""

        data = await self._transport.async_graphql(
            "PNCServiceStatus",
            operations.PNC_SERVICE_STATUS,
            {"vin": vin},
        )
        return parse_pnc_service_status(data)

    async def async_get_v1g_monitored_charging_account_status(
        self,
        vin: str,
    ) -> V1GMonitoredChargingAccountStatusResult | None:
        """Return raw V1G Charging Insights enrollment and notification state."""

        data = await self._transport.async_graphql(
            "V1GMonitoredChargingAccountStatus",
            operations.V1G_MONITORED_CHARGING_ACCOUNT_STATUS,
            v1g_monitored_charging_account_status_variables(vin),
        )
        return parse_v1g_monitored_charging_account_status(data)

    async def async_get_v1g_tokenized_url(
        self,
        vin: str,
    ) -> V1GTokenizedUrlResult | None:
        """Return the sensitive, potentially ephemeral V1G web-view URL."""

        data = await self._transport.async_graphql(
            "V1GTokenizedUrl",
            operations.V1G_TOKENIZED_URL,
            v1g_tokenized_url_variables(vin),
        )
        return parse_v1g_tokenized_url(data)

    async def async_get_public_charge_session_status(
        self,
        vin: str,
    ) -> PublicChargeSessionStatus | None:
        """Return the current Nissan Energy public charging-session state."""

        data = await self._transport.async_graphql(
            "ChargeSessionStatus",
            operations.CHARGE_SESSION_STATUS,
            {"vin": vin},
        )
        return parse_charge_session_status(data)

    async def async_get_vehicle_preferred_dealer(
        self,
        vin: str,
    ) -> VehiclePreferredDealer | None:
        """Return the preferred dealer currently associated with the vehicle."""

        data = await self._transport.async_graphql(
            "VehiclePreferredDealer",
            operations.VEHICLE_PREFERRED_DEALER,
            vehicle_preferred_dealer_variables(vin),
        )
        return parse_vehicle_preferred_dealer(data)

    async def async_get_vehicle_recalls(
        self,
        vin: str,
    ) -> tuple[VehicleRecall, ...] | None:
        """Return the vehicle's non-null recall and service-campaign list."""

        data = await self._transport.async_graphql(
            "VehicleRecalls",
            operations.VEHICLE_RECALLS,
            vehicle_recalls_variables(vin),
        )
        return parse_vehicle_recalls(data)

    async def async_get_vehicle_roadside_assistance(
        self,
        vin: str,
    ) -> VehicleRoadsideAssistance | None:
        """Return roadside and towing coverage limits reported by Nissan."""

        data = await self._transport.async_graphql(
            "VehicleRoadsideAssistance",
            operations.VEHICLE_ROADSIDE_ASSISTANCE,
            vehicle_roadside_assistance_variables(vin),
        )
        return parse_vehicle_roadside_assistance(data)

    async def async_get_vehicle_service_history(
        self,
        vin: str,
        *,
        unit: DistanceUnit | UnsetType | None = UNSET,
    ) -> tuple[VehicleServiceHistoryEntry, ...] | None:
        """Return completed service records in the requested distance unit."""

        data = await self._transport.async_graphql(
            "VehicleServiceHistory",
            operations.VEHICLE_SERVICE_HISTORY,
            vehicle_service_history_variables(vin, unit=unit),
        )
        return parse_vehicle_service_history(data)

    async def async_get_warranty_info(
        self,
        vin: str,
        *,
        mileage: int | UnsetType | None = UNSET,
    ) -> VehicleWarranty | None:
        """Return the vehicle warranty at an optional caller-supplied mileage."""

        data = await self._transport.async_graphql(
            "WarrantyInfo",
            operations.WARRANTY_INFO,
            warranty_info_variables(vin, mileage=mileage),
        )
        return parse_warranty_info(data)

    async def async_wait_for_pnc_service_status(
        self,
        vin: str,
        desired_state: PlugAndChargeServiceState,
        *,
        poll_interval_seconds: float = 3.0,
        timeout_seconds: float = 210.0,
    ) -> PlugAndChargeServiceStatus | None:
        """Poll enrollment while it remains in the desired transition state."""

        match desired_state:
            case PlugAndChargeServiceState.ENABLED:
                transitional_state = PlugAndChargeServiceState.ENABLING
            case PlugAndChargeServiceState.DISABLED:
                transitional_state = PlugAndChargeServiceState.DISABLING
            case _:
                raise ValueError("desired_state must be ENABLED or DISABLED")
        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        try:
            async with asyncio.timeout(timeout_seconds):
                while True:
                    result = await self.async_get_pnc_service_status(vin)
                    state = (
                        result.data.state
                        if result is not None and result.data is not None
                        else None
                    )
                    if state is not None and state is not transitional_state:
                        return result
                    await asyncio.sleep(poll_interval_seconds)
        except TimeoutError:
            return None

    async def async_wait_for_energy_account_status(
        self,
        vin: str,
        *,
        poll_interval_seconds: float = ACCOUNT_STATUS_POLL_INTERVAL_SECONDS,
        timeout_seconds: float = ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS,
    ) -> EnergyAccountStatusResult | None:
        """Poll Nissan Energy account status until it leaves enrollment transition."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        try:
            async with asyncio.timeout(timeout_seconds):
                while True:
                    result = await self.async_get_energy_account_status(vin)
                    if (
                        account_status_polling_outcome(result)
                        is EnergyAccountPollingOutcome.COMPLETE
                    ):
                        return result
                    await asyncio.sleep(poll_interval_seconds)
        except TimeoutError:
            return None

    async def async_wait_for_public_charge_session_status(
        self,
        vin: str,
        *,
        poll_interval_seconds: float = 3.0,
        timeout_seconds: float = 210.0,
    ) -> PublicChargeSessionStatus | None:
        """Poll a public session until it leaves pending or reservation state."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        terminal_states = {
            PublicChargeSessionState.ACTIVE,
            PublicChargeSessionState.COMPLETED,
            PublicChargeSessionState.FAILED,
        }
        try:
            async with asyncio.timeout(timeout_seconds):
                while True:
                    result = await self.async_get_public_charge_session_status(vin)
                    if result is None or result.data is None:
                        return None
                    state = result.data.status
                    if state is None or state in terminal_states:
                        return result
                    await asyncio.sleep(poll_interval_seconds)
        except TimeoutError:
            return None

    async def async_get_climate_schedules(
        self,
        vin: str,
        *,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> VehicleClimateSchedules:
        """Return recurring and one-time climate schedules and their accessories."""

        data = await self._transport.async_graphql(
            "VehicleClimateSchedules",
            operations.VEHICLE_CLIMATE_SCHEDULES,
            {"vin": vin, "temperatureUnit": temperature_unit.value},
        )
        return parse_climate_schedules(data)

    async def async_get_climate_defaults(
        self,
        vin: str,
        *,
        temperature_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
    ) -> ClimateDefaults | None:
        """Return saved climate defaults when supported by the vehicle."""

        data = await self._transport.async_graphql(
            "VehicleClimateDefaults",
            operations.VEHICLE_CLIMATE_DEFAULTS,
            {"vin": vin, "temperatureUnit": temperature_unit.value},
        )
        return parse_climate_defaults(data)

    async def async_start_climate(
        self,
        vin: str,
        climate: ClimateSettings,
        *,
        set_as_default: bool | None = None,
    ) -> ServiceRequest:
        """Start cabin climate control."""

        variables = _optional_variables(
            vin=vin,
            climate=_start_climate_input(climate),
            parameters=_climate_parameters_input(climate.parameters),
            setAsDefault=set_as_default,
        )
        return await self._async_service_request(
            "StartClimate",
            operations.START_CLIMATE,
            "startClimate",
            variables,
            ServiceRequestKind.CLIMATE,
        )

    async def async_adjust_climate(
        self,
        vin: str,
        climate: ClimateSettings,
        *,
        set_as_default: bool | None = None,
    ) -> ServiceRequest:
        """Adjust climate settings while remote climate is active."""

        variables = _optional_variables(
            vin=vin,
            climate=_start_climate_input(climate),
            parameters=_climate_parameters_input(climate.parameters),
            setAsDefault=set_as_default,
        )
        return await self._async_service_request(
            "AdjustClimate",
            operations.ADJUST_CLIMATE,
            "adjustClimate",
            variables,
            ServiceRequestKind.CLIMATE,
        )

    async def async_stop_climate(self, vin: str) -> ServiceRequest:
        """Stop remote cabin climate control."""

        return await self._async_simple_service_request(
            "StopClimate",
            operations.STOP_CLIMATE,
            "stopClimate",
            vin,
            ServiceRequestKind.CLIMATE,
        )

    async def async_set_climate_defaults(
        self,
        vin: str,
        climate: ClimateSettings,
    ) -> bool:
        """Save the vehicle's default climate temperature and accessories."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SetClimateDefaults",
            operations.SET_CLIMATE_DEFAULTS,
            _optional_variables(
                vin=vin,
                climate=_start_climate_input(climate),
                parameters=_climate_parameters_input(climate.parameters),
            ),
        )
        return _success(data, "setClimateDefaults")

    async def async_set_delayed_climate(
        self,
        vin: str,
        start_date_time: datetime,
        climate: ClimateSettings,
    ) -> ServiceRequest:
        """Schedule a one-time delayed climate start."""

        return await self._async_service_request(
            "SetDelayedClimate",
            operations.SET_DELAYED_CLIMATE,
            "setDelayedClimate",
            _optional_variables(
                vin=vin,
                startDateTime=_date_time_input(start_date_time),
                climate=_start_climate_input(climate),
                climateAccessories=_climate_parameters_input(climate.parameters),
            ),
            ServiceRequestKind.CLIMATE,
        )

    async def async_cancel_delayed_climate(self, vin: str) -> ServiceRequest:
        """Cancel the one-time delayed climate request."""

        return await self._async_simple_service_request(
            "CancelDelayedClimate",
            operations.CANCEL_DELAYED_CLIMATE,
            "cancelDelayedClimate",
            vin,
            ServiceRequestKind.CLIMATE,
        )

    async def async_start_charge(self, vin: str) -> ServiceRequest:
        """Start charging an attached electric vehicle."""

        return await self._async_simple_service_request(
            "StartCharge",
            operations.START_CHARGE,
            "startCharge",
            vin,
            ServiceRequestKind.CHARGE,
        )

    async def async_stop_charge(self, vin: str) -> ServiceRequest:
        """Stop charging an attached electric vehicle."""

        return await self._async_simple_service_request(
            "StopCharge",
            operations.STOP_CHARGE,
            "stopCharge",
            vin,
            ServiceRequestKind.CHARGE,
        )

    async def async_start_public_charge_session(
        self,
        vin: str,
        evse_id: str,
        *,
        location_id: str | UnsetType | None = UNSET,
    ) -> PublicChargeSessionStartResult | None:
        """Start a Nissan Energy public charging session at one EVSE."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "StartChargeSession",
            operations.START_CHARGE_SESSION,
            start_charge_session_variables(
                vin,
                evse_id,
                location_id=location_id,
            ),
        )
        return parse_start_charge_session(data)

    async def async_enroll_charge_plan(
        self,
        vin: str,
        product_sku: str,
        model: str,
        year: str,
    ) -> ChargePlanEnrollmentResult | None:
        """Enroll the vehicle in an EMP charging product."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "EnrollChargePlan",
            operations.ENROLL_CHARGE_PLAN,
            enroll_charge_plan_variables(vin, product_sku, model, year),
        )
        return parse_enroll_charge_plan(data)

    async def async_cancel_charge_plan(
        self,
        vin: str,
    ) -> ChargePlanCancellationResult | None:
        """Cancel the vehicle's EMP charging-product enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelChargePlan",
            operations.CANCEL_CHARGE_PLAN,
            cancel_charge_plan_variables(vin),
        )
        return parse_cancel_charge_plan(data)

    async def async_stop_public_charge_session(
        self,
        vin: str,
    ) -> PublicChargeSessionStopResult | None:
        """Stop the active Nissan Energy public charging session."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "StopChargeSession",
            operations.STOP_CHARGE_SESSION,
            stop_charge_session_variables(vin),
        )
        return parse_stop_charge_session(data)

    async def async_update_pnc_service_status(
        self,
        vin: str,
        status: PlugAndChargeStatusInput,
    ) -> PlugAndChargeServiceStatus | None:
        """Enable or disable Nissan Energy Plug & Charge enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePnCServiceStatus",
            operations.UPDATE_PNC_SERVICE_STATUS,
            update_pnc_service_status_variables(vin, status),
        )
        return parse_update_pnc_service_status(data)

    async def async_retry_pnc_certificate_install(
        self,
        vin: str,
    ) -> PlugAndChargeCertificateRetryResult | None:
        """Retry installation of the vehicle's Plug & Charge certificate."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RetryCertInstall",
            operations.RETRY_CERT_INSTALL,
            retry_certificate_install_variables(vin),
        )
        return parse_retry_certificate_install(data)

    async def async_enroll_v1g_monitored_charging_plan(
        self,
        vin: str,
        model: str,
        year: str,
        *,
        plan: str | UnsetType | None = UNSET,
    ) -> V1GMonitoredChargingPlanEnrollmentResult | None:
        """Enroll in V1G Charging Insights with an explicit caller-selected plan."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "V1GEnrollMonitoredChargingPlan",
            operations.V1G_ENROLL_MONITORED_CHARGING_PLAN,
            v1g_enroll_monitored_charging_plan_variables(
                vin,
                model,
                year,
                plan=plan,
            ),
        )
        return parse_v1g_enroll_monitored_charging_plan(data)

    async def async_cancel_v1g_monitored_charging_plan(
        self,
        vin: str,
    ) -> V1GMonitoredChargingPlanCancellationResult | None:
        """Permanently cancel V1G Charging Insights enrollment for a vehicle."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "V1GCancelMonitoredChargingPlan",
            operations.V1G_CANCEL_MONITORED_CHARGING_PLAN,
            v1g_cancel_monitored_charging_plan_variables(vin),
        )
        return parse_v1g_cancel_monitored_charging_plan(data)

    async def async_update_v1g_notification_preferences(
        self,
        vin: str,
        *,
        preferences: (tuple[V1GNotificationPreferenceInput | None, ...] | UnsetType | None) = UNSET,
    ) -> V1GNotificationPreferencesUpdateResult | None:
        """Patch V1G Charging Insights notification channels."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "V1GUpdateNotificationPreferences",
            operations.V1G_UPDATE_NOTIFICATION_PREFERENCES,
            v1g_update_notification_preferences_variables(
                vin,
                preferences=preferences,
            ),
        )
        return parse_v1g_update_notification_preferences(data)

    async def async_set_charge_limit(self, vin: str, percent: int) -> ServiceRequest:
        """Set the electric vehicle charging limit."""

        return await self._async_service_request(
            "SetChargeLimit",
            operations.SET_CHARGE_LIMIT,
            "setChargeLimit",
            {"vin": vin, "percent": percent},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_set_charge_notification_threshold(
        self,
        vin: str,
        percent: int,
    ) -> ServiceRequest:
        """Set the battery percentage that triggers a charge notification."""

        return await self._async_service_request(
            "SetNotificationLimit",
            operations.SET_NOTIFICATION_LIMIT,
            "setChargeNotificationThreshold",
            {"vin": vin, "percent": percent},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_set_v2l_minimum_battery_charge_level(
        self,
        vin: str,
        percent: int,
    ) -> ServiceRequest:
        """Set the minimum battery percentage reserved while using V2L."""

        return await self._async_service_request(
            "SetV2L",
            operations.SET_V2L,
            "setV2L",
            {"vin": vin, "input": {"minimumBatteryChargeLevel": percent}},
            ServiceRequestKind.V2L,
        )

    async def async_lock_doors(self, vin: str) -> ServiceRequest:
        """Lock the vehicle doors."""

        return await self._async_simple_service_request(
            "DoorLock",
            operations.DOOR_LOCK,
            "doorLock",
            vin,
            ServiceRequestKind.DOOR,
        )

    async def async_unlock_doors(self, vin: str) -> ServiceRequest:
        """Unlock the vehicle doors."""

        return await self._async_simple_service_request(
            "DoorUnlock",
            operations.DOOR_UNLOCK,
            "doorUnlock",
            vin,
            ServiceRequestKind.DOOR,
        )

    async def async_flash_lights(self, vin: str) -> ServiceRequest:
        """Flash the vehicle lights."""

        return await self._async_simple_service_request(
            "FlashLights",
            operations.FLASH_LIGHTS,
            "flashLights",
            vin,
            ServiceRequestKind.HORN_LIGHT,
        )

    async def async_flash_lights_and_horn(self, vin: str) -> ServiceRequest:
        """Flash the lights and sound the horn."""

        return await self._async_simple_service_request(
            "FlashLightsHorn",
            operations.FLASH_LIGHTS_HORN,
            "flashLightsHorn",
            vin,
            ServiceRequestKind.HORN_LIGHT,
        )

    async def async_locate_vehicle(self, vin: str) -> ServiceRequest:
        """Request a fresh vehicle location."""

        return await self._async_simple_service_request(
            "LocateVehicle",
            operations.LOCATE_VEHICLE,
            "locateVehicle",
            vin,
            ServiceRequestKind.LOCATION,
        )

    async def async_start_engine(
        self,
        vin: str,
        *,
        climate: ClimateSettings | None = None,
        set_as_default: bool | None = None,
    ) -> ServiceRequest:
        """Start the engine, optionally with a climate configuration."""

        engine_climate = None
        if climate is not None:
            engine_climate = _optional_variables(
                temperature=_temperature_input(climate),
                parameters=_climate_parameters_input(climate.parameters),
            )
        return await self._async_service_request(
            "EngineStart",
            operations.ENGINE_START,
            "engineStart",
            _optional_variables(
                vin=vin,
                climate=engine_climate,
                setAsDefault=set_as_default,
            ),
            ServiceRequestKind.ENGINE,
        )

    async def async_stop_engine(self, vin: str) -> ServiceRequest:
        """Stop a remotely started engine."""

        return await self._async_simple_service_request(
            "EngineStop",
            operations.ENGINE_STOP,
            "engineStop",
            vin,
            ServiceRequestKind.ENGINE,
        )

    async def async_refresh_vehicle_status(self, vin: str) -> ServiceRequest:
        """Ask the vehicle to publish fresh dynamic status."""

        return await self._async_simple_service_request(
            "RefreshVehicleStatus",
            operations.REFRESH_VEHICLE_STATUS,
            "refreshVehicleStatus",
            vin,
            ServiceRequestKind.VEHICLE_STATUS,
        )

    async def async_refresh_battery_status(self, vin: str) -> bool:
        """Ask the electric vehicle to refresh its battery status."""

        return await self._async_success_operation(
            "RefreshBatteryStatus",
            operations.REFRESH_BATTERY_STATUS,
            "refreshBatteryStatus",
            {"vin": vin},
        )

    async def async_refresh_climate_status(self, vin: str) -> bool:
        """Ask the vehicle to refresh its climate status."""

        return await self._async_success_operation(
            "RefreshClimateStatus",
            operations.REFRESH_CLIMATE_STATUS,
            "refreshClimateStatus",
            {"vin": vin},
        )

    async def async_wake_up_vehicle(self, vin: str) -> bool:
        """Wake the vehicle telematics unit."""

        return await self._async_success_operation(
            "WakeUpVehicle",
            operations.WAKE_UP_VEHICLE,
            "wakeUp",
            {"vin": vin},
        )

    async def async_take_photos_around_vehicle(self, vin: str) -> ServiceRequest:
        """Request exterior camera photos on supported vehicles."""

        return await self._async_simple_service_request(
            "TakePhotosAroundVehicle",
            operations.TAKE_PHOTOS_AROUND_VEHICLE,
            "takePhotosAroundVehicle",
            vin,
            ServiceRequestKind.PHOTO,
        )

    async def async_create_charge_schedule(
        self,
        vin: str,
        schedule: ChargeScheduleInput,
    ) -> ServiceRequest:
        """Create a recurring charge schedule."""

        return await self._async_service_request(
            "CreateChargeSchedule",
            operations.CREATE_CHARGE_SCHEDULE,
            "createChargeSchedule",
            {"vin": vin, "schedule": _charge_schedule_input(schedule)},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_update_charge_schedule(
        self,
        vin: str,
        schedule_id: str,
        schedule: ChargeScheduleInput,
    ) -> ServiceRequest:
        """Replace a recurring charge schedule."""

        schedule_input = {"id": schedule_id, **_charge_schedule_input(schedule)}
        return await self._async_service_request(
            "UpdateChargeSchedule",
            operations.UPDATE_CHARGE_SCHEDULE,
            "updateChargeSchedule",
            {"vin": vin, "schedule": schedule_input},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_delete_charge_schedule(self, vin: str, schedule_id: str) -> ServiceRequest:
        """Delete a recurring charge schedule."""

        return await self._async_service_request(
            "DeleteChargeSchedule",
            operations.DELETE_CHARGE_SCHEDULE,
            "deleteChargeSchedule",
            {"vin": vin, "id": schedule_id},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_toggle_charge_schedule(
        self,
        vin: str,
        schedule_id: str,
        *,
        enabled: bool,
    ) -> ServiceRequest:
        """Enable or disable a recurring charge schedule."""

        return await self._async_service_request(
            "ToggleChargeSchedule",
            operations.TOGGLE_CHARGE_SCHEDULE,
            "toggleChargeSchedule",
            {"vin": vin, "schedule": {"id": schedule_id, "enable": enabled}},
            ServiceRequestKind.CHARGE_CONFIGURATION,
        )

    async def async_create_climate_schedule(
        self,
        vin: str,
        schedule: ClimateScheduleInput,
    ) -> ServiceRequest:
        """Create a recurring climate schedule."""

        return await self._async_service_request(
            "CreateClimateSchedule",
            operations.CREATE_CLIMATE_SCHEDULE,
            "createClimateSchedule",
            _optional_variables(
                vin=vin,
                schedule=_climate_schedule_input(schedule),
                climateAccessories=_climate_parameters_input(schedule.climate.parameters),
            ),
            ServiceRequestKind.CLIMATE,
        )

    async def async_update_climate_schedule(
        self,
        vin: str,
        schedule_id: str,
        schedule: ClimateScheduleInput,
    ) -> ServiceRequest:
        """Replace a recurring climate schedule."""

        schedule_input = {"id": schedule_id, **_climate_schedule_input(schedule)}
        return await self._async_service_request(
            "UpdateClimateSchedule",
            operations.UPDATE_CLIMATE_SCHEDULE,
            "updateClimateSchedule",
            _optional_variables(
                vin=vin,
                schedule=schedule_input,
                climateAccessories=_climate_parameters_input(schedule.climate.parameters),
            ),
            ServiceRequestKind.CLIMATE,
        )

    async def async_delete_climate_schedule(self, vin: str, schedule_id: str) -> ServiceRequest:
        """Delete a recurring climate schedule."""

        return await self._async_service_request(
            "DeleteClimateSchedule",
            operations.DELETE_CLIMATE_SCHEDULE,
            "deleteClimateSchedule",
            {"vin": vin, "id": schedule_id},
            ServiceRequestKind.CLIMATE,
        )

    async def async_toggle_climate_schedule(
        self,
        vin: str,
        schedule_id: str,
        *,
        enabled: bool,
    ) -> ServiceRequest:
        """Enable or disable a recurring climate schedule."""

        return await self._async_service_request(
            "ToggleClimateSchedule",
            operations.TOGGLE_CLIMATE_SCHEDULE,
            "toggleClimateSchedule",
            {"vin": vin, "schedule": {"id": schedule_id, "enable": enabled}},
            ServiceRequestKind.CLIMATE,
        )

    async def async_send_journey(
        self,
        vin: str,
        waypoints: tuple[DestinationInput, ...],
        *,
        avoid_highway: bool | UnsetType | None = UNSET,
        avoid_tolls: bool | UnsetType | None = UNSET,
        avoid_ferries: bool | UnsetType | None = UNSET,
        estimated_time_of_arrival: datetime | UnsetType | None = UNSET,
        estimated_time_of_departure: datetime | UnsetType | None = UNSET,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> bool:
        """Send an ad-hoc journey and its waypoints to the vehicle."""

        return await self._async_nullable_success_operation(
            "SendJourney",
            operations.SEND_JOURNEY,
            "sendJourney",
            optional_input_fields(
                vin=vin,
                waypoints=[destination_input(waypoint) for waypoint in waypoints],
                avoidHighway=avoid_highway,
                avoidTolls=avoid_tolls,
                avoidFerries=avoid_ferries,
                estimatedTimeOfArrival=optional_destination_time(estimated_time_of_arrival),
                estimatedTimeOfDeparture=optional_destination_time(estimated_time_of_departure),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            extra_headers=_navigation_headers(data_source),
        )

    async def async_send_planned_route(
        self,
        vin: str,
        route_id: str,
        *,
        estimated_time_of_arrival: datetime | UnsetType | None = UNSET,
        estimated_time_of_departure: datetime | UnsetType | None = UNSET,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> bool:
        """Send a previously saved route to the vehicle."""

        return await self._async_nullable_success_operation(
            "SendPlannedRoute",
            operations.SEND_PLANNED_ROUTE,
            "sendPlannedRoute",
            optional_input_fields(
                vin=vin,
                routeId=route_id,
                estimatedTimeOfArrival=optional_destination_time(estimated_time_of_arrival),
                estimatedTimeOfDeparture=optional_destination_time(estimated_time_of_departure),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            extra_headers=_navigation_headers(data_source),
        )

    async def async_send_point_of_interest(
        self,
        vin: str,
        folder: PointOfInterestFolder,
        destination: DestinationInput,
        *,
        calculation_condition: RouteCalculationCondition | UnsetType | None = UNSET,
        avoid_highway: bool | UnsetType | None = UNSET,
        avoid_tolls: bool | UnsetType | None = UNSET,
        avoid_ferries: bool | UnsetType | None = UNSET,
    ) -> bool:
        """Send a favorite or recent point of interest to the vehicle."""

        return await self._async_nullable_success_operation(
            "SendPointOfInterest",
            operations.SEND_POINT_OF_INTEREST,
            "sendPointOfInterest",
            optional_input_fields(
                vin=vin,
                folderName=navigation_enum_input(folder),
                destinationInput=destination_input(destination),
                calculationCondition=optional_navigation_enum(calculation_condition),
                avoidHighway=avoid_highway,
                avoidTolls=avoid_tolls,
                avoidFerries=avoid_ferries,
            ),
        )

    async def async_save_route(
        self,
        vin: str,
        route: PlannedRouteInput,
        *,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
        data_source: NavigationDataSource | None = None,
    ) -> ServiceRequest:
        """Save a planned route in the vehicle account."""

        return await self._async_service_request(
            "SaveRoute",
            operations.SAVE_ROUTE,
            "saveRoute",
            optional_input_fields(
                vin=vin,
                plannedRoute=planned_route_input(route),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            ServiceRequestKind.ROUTE,
            extra_headers=_navigation_headers(data_source),
        )

    async def async_update_route(
        self,
        vin: str,
        route: PlannedRouteUpdate,
        *,
        arrival_flag: bool | UnsetType | None = UNSET,
        departure_flag: bool | UnsetType | None = UNSET,
    ) -> ServiceRequest:
        """Patch a saved planned route."""

        return await self._async_service_request(
            "UpdateRoute",
            operations.UPDATE_ROUTE,
            "updateRoute",
            optional_input_fields(
                vin=vin,
                plannedRoute=planned_route_update_input(route),
                arrivalFlag=arrival_flag,
                departureFlag=departure_flag,
            ),
            ServiceRequestKind.ROUTE,
        )

    async def async_delete_route(self, vin: str, route_id: str) -> bool:
        """Delete a saved planned route."""

        return await self._async_nullable_success_operation(
            "DeleteRoute",
            operations.DELETE_ROUTE,
            "deleteRoute",
            {"vin": vin, "routeId": route_id},
        )

    async def async_delete_favorite_point_of_interest(
        self,
        vin: str,
        destination_id: str,
    ) -> bool:
        """Delete a destination from the vehicle's favorites."""

        return await self._async_nullable_success_operation(
            "DeleteFavoritePointOfInterest",
            operations.DELETE_FAVORITE_POINT_OF_INTEREST,
            "deleteFavoritePointOfInterest",
            {"vin": vin, "destinationId": destination_id},
        )

    async def async_save_t_junction_locations(
        self,
        vin: str,
        last_updated_at: str,
        locations: tuple[TJunctionLocationInput, ...],
    ) -> ServiceRequest:
        """Save selected T-junction camera locations."""

        return await self._async_service_request(
            "SaveTJunctionLocations",
            operations.SAVE_T_JUNCTION_LOCATIONS,
            "saveTJunctionLocations",
            {
                "input": save_t_junction_locations_input(
                    vin,
                    last_updated_at,
                    locations,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_update_saved_t_junction_location(
        self,
        vin: str,
        location_id: str,
        location_name: str,
    ) -> ServiceRequest:
        """Rename a saved T-junction camera location."""

        return await self._async_service_request(
            "UpdateSavedTJunctionLocation",
            operations.UPDATE_SAVED_T_JUNCTION_LOCATION,
            "updateSavedTJunctionLocation",
            {
                "input": update_saved_t_junction_location_input(
                    vin,
                    location_id,
                    location_name,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_delete_saved_t_junction_locations(
        self,
        vin: str,
        location_ids: tuple[str, ...],
        *,
        last_updated_at: str,
    ) -> ServiceRequest:
        """Delete saved T-junction camera locations."""

        return await self._async_service_request(
            "DeleteSavedTJunctionLocations",
            operations.DELETE_SAVED_T_JUNCTION_LOCATIONS,
            "deleteSavedTJunctionLocations",
            {
                "input": delete_saved_t_junction_locations_input(
                    vin,
                    location_ids,
                    last_updated_at,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_delete_unsaved_t_junction_locations(
        self,
        vin: str,
        location_ids: tuple[str, ...],
    ) -> ServiceRequest:
        """Discard unsaved T-junction camera locations."""

        return await self._async_service_request(
            "DeleteUnsavedTJunctionLocations",
            operations.DELETE_UNSAVED_T_JUNCTION_LOCATIONS,
            "deleteUnsavedTJunctionLocations",
            {
                "input": delete_unsaved_t_junction_locations_input(
                    vin,
                    location_ids,
                )
            },
            ServiceRequestKind.T_JUNCTION,
        )

    async def async_download_ota_update(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Ask a compatible vehicle to download an offered OTA campaign."""

        return await self._async_service_request(
            "DownloadOTAUpdate",
            operations.DOWNLOAD_OTA_UPDATE,
            "downloadOTAUpdate",
            {
                "vin": vin,
                "input": download_ota_update_input(ota_update_id),
            },
            ServiceRequestKind.OTA,
        )

    async def async_activate_ota_update(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Ask a compatible vehicle to activate a downloaded OTA campaign."""

        return await self._async_service_request(
            "ActivateOTAUpdate",
            operations.ACTIVATE_OTA_UPDATE,
            "activateOTAUpdate",
            {"vin": vin, "otaUpdateId": ota_update_id},
            ServiceRequestKind.OTA,
        )

    async def async_cancel_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Cancel an OTA campaign activation in progress."""

        return await self._async_service_request(
            "CancelActivationOTAUpdate",
            operations.CANCEL_ACTIVATION_OTA_UPDATE,
            "cancelActivationOTAUpdate",
            {"vin": vin, "otaUpdateId": ota_update_id},
            ServiceRequestKind.OTA,
        )

    async def async_schedule_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
        scheduled_date: datetime,
    ) -> ServiceRequest:
        """Schedule activation of a downloaded OTA campaign."""

        return await self._async_service_request(
            "ScheduleActivationOTAUpdate",
            operations.SCHEDULE_ACTIVATION_OTA_UPDATE,
            "scheduleActivationOTAUpdate",
            {
                "vin": vin,
                "input": ota_activation_schedule_input(
                    ota_update_id,
                    scheduled_date,
                ),
            },
            ServiceRequestKind.OTA,
        )

    async def async_update_scheduled_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
        scheduled_date: datetime,
    ) -> ServiceRequest:
        """Move an already scheduled OTA campaign activation."""

        return await self._async_service_request(
            "UpdateScheduledActivationOTAUpdate",
            operations.UPDATE_SCHEDULED_ACTIVATION_OTA_UPDATE,
            "updateScheduledActivationOTAUpdate",
            {
                "vin": vin,
                "input": ota_activation_schedule_input(
                    ota_update_id,
                    scheduled_date,
                ),
            },
            ServiceRequestKind.OTA,
        )

    async def async_cancel_scheduled_ota_activation(
        self,
        vin: str,
        ota_update_id: str,
    ) -> ServiceRequest:
        """Cancel a scheduled OTA campaign activation."""

        return await self._async_service_request(
            "CancelScheduledActivationOTAUpdate",
            operations.CANCEL_SCHEDULED_ACTIVATION_OTA_UPDATE,
            "cancelScheduledActivationOTAUpdate",
            {"vin": vin, "otaUpdateId": ota_update_id},
            ServiceRequestKind.OTA,
        )

    async def async_wipe_vehicle_data(
        self,
        vin: str,
        *,
        data_wipe_type: DataWipeType | UnsetType | None = UNSET,
    ) -> ServiceRequest:
        """Submit Nissan's remote vehicle data-wipe operation."""

        serialized_type: object = data_wipe_type
        if isinstance(data_wipe_type, DataWipeType):
            serialized_type = data_wipe_type_input(data_wipe_type)
        return await self._async_service_request(
            "DataWipe",
            operations.DATA_WIPE,
            "dataWipe",
            optional_input_fields(vin=vin, dataWipeType=serialized_type),
            ServiceRequestKind.DATA_WIPE,
        )

    async def async_set_notification_preferences(
        self,
        vin: str,
        preferences: tuple[NotificationPreferenceInput | None, ...],
    ) -> tuple[NotificationPreference | None, ...] | None:
        """Replace vehicle notification opt-ins with the supplied preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "SetNotificationPreferences",
            operations.SET_NOTIFICATION_PREFERENCES,
            {
                "vin": vin,
                "preferences": notification_preferences_input(preferences),
            },
        )
        return parse_notification_preferences(data, "setNotificationPreferences")

    async def async_update_nissan_energy_notification_preferences(
        self,
        vin: str,
        *,
        email_status: bool | UnsetType | None = UNSET,
        push_status: bool | UnsetType | None = UNSET,
        sms_status: bool | UnsetType | None = UNSET,
    ) -> NissanEnergyNotificationPreferencesUpdate | None:
        """Patch Nissan Energy delivery flags, preserving omitted and null values."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateNotificationPreferences",
            operations.UPDATE_NISSAN_ENERGY_NOTIFICATION_PREFERENCES,
            update_nissan_energy_notification_preferences_variables(
                vin,
                email_status=email_status,
                push_status=push_status,
                sms_status=sms_status,
            ),
        )
        return parse_update_nissan_energy_notification_preferences(data)

    async def async_register_push_notifications(
        self,
        device_id: str,
        token: str,
        device_os: DeviceOS,
    ) -> bool | None:
        """Register a legacy push token for the authenticated account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RegisterPushNotifications",
            operations.REGISTER_PUSH_NOTIFICATIONS,
            register_push_notifications_variables(device_id, token, device_os),
        )
        return parse_register_push_notifications(data)

    async def async_unregister_push_notifications(
        self,
        device_id: str,
        device_os: DeviceOS,
    ) -> bool | None:
        """Unregister a legacy push token for the authenticated account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UnregisterPushNotifications",
            operations.UNREGISTER_PUSH_NOTIFICATIONS,
            unregister_push_notifications_variables(device_id, device_os),
        )
        return parse_unregister_push_notifications(data)

    async def async_register_device_for_push_notifications(
        self,
        mobile_info: MobileInfoInput,
    ) -> PushNotificationResult | None:
        """Register a mobile installation through Nissan's current push API."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "RegisterDeviceForPushNotifications",
            operations.REGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS,
            register_device_for_push_notifications_variables(mobile_info),
        )
        return parse_register_device_for_push_notifications(data)

    async def async_unregister_device_for_push_notifications(
        self,
        app_name: str,
        device_id: str,
        device_os: DeviceOS,
    ) -> PushNotificationResult | None:
        """Unregister a mobile installation from Nissan's current push API."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UnregisterDeviceForPushNotifications",
            operations.UNREGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS,
            unregister_device_for_push_notifications_variables(
                app_name,
                device_id,
                device_os,
            ),
        )
        return parse_unregister_device_for_push_notifications(data)

    async def async_check_service_request(
        self,
        vin: str,
        request: ServiceRequest,
    ) -> ServiceRequestResult:
        """Check an asynchronous request using its matching Nissan operation."""

        checks = {
            ServiceRequestKind.CHARGE: (
                "CheckChargeServiceRequest",
                operations.CHECK_CHARGE_REQUEST,
                "checkChargeServiceRequest",
            ),
            ServiceRequestKind.CHARGE_CONFIGURATION: (
                "CheckChargeConfigServiceRequest",
                operations.CHECK_CHARGE_CONFIGURATION_REQUEST,
                "checkChargeConfigServiceRequest",
            ),
            ServiceRequestKind.CLIMATE: (
                "CheckRemoteClimateRequest",
                operations.CHECK_CLIMATE_REQUEST,
                "checkRemoteClimateRequest",
            ),
            ServiceRequestKind.DOOR: (
                "CheckDoorServiceRequest",
                operations.CHECK_DOOR_REQUEST,
                "checkDoorServiceRequest",
            ),
            ServiceRequestKind.ENGINE: (
                "CheckEngineServiceRequest",
                operations.CHECK_ENGINE_REQUEST,
                "checkEngineServiceRequest",
            ),
            ServiceRequestKind.HORN_LIGHT: (
                "CheckHornLightServiceRequest",
                operations.CHECK_HORN_LIGHT_REQUEST,
                "checkHornLightServiceRequest",
            ),
            ServiceRequestKind.LOCATION: (
                "CheckLocationServiceRequest",
                operations.CHECK_LOCATION_REQUEST,
                "checkLocationServiceRequest",
            ),
            ServiceRequestKind.OTA: (
                "CheckOtaUpdateServiceRequest",
                operations.CHECK_OTA_UPDATE_REQUEST,
                "checkOtaUpdateServiceRequest",
            ),
            ServiceRequestKind.PHOTO: (
                "CheckTakePhotosAroundVehicleServiceRequest",
                operations.CHECK_PHOTO_REQUEST,
                "checkTakePhotosAroundVehicleServiceRequest",
            ),
            ServiceRequestKind.ROUTE: (
                "CheckRouteServiceRequest",
                operations.CHECK_ROUTE_REQUEST,
                "checkRouteServiceRequest",
            ),
            ServiceRequestKind.T_JUNCTION: (
                "CheckTJunctionServiceRequest",
                operations.CHECK_T_JUNCTION_REQUEST,
                "checkTJunctionServiceRequest",
            ),
            ServiceRequestKind.V2L: (
                "CheckV2LServiceRequest",
                operations.CHECK_V2L_REQUEST,
                "checkV2LServiceRequest",
            ),
            ServiceRequestKind.VEHICLE_STATUS: (
                "CheckRefreshVehicleStatusRequest",
                operations.CHECK_REFRESH_VEHICLE_STATUS_REQUEST,
                "checkRefreshVehicleStatusRequest",
            ),
        }
        check = checks.get(request.kind)
        if check is None:
            raise ResponseError(
                f"Nissan does not expose a status operation for {request.kind.value} requests"
            )
        operation_name, document, root_field = check
        data = await self._transport.async_graphql(
            operation_name,
            document,
            {"vin": vin, "serviceRequestId": request.id},
        )
        return parse_service_request_result(data, root_field, vin)

    async def async_wait_for_service_request(
        self,
        vin: str,
        request: ServiceRequest,
        *,
        poll_interval_seconds: float = 3.0,
        timeout_seconds: float = 210.0,
    ) -> ServiceRequestResult:
        """Poll a remote request until Nissan returns a terminal status."""

        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be a positive finite number")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive finite number")

        async with asyncio.timeout(timeout_seconds):
            while True:
                result = await self.async_check_service_request(vin, request)
                if _is_terminal_service_request(request.kind, result):
                    return result
                await asyncio.sleep(poll_interval_seconds)

    async def _async_simple_service_request(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        vin: str,
        kind: ServiceRequestKind,
    ) -> ServiceRequest:
        return await self._async_service_request(
            operation_name,
            document,
            root_field,
            {"vin": vin},
            kind,
        )

    async def _async_service_request(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
        kind: ServiceRequestKind,
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> ServiceRequest:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            operation_name,
            document,
            variables,
            extra_headers=extra_headers,
        )
        return parse_service_request(data, root_field, kind)

    async def _async_vehicle_alert_request(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
        kind: VehicleAlertKind,
    ) -> VehicleAlertRequest:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(operation_name, document, variables)
        return parse_vehicle_alert_request(data, root_field, kind)

    async def _async_success_operation(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
    ) -> bool:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(operation_name, document, variables)
        return _success(data, root_field)

    async def _async_nullable_success_operation(
        self,
        operation_name: str,
        document: str,
        root_field: str,
        variables: Mapping[str, object],
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> bool:
        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            operation_name,
            document,
            variables,
            extra_headers=extra_headers,
        )
        return _nullable_success(data, root_field)

    def _ensure_write_allowed(self) -> None:
        if self._read_only:
            raise ReadOnlyError(
                "State-changing operations are disabled; construct the client with read_only=False"
            )


def _start_climate_input(climate: ClimateSettings) -> dict[str, object]:
    return {
        "unit": climate.unit.value,
        "temperatureValue": climate.temperature,
    }


def _temperature_input(climate: ClimateSettings) -> dict[str, object]:
    return {"value": climate.temperature, "unit": climate.unit.value}


def _climate_parameters_input(parameters: ClimateParameters | None) -> dict[str, object] | None:
    if parameters is None:
        return None
    seats = parameters.seats
    seats_input = None
    if seats is not None:
        seats_input = _optional_variables(
            frontDriverState=_enum_value(seats.front_driver),
            frontPassengerState=_enum_value(seats.front_passenger),
            rearLeftPassengerState=_enum_value(seats.rear_left),
            rearRightPassengerState=_enum_value(seats.rear_right),
            rearCenterPassengerState=_enum_value(seats.rear_center),
            thirdLeftState=_enum_value(seats.third_left),
            thirdRightState=_enum_value(seats.third_right),
        )
    return _optional_variables(
        seatsClimate=seats_input,
        steeringWheelHeaterState=_on_off(parameters.steering_wheel_heater),
        defrostAndDeicerState=_on_off(parameters.defrost_and_deicer),
    )


def _charge_schedule_input(schedule: ChargeScheduleInput) -> dict[str, object]:
    return {
        "startDateTime": _date_time_input(schedule.start_date_time),
        "duration": schedule.duration,
        "weekDays": [day.value for day in schedule.week_days],
    }


def _climate_schedule_input(schedule: ClimateScheduleInput) -> dict[str, object]:
    return {
        "startDateTime": _date_time_input(schedule.start_date_time),
        "weekDays": [day.value for day in schedule.week_days],
        "temperature": _temperature_input(schedule.climate),
    }


def _date_time_input(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Nissan date-time inputs must include a UTC offset")
    return value.isoformat()


def _enum_value(value: object) -> str | None:
    enum_value = getattr(value, "value", None)
    return enum_value if isinstance(enum_value, str) else None


def _on_off(value: bool | None) -> str | None:
    if value is None:
        return None
    return "ON" if value else "OFF"


def _optional_variables(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value is not None}


def _validate_positive_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _response_object(data: Mapping[str, object], root_field: str) -> Mapping[str, object]:
    result = data.get(root_field)
    if not isinstance(result, Mapping):
        raise ResponseError(f"{root_field} is missing from the Nissan response")
    return result


def _success(data: Mapping[str, object], root_field: str) -> bool:
    result = _response_object(data, root_field)
    success = result.get("success")
    if isinstance(success, bool):
        return success
    message = result.get("message")
    if isinstance(message, str) and message:
        raise ResponseError(message)
    raise ResponseError(f"{root_field} did not return a success value")


def _nullable_success(data: Mapping[str, object], root_field: str) -> bool:
    raw_result = data.get(root_field)
    if raw_result is None:
        return False
    if not isinstance(raw_result, Mapping):
        raise ResponseError(f"{root_field} is not an object")
    result = raw_result
    success = result.get("success")
    if isinstance(success, bool):
        return success
    message = result.get("message")
    if isinstance(message, str) and message:
        raise ResponseError(message)
    return False


def _navigation_headers(
    data_source: NavigationDataSource | None,
) -> Mapping[str, str] | None:
    if data_source is None:
        return None
    return {"x-tsp-datasource": data_source.value}


def _is_terminal_service_request(
    kind: ServiceRequestKind,
    result: ServiceRequestResult,
) -> bool:
    if kind in {ServiceRequestKind.ROUTE, ServiceRequestKind.T_JUNCTION}:
        return result.status in {
            ServiceRequestStatus.SUCCESS,
            ServiceRequestStatus.FAILED,
        }
    return result.is_terminal
