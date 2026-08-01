# ruff: noqa: E501

VEHICLES_STATIC_DATA_OPERATION_ID = (
    "d5f2a6e347c296ec88e9e80915bdf5df3c3a2776094077b5323f45e624d84a50"
)
VEHICLES_STATIC_DATA = "query VehiclesStaticData { vehicles { __typename vin year model color nickname image quickGuidesUrl driverType isAnniversary anniversaryYear plate hologram engineNumber emissionSticker manualMileage circulationRules { __typename ... on VehicleCirculationRulesSuccessResponse { today { __typename allowed } monday { __typename allowed } tuesday { __typename allowed } wednesday { __typename allowed } thursday { __typename allowed } friday { __typename allowed } firstSaturday { __typename allowed } secondSaturday { __typename allowed } thirdSaturday { __typename allowed } fourthSaturday { __typename allowed } } ... on VehicleCirculationRulesGeneralErrorFailureResponse { message } } complimentaryMaintenancePackage } user { __typename firstName lastName accountId mobileNumber address { __typename address1 address2 city state postalCode country } } pendingDriverInvitations { __typename ... on PendingDriverInvitationsSuccessResponse { invites { __typename inviteId inviterFirstName inviterLastName inviteePhoneNumber vin vehicleModel vehicleYear inviteDateTime expiresIn } } } }"


VEHICLE_DYNAMIC_DATA_OPERATION_ID = (
    "e15d8ac52efcf62a3acad20d50220c9d76fd8080f7d669e20bc1e6de41097ec6"
)
VEHICLE_DYNAMIC_DATA = "query VehicleDynamicData($vin: String!, $unit: DistanceUnit, $temperatureUnit: TemperatureUnitEnumType) { vehicle(vin: $vin) { __typename ...DynamicVehicleDetails ...VehicleTirePressureAndMilsDetails ... on BaseElectricVehicle { batteryStatus { __typename ...BatteryStatusDetails } chargeSchedules { __typename ...ChargeSchedulesDetails } climateStatus { __typename ...ClimateStatusDetails } climateSchedules { __typename ...ClimateSchedulesDetails } } ... on AVK2Vehicle { engineOilDrainRange(unit: $unit) { __typename range unit lastUpdatedAt } } ... on EVOVehicle { engineOilDrainRange(unit: $unit) { __typename range unit lastUpdatedAt } } } }  fragment DoorsStatusDetails on DoorsStatus { __typename lastUpdatedAt doorFrontLeft { __typename ajar window lock } doorFrontRight { __typename ajar window lock } doorRearLeft { __typename ajar window lock } doorRearRight { __typename ajar window lock } engineHood { __typename ajar } hatch { __typename ajar } sunroof { __typename ajar } trunk { __typename lock } overallLock { __typename lock } }  fragment DynamicVehicleDetails on BaseVehicle { __typename ... on BaseAVKVehicle { doorsStatus { __typename ...DoorsStatusDetails } fuelAutonomy(unit: $unit) { __typename lastUpdatedAt value unit } mileage(unit: $unit) { __typename total recordedTime unit } } }  fragment VehicleTirePressureAndMilsDetails on BaseVehicle { __typename ... on BaseAVKVehicle { tirePressure { __typename lastUpdatedAt flPressure frPressure rlPressure rrPressure flStatus frStatus rlStatus rrStatus } mils { __typename active detailedMessage type } } }  fragment BatteryStatusDetails on BatteryStatus { __typename level isPluggedIn isCharging remainingChargeTime remainingMileage(unit: $unit) { __typename unit value } }  fragment ChargeSchedulesDetails on ChargeSchedule { __typename id state startDateTime duration weekDays }  fragment ClimateStatusDetails on ClimateStatus { __typename state temperature(unit: $temperatureUnit) { __typename value unit } }  fragment ClimateSchedulesDetails on ClimateSchedule { __typename id state startDateTime weekDays temperature(unit: $temperatureUnit) { __typename value unit } }"


VEHICLE_LOCATION_OPERATION_ID = "10e24e78b7cdf1747cb444029b4a063f990330c47306a5bdf3e21e405d7b32bb"
VEHICLE_LOCATION = "query VehicleLocation($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { location { __typename latitude longitude lastUpdatedAt } } } }"


PHOTOS_AROUND_VEHICLE_OPERATION_ID = (
    "753e5275b0e644af2744dc675de67845174e96d027a27a4dde8dc4cea509f935"
)
PHOTOS_AROUND_VEHICLE = "query PhotosAroundVehicle($vin: String!) { vehicle(vin: $vin) { __typename year model vin ... on BaseAVK2Vehicle { photosAroundVehicle { __typename id filename link timeStamp cameraPosition cameraService } } } }"


VEHICLE_JOURNEYS_OPERATION_ID = "927d5e81523119802f9a69ac0121ffe5cb0a6c694bb51ba4e03ae64d4d03c04d"
VEHICLE_JOURNEYS = "query VehicleJourneys($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { journeys { __typename waypoints { __typename id name address { __typename address1 address2 city state postalCode country } coordinate { __typename latitude longitude } phoneNumber } } } } }"


VEHICLE_PLANNED_ROUTES_OPERATION_ID = (
    "88cacd15f73fa71505f02eeccef6947b6383feefeb8d77d9c2c3daedf5547c46"
)
VEHICLE_PLANNED_ROUTES = "query VehiclePlannedRoutes($vin: String!, $distanceUnit: DistanceUnit, $temperatureUnit: TemperatureUnitEnumType) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { plannedRoutes { __typename id name estimatedTimeOfDeparture estimatedTimeOfArrival distance(unit: $distanceUnit) { __typename value unit } temperature(unit: $temperatureUnit) { __typename value unit } routes { __typename name phoneNumber address { __typename address1 address2 city state postalCode country } location { __typename latitude longitude } recalculatedWaypointType chargingOutput } avoidHighway avoidTolls avoidFerries shouldRecalculateRoute shouldEnableNotification notificationInterval { __typename value unit } arrivalFlag departureFlag } } } }"


VEHICLE_POINT_OF_INTEREST_DESTINATIONS_OPERATION_ID = (
    "29d3fde96ed17fdde9ce208785144bf466917f529b1e5ac062799379b7148887"
)
VEHICLE_POINT_OF_INTEREST_DESTINATIONS = "query VehiclePOIDestinations($vin: String!, $folderName: FolderNameEnumType) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { pointOfInterestDestination(folderName: $folderName) { __typename folders { __typename folderName destinations { __typename id phoneNumber name address { __typename address1 address2 city state postalCode country } coordinate { __typename latitude longitude } } } } } } }"


ROUTES_HISTORY_OPERATION_ID = "42659d6ff50cc08fb8a41d1fc0923e1af9b4876225cd4d813268dea82e810901"
ROUTES_HISTORY = "query RoutesHistory($vin: String!, $distanceUnit: DistanceUnit, $temperatureUnit: TemperatureUnitEnumType, $status: RouteStatusEnumType) { vehicle(vin: $vin) { __typename ... on ElectricAVK2Vehicle { routeHistory(status: $status) { __typename id name estimatedTimeOfDeparture estimatedTimeOfArrival status distance(unit: $distanceUnit) { __typename value unit } temperature(unit: $temperatureUnit) { __typename value unit } routes { __typename name phoneNumber address { __typename address1 address2 city state postalCode country } location { __typename latitude longitude } recalculatedWaypointType chargingOutput } arrivalFlag departureFlag } } } }"


T_JUNCTION_LOCATIONS_OPERATION_ID = (
    "4b660b6661be6c7bde3e9810617349867a83e9c3adf3d6e82f77391a0c70881d"
)
T_JUNCTION_LOCATIONS = "query TJunctionLocations($vin: String!) { vehicle(vin: $vin) { __typename ... on EVOVehicle { unsavedTJunctionLocations { __typename id latitude longitude direction launchDate address { __typename ...AddressDetails } } savedTJunctionLocations { __typename id latitude longitude direction locationName address { __typename ...AddressDetails } } } } }  fragment AddressDetails on Address { __typename address1 address2 city state country postalCode }"


VEHICLE_EV_WAYPOINTS_OPERATION_ID = (
    "be09c18e0cedd291e1c4983eb3dd9c8ec90c44f45db4ca552d07be1cd9d05039"
)
VEHICLE_EV_WAYPOINTS = "query VehicleEVWaypoints($vin: String!, $departAt: DateTime, $arrivedBy: DateTime, $socAtDestination: Int, $routes: [RouteInputType]!, $distanceUnit: DistanceUnit, $plugConnectorTypes: [PlugConnectorType]!, $estimatedBatteryLevelAtDeparture: String, $minPower: Float, $socAtStop: Int, $useHvac: Boolean, $avoidHighway: Boolean, $avoidTolls: Boolean, $avoidFerries: Boolean) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { evWaypoints(routes: $routes, departAt: $departAt, arriveBy: $arrivedBy, socAtDestination: $socAtDestination, plugConnectorTypes: $plugConnectorTypes, estimatedBatteryLevelAtDeparture: $estimatedBatteryLevelAtDeparture, minPower: $minPower, socAtStop: $socAtStop, useHvac: $useHvac, avoidHighway: $avoidHighway, avoidTolls: $avoidTolls, avoidFerries: $avoidFerries) { __typename ... on EVWaypoint { departureTime arrivalTime totalChargingTimeInSeconds totalTravelTimeInSeconds totalDistance(unit: $distanceUnit) { __typename unit value } routes { __typename name arrivalTime chargingTimeInSeconds level type address { __typename address1 address2 city state postalCode country } location { __typename latitude longitude } status chargingOutput } } ... on MinimumRequirementNotMetError { message } ... on LimitReachedError { message } ... on UnableToCompleteRouteError { reason message details { __typename ... on MissingBatteryDetailsErrorDetails { batteryCapacity startingBatteryLevel } ... on NoChargingStationWithinRangeErrorDetails { center radius chargingConnectors minPower } ... on UnableToCompleteSubStepErrorDetails { start end distance speed slope startingBattery batteryCapacity batteryConsumption socAfterChargingNearStart minimumBattery chargingStationMaxPower } } } } } } }"


VEHICLE_ALERTS_OPERATION_ID = "25e79bb684b4ac4244d1173ec80af13593d360a32756634cfebca31f65a86f28"
VEHICLE_ALERTS = "query VehicleAlerts($vin: String!, $speedUnit: SpeedUnit, $distanceUnit: DistanceUnit) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { boundaryAlerts { __typename ...BoundaryAlertDetails } curfewAlerts { __typename ...CurfewAlertDetails } speedAlerts(speedUnit: $speedUnit) { __typename ...SpeedAlertDetails } valetAlert { __typename ...ValetAlertDetails } } } }  fragment BoundaryAlertDetails on BoundaryAlert { __typename serviceRequestId alertType name enabled inVehicleWarning address { __typename address1 address2 city state country postalCode } location { __typename latitude longitude } radius(unit: $distanceUnit) { __typename value unit } }  fragment CurfewAlertDetails on CurfewAlert { __typename serviceRequestId name enabled inVehicleWarning schedule { __typename allDay startDateTime duration weekDays } }  fragment SpeedAlertDetails on SpeedAlert { __typename serviceRequestId name enabled inVehicleWarning speedThreshold { __typename type value } }  fragment ValetAlertDetails on ValetAlert { __typename serviceRequestId radius(unit: $distanceUnit) { __typename unit value } }"


BREACH_ALERTS_OPERATION_ID = "7e3a5e10894be05f63160f80aca3dcb910474ef505f16c427c014fd9fec28f38"
BREACH_ALERTS = "query BreachAlerts($vin: String!, $pageNumber: Int!, $itemsPerPage: Int!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { breachAlerts(paginate: { itemsPerPage: $itemsPerPage pageNumber: $pageNumber } ) { __typename itemsPerPage pageNumber totalItems totalPages alerts { __typename serviceType breachDateTime name location { __typename latitude longitude } } } } } }"


VEHICLE_BOUNDARY_ALERT_OPERATION_ID = (
    "eadbeafea1f2da0eab04c4165a4ffdf29748244459178ba8f344795a42bdc05d"
)
VEHICLE_BOUNDARY_ALERT = "query VehicleBoundaryAlert($vin: String!, $serviceRequestId: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { boundaryAlert(serviceRequestId: $serviceRequestId) { __typename status } } } }"


VEHICLE_CURFEW_ALERT_OPERATION_ID = (
    "392950dffe3b2fb5b32038e1b40c5d24630db395d77a46759cd45c1007b8e58d"
)
VEHICLE_CURFEW_ALERT = "query VehicleCurfewAlert($vin: String!, $serviceRequestId: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { curfewAlert(serviceRequestId: $serviceRequestId) { __typename status } } } }"


VEHICLE_SPEED_ALERT_OPERATION_ID = (
    "e9efcfddaae40d119bf2a4bd1297744941a7b283f6f7bfb6cc3e00206d18855e"
)
VEHICLE_SPEED_ALERT = "query VehicleSpeedAlert($vin: String!, $serviceRequestId: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { speedAlert(serviceRequestId: $serviceRequestId) { __typename status } } } }"


VEHICLE_VALET_ALERT_OPERATION_ID = (
    "965fc8e8594ccf5ea79712a00fa70f03fbd0f49f2b16ab1a9a5ff250abde8f7f"
)
VEHICLE_VALET_ALERT = "query VehicleValetAlert($vin: String!, $serviceRequestId: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { valetAlert(serviceRequestId: $serviceRequestId) { __typename status } } } }"


CREATE_BOUNDARY_ALERT_OPERATION_ID = (
    "d7d567834de039200e907227e8988e16732190e7998e73b0fb1fac2ff4f4034f"
)
CREATE_BOUNDARY_ALERT = "mutation CreateBoundaryAlert($vin: String!, $alert: BoundaryAlertInput!) { createBoundaryAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


UPDATE_BOUNDARY_ALERT_OPERATION_ID = (
    "386b14b67cba523f85fd39911191726262ed47344546fcb649a02b3615a1b0a1"
)
UPDATE_BOUNDARY_ALERT = "mutation SetBoundaryAlert($vin: String!, $alert: SetBoundaryAlertInput!) { setBoundaryAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


DELETE_BOUNDARY_ALERT_OPERATION_ID = (
    "6a68ead88e178f7063d4693e90531a876f19fc912e40d34bf81799238bd41b72"
)
DELETE_BOUNDARY_ALERT = "mutation CancelBoundaryAlert($vin: String!, $serviceRequestId: String!) { cancelBoundaryAlert(vin: $vin, serviceRequestId: $serviceRequestId) { __typename serviceRequestId } }"


TOGGLE_BOUNDARY_ALERT_OPERATION_ID = (
    "c3266069329032064e554a987e2f09397ff4ae846b1e02446e448979447823b4"
)
TOGGLE_BOUNDARY_ALERT = "mutation ToggleBoundaryAlert($vin: String!, $alert: ToggleBoundaryAlertInput!) { toggleBoundaryAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


CREATE_CURFEW_ALERT_OPERATION_ID = (
    "6f753549d4b389ba09753158b6af471eedcc8cf0643e4c0a4f8c678426265b5b"
)
CREATE_CURFEW_ALERT = "mutation CreateCurfewAlert($vin: String!, $alert: CurfewAlertInput!) { createCurfewAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


UPDATE_CURFEW_ALERT_OPERATION_ID = (
    "71d942a320a3899cd12ad935056d68499234588123da8fce01733a3e915e19ea"
)
UPDATE_CURFEW_ALERT = "mutation SetCurfewAlert($vin: String!, $serviceRequestId: String!, $alert: CurfewAlertInput!) { setCurfewAlert(vin: $vin, serviceRequestId: $serviceRequestId, alert: $alert) { __typename serviceRequestId } }"


DELETE_CURFEW_ALERT_OPERATION_ID = (
    "5b940569c52dde6ad90e0f47d4e2a99b2e2350941ed6739e3d48bfeda2f3f798"
)
DELETE_CURFEW_ALERT = "mutation CancelCurfewAlert($vin: String!, $serviceRequestId: String!) { cancelCurfewAlert(vin: $vin, serviceRequestId: $serviceRequestId) { __typename serviceRequestId } }"


TOGGLE_CURFEW_ALERT_OPERATION_ID = (
    "5853c0b6b40cae1934bb5d5593434f088fd1c817766ef47e4d401c9561af8a42"
)
TOGGLE_CURFEW_ALERT = "mutation ToggleCurfewAlert($vin: String!, $alert: ToggleCurfewAlertInput!) { toggleCurfewAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


CREATE_SPEED_ALERT_OPERATION_ID = "6755b778b31aa31bb781bdaa7fbc3d8d9eb1dffce0c4f03694d6d4a6b414734c"
CREATE_SPEED_ALERT = "mutation CreateSpeedAlert($vin: String!, $alert: CreateSpeedAlertInput!) { createSpeedAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


UPDATE_SPEED_ALERT_OPERATION_ID = "46596adcea55be9f1737e5dcc4e16e2c45e31d8fbf5755ee319417f6ae221084"
UPDATE_SPEED_ALERT = "mutation SetSpeedAlert($vin: String!, $alert: SetSpeedAlertInput!) { setSpeedAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


DELETE_SPEED_ALERT_OPERATION_ID = "9b08210ac4d1fa21a3b5f4d459dc02df3fc8d66b7fbcc0be598b5acaef2c1a1e"
DELETE_SPEED_ALERT = "mutation CancelSpeedAlert($vin: String!, $serviceRequestId: String!) { cancelSpeedAlert(vin: $vin, serviceRequestId: $serviceRequestId) { __typename serviceRequestId } }"


TOGGLE_SPEED_ALERT_OPERATION_ID = "dd88004fabc61552f033f835ac14817936391c755cc51e94c5947dce9988214d"
TOGGLE_SPEED_ALERT = "mutation ToggleSpeedAlert($vin: String!, $alert: ToggleSpeedAlertInput!) { toggleSpeedAlert(vin: $vin, alert: $alert) { __typename serviceRequestId } }"


ACTIVATE_VALET_ALERT_OPERATION_ID = (
    "a56670441e5d8e35ed38e710f9d7b5bf1d5fa9ec5312d381f3e7c37374a4c244"
)
ACTIVATE_VALET_ALERT = "mutation ActivateValetAlert($vin: String!, $radiusWithUnit: FloatDistanceInput, $location: LocationInput) { activateValetAlert(vin: $vin, radiusWithUnit: $radiusWithUnit, location: $location) { __typename serviceRequestId } }"


DEACTIVATE_VALET_ALERT_OPERATION_ID = (
    "939f6c15456f1350d0355c298e2ea437d370e92f9184957010ee965cfa3e62ce"
)
DEACTIVATE_VALET_ALERT = "mutation DeactivateValetAlert($vin: String!, $serviceRequestId: String!) { deactivateValetAlert(vin: $vin, serviceRequestId: $serviceRequestId) { __typename serviceRequestId } }"


REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE_OPERATION_ID = (
    "399e20f8294e64cd1d364eb2fe5255a627d9e342ae46874ba552f36f59f0b499"
)
REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE = "query ReminderNotificationsAfterLeavingVehicle($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { reminderNotificationsAfterLeavingVehicle { __typename lock door trunk sunroof window } } } }"


TOGGLE_REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE_OPERATION_ID = (
    "728a557f0ba554836dc806d4b6c4e4d201938ab58f675127358f7c19d95caab3"
)
TOGGLE_REMINDER_NOTIFICATIONS_AFTER_LEAVING_VEHICLE = "mutation ToggleReminderNotificationsAfterLeavingVehicle($vin: String!, $reminderNotifications: ToggleReminderNotificationsAfterLeavingVehicleInput!) { toggleReminderNotificationsAfterLeavingVehicle(vin: $vin, reminderNotifications: $reminderNotifications) { __typename success } }"


VEHICLE_DATA_PRIVACY_MODE_OPERATION_ID = (
    "f7214e45fa23ef8da0562d1afa26a43cd8563d0137602a51c938bedc438b28d5"
)
VEHICLE_DATA_PRIVACY_MODE = "query VehicleDataPrivacyMode($vin: String!) { vehicle(vin: $vin) { __typename dataPrivacyMode } }"


VEHICLE_WIFI_CONSUMPTION_OPERATION_ID = (
    "6a066029ce89bde44f1f25788449e37dbd81e11dd4306216e8b36080a74663c0"
)
VEHICLE_WIFI_CONSUMPTION = "query VehicleWifiConsumption($vin: String!) { vehicle(vin: $vin) { __typename capabilities { __typename wifiConsumption { __typename usagePercent usageAmount dataCapAmount updatedAt } } } }"


VEHICLE_PREFERENCES_OPERATION_ID = (
    "e002089b858510036b57054b6c13c89cc1c9cbbf49e87bc533cb5fada0dbe24e"
)
VEHICLE_PREFERENCES = "query VehiclePreferences($vin: String!) { vehicle(vin: $vin) { __typename preferences { __typename communication { __typename milDataSharing { __typename enabled text phone email } } } } }"


VEHICLE_SUBSCRIPTIONS_OPERATION_ID = (
    "f73083b80399d14527938d7dfd92db232b5376ea2d36d9bc481e561bae67f566"
)
VEHICLE_SUBSCRIPTIONS = "query VehicleSubscriptions($vin: String!) { vehicle(vin: $vin) { __typename capabilities { __typename subscriptions { __typename subscriptionId subscriptionServiceType purchaseType productType nextBillingDate goodwillEndDate goodwillStartDate graceEndDate subscriptionStartDate subscriptionEndDate isActive npSubscriptionPrice product { __typename productId marketingName description services } pendingOrder { __typename pendingOrderId packageName activationDate } } } } }"


UPDATE_VEHICLE_PREFERENCES_OPERATION_ID = (
    "f6e5b1e4b9098a6961b2e021e53a5f5ea1f1e494eb47fe4515afabd113070d05"
)
UPDATE_VEHICLE_PREFERENCES = "mutation UpdateVehiclePreferences($vin: String!, $communication: UpdateVehiclePreferencesCommunicationInput!) { updateVehiclePreferences(vin: $vin, communication: $communication) { __typename ... on ResponseStatus { success } ... on GeneralError { message } } }"


REMOTE_SERVICE_HISTORY_OPERATION_ID = (
    "d20475a83849509463576b63e0239de4fa65cf9e3ad31ca2b55872dacc651c26"
)
REMOTE_SERVICE_HISTORY = "query RemoteServiceHistory($vin: String!, $pageNumber: Int!, $itemsPerPage: Int!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { remoteServiceHistory(paginate: { pageNumber: $pageNumber itemsPerPage: $itemsPerPage } ) { __typename pageNumber itemsPerPage totalItems totalPages history { __typename serviceRequestId status serviceType statusChangeDateTime } } } } }"


VEHICLE_CAPABILITIES_OPERATION_ID = (
    "5b836761ba484dd13e8daf26745112907203e481a86398fd3c90dc00abbfcf9a"
)
VEHICLE_CAPABILITIES = "query VehicleCapabilities($vin: String!, $unit: TemperatureUnitEnumType = FAHRENHEIT ) { vehicle(vin: $vin) { __typename capabilities { __typename telematicsProgram status serviceCapability { __typename type enabled subscribed } accessoriesDetails { __typename seatHeater { __typename enabled accessories { __typename assistantSeat driverSeat secondCentreSeat secondLeftSeat secondRightSeat thirdLeftSeat thirdRightSeat } } steeringHeat { __typename enabled } sunRoof { __typename type enabled } windowStatus { __typename enabled } wayPoint { __typename enabled maxNumber } hvacTemperatures(unit: $unit) { __typename unit default min max resolution } } } } }"


VEHICLE_CHARGE_SCHEDULES_OPERATION_ID = (
    "7821c102ca9e6b1814bd89e0c6263da8741a542815777e2a6da28678f3083563"
)
VEHICLE_CHARGE_SCHEDULES = "query VehicleChargeSchedules($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { chargeSchedules { __typename ...ChargeSchedulesDetails } } } }  fragment ChargeSchedulesDetails on ChargeSchedule { __typename id state startDateTime duration weekDays }"


CHARGE_CONFIG_OPERATION_ID = "aa21136ff533f3606b181ec3adfd5f4d2fa880e34e6b8df61f53166073f436eb"
CHARGE_CONFIG = "query ChargeConfig($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseElectric2Vehicle { chargeConfig { __typename limits { __typename notification { __typename percent } charge { __typename percent } } } } } }"


V2L_STATUS_OPERATION_ID = "0126a9729920e465eb60cf5e02f1b51476b3be24670cebd84c8e207c2fd0167f"
V2L_STATUS = "query V2lStatus($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseElectric2Vehicle { v2lStatus { __typename state chargeLimitationLevel chargeMinimumLimitationLevel } } } }"


VEHICLE_CHARGE_HISTORY_OPERATION_ID = (
    "79659823ebfc155520841f03d09715fdc889ead39d7fa21ad1bbcbc7d20e79ed"
)
VEHICLE_CHARGE_HISTORY = "query VehicleChargeHistory($vin: String!, $aggregator: ChargeHistoryAggregator!) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { chargeHistory(aggregator: $aggregator) { __typename charges { __typename start end duration recoveredEnergy } chargeSummaries { __typename day month year numberOfChargeSessions totalEnergyRecovered totalDuration numberOfErrors userId roleType } } } } }"


VEHICLE_CLIMATE_SCHEDULES_OPERATION_ID = (
    "6cba7d41c1653a0d80028cbac4cd71c76d41ee65074aea74247e5e970be497a4"
)
VEHICLE_CLIMATE_SCHEDULES = "query VehicleClimateSchedules($vin: String!, $temperatureUnit: TemperatureUnitEnumType!) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { climateSchedules { __typename ...ClimateSchedulesDetails } } ... on BaseElectric2Vehicle { climateSchedulesAccessories { __typename defrostAndDeicerState steeringWheelHeaterState seatsClimate { __typename frontDriverState frontPassengerState rearLeftPassengerState rearCenterPassengerState rearRightPassengerState thirdLeftState thirdRightState } } } ... on ElectricAVK2Vehicle { delayedClimateSchedule { __typename startDateTime } } } }  fragment ClimateSchedulesDetails on ClimateSchedule { __typename id state startDateTime weekDays temperature(unit: $temperatureUnit) { __typename value unit } }"


VEHICLE_CLIMATE_DEFAULTS_OPERATION_ID = (
    "3f9774feeaacb0808d17af4a1195f2095aa7a8ea8200f457085609f1691459a4"
)
VEHICLE_CLIMATE_DEFAULTS = "query VehicleClimateDefaults($vin: String!, $temperatureUnit: TemperatureUnitEnumType) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { climateDefaults { __typename climate(unit: $temperatureUnit) { __typename value unit } parameters { __typename steeringWheelHeaterState defrostAndDeicerState seatsClimate { __typename frontDriverState frontPassengerState rearLeftPassengerState rearRightPassengerState rearCenterPassengerState thirdLeftState thirdRightState } } } } } }"


START_CLIMATE_OPERATION_ID = "8e5a3949c1be015b350a4561206269c6266e40c0391429ffeeb7a75a6dda9fc5"
START_CLIMATE = "mutation StartClimate($vin: String!, $climate: StartClimateInput!, $parameters: SetClimateParametersInput, $setAsDefault: Boolean) { startClimate(vin: $vin, climate: $climate, parameters: $parameters, setAsDefault: $setAsDefault) { __typename ... on TelematicsResponse { serviceRequestId additionalData { __typename ... on SetClimateDefaultsResponse { success } ... on SetClimateDefaultsError { message } } } } }"


ADJUST_CLIMATE_OPERATION_ID = "458694ffb6b46b91698ff743eb6bb3e26b9295382eb97f91ee51e908d04474f4"
ADJUST_CLIMATE = "mutation AdjustClimate($vin: String!, $climate: AdjustClimateInput!, $parameters: SetClimateParametersInput, $setAsDefault: Boolean) { adjustClimate(vin: $vin, climate: $climate, parameters: $parameters, setAsDefault: $setAsDefault) { __typename ... on TelematicsResponse { serviceRequestId additionalData { __typename ... on SetClimateDefaultsResponse { success } ... on SetClimateDefaultsError { message } } } } }"


STOP_CLIMATE_OPERATION_ID = "e7a7f92ae5f99ca8260c284f65d688004a15c51719993229314be86a8aebb74e"
STOP_CLIMATE = (
    "mutation StopClimate($vin: String!) { stopClimate(vin: $vin) { __typename serviceRequestId } }"
)


SET_CLIMATE_DEFAULTS_OPERATION_ID = (
    "aa4d914489f91dfba1c1c29ce215b967621c840252cd789b8f7ac3546f5c2c60"
)
SET_CLIMATE_DEFAULTS = "mutation SetClimateDefaults($vin: String!, $climate: StartClimateInput!, $parameters: SetClimateParametersInput) { setClimateDefaults(vin: $vin, climate: $climate, parameters: $parameters) { __typename ... on SetClimateDefaultsResponse { success } ... on SetClimateDefaultsError { message } } }"


SET_DELAYED_CLIMATE_OPERATION_ID = (
    "e8132dd6d0baf0a3cfe45f22e3ebb28adf605fba06a90d1b83184f6249f6e11c"
)
SET_DELAYED_CLIMATE = "mutation SetDelayedClimate($vin: String!, $startDateTime: DateTime!, $climate: StartClimateInput!, $climateAccessories: SetClimateParametersInput) { setDelayedClimate(vin: $vin, startDateTime: $startDateTime, climate: $climate, climateAccessories: $climateAccessories) { __typename ... on TelematicsResponse { serviceRequestId } ... on LimitReachedError { message } } }"


CANCEL_DELAYED_CLIMATE_OPERATION_ID = (
    "25311e2500e8668525074ef506c1aa5df2dfe845b5f07f915468c34da6c8eca3"
)
CANCEL_DELAYED_CLIMATE = "mutation CancelDelayedClimate($vin: String!) { cancelDelayedClimate(vin: $vin) { __typename ... on TelematicsResponse { serviceRequestId } } }"


START_CHARGE_OPERATION_ID = "e50738527dfbf488313bac7d2f4a5fd05826e09f42c2e190145a4ba59d74be47"
START_CHARGE = (
    "mutation StartCharge($vin: String!) { startCharge(vin: $vin) { __typename serviceRequestId } }"
)


STOP_CHARGE_OPERATION_ID = "ffb2002b1242a7ba11fd2d0da63614b1fcb53ac072bb8df109a9b72223b55d66"
STOP_CHARGE = (
    "mutation StopCharge($vin: String!) { stopCharge(vin: $vin) { __typename serviceRequestId } }"
)


SET_CHARGE_LIMIT_OPERATION_ID = "5d4274c1cf71e701fbeaca1c0b1e74cb7d6040ace35262a5a14cb712ed6e10f5"
SET_CHARGE_LIMIT = "mutation SetChargeLimit($vin: String!, $percent: Int!) { setChargeLimit(vin: $vin, percent: $percent) { __typename serviceRequestId } }"


SET_NOTIFICATION_LIMIT_OPERATION_ID = (
    "c48582a01e4ae9161d1cb9bf012d06e434de56a564b08df491ccb9c0a5367f0f"
)
SET_NOTIFICATION_LIMIT = "mutation SetNotificationLimit($vin: String!, $percent: Int!) { setChargeNotificationThreshold(vin: $vin, percent: $percent) { __typename serviceRequestId } }"


SET_V2L_OPERATION_ID = "6c89e90865037c2d48c82f755b35a94a8a3d57e8467024976be4de66e76f0d5c"
SET_V2L = "mutation SetV2L($vin: String!, $input: SetV2LInput!) { setV2L(vin: $vin, input: $input) { __typename serviceRequestId } }"


DOOR_LOCK_OPERATION_ID = "87753620a0bc7039fb1b978e547279ac395cf7bce137599dd4470e7220c85ee7"
DOOR_LOCK = (
    "mutation DoorLock($vin: String!) { doorLock(vin: $vin) { __typename serviceRequestId } }"
)


DOOR_UNLOCK_OPERATION_ID = "20411054e3e66698dc11f9cffe40902e5301fac7f59edd27df7fe02dec97de8c"
DOOR_UNLOCK = (
    "mutation DoorUnlock($vin: String!) { doorUnlock(vin: $vin) { __typename serviceRequestId } }"
)


FLASH_LIGHTS_OPERATION_ID = "8aacded57976781bad7fee92d32e2d7324bb3d158cd533b7becd4145a3ed503b"
FLASH_LIGHTS = (
    "mutation FlashLights($vin: String!) { flashLights(vin: $vin) { __typename serviceRequestId } }"
)


FLASH_LIGHTS_HORN_OPERATION_ID = "be9600791b6ffa6568714426a1af3dc59be67594c1f0228a7334413f4304c366"
FLASH_LIGHTS_HORN = "mutation FlashLightsHorn($vin: String!) { flashLightsHorn(vin: $vin) { __typename serviceRequestId } }"


LOCATE_VEHICLE_OPERATION_ID = "dc31a8fb8daabe25b2d6d1934a0efe802ba5a1ca83fa3913debd9805444f8a95"
LOCATE_VEHICLE = "mutation LocateVehicle($vin: String!) { locateVehicle(vin: $vin) { __typename serviceRequestId } }"


ENGINE_START_OPERATION_ID = "a6cd4efd4d8f0e2f4a8cfd78822f4cb7b133208bdce4387bc4fc95389a147fb4"
ENGINE_START = "mutation EngineStart($vin: String!, $climate: EngineStartClimateInput, $setAsDefault: Boolean) { engineStart(vin: $vin, climate: $climate, setAsDefault: $setAsDefault) { __typename serviceRequestId additionalData { __typename ... on SetClimateDefaultsResponse { success } ... on SetClimateDefaultsError { message } } } }"


ENGINE_STOP_OPERATION_ID = "ca8b381a0abe022e8f06956276c18d83872f721cf323cb61ea01074d871c127d"
ENGINE_STOP = (
    "mutation EngineStop($vin: String!) { engineStop(vin: $vin) { __typename serviceRequestId } }"
)


REFRESH_VEHICLE_STATUS_OPERATION_ID = (
    "e60d3c9c99f564736751cbd529b25dc21cf52fa71bf02b02e05c2ff4331d596f"
)
REFRESH_VEHICLE_STATUS = "mutation RefreshVehicleStatus($vin: String!) { refreshVehicleStatus(vin: $vin) { __typename serviceRequestId } }"


REFRESH_BATTERY_STATUS_OPERATION_ID = (
    "da6bfc5f9d01414aae0eb72ee2190b99ba65b44eeb02d7e01ad9bbefb224049d"
)
REFRESH_BATTERY_STATUS = "mutation RefreshBatteryStatus($vin: String!) { refreshBatteryStatus(vin: $vin) { __typename success } }"


REFRESH_CLIMATE_STATUS_OPERATION_ID = (
    "89401dbe15c4014839f7a162ff221598686e3d71306032377c0b8c4f18fa5900"
)
REFRESH_CLIMATE_STATUS = "mutation RefreshClimateStatus($vin: String!) { refreshClimateStatus(vin: $vin) { __typename success } }"


WAKE_UP_VEHICLE_OPERATION_ID = "ef21fb5c095319bdb96355a9ef1e4bd7d8d95d6c676d5ab4bb1c0e55490e2583"
WAKE_UP_VEHICLE = (
    "mutation WakeUpVehicle($vin: String!) { wakeUp(vin: $vin) { __typename success } }"
)


TAKE_PHOTOS_AROUND_VEHICLE_OPERATION_ID = (
    "bfe62e672b070a8ed15b214e2e25a6f0bbeb75e1a238aa0c3cc8fcd60541a81f"
)
TAKE_PHOTOS_AROUND_VEHICLE = "mutation TakePhotosAroundVehicle($vin: String!) { takePhotosAroundVehicle(vin: $vin) { __typename serviceRequestId } }"


CREATE_CHARGE_SCHEDULE_OPERATION_ID = (
    "adf8a36e101badffac799e610a26b5348c11154411ff21c2afde73d78f10ffd2"
)
CREATE_CHARGE_SCHEDULE = "mutation CreateChargeSchedule($vin: String!, $schedule: CreateChargeScheduleInput!) { createChargeSchedule(vin: $vin, schedule: $schedule) { __typename ... on TelematicsResponse { serviceRequestId } } }"


UPDATE_CHARGE_SCHEDULE_OPERATION_ID = (
    "9e65c3b20d8d7f8f2218ccb1bf0213b0a63a4950b9a466a8c382bf31d89d1015"
)
UPDATE_CHARGE_SCHEDULE = "mutation UpdateChargeSchedule($vin: String!, $schedule: UpdateChargeScheduleInput!) { updateChargeSchedule(vin: $vin, schedule: $schedule) { __typename serviceRequestId } }"


DELETE_CHARGE_SCHEDULE_OPERATION_ID = (
    "5a01d142da99b0abff743f03718ba797ae35bbe3c46039e6efe419897e1235ed"
)
DELETE_CHARGE_SCHEDULE = "mutation DeleteChargeSchedule($vin: String!, $id: String!) { deleteChargeSchedule(vin: $vin, id: $id) { __typename serviceRequestId } }"


TOGGLE_CHARGE_SCHEDULE_OPERATION_ID = (
    "b0c4ad346edebbef628f6725c7d0eb2dfb77c470fd176d8b194be23ac825a936"
)
TOGGLE_CHARGE_SCHEDULE = "mutation ToggleChargeSchedule($vin: String!, $schedule: ToggleChargeScheduleInput!) { toggleChargeSchedule(vin: $vin, schedule: $schedule) { __typename serviceRequestId } }"


CREATE_CLIMATE_SCHEDULE_OPERATION_ID = (
    "d53300ee3969664cf32b1f2a8a55bc1619518b350820707633dbf6ce2e589329"
)
CREATE_CLIMATE_SCHEDULE = "mutation CreateClimateSchedule($vin: String!, $schedule: CreateClimateScheduleInput!, $climateAccessories: SetClimateParametersInput) { createClimateSchedule(vin: $vin, schedule: $schedule, climateAccessories: $climateAccessories) { __typename ... on TelematicsResponse { serviceRequestId } } }"


UPDATE_CLIMATE_SCHEDULE_OPERATION_ID = (
    "2db449c4f5f28a3e813ea62c955e470b586cb971399a21853b40bbc9ef35ccc9"
)
UPDATE_CLIMATE_SCHEDULE = "mutation UpdateClimateSchedule($vin: String!, $schedule: UpdateClimateScheduleInput!, $climateAccessories: SetClimateParametersInput) { updateClimateSchedule(vin: $vin, schedule: $schedule, climateAccessories: $climateAccessories) { __typename ... on TelematicsResponse { serviceRequestId } } }"


DELETE_CLIMATE_SCHEDULE_OPERATION_ID = (
    "0b2156d3de66858182d908ab56ee02398203a3edcf80b637d5f033598405e15e"
)
DELETE_CLIMATE_SCHEDULE = "mutation DeleteClimateSchedule($vin: String!, $id: String!) { deleteClimateSchedule(vin: $vin, id: $id) { __typename serviceRequestId } }"


TOGGLE_CLIMATE_SCHEDULE_OPERATION_ID = (
    "0e34850dd8bd95923eb037f00f342286144df5cdcf64dd80b2449dd3d575e12d"
)
TOGGLE_CLIMATE_SCHEDULE = "mutation ToggleClimateSchedule($vin: String!, $schedule: ToggleClimateScheduleInput!) { toggleClimateSchedule(vin: $vin, schedule: $schedule) { __typename serviceRequestId } }"


SEND_JOURNEY_OPERATION_ID = "e9a23281eb2b53ca40aadd3f880a631f3da770d0498518ab631b2f4971514f3f"
SEND_JOURNEY = "mutation SendJourney($vin: String!, $waypoints: [DestinationInput!]!, $avoidHighway: Boolean, $avoidTolls: Boolean, $avoidFerries: Boolean, $estimatedTimeOfArrival: DateTime, $estimatedTimeOfDeparture: DateTime, $arrivalFlag: Boolean, $departureFlag: Boolean) { sendJourney(vin: $vin, waypoints: $waypoints, avoidHighway: $avoidHighway, avoidTolls: $avoidTolls, avoidFerries: $avoidFerries, estimatedTimeOfArrival: $estimatedTimeOfArrival, estimatedTimeOfDeparture: $estimatedTimeOfDeparture, arrivalFlag: $arrivalFlag, departureFlag: $departureFlag) { __typename ... on ResponseStatus { success } } }"


SEND_PLANNED_ROUTE_OPERATION_ID = "48e3ca1cfe6e3d9f584c65b21b5c6f9332f5829a3c012a3c87231d890d8868c0"
SEND_PLANNED_ROUTE = "mutation SendPlannedRoute($vin: String!, $routeId: String!, $estimatedTimeOfArrival: DateTime, $estimatedTimeOfDeparture: DateTime, $arrivalFlag: Boolean, $departureFlag: Boolean) { sendPlannedRoute(vin: $vin, routeId: $routeId, estimatedTimeOfArrival: $estimatedTimeOfArrival, estimatedTimeOfDeparture: $estimatedTimeOfDeparture, arrivalFlag: $arrivalFlag, departureFlag: $departureFlag) { __typename success } }"


SEND_POINT_OF_INTEREST_OPERATION_ID = (
    "2d1e53653db35b8b61a52510e8645ac91a0afb62c284672e8e5aefa2c2fe4219"
)
SEND_POINT_OF_INTEREST = "mutation SendPointOfInterest($vin: String!, $folderName: FolderNameEnumInputType!, $destinationInput: DestinationInput!, $calculationCondition: CalculateConditionEnumInputType, $avoidHighway: Boolean, $avoidTolls: Boolean, $avoidFerries: Boolean) { sendPointOfInterest(vin: $vin, folderName: $folderName, destination: $destinationInput, calculationCondition: $calculationCondition, avoidHighway: $avoidHighway, avoidTolls: $avoidTolls, avoidFerries: $avoidFerries) { __typename ... on ResponseStatus { success } ... on LimitReachedError { message } } }"


SAVE_ROUTE_OPERATION_ID = "80f030c6494ac87e620c9e770c8c6ae99799bc3d28340fa7a2ab826c39bcf29e"
SAVE_ROUTE = "mutation SaveRoute($vin: String!, $plannedRoute: PlannedRouteInput!, $arrivalFlag: Boolean, $departureFlag: Boolean) { saveRoute(vin: $vin, plannedRoute: $plannedRoute, arrivalFlag: $arrivalFlag, departureFlag: $departureFlag) { __typename ... on TelematicsResponse { serviceRequestId } } }"


UPDATE_ROUTE_OPERATION_ID = "5ed2f87f17b7dffdbed235cb35163ebc8dc53315c46fd8c62a9561c5252729d6"
UPDATE_ROUTE = "mutation UpdateRoute($vin: String!, $plannedRoute: UpdatePlannedRouteInput!, $arrivalFlag: Boolean, $departureFlag: Boolean) { updateRoute(vin: $vin, plannedRoute: $plannedRoute, arrivalFlag: $arrivalFlag, departureFlag: $departureFlag) { __typename ... on TelematicsResponse { serviceRequestId } } }"


DELETE_ROUTE_OPERATION_ID = "0505b24377e79a87749a68be60594842d9ccf8757f4d91a8872585069bdb421c"
DELETE_ROUTE = "mutation DeleteRoute($vin: String!, $routeId: String!) { deleteRoute(vin: $vin, routeId: $routeId) { __typename success } }"


DELETE_FAVORITE_POINT_OF_INTEREST_OPERATION_ID = (
    "0d1329ab2d5d5b8cc3266b5c6204ed8bcd725af2e6bacbf94f41e0fe1197a484"
)
DELETE_FAVORITE_POINT_OF_INTEREST = "mutation DeleteFavoritePointOfInterest($vin: String!, $destinationId: String!) { deleteFavoritePointOfInterest(vin: $vin, destinationId: $destinationId) { __typename success } }"


SAVE_T_JUNCTION_LOCATIONS_OPERATION_ID = (
    "d6a5fa7034b9703ce0a32117fa5ffc0189131c016469480ae7ff22852b22e819"
)
SAVE_T_JUNCTION_LOCATIONS = "mutation SaveTJunctionLocations($input: SaveTJunctionLocationsInput!) { saveTJunctionLocations(input: $input) { __typename serviceRequestId } }"


UPDATE_SAVED_T_JUNCTION_LOCATION_OPERATION_ID = (
    "333534b63d1391372e75c93760d1e93da2df6ebea47799efc88c60e6a1c71034"
)
UPDATE_SAVED_T_JUNCTION_LOCATION = "mutation UpdateSavedTJunctionLocation($input: UpdateSavedLocationInput!) { updateSavedTJunctionLocation(input: $input) { __typename serviceRequestId } }"


DELETE_SAVED_T_JUNCTION_LOCATIONS_OPERATION_ID = (
    "08b97319e85fd61d7b0d2b7fd85db352ec00d777079ff8b2737d38566d4080db"
)
DELETE_SAVED_T_JUNCTION_LOCATIONS = "mutation DeleteSavedTJunctionLocations($input: DeleteSavedTJunctionLocationInput!) { deleteSavedTJunctionLocations(input: $input) { __typename serviceRequestId } }"


DELETE_UNSAVED_T_JUNCTION_LOCATIONS_OPERATION_ID = (
    "90ecaf1c65e492b1a2ed5503ca4c63d72c64fdc159475b19e773a022cc13f267"
)
DELETE_UNSAVED_T_JUNCTION_LOCATIONS = "mutation DeleteUnsavedTJunctionLocations($input: DeleteUnsavedTJunctionLocationsInput!) { deleteUnsavedTJunctionLocations(input: $input) { __typename serviceRequestId } }"


CHECK_CHARGE_REQUEST_OPERATION_ID = (
    "559db1ceba0268d2ca6ce2647dbb51a415f1c0b55710e4da52c39ec8beb443ae"
)
CHECK_CHARGE_REQUEST = "mutation CheckChargeServiceRequest($vin: String!, $serviceRequestId: String!) { checkChargeServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_CHARGE_CONFIGURATION_REQUEST_OPERATION_ID = (
    "01d7e6dc0ab1c84318b7fcf424bc1dc1b283a928c5fd726dd7855e2d7ade35b6"
)
CHECK_CHARGE_CONFIGURATION_REQUEST = "mutation CheckChargeConfigServiceRequest($vin: String!, $serviceRequestId: String!) { checkChargeConfigServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_V2L_REQUEST_OPERATION_ID = "3054ae7bb0305f9b531acbbce1c230038e42b49e4e9217020f06838455821202"
CHECK_V2L_REQUEST = "mutation CheckV2LServiceRequest($vin: String!, $serviceRequestId: String!) { checkV2LServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_CLIMATE_REQUEST_OPERATION_ID = (
    "0204baf97ac721a661b3f6dff436bff5eaa8f4899af5bac998cbaf79b24fd709"
)
CHECK_CLIMATE_REQUEST = "mutation CheckRemoteClimateRequest($vin: String!, $serviceRequestId: String!) { checkRemoteClimateRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status statusDetails } }"


CHECK_DOOR_REQUEST_OPERATION_ID = "86896f1ea2564c44e864639f640fb2d9e3d85bd2d62fdb1b6858ddc7fec45dd7"
CHECK_DOOR_REQUEST = "mutation CheckDoorServiceRequest($vin: String!, $serviceRequestId: String!) { checkDoorServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_ENGINE_REQUEST_OPERATION_ID = (
    "184b94324cfaca65ff8e2a3b1a7d506f7984e6234c184fc9929a95b574b64cc1"
)
CHECK_ENGINE_REQUEST = "mutation CheckEngineServiceRequest($vin: String!, $serviceRequestId: String!) { checkEngineServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status statusDetails } }"


CHECK_HORN_LIGHT_REQUEST_OPERATION_ID = (
    "eb8834bf39cbfbab251c2b1874f35c0a59eec8c24a4d86507fb6150c912d0c9b"
)
CHECK_HORN_LIGHT_REQUEST = "mutation CheckHornLightServiceRequest($vin: String!, $serviceRequestId: String!) { checkHornLightServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_LOCATION_REQUEST_OPERATION_ID = (
    "bf1f9f08f17a31131e340b0f392cbfd69ab6bc0d452229cac0fd180453522631"
)
CHECK_LOCATION_REQUEST = "mutation CheckLocationServiceRequest($vin: String!, $serviceRequestId: String!) { checkLocationServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status location { __typename lastUpdatedAt latitude longitude } } }"


CHECK_REFRESH_VEHICLE_STATUS_REQUEST_OPERATION_ID = (
    "f60bf5755789f087f6c52393c6296d4b71cd3f5189e89453991d572dc995be00"
)
CHECK_REFRESH_VEHICLE_STATUS_REQUEST = "mutation CheckRefreshVehicleStatusRequest($vin: String!, $serviceRequestId: String!) { checkRefreshVehicleStatusRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_PHOTO_REQUEST_OPERATION_ID = (
    "0cbb6da7c11e6d2fe8d571bcf135b82d57014cfaf9dbde49c1344b3d93248058"
)
CHECK_PHOTO_REQUEST = "mutation CheckTakePhotosAroundVehicleServiceRequest($vin: String!, $serviceRequestId: String!) { checkTakePhotosAroundVehicleServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename activationDateTime statusChangeDateTime serviceRequestId status } }"


CHECK_ROUTE_REQUEST_OPERATION_ID = (
    "813b4ff2edb2d9f226f767ed09e206b14249b6edb50098350acf9c4c9bffc97b"
)
CHECK_ROUTE_REQUEST = "mutation CheckRouteServiceRequest($vin: String!, $serviceRequestId: String!) { checkRouteServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


CHECK_T_JUNCTION_REQUEST_OPERATION_ID = (
    "d2b1417e81e2f8a6303a6d77f21f15c95c39f48e245004df008a1d6e15bdb3ec"
)
CHECK_T_JUNCTION_REQUEST = "mutation CheckTJunctionServiceRequest($vin: String!, $serviceRequestId: String!) { checkTJunctionServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status statusDetails } }"


OTA_UPDATE_OPERATION_ID = "72fd96c1c8c2ca21b6f315f4c9f6b6290931794c551aa972d30864036f519ec6"
OTA_UPDATE = "query OtaUpdate($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseEVOVehicle { otaUpdate { __typename campaignOperationId status { __typename status activationTimerValue progress countDownTimeStart countDownDelay } campaignDescription { __typename globalReleaseNote downloadDisclaimer activationDisclaimer activationEstimatedTime } batteryLevel { __typename activationEnabled stateOfCharge activationMinimumBatteryLevel } size lastChecked activationTimerValue } } } }"


OTA_UPDATE_PROGRESS_OPERATION_ID = (
    "2d4dec80522a257b5e4aa375c60708019de3cde363fb59a1037f8f776f2c82e7"
)
OTA_UPDATE_PROGRESS = "query OtaUpdateProgress($campaignOperationId: String!, $vin: String!) { vehicle(vin: $vin) { __typename ... on BaseEVOVehicle { otaUpdateProgress(campaignOperationId: $campaignOperationId) { __typename status percentage errorInfo { __typename errorCode errorMessage isRetryable } } } } }"


NOTIFICATION_PREFERENCES_OPERATION_ID = (
    "528ef75002be5eb87187ff2d353cb410d860438cf7aab7e541dfb33c12d870f3"
)
NOTIFICATION_PREFERENCES = "query NotificationPreferences($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { notificationPreferences { __typename notificationCategory notificationType { __typename destination optIn } } } } }"


DOWNLOAD_OTA_UPDATE_OPERATION_ID = (
    "99a03727b8ea38db53b30422cdbd0fe741e540491d16deeafba9c846bf32e366"
)
DOWNLOAD_OTA_UPDATE = "mutation DownloadOTAUpdate($vin: String!, $input: DownloadOTAUpdateInput!) { downloadOTAUpdate(vin: $vin, input: $input) { __typename ... on OperationInProgressError { message } ... on TelematicsResponse { serviceRequestId } } }"


ACTIVATE_OTA_UPDATE_OPERATION_ID = (
    "0afb1c17ab697383cfabcff99d8d6e8a3c90a454326920e2f846c80a6f0219a0"
)
ACTIVATE_OTA_UPDATE = "mutation ActivateOTAUpdate($vin: String!, $otaUpdateId: String!) { activateOTAUpdate(vin: $vin, otaUpdateId: $otaUpdateId) { __typename ... on TelematicsResponse { serviceRequestId } } }"


CANCEL_ACTIVATION_OTA_UPDATE_OPERATION_ID = (
    "a8540d16d7a5fa66db69d71d78eb382ddd6510f3b2e37a05c7cec8cda9490c27"
)
CANCEL_ACTIVATION_OTA_UPDATE = "mutation CancelActivationOTAUpdate($vin: String!, $otaUpdateId: String!) { cancelActivationOTAUpdate(vin: $vin, otaUpdateId: $otaUpdateId) { __typename ... on TelematicsResponse { serviceRequestId } } }"


SCHEDULE_ACTIVATION_OTA_UPDATE_OPERATION_ID = (
    "d5d986a7af80173def1427a91fe04635ff177b09ce197d1a0d058648b5adda80"
)
SCHEDULE_ACTIVATION_OTA_UPDATE = "mutation ScheduleActivationOTAUpdate($vin: String!, $input: ScheduleActivationOTAUpdateInput!) { scheduleActivationOTAUpdate(vin: $vin, input: $input) { __typename ... on TelematicsResponse { serviceRequestId additionalData { __typename ... on SetClimateDefaultsResponse { success } ... on SetClimateDefaultsError { message } } } } }"


UPDATE_SCHEDULED_ACTIVATION_OTA_UPDATE_OPERATION_ID = (
    "117ba35691d0258a0a2b46365aeadf5841eba6783c29c2c36306d0cb6d88a620"
)
UPDATE_SCHEDULED_ACTIVATION_OTA_UPDATE = "mutation UpdateScheduledActivationOTAUpdate($vin: String!, $input: UpdateScheduledActivationOTAUpdateInput!) { updateScheduledActivationOTAUpdate(vin: $vin, input: $input) { __typename ... on TelematicsResponse { serviceRequestId additionalData { __typename ... on SetClimateDefaultsResponse { success } ... on SetClimateDefaultsError { message } } } } }"


CANCEL_SCHEDULED_ACTIVATION_OTA_UPDATE_OPERATION_ID = (
    "a6305427b8083b1956f2b22f6527ce2e457c54ed3522fbd336d7428c6fcf47c4"
)
CANCEL_SCHEDULED_ACTIVATION_OTA_UPDATE = "mutation CancelScheduledActivationOTAUpdate($vin: String!, $otaUpdateId: String!) { cancelScheduledActivationOTAUpdate(vin: $vin, otaUpdateId: $otaUpdateId) { __typename ... on TelematicsResponse { serviceRequestId } } }"


CHECK_OTA_UPDATE_REQUEST_OPERATION_ID = (
    "34b8e6e84c5e6798e6f7c8f9d376682b9b267a6221b6ca166499cfcc2907c54a"
)
CHECK_OTA_UPDATE_REQUEST = "mutation CheckOtaUpdateServiceRequest($vin: String!, $serviceRequestId: String!) { checkOtaUpdateServiceRequest(vin: $vin, serviceRequestId: $serviceRequestId) { __typename status } }"


DATA_WIPE_OPERATION_ID = "e3b3899dabe68c81622e3523344c8471860512ed04bd6fe7740b5ea87924077b"
DATA_WIPE = "mutation DataWipe($vin: String!, $dataWipeType: DataWipeTypeEnum) { dataWipe(vin: $vin, dataWipeType: $dataWipeType) { __typename serviceRequestId } }"


SET_NOTIFICATION_PREFERENCES_OPERATION_ID = (
    "133118b0043f24f7c30a86405d4d1bec6e9a63cba529c2b4205270a93f4dfe50"
)
SET_NOTIFICATION_PREFERENCES = "mutation SetNotificationPreferences($vin: String!, $preferences: [NotificationOptInInput]!) { setNotificationPreferences(vin: $vin, preferences: $preferences) { __typename notificationPreferences { __typename notificationCategory notificationType { __typename destination optIn } } } }"


REGISTER_PUSH_NOTIFICATIONS_OPERATION_ID = (
    "6aaa0d8920366e92e51c51adc4b64a107ca2dfb8f52c56a1e39724b74e86ad34"
)
REGISTER_PUSH_NOTIFICATIONS = "mutation RegisterPushNotifications($deviceId: String!, $token: String!, $deviceOS: DeviceOS!) { registerNotifications(deviceId: $deviceId, token: $token, deviceOS: $deviceOS) }"


UNREGISTER_PUSH_NOTIFICATIONS_OPERATION_ID = (
    "a80b792afc2fe0b86748f76f37e0453b0b58a38c933e292452d3b142fc3aef03"
)
UNREGISTER_PUSH_NOTIFICATIONS = "mutation UnregisterPushNotifications($deviceId: String!, $deviceOS: DeviceOS!) { unregisterNotifications(deviceId: $deviceId, deviceOS: $deviceOS) }"


REGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS_OPERATION_ID = (
    "7c8d849d68906dc3a437ecc7921524482fc33f24b2036ea9c814b4e41e24025d"
)
REGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS = "mutation RegisterDeviceForPushNotifications($mobileInfoInput: MobileInfoInput!) { registerDeviceForPushNotifications(mobileInfoInput: $mobileInfoInput) { __typename ... on GeneralMessage { message } ... on DatabaseError { errorMessage } ... on TokenError { errorMessage } } }"


UNREGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS_OPERATION_ID = (
    "404eb84bb076aa09b4c4fe1e734d33ea4f4333886e8f2cae88905e5735ca0d20"
)
UNREGISTER_DEVICE_FOR_PUSH_NOTIFICATIONS = "mutation UnregisterDeviceForPushNotifications($appName: String!, $deviceId: String!, $deviceType: String!) { unregisterDeviceForPushNotifications(appName: $appName, deviceType: $deviceType, deviceId: $deviceId) { __typename ... on GeneralMessage { message } ... on DatabaseError { errorMessage } ... on TokenError { errorMessage } } }"


IN_VEHICLE_MESSAGES_OPERATION_ID = (
    "8ed19a840ad694696ad12c88f088e3490a84de22c4559955595fbe860f47331b"
)
IN_VEHICLE_MESSAGES = "query InVehicleMessages($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { inVehicleMessages { __typename campaignId createdDateTime title viewed } } } }"


IN_VEHICLE_MESSAGE_OPERATION_ID = "38bc6249c0ae07c288e8b332739c5729f2da0a76c67c1f2f7e209d718dab949b"
IN_VEHICLE_MESSAGE = "query InVehicleMessage($vin: String!, $campaignId: String!, $push: Boolean) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { inVehicleMessage(campaignId: $campaignId, push: $push) { __typename title campaignId viewed text expireDate } } } }"


NISSAN_ENERGY_NOTIFICATION_PREFERENCES_OPERATION_ID = (
    "fbee78c4bc150c323d5b26f9128735057144ef767047c71da6cbd4214362c8dc"
)
NISSAN_ENERGY_NOTIFICATION_PREFERENCES = "query NissanEnergyNotificationPreferences($vin: String!) { accountStatus(vin: $vin) { __typename data { __typename notificationPreferences { __typename emailStatus pushStatus smsStatus } } } }"


UPDATE_NISSAN_ENERGY_NOTIFICATION_PREFERENCES_OPERATION_ID = (
    "7c3e8c1d776c4f17e5e09ed9b2c9b90a9e6d10af5b013aade8c71e55a40eb95c"
)
UPDATE_NISSAN_ENERGY_NOTIFICATION_PREFERENCES = "mutation UpdateNotificationPreferences($config: EmpUpdateNotificationPreferencesInput!) { updateNotificationPreferences(config: $config) { __typename statusCode statusMessage timestamp data { __typename emailStatus pushStatus smsStatus } } }"


DRIVING_HISTORY_OPERATION_ID = "26c4b7fdbfd868b440d1bcf15e6ad2d68196a1648a4c566139ac81921124e456"
DRIVING_HISTORY = "query DrivingHistory($vin: String!, $aggregator: DrivingHistoryAggregator!, $distanceUnit: DistanceUnit, $weightUnit: WeightUnit, $speedUnit: SpeedUnit) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { drivingHistory(aggregator: $aggregator) { __typename tripSummaries { __typename userId day month year numberOfTrips distanceTraveled(unit: $distanceUnit) { __typename unit value } duration averageSpeed(unit: $speedUnit) { __typename type value } energyConsumed co2Saved(unit: $weightUnit) { __typename unit value } } trips { __typename distance(unit: $distanceUnit) { __typename unit value } startDate endDate duration startLocation { __typename latitude longitude } endLocation { __typename latitude longitude } averageSpeed(unit: $speedUnit) { __typename type value } energyConsumed energySaved co2Saved(unit: $weightUnit) { __typename unit value } userId } } } } }"


EV_CHARGE_STATIONS_OPERATION_ID = "761aaf8adf94f10cb9eacf5c87169d8e109cbcf1d715689e17e529f9091eeb7e"
EV_CHARGE_STATIONS = "query EVChargeStations($vin: String!, $coordinate: CoordinateInput!, $plugConnectorTypes: [PlugConnectorType], $enableWithinRangeRestriction: Boolean) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { evChargeStations(coordinate: $coordinate, plugConnectorTypes: $plugConnectorTypes, enableWithinRangeRestriction: $enableWithinRangeRestriction) { __typename id name phoneNumber address { __typename address1 address2 city country postalCode state } location { __typename latitude longitude } connectors { __typename plugConnectorType ratedPowerKW voltageV currentA currentType } } } } }"


E_VEHICLE_ELIGIBILITY_OPERATION_ID = (
    "a12f2643531bfdea27456ca7518b22ae7fd231069095175eded3aecd86831a6c"
)
E_VEHICLE_ELIGIBILITY = "query eVehicleEligibility($vin: String!) { eVehicleEligibility(vin: $vin) { __typename statusCode statusMessage timestamp data { __typename vin v1GEligible } } }"


LAST_KNOWN_CAMERA_USAGE_COUNTER_OPERATION_ID = (
    "2e05c5ab9633f9bc7530b24d16c892b1ec7599df22360cc1750fd14c97a7fa60"
)
LAST_KNOWN_CAMERA_USAGE_COUNTER = "query LastKnownCameraUsageCounter($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { lastKnownCameraUsageCounter { __typename counter lastUpdateTime } } } }"


LOCATION_DETAILS_OPERATION_ID = "28ecd05ac2ca0c18a3b1e56d3a457dbef94c218e9c1ddd73908e1ccdc7c0cd7e"
LOCATION_DETAILS = "query LocationDetails($vin: String!, $latitude: String!, $longitude: String!, $inNetworkOnly: Boolean!, $range: Int!, $operatorName: [String], $evse: EmpEvseStatusInput, $plugType: [String], $chargeLevel: EmpCnctrLvlInput, $pncStationsOnly: Boolean) { locationDetails(vin: $vin, latitude: $latitude, longitude: $longitude, inNetworkOnly: $inNetworkOnly, range: $range, operatorName: $operatorName, evse: $evse, plugType: $plugType, chargeLevel: $chargeLevel, pncStationsOnly: $pncStationsOnly) { __typename statusCode statusMessage timestamp data { __typename locationId locationType locationName locationLogo locationOperatorName locationSubOperatorName locationAddress locationCity locationState locationCountry locationPostalCode locationTwentyfourseven locationOpeningTimings { __typename weekday periodBegin periodEnd } locationInNetwork phone locationCoordinates { __typename latitude longitude } evses { __typename evseId evseLocationId evseStatus evseCapability evsePhysicalReference connector { __typename connectorId connectorType connectorPowerRating connectorDescription } } } } }"


PARKING_CHARGEABLE_OPERATION_ID = "5843ee747a507576e3cf2ecce601c61066ad91d411da66935ca020492064df00"
PARKING_CHARGEABLE = "query ParkingChargeable($evseId: String!) { parkingChargeable(evseId: $evseId) { __typename statusCode statusMessage timestamp data { __typename evseId isParkingChargeable isCongestionChargeable } } }"


SHAREABLE_CAPABILITIES_OPERATION_ID = (
    "17675343f100b0f2a94df2661bd13cd52f168d44ca50e80f84c3fa1bb63f15cf"
)
SHAREABLE_CAPABILITIES = "query ShareableCapabilities($vin: String!, $driverId: ID) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { shareableCapabilities(driverId: $driverId) { __typename group { __typename id name shared capabilities { __typename id name shareable } } } } } }"


TARIFF_PRICING_OPERATION_ID = "3cdfc57f13baa238fb2a6af6c89948f16d4d4899b308c281c541957e8b02af10"
TARIFF_PRICING = "query TariffPricing($vin: String!, $locationId: String!) { tariffPricing(vin: $vin, locationId: $locationId) { __typename statusCode statusMessage timestamp data { __typename locationId maxChargeLimit tariffDetails { __typename connectorType connectorPower sessionFee tariffAltText { __typename en fr } idleFees { __typename gracePeriod idleFeesTier { __typename congestionLevel timeStart timeEnd durationStart durationEnd durationUnit price unit } } congestionFees { __typename gracePeriod congestionTier { __typename congestionLevel vehicleSOCLimit price unit } } energyFees { __typename energyFeeTier { __typename applicableDay timeStart timeEnd durationStart durationEnd durationUnit minRange maxRange rangeUnit price unit } } } } } }"


PNC_SERVICE_STATUS_OPERATION_ID = "ee2a533d091d7d67779c214e32ca8e6a761cfc4d745ec20fc36fbda7ba8c2f6d"
PNC_SERVICE_STATUS = "query PNCServiceStatus($vin: String!) { pncServiceStatus(vin: $vin) { __typename statusCode statusMessage timestamp data { __typename vin pncServiceStatus } } }"


START_CHARGE_SESSION_OPERATION_ID = (
    "8ffca8e8b6245d915b6af71948650b9b287ee0d5b8a908aeecdb8a2644db874a"
)
START_CHARGE_SESSION = "mutation StartChargeSession($config: EmpStartChargeSessionInput!) { startChargeSession(config: $config) { __typename statusCode statusMessage timestamp data { __typename vin evseId status message stopSessionAllowed } } }"


STOP_CHARGE_SESSION_OPERATION_ID = (
    "48cb129cae3efd9063f650490a4913d7050a6c907220ca39af934db34c3fe6eb"
)
STOP_CHARGE_SESSION = "mutation StopChargeSession($config: EmpStopChargeSessionInput!) { stopChargeSession(config: $config) { __typename statusCode statusMessage timestamp } }"


UPDATE_PNC_SERVICE_STATUS_OPERATION_ID = (
    "0ec4a5cd4c85ed1629ad4b3b543cad3410ff78da13cc072564a45cbebd05a5ec"
)
UPDATE_PNC_SERVICE_STATUS = "mutation UpdatePnCServiceStatus($config: EmpUpdatePnCServiceStatusInput!) { updatePnCServiceStatus(config: $config) { __typename statusCode statusMessage timestamp data { __typename vin pncServiceStatus } } }"


RETRY_CERT_INSTALL_OPERATION_ID = "953831afa852a33defdd3b8d9d1ab8f9c41599af086a6b4fdffb1662dfe08311"
RETRY_CERT_INSTALL = "mutation RetryCertInstall($config: EmpRetryCertInstallInput!) { retryCertInstall(config: $config) { __typename statusCode } }"


CHARGE_SESSION_STATUS_OPERATION_ID = (
    "c6a8b2da031357b36bac7d4a1009d038b3cb09c453dabc78bd8c49e6fd9c90b3"
)
CHARGE_SESSION_STATUS = "query ChargeSessionStatus($vin: String!) { sessionStatus(vin: $vin) { __typename statusCode statusMessage timestamp data { __typename sessionUid status message stopSessionAllowed cpoName physicalReference locationAddress locationCity locationState locationCoordinates { __typename latitude longitude } } } }"


VEHICLE_PREFERRED_DEALER_OPERATION_ID = (
    "bb40f9d98af9c0eba297b137a80e1435994aad62db5b3dea216905ecdb035c80"
)
VEHICLE_PREFERRED_DEALER = "query VehiclePreferredDealer($vin: String!) { vehicle(vin: $vin) { __typename preferredDealer { __typename id hashId name address { __typename address1 address2 city state postalCode country } hours phone servicePhone nativeServiceBooking schedulingUrlMobile location { __typename latitude longitude } languagesSpoken } } }"


VEHICLE_RECALLS_OPERATION_ID = "c512fdca23733b4c186e6795da768d26e2889c33fea9b359f37df4cf8cb37f4e"
VEHICLE_RECALLS = "query VehicleRecalls($vin: String!) { vehicle(vin: $vin) { __typename recalls { __typename effectiveDate nhtsaId primaryDescription remedyDescription riskDescription title type recallCode } } }"


VEHICLE_ROADSIDE_ASSISTANCE_OPERATION_ID = (
    "a8c4809aa3dd2d3d9bb79128141c8514502c06de6fa921d35f472b81f3fee71e"
)
VEHICLE_ROADSIDE_ASSISTANCE = "query VehicleRoadsideAssistance($vin: String!) { vehicle(vin: $vin) { __typename roadsideAssistance { __typename roadsideMonths roadsideMiles towingMonths towingMiles } } }"


VEHICLE_SERVICE_HISTORY_OPERATION_ID = (
    "5c86fd1c4ce70d026aa0674961587bd1787abae161fd395eebd40ea5696d7e29"
)
VEHICLE_SERVICE_HISTORY = "query VehicleServiceHistory($vin: String!, $unit: DistanceUnit) { vehicle(vin: $vin) { __typename serviceHistory { __typename mileageWithUnit(unit: $unit) { __typename unit value } serviceDate dealerName dealerCode services comment maintenanceId serviceOperation { __typename serviceCategoryId serviceCategoryName opCodeID opCodeDescription } } } }"


WARRANTY_INFO_OPERATION_ID = "da1a623c50e2ab26a8921737b2fd64596de2605245ec3dd327f71d3acba5c47b"
WARRANTY_INFO = "query WarrantyInfo($vin: String!, $mileage: Int) { vehicle(vin: $vin) { __typename warranty(mileage: $mileage) { __typename warrantyInfo { __typename colorStatus warrantyStatus totalMileage totalMonths } startPeriod { __typename mileage date } endPeriod { __typename mileage date } currentPeriod { __typename mileage date } } } }"


CHARGE_PRODUCT_OPERATION_ID = "055e99eb614998373b5af75e4ac65a6c280e299ddd64c62ddba0a71b463ad8e4"
CHARGE_PRODUCT = "query ChargeProduct($vin: String!) { chargeProduct(vin: $vin) { __typename statusCode statusMessage timestamp data { __typename productSKU price description } } }"


PRICING_DETAILS_OPERATION_ID = "7e3c077680f18e8d7e393b2946a7dd3696d6eae551c58415a5429f095a7f0882"
PRICING_DETAILS = "query PricingDetails($locationId: String!, $vin: String!) { pricingDetails(locationId: $locationId, vin: $vin) { __typename data { __typename parkingTariff flatFee congestionFee evses { __typename connectors { __typename connectorId tariff } } } } }"


ENROLL_CHARGE_PLAN_OPERATION_ID = "c0f279e485d0439d8a75bfae53b99044cd092edbd05db3fa7c6953e302fe9338"
ENROLL_CHARGE_PLAN = "mutation EnrollChargePlan($config: EmpEnrollChargePlanInput!) { enrollChargePlan(config: $config) { __typename statusCode statusMessage timestamp data { __typename vin status } } }"


CANCEL_CHARGE_PLAN_OPERATION_ID = "f5b298864d03dd13a383961455c2f0e7625eed3fac59b697c8207a1c131d0126"
CANCEL_CHARGE_PLAN = "mutation CancelChargePlan($config: EmpCancelChargePlanInput!) { cancelChargePlan(config: $config) { __typename statusCode statusMessage timestamp } }"


WEARABLE_VEHICLES_OPERATION_ID = "ba7b89a00f05ce82ede35558ebf0464d3f22cd2c9b0b5559a4a2f587a9b843db"
WEARABLE_VEHICLES = "query WearableVehicles { vehicles { __typename vin nickname image year model driverType capabilities { __typename telematicsProgram status serviceCapability { __typename type enabled subscribed } } } }"


V1G_MONITORED_CHARGING_ACCOUNT_STATUS_OPERATION_ID = (
    "63fe4573ce90476a520432a5390392ef33dafa9c057a4cb2c3768151e9400ffc"
)
V1G_MONITORED_CHARGING_ACCOUNT_STATUS = "query V1GMonitoredChargingAccountStatus($vin: String!) { v1GMonitoredChargingAccountStatus(vin: $vin) { __typename statusCode data { __typename v1GMonitoredChargingAccountStatus v1GNotificationPreferences { __typename v1GNotificationCategory v1GEmailStatus v1GPushStatus v1GSmsStatus } vin } } }"


V1G_UPDATE_NOTIFICATION_PREFERENCES_OPERATION_ID = (
    "ed2bc5680bfdd855e6937d5a20d2dfa65f5a30334a6b58bb4b58022873f9a923"
)
V1G_UPDATE_NOTIFICATION_PREFERENCES = "mutation V1GUpdateNotificationPreferences($config: V1GUpdateNotificationPreferencesInput!) { v1GUpdateNotificationPreferences(config: $config) { __typename statusCode statusMessage timestamp v1GNotificationPreferences { __typename v1GNotificationCategory v1GEmailStatus v1GPushStatus v1GSmsStatus } } }"


V1G_TOKENIZED_URL_OPERATION_ID = "73efdb614f50e45ada4d6fa3a9c6e4a132158105c9b8925e5639db596872db05"
V1G_TOKENIZED_URL = "query V1GTokenizedUrl($vin: String!) { v1GTokenizedUrl(vin: $vin) { __typename data { __typename url vin } } }"


V1G_ENROLL_MONITORED_CHARGING_PLAN_OPERATION_ID = (
    "08220397d2eef0c6b869383b0ffe39d0e1f5c54f90b9057e68fb372ef87ee7b5"
)
V1G_ENROLL_MONITORED_CHARGING_PLAN = "mutation V1GEnrollMonitoredChargingPlan($config: V1GEnrollMonitoredChargingPlanInput!) { v1GEnrollMonitoredChargingPlan(config: $config) { __typename data { __typename v1GMonitoredChargingAccountStatus } } }"


V1G_CANCEL_MONITORED_CHARGING_PLAN_OPERATION_ID = (
    "08753ed869beca2914e8b6507bccf673ab6f97b1c099bfb3aee42615fe484b97"
)
V1G_CANCEL_MONITORED_CHARGING_PLAN = "mutation V1GCancelMonitoredChargingPlan($config: V1GCancelMonitoredChargingPlanInput!) { v1GCancelMonitoredChargingPlan(config: $config) { __typename statusCode } }"


ACCOUNT_STATUS_OPERATION_ID = "fa9270fd8f34b96477a72ee8b6f0207707e2173d34cc45b25fe5049db85a6def"
ACCOUNT_STATUS = "query AccountStatus($vin: String!) { accountStatus(vin: $vin) { __typename statusCode statusMessage timestamp data { __typename status statusReason pncStatus pncStatusReason toggleStatus nacsStatus connectors { __typename id connectorName } } } }"


EMERGENCY_CONTACTS_OPERATION_ID = "2348fc6a620766d6de79b378e41b4dd0c96f7cf293406425bb2473822eef7150"
EMERGENCY_CONTACTS = "query EmergencyContacts($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { emergencyContacts { __typename id firstName lastName primaryPhone secondaryPhone relationship } } } }"


CREATE_EMERGENCY_CONTACT_OPERATION_ID = (
    "2e893b1d3fbebe34da08ca5656764b761e2fda821a61d7e7668cf30d4deb8696"
)
CREATE_EMERGENCY_CONTACT = "mutation CreateEmergencyContact($vin: String!, $contact: CreateEmergencyContact!) { createEmergencyContact(vin: $vin, contact: $contact) { __typename ... on ResponseStatus { success } } }"


UPDATE_EMERGENCY_CONTACT_OPERATION_ID = (
    "6febe7ad2d032ea40ad0cd62a566a251ca9ff44fcda99160d1a0e4234b465448"
)
UPDATE_EMERGENCY_CONTACT = "mutation UpdateEmergencyContact($vin: String!, $contact: UpdateEmergencyContact!) { updateEmergencyContact(vin: $vin, contact: $contact) { __typename success } }"


DELETE_EMERGENCY_CONTACT_OPERATION_ID = (
    "8d4b23fabc22621f8a33e4f077b72f6f43f533bea3eb377fc24b5fcaf76b3e89"
)
DELETE_EMERGENCY_CONTACT = "mutation DeleteEmergencyContact($vin: String!, $emergencyContactId: String!) { deleteEmergencyContact(vin: $vin, emergencyContactId: $emergencyContactId) { __typename success } }"


DRIVER_INVITES_OPERATION_ID = "8b2bdc815ae1749b82ffdd3ff4551d4baf17c3fcc9d83cc0b36b3ac99d9b1348"
DRIVER_INVITES = "query DriverInvites($vin: String!) { driverInvites(vin: $vin) { __typename ... on DriverInvitesSuccessResponse { invites { __typename inviteId driverFirstName driverLastName driverEmail driverPhoneNumber inviteDateTime inviteExpiryDateTime inviteType notificationsToPrimary usageHistory status cdiid } } ... on GeneralErrors { errorMessage } ... on DatabaseError { errorMessage } ... on BrandError { errorMessage } ... on TokenError { errorMessage } ... on VinValidationError { errorMessage } } }"


INVITE_DRIVER_OPERATION_ID = "821d71afcb939415ab92744e14832a6b69f6fbc5965335843330546d7d05aeee"
INVITE_DRIVER = "mutation InviteDriver($config: DriverInviteInput) { inviteDriver(config: $config) { __typename ... on InviteDriverSuccessResponse { vin inviteId driverFirstName driverLastName driverEmail driverPhoneNumber entitlements inviteType usageHistory notificationsToPrimary inviteDateTime status } ... on FirstNameValidationError { errorMessage } ... on LastNameValidationError { errorMessage } ... on EmailValidationError { errorMessage } ... on PhoneValidationError { errorMessage } ... on ExistingInviteError { errorMessage } ... on MaxInvitesReachedError { errorMessage } } }"


DRIVER_INVITE_ACTION_OPERATION_ID = (
    "55a68a9eb65b98ec618027939b427cb86c8a9304d1c36f999d0a36397c80bdfb"
)
DRIVER_INVITE_ACTION = "mutation DriverInviteAction($config: DriverInviteActionInput) { driverInviteAction(config: $config) { __typename ... on DriverInviteActionSuccessResponse { success } ... on GeneralErrors { errorMessage } ... on DatabaseError { errorMessage } ... on InvalidInviteIdError { errorMessage } ... on TokenError { errorMessage } ... on BrandError { errorMessage } ... on TermsAndConditionsError { errorMessage } ... on CountryError { errorMessage } } }"


DELETE_DRIVER_OPERATION_ID = "0468e9b1a759fd8442e8946634aeb9199cbbd7f64a08b30715934c4afec32684"
DELETE_DRIVER = "mutation DeleteDriver($inviteId: ID!) { deleteDriver(inviteId: $inviteId) { __typename ... on DeleteDriverSuccessResponse { success } } }"


UPDATE_DRIVER_OPERATION_ID = "f6621737f3be3e2cc72df04d2ee05c50ded481cf6b2878a60ea4a27d8f2eaf26"
UPDATE_DRIVER = "mutation UpdateDriver($config: UpdateDriverInput!) { updateDriver(config: $config) { __typename ... on UpdateDriverSuccessResponse { entitlements usageHistory notificationsToPrimary success } } }"


OWNER_INVITE_ACTION_OPERATION_ID = (
    "3101dd28c49a6741bfb90a9f10b4899a0fba0d38e2e0bc3bc825e39355065319"
)
OWNER_INVITE_ACTION = "mutation OwnerInviteAction($config: OwnerInviteActionInput) { ownerInviteAction(config: $config) { __typename ... on OwnerInviteActionSuccessResponse { success } } }"


CREATE_RSA_LINK_OPERATION_ID = "c51946c709ec79f3284218ef67a01a8ddd2afe73b3c0f5a5e8aa3bff1d9fdefd"
CREATE_RSA_LINK = (
    "mutation CreateRSALink($vin: String!) { createRSALink(vin: $vin) { __typename link } }"
)


ADD_VEHICLE_OPERATION_ID = "8e3e8b7d9f3d09f3f1e066bd098d4e2bab5dcf60d1e18b428d3fabaa1942a6cd"
ADD_VEHICLE = "mutation AddVehicle($vin: String!, $termsAndConditionsAccepted: Boolean!) { addVehicle(vin: $vin, termsAndConditionsAccepted: $termsAndConditionsAccepted) { __typename ... on AddVehicleSuccessResponse { vin } ... on RegisterGeneralError { message } ... on RequireOwnershipVerification { message } ... on RegisterCorporateVehicleEmailSentToPrimaryOwnerError { message } ... on RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError { message } ... on VINAlreadyExistsInAnotherGarageError { message } } }"


DELETE_VEHICLE_OPERATION_ID = "87fb1fb425f9de2ed5ff7a3b2e8b344a852c81c52c7d5bb0069b20cbd07d5b03"
DELETE_VEHICLE = "mutation DeleteVehicle($vin: String!) { deleteVehicle(vin: $vin) { __typename ... on DeleteVehicleSuccessResponse { vin } ... on DeleteVehicleError { message } } }"


NCAR_ICAR_ADD_VEHICLE_OPERATION_ID = (
    "680ade9370bb6bcf84236ef057bc551a04a73bb2404f1c45ed80956ad1763dd7"
)
NCAR_ICAR_ADD_VEHICLE = "mutation NcarIcarAddVehicle($termsAndConditionsAccepted: Boolean!, $guid: ID!, $account: NCARICARRegisterAccountInput) { ncarIcarAddVehicle(termsAndConditionsAccepted: $termsAndConditionsAccepted, guid: $guid, account: $account) { __typename ... on AddVehicleSuccessResponse { vin } ... on RegisterGeneralError { message } ... on RequireOwnershipVerification { message } } }"


PENDING_VEHICLES_OPERATION_ID = "e41202c3f1905f5ee4e93b9760b88c9e0e574d60ff553af4fb4bd918e2e58f25"
PENDING_VEHICLES = "query PendingVehicles { pendingVehicles { __typename vin caseStatus model caseId caseNumber year } }"


OWNERSHIP_STATUS_OPERATION_ID = "e841a9a8511c8d15ba667342f54fea02d641c52ba2a2d0a84f59632e56c92cf5"
OWNERSHIP_STATUS = "query OwnershipStatus($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { ownershipStatus { __typename isSignedIn } } } }"


APC_AGREEMENT_OPERATION_ID = "a7c864aa4a081f2b9be359d0b2b7ada83a81aaed4a17f4457fab9aea4b5498e1"
APC_AGREEMENT = "query APCAgreement($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { apcAgreement { __typename optIn } } } }"


APC_DOCUMENT_URL_OPERATION_ID = "87b4cffe7e8643276ca40278b13f56e7b19897e89a9a5e218addfde059703eb6"
APC_DOCUMENT_URL = "query APCDocumentURL($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { apcAgreement { __typename documentURL } } } }"


CREATE_APC_AGREEMENT_OPERATION_ID = (
    "2c0547cdfff32989e778bd9ce306f7ac601d54a160381834fca53a461209af4e"
)
CREATE_APC_AGREEMENT = "mutation CreateAPCAgreement($optIn: Boolean!, $vin: String!) { createAPCAgreement(optIn: $optIn, vin: $vin) { __typename success } }"


UPDATE_APC_AGREEMENT_OPERATION_ID = (
    "56fda3769c97c60791097c2b8ec66b05546e484b90a05af669b860dea395d9c9"
)
UPDATE_APC_AGREEMENT = "mutation UpdateAPCAgreement($optIn: Boolean!, $vin: String!) { updateAPCAgreement(optIn: $optIn, vin: $vin) { __typename success } }"


CONNECTED_TERMS_AND_CONDITIONS_BY_VIN_OPERATION_ID = (
    "c7cdfd6ecef4324694ea635ec6a83ff15292a27568b2fc606f672a00cbccbba8"
)
CONNECTED_TERMS_AND_CONDITIONS_BY_VIN = "mutation ConnectedTermsAndConditionsByVIN($vin: String!) { connectedTermsAndConditionsByVIN(vin: $vin) { __typename ... on TermsAndConditionsResponse { title body url } ... on InvalidVINError { message } ... on NonConnectedVehicleResponse { message } ... on ValidVINResponse { message } } }"


ONBOARDING_FEATURES_OPERATION_ID = (
    "66dc0a058684d51cb7c6cc734c003157162bb37105ad18c7197ba88adadbee4c"
)
ONBOARDING_FEATURES = "query OnboardingFeatures($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseVehicle { onboardingFeatures { __typename position title body imageType } } } }"


UPDATE_VEHICLE_OPERATION_ID = "bc1b19df9f02d4514da0f79f94862311e1f87a37e7090ddb78f8acf16f1bea7e"
UPDATE_VEHICLE = "mutation UpdateVehicle($vin: String!, $licensePlate: String, $hologram: VehicleHologramEnum) { updateVehicle(vin: $vin, licensePlate: $licensePlate, hologram: $hologram) { __typename ... on UpdateVehicleSuccessResponse { licensePlate hologram } ... on UpdateVehicleInvalidLicensePlateError { message } ... on UpdateVehicleHologramInvalidLengthError { message } ... on InvalidVINError { message } ... on VINNotFoundError { message } ... on UpdateVehicleGeneralError { message } } }"


UPDATE_VEHICLE_MANUAL_MILEAGE_OPERATION_ID = (
    "946be7d04047ebd791fd61c7d6a944680ef157535dd04cdd54e285b66206200e"
)
UPDATE_VEHICLE_MANUAL_MILEAGE = "mutation UpdateVehicleManualMileage($vin: String!, $manualMileage: Int) { updateVehicle(vin: $vin, manualMileage: $manualMileage) { __typename ... on UpdateVehicleSuccessResponse { manualMileage } ... on UpdateVehicleInvalidMileageError { message } ... on InvalidVINError { message } ... on VINNotFoundError { message } ... on UpdateVehicleGeneralError { message } } }"


UPDATE_VEHICLE_NICKNAME_OPERATION_ID = (
    "fe0369641faf07713aada842d81e9a1247b8785e469b2c945e45a3a6647e876c"
)
UPDATE_VEHICLE_NICKNAME = "mutation UpdateVehicleNickname($vin: String!, $nickname: String!) { updateVehicle(vin: $vin, nickname: $nickname) { __typename ... on UpdateVehicleSuccessResponse { nickname } ... on UpdateVehicleNicknameMalformedError { message } ... on InvalidVINError { message } ... on VINNotFoundError { message } ... on UpdateVehicleGeneralError { message } } }"


UPLOAD_OWNERSHIP_VERIFICATION_OPERATION_ID = (
    "1791a844ea55c19e2758c08fd2f7860dce6a82f7b0928553f1c960c43db422e4"
)
UPLOAD_OWNERSHIP_VERIFICATION = "mutation UploadOwnershipVerification($vin: String!, $filename: String!, $attachment: String!, $optInSMS: Boolean!) { uploadOwnershipVerification(vin: $vin, filename: $filename, attachment: $attachment, optInSMS: $optInSMS) { __typename ... on UploadOwnershipVerificationSuccess { caseNumber } ... on RegisterGeneralError { message } } }"


GET_MAINTENANCE_TIMELINE_OPERATION_ID = (
    "6bad114fbfd471b87bd47b5648b5f0637a93d0c23bd2eb6d274a39550dcf32d8"
)
GET_MAINTENANCE_TIMELINE = "query GetMaintenanceTimeline($vin: String!, $mileageUnit: DistanceUnit!) { vehicle(vin: $vin) { __typename maintenanceTimeline(mileageUnit: $mileageUnit) { __typename lastServiceDate lastServiceMileage nextServiceDate nextServiceMileage remainingServiceMileage remainingServiceMonths mileageUnit currentMileage } } }"


GET_SERVICE_CONTRACTS_OPERATION_ID = (
    "e962736c9aae011b2a36e6e58389149f31918e7857ce18600764875de90119ed"
)
GET_SERVICE_CONTRACTS = "query GetServiceContracts($vin: String!, $mileage: Int!) { vehicle(vin: $vin) { __typename warranty(mileage: $mileage) { __typename serviceContracts { __typename status coverage coverageDescription coverageName planEffectiveDate planEffectiveMiles planExpirationDate planExpirationOdometer planCancelledDate planCancelledOdometer agreement deductibleAmount expiringSoon } } } }"


ADD_PAST_SERVICE_OPERATION_ID = "cafadb5455f97421a20e39cd512e4f6d330571bec51ead159d4475b4dcd232f4"
ADD_PAST_SERVICE = "mutation AddPastService($input: PastServiceInput) { addPastService(input: $input) { __typename ... on PastServiceSuccess { success } ... on RegisterGeneralError { message } ... on PastServiceExists { message } } }"


UPDATE_PAST_SERVICE_OPERATION_ID = (
    "fa9c97a384127dffe11abb854538bfa76f8d21420c043c4414a2fef348586b7b"
)
UPDATE_PAST_SERVICE = "mutation UpdatePastService($input: UpdatePastServiceInput!) { updatePastService(input: $input) { __typename ... on PastServiceSuccess { success } ... on RegisterGeneralError { message } ... on PastServiceExists { message } } }"


PARTS_REMINDERS_OPERATION_ID = "4b5fb536d6007cd8c5f17a64a93dc6511ae69954c522f211ca4d42a69b0aeb7b"
PARTS_REMINDERS = "query PartsReminders($vin: String!, $unit: DistanceUnit) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { parts { __typename ...PartFields } partsReminders { __typename id overdue date monthsInterval distanceInterval { __typename ...DistanceFields } nextReminderDistance { __typename ...DistanceFields } nextReminderDate status parts { __typename ...PartFields } mileage(unit: $unit) { __typename unit value } } } } }  fragment ConfigurationThresholds on PartsReminderConfigurationThresholds { __typename min max interval distanceUnit }  fragment ReminderConfigurations on PartReminderConfiguration { __typename months { __typename ...ConfigurationThresholds } distance { __typename ...ConfigurationThresholds } }  fragment PartFields on Part { __typename id name reminderConfiguration { __typename ...ReminderConfigurations } }  fragment DistanceFields on Distance { __typename unit value }"


CREATE_PARTS_REMINDER_OPERATION_ID = (
    "488ccc2a7e7a0af3112ab1a91ce224e2c83f7dbcdcf824df99049fdf0ab607f4"
)
CREATE_PARTS_REMINDER = "mutation CreatePartsReminder($vin: String!, $reminder: CreatePartsReminderInput!) { createPartsReminder(vin: $vin, reminder: $reminder) { __typename success } }"


UPDATE_PARTS_REMINDER_OPERATION_ID = (
    "08531ffe6e151b3bf7c8b6f33d04ca3408232f0c83bc743948e9dda9b2efd5ce"
)
UPDATE_PARTS_REMINDER = "mutation UpdatePartsReminder($vin: String!, $reminder: UpdatePartsReminderInput!) { updatePartsReminder(vin: $vin, reminder: $reminder) { __typename ... on ResponseStatus { success } } }"


RESET_PARTS_REMINDER_OPERATION_ID = (
    "2e015a323d69646298637c701cc5fb6842dfdb9e295ac18a6b93b68d9b582ea5"
)
RESET_PARTS_REMINDER = "mutation ResetPartsReminder($vin: String!, $reminder: ResetPartsReminderInput!) { resetPartsReminder(vin: $vin, reminder: $reminder) { __typename ... on ResponseStatus { success } } }"


DELETE_PARTS_REMINDER_OPERATION_ID = (
    "237b3f40451ba30e043a8b0b1dccd679bfd389924c16e1026c15ebdf10542b77"
)
DELETE_PARTS_REMINDER = "mutation DeletePartsReminder($vin: String!, $reminderId: String!) { deletePartsReminder(vin: $vin, reminderId: $reminderId) { __typename ... on ResponseStatus { success } } }"


COLLISION_HISTORY_OPERATION_ID = "ca2779551c7312455dbe80dce6dac3199494f71a1010f53bc211616ce8776622"
COLLISION_HISTORY = "query CollisionHistory($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseVehicle { collisionHistory { __typename collisionId reportDateTime collisionDateTime } } } }"


COLLISION_PROBE_DATA_OPERATION_ID = (
    "f151d6ce54b3bc683412838ff8ce6460e06874e61a671da481d7d6238723c547"
)
COLLISION_PROBE_DATA = "query CollisionProbeData($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVK2Vehicle { collisionProbeReadings { __typename collisionTime latitude longitude milCount milData odometer speed unit } } } }"


VEHICLE_BATTERY_STATUS_OPERATION_ID = (
    "d157b289331668ddf5f7eecaf93efe73a95f12794d424f5bb3edbbcc1536defc"
)
VEHICLE_BATTERY_STATUS = "query VehicleBatteryStatus($vin: String!, $unit: DistanceUnit) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { batteryStatus { __typename ...BatteryStatusDetails } } } }  fragment BatteryStatusDetails on BatteryStatus { __typename level isPluggedIn isCharging remainingChargeTime remainingMileage(unit: $unit) { __typename unit value } }"


VEHICLE_BOUNDARY_ALERTS_OPERATION_ID = (
    "1b39f2447a0b7f2b87172930d52884163821cba61390c1ed574f7091eb329590"
)
VEHICLE_BOUNDARY_ALERTS = "query VehicleBoundaryAlerts($vin: String!, $distanceUnit: DistanceUnit) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { boundaryAlerts { __typename ...BoundaryAlertDetails } } } }  fragment BoundaryAlertDetails on BoundaryAlert { __typename serviceRequestId alertType name enabled inVehicleWarning address { __typename address1 address2 city state country postalCode } location { __typename latitude longitude } radius(unit: $distanceUnit) { __typename value unit } }"


VEHICLE_CLIMATE_STATUS_OPERATION_ID = (
    "613bc1a2d4fe33cfbcfe05ceb0822fdec1e4b6b44d1c1835614ecff1dda05bbf"
)
VEHICLE_CLIMATE_STATUS = "query VehicleClimateStatus($vin: String!, $temperatureUnit: TemperatureUnitEnumType!) { vehicle(vin: $vin) { __typename ... on BaseElectricVehicle { climateStatus { __typename ...ClimateStatusDetails } } } }  fragment ClimateStatusDetails on ClimateStatus { __typename state temperature(unit: $temperatureUnit) { __typename value unit } }"


VEHICLE_CURFEW_ALERTS_OPERATION_ID = (
    "8c32c5e7976dc8f1f05c02dca78c1b2772b621a67b795f9dd54c1c9c85e6cefe"
)
VEHICLE_CURFEW_ALERTS = "query VehicleCurfewAlerts($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { curfewAlerts { __typename ...CurfewAlertDetails } } } }  fragment CurfewAlertDetails on CurfewAlert { __typename serviceRequestId name enabled inVehicleWarning schedule { __typename allDay startDateTime duration weekDays } }"


VEHICLE_DOORS_STATUS_OPERATION_ID = (
    "2615e0f31156f0c197c8cda7fbd5faf242b1be3ee2315323f554361de5ce710d"
)
VEHICLE_DOORS_STATUS = "query VehicleDoorsStatus($vin: String!) { vehicle(vin: $vin) { __typename ... on BaseAVKVehicle { doorsStatus { __typename ...DoorsStatusDetails } } } }  fragment DoorsStatusDetails on DoorsStatus { __typename lastUpdatedAt doorFrontLeft { __typename ajar window lock } doorFrontRight { __typename ajar window lock } doorRearLeft { __typename ajar window lock } doorRearRight { __typename ajar window lock } engineHood { __typename ajar } hatch { __typename ajar } sunroof { __typename ajar } trunk { __typename lock } overallLock { __typename lock } }"


VEHICLE_MODEL_YEAR_OPERATION_ID = "68caf946fc54a0decc35dd011ab528649823b17d89f60f83d47db0270c89c625"
VEHICLE_MODEL_YEAR = (
    "query VehicleModelYear($vin: String!) { vehicle(vin: $vin) { __typename model year } }"
)


VEHICLE_NICKNAME_OPERATION_ID = "548cbf9cb3accff338e62dc1b03f46e77daf056b13f5e7c71f3318f9bc188255"
VEHICLE_NICKNAME = (
    "query VehicleNickname($vin: String!) { vehicle(vin: $vin) { __typename nickname } }"
)


VEHICLE_SPEED_ALERTS_OPERATION_ID = (
    "3250f9f2c20de1e6635592a1e7e084db04f588930739d58f57b1f6a2557fc553"
)
VEHICLE_SPEED_ALERTS = "query VehicleSpeedAlerts($vin: String!, $speedUnit: SpeedUnit) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { speedAlerts(speedUnit: $speedUnit) { __typename ...SpeedAlertDetails } } } }  fragment SpeedAlertDetails on SpeedAlert { __typename serviceRequestId name enabled inVehicleWarning speedThreshold { __typename type value } }"


VEHICLE_STATUS_OPERATION_ID = "fcce613d98daca4c170d6293b45183422a145f9d4c0f6a124b01bdc5405f2407"
VEHICLE_STATUS = "query VehicleStatus($vin: String!, $unit: DistanceUnit) { vehicle(vin: $vin) { __typename ...DynamicVehicleDetails ...VehicleTirePressureAndMilsDetails } }  fragment DoorsStatusDetails on DoorsStatus { __typename lastUpdatedAt doorFrontLeft { __typename ajar window lock } doorFrontRight { __typename ajar window lock } doorRearLeft { __typename ajar window lock } doorRearRight { __typename ajar window lock } engineHood { __typename ajar } hatch { __typename ajar } sunroof { __typename ajar } trunk { __typename lock } overallLock { __typename lock } }  fragment DynamicVehicleDetails on BaseVehicle { __typename ... on BaseAVKVehicle { doorsStatus { __typename ...DoorsStatusDetails } fuelAutonomy(unit: $unit) { __typename lastUpdatedAt value unit } mileage(unit: $unit) { __typename total recordedTime unit } } }  fragment VehicleTirePressureAndMilsDetails on BaseVehicle { __typename ... on BaseAVKVehicle { tirePressure { __typename lastUpdatedAt flPressure frPressure rlPressure rrPressure flStatus frStatus rlStatus rrStatus } mils { __typename active detailedMessage type } } }"


VEHICLE_STATUS_AND_RECALLS_OPERATION_ID = (
    "1b52ab3c1b996e32f3908ae6f270f87a064516f16b94de07a9f0cc5002687f1e"
)
VEHICLE_STATUS_AND_RECALLS = "query VehicleStatusAndRecalls($vin: String!, $unit: DistanceUnit) { vehicle(vin: $vin) { __typename ...DynamicVehicleDetails ...VehicleTirePressureAndMilsDetails recalls { __typename type nhtsaId title effectiveDate primaryDescription remedyDescription riskDescription recallCode } } }  fragment DoorsStatusDetails on DoorsStatus { __typename lastUpdatedAt doorFrontLeft { __typename ajar window lock } doorFrontRight { __typename ajar window lock } doorRearLeft { __typename ajar window lock } doorRearRight { __typename ajar window lock } engineHood { __typename ajar } hatch { __typename ajar } sunroof { __typename ajar } trunk { __typename lock } overallLock { __typename lock } }  fragment DynamicVehicleDetails on BaseVehicle { __typename ... on BaseAVKVehicle { doorsStatus { __typename ...DoorsStatusDetails } fuelAutonomy(unit: $unit) { __typename lastUpdatedAt value unit } mileage(unit: $unit) { __typename total recordedTime unit } } }  fragment VehicleTirePressureAndMilsDetails on BaseVehicle { __typename ... on BaseAVKVehicle { tirePressure { __typename lastUpdatedAt flPressure frPressure rlPressure rrPressure flStatus frStatus rlStatus rrStatus } mils { __typename active detailedMessage type } } }"


VEHICLE_VALET_ALERTS_OPERATION_ID = (
    "9e8b9ea4c2c34471e1f94fa2a81963a1d226fa22cde37c104e31b35b09057a76"
)
VEHICLE_VALET_ALERTS = "query VehicleValetAlerts($vin: String!, $distanceUnit: DistanceUnit) { vehicle(vin: $vin) { __typename ... on BaseConnectedVehicle { valetAlert { __typename ...ValetAlertDetails } } } }  fragment ValetAlertDetails on ValetAlert { __typename serviceRequestId radius(unit: $distanceUnit) { __typename unit value } }"


VALIDATE_NISSAN_ID_OPERATION_ID = "b5f146397db98fabeae691a05a8f2105d5f0467f6249d8d9aa2e3cbf2f78b496"
VALIDATE_NISSAN_ID = "query ValidateNissanID($nissanId: String!) { validateNissanID(nissanId: $nissanId) { __typename ... on NissanIdExists { nissanId } ... on NissanIdDoesNotExist { nissanId } ... on NissanIdRequiresOwnerPortalPWReset { nissanId link } ... on NissanIdRequiresOwnerPortalProfileCompletion { nissanId link } ... on NissanIdRequiresNMACPWReset { nissanId link } } }"


SECURITY_QUESTIONS_OPERATION_ID = "0f4e903f6e7aaab9f1d395f63389b5e851a620b7aae75fb0f2c2590c832eb3ee"
SECURITY_QUESTIONS = "query SecurityQuestions { securityQuestions { __typename id question } }"


USER_INFO_OPERATION_ID = "e90c04b6e66bda2df2f3017a3ddfae4c3ca8780c1f883d199c74390acc786287"
USER_INFO = "query UserInfo { user { __typename pinConfigured securityQuestionId isLiteAccount } }"


TERMS_AND_CONDITIONS_OPERATION_ID = (
    "7ce8d6e19ea35543909809c8eb0c221a29dab74eb312b4a54ca251964bd70c17"
)
TERMS_AND_CONDITIONS = "query TermsAndConditions { termsAndConditions }"


MARKETING_PREFERENCES_OPERATION_ID = (
    "281cf505506de3bb2011c410413cad23f6e12baae9097c4089aa0d55c6461a7d"
)
MARKETING_PREFERENCES = "query MarketingPreferences { user { __typename countryMarketingPreferences { __typename ... on NCIMarketingPreferences { email productUpdates { __typename email textMessage directMail inApp inVehicle } newsEvents { __typename email textMessage directMail inApp inVehicle } offersPromotion { __typename email textMessage directMail inApp inVehicle } } ... on NNAMarketingPreferences { feedback newsletter productOffers serviceOffers scheduledMaintenance } } } }"


REGISTER_ACCOUNT_OPERATION_ID = "f3306b7a7b99ae529b4bf40cf2d4dc89aff592ffa27d71950bdda418a138a76a"
REGISTER_ACCOUNT = "mutation RegisterAccount($config: RegisterAccountInput!) { registerAccount(config: $config) { __typename ... on RegisterAccountSuccessResponse { userId } ... on RegisterAccountFirstNameError { message } ... on RegisterAccountLastNameError { message } ... on RegisterAccountEmailError { message } ... on RegisterAccountAddressError { message } ... on RegisterAccountCityError { message } ... on RegisterAccountStateError { message } ... on RegisterAccountPostalCodeError { message } ... on RegisterAccountPhoneError { message } ... on RegisterAccountPasswordError { message } ... on RegisterAccountDuplicateEmailError { message } ... on RegisterGeneralError { message } } }"


NCAR_ICAR_REGISTER_ACCOUNT_OPERATION_ID = (
    "75e5b49f52d986ba013048f306a24dfb97bbaf72fb5f5ca3573d2f27b93a76d2"
)
NCAR_ICAR_REGISTER_ACCOUNT = "mutation NcarIcarRegisterAccount($config: RegisterAccountInput!) { ncarIcarRegisterAccount(config: $config) { __typename ... on RegisterAccountSuccessResponse { userId } ... on RegisterAccountFirstNameError { message } ... on RegisterAccountLastNameError { message } ... on RegisterAccountEmailError { message } ... on RegisterAccountAddressError { message } ... on RegisterAccountCityError { message } ... on RegisterAccountStateError { message } ... on RegisterAccountPostalCodeError { message } ... on RegisterAccountPhoneError { message } ... on RegisterAccountPasswordError { message } ... on RegisterAccountDuplicateEmailError { message } ... on RegisterGeneralError { message } } }"


NCAR_ICAR_VERIFY_ACCOUNT_OPERATION_ID = (
    "7e26704ab9c5bf1cb164adb26e2173cb00e2c936a378648c1034f33d5fe34c3c"
)
NCAR_ICAR_VERIFY_ACCOUNT = "mutation NcarIcarVerifyAccount($guid: ID!) { ncarIcarVerifyAccount(guid: $guid) { __typename ... on NCARICARAccountAvailable { email phoneNumber isOTPRequired } ... on NCARICARAccountUnavailable { email vin } ... on NCARICARCustomerEnrollmentExpiredError { message } ... on NCARICARCustomerEnrollmentGeneralError { message } ... on GeneralError { message } } }"


NCAR_ICAR_CUSTOMER_ENROLLMENT_OPERATION_ID = (
    "d857de7c920940fa00b5cf4dfedf51805a55c1156954b5016144a7f1ba54cbf9"
)
NCAR_ICAR_CUSTOMER_ENROLLMENT = "mutation NcarIcarCustomerEnrollment($guid: ID!) { ncarIcarCustomerEnrollment(guid: $guid) { __typename ... on NCARICARCustomerEnrollmentResponse { vin firstName lastName email phoneNumber address { __typename address1 address2 city state postalCode country } } ... on NCARICARCustomerEnrollmentGeneralError { message } ... on NCARICARCustomerEnrollmentExpiredError { message } ... on GeneralError { message } } }"


NCAR_ICAR_GENERATE_OTP_OPERATION_ID = (
    "50f54a2e7c81b43e91dcf0f223c9f962d34f93bdeda9a4b7021d975dc6370625"
)
NCAR_ICAR_GENERATE_OTP = "mutation NcarIcarGenerateOTP($guid: ID!, $phoneNumber: String!) { ncarIcarGenerateOTP(guid: $guid, phoneNumber: $phoneNumber) { __typename ... on GenerateOTPResponse { referenceId retryAvailable } ... on NCARICARGuidDeactivated { message } ... on NCARICARGenerateOTPExhausted { message } } }"


NCAR_ICAR_VERIFY_OTP_OPERATION_ID = (
    "9efcc780691e03a32ee58344f4017a28008c8e2735ff4e0c67ed756f05ab5eb2"
)
NCAR_ICAR_VERIFY_OTP = "mutation NcarIcarVerifyOTP($guid: ID!, $phoneNumber: String!, $referenceId: ID!, $otp: String!) { ncarIcarVerifyOTP(guid: $guid, phoneNumber: $phoneNumber, referenceId: $referenceId, otp: $otp) { __typename ... on NCARICARCustomerEnrollmentResponse { vin email firstName lastName phoneNumber address { __typename address1 address2 city state postalCode country } } ... on NCARICARCustomerEnrollmentExpiredError { message } ... on NCARICARCustomerEnrollmentGeneralError { message } ... on NCARICARVerifyOTPFailed { referenceId retryAvailable } ... on NCARICARVerifyOTPRetryExhausted { message } ... on NCARICARGuidDeactivated { message } } }"


GENERATE_OTP_OPERATION_ID = "c6c7a86861f37af8adb5376d3d73cc42e2ec045fe064c6d39d7c0de07ec9c612"
GENERATE_OTP = "mutation GenerateOTP($phoneNumber: String!) { nissanGenerateOTP(phoneNumber: $phoneNumber) { __typename ... on GenerateOTPResponse { referenceId retryAvailable } } }"


VERIFY_OTP_OPERATION_ID = "7d165e2df809afaf6ba02224431b4d829cb1938d09487574643814ec99980f64"
VERIFY_OTP = "mutation VerifyOTP($phoneNumber: String!, $otp: String!, $referenceId: String!) { nissanVerifyOTP(phoneNumber: $phoneNumber, otp: $otp, referenceId: $referenceId) { __typename ... on VerifyOTPSuccess { message } ... on VerifyOTPFailed { message retryAvailable } ... on VerifyOTPRetryExhausted { message } } }"


CREATE_PIN_OPERATION_ID = "181d5a83c7afa1cbae2b5b778b722fbc37c76f971ca572dbba1e395dd306c98a"
CREATE_PIN = "mutation CreatePin($questionId: String!, $answer: String!, $newPin: String!) { createPin(questionId: $questionId, answer: $answer, newPin: $newPin) { __typename ... on ResponseStatus { success } ... on CreatePINError { message } } }"


UPDATE_PIN_OPERATION_ID = "b99a8380729759799933da39704f52703b4cab6131cf45ed9211d3730fd218a8"
UPDATE_PIN = "mutation UpdatePin($questionId: String!, $answer: String!, $newPin: String!) { updatePin(questionId: $questionId, answer: $answer, newPin: $newPin) { __typename ... on ResponseStatus { success } ... on ValidationError { message } } }"


UPDATE_ACCOUNT_OPERATION_ID = "aad3256b184b448f93a68f725ba963908f532d6f381e1e5fa2a99851b3d81d14"
UPDATE_ACCOUNT = "mutation UpdateAccount($config: UpdateAccountInput) { updateAccount(config: $config) { __typename ... on User { firstName lastName email mobileNumber address { __typename address1 address2 city state country postalCode country district streetNumber } mobileNetworkOperator { __typename code id name } } ... on UpdateAccountFirstNameError { message } ... on UpdateAccountLastNameError { message } ... on UpdateAccountAddressError { message } ... on UpdateAccountPostalCodeError { message } ... on UpdateAccountMobileNumberError { message } ... on UpdateAccountLandlineNumberError { message } ... on UpdateAccountGeneralError { message } } }"


DELETE_ACCOUNT_OPERATION_ID = "c82dce2ce140e41c131860bc25d3c2c67b91d3c8f4cb7cae0fdb9e0d3e70597e"
DELETE_ACCOUNT = "mutation DeleteAccount { deleteAccount { __typename success } }"


UPDATE_NCI_MARKETING_PREFERENCES_OPERATION_ID = (
    "fcb00c4f6a74e8e25da1764e2fcc61866b924f9bf8b18bd317e866e2757568d2"
)
UPDATE_NCI_MARKETING_PREFERENCES = "mutation UpdateNCIMarketingPreferences($marketingPreferences: NCIMarketingPreferenceInput!) { updateNCIAccountPreferences(config: { marketingPreferences: $marketingPreferences } ) { __typename countryMarketingPreferences { __typename ... on NCIMarketingPreferences { email productUpdates { __typename email textMessage directMail inApp inVehicle } newsEvents { __typename email textMessage directMail inApp inVehicle } offersPromotion { __typename email textMessage directMail inApp inVehicle } } } } }"


UPDATE_NNA_MARKETING_PREFERENCES_OPERATION_ID = (
    "b1e334a1e2b9a92e58ad12d0ad10a967ea17d3c7dc7c4de73a88bb74607c3cf8"
)
UPDATE_NNA_MARKETING_PREFERENCES = "mutation UpdateNNAMarketingPreferences($marketingPreferences: MarketingPreferenceInput) { updateAccountPreferences(config: { marketingPreferences: $marketingPreferences } ) { __typename countryMarketingPreferences { __typename ... on NNAMarketingPreferences { newsletter productOffers serviceOffers scheduledMaintenance feedback } } } }"


CONTACT_US_OPERATION_ID = "1a2cb197c34dd46fa630db96c73045b2db32ba1ebdeaada4317094c5e388477a"
CONTACT_US = "query ContactUs($clientType: ClientType!) { contactUs { __typename link { __typename privacyPolicy dataPrivacy collisionRepair accidentHelper checkOwnersPortal warranty forgotPassword editContactInformationAndChangePassword partsAndAccessories ifsAccount(client: $clientType) ncesiInsurance roadsideAid buyProtection nissanAddedSecurityPlanVideo nissanCertifiedPreOwnedVideo nissanPrepaidMaintenancePlanVideo secondDeliveryMarketingVideo disconnectRemoteAccess deleteAccount ariesApp(client: ANDROID) } phoneNumber { __typename customerCare stolenVehicleLocator stolenVehicleInfo personalAssistant roadsideAssistant ownershipVerification resetVoicePin secondDeliveryCustomerSupport plugAndChargeSupport nissanStore } email { __typename secondDeliveryCustomerSupport } } }"


CPO_DETAILS_OPERATION_ID = "72e02068df86ded6c9c68b75bcc2854a4cddfc8304d78b0e8334c5e72571753b"
CPO_DETAILS = "query CpoDetails { cpoDetails { __typename statusCode statusMessage timestamp data { __typename brandName preferredProvider } } }"


FAQ_OPERATION_ID = "5896b6271d98fa7ad09ea38a7c1cf04e371b87514719d7ce8b4999bc60c0346d"
FAQ = "query FAQ($categories: [String]) { faqs(categories: $categories) { __typename category data { __typename question answer } } }"


LIVE_CHAT_HOURS_OPERATION_ID = "92c22ee63380315cd5c61993db910e8c451495d0f822c7a008a76642282d98a9"
LIVE_CHAT_HOURS = "query LiveChatHours($departments: [String], $enhancedChat: Boolean) { contactUs { __typename liveChatHours(departments: $departments, enhancedChat: $enhancedChat) { __typename departmentName openingTime closingTime afterHourMessage availableNow } } }"


MOBILE_CARRIERS_OPERATION_ID = "5092ec79bc33ce00b3955693e1ecc513c3728bfe5be2c722dbf0525bdead660d"
MOBILE_CARRIERS = "query MobileCarriers { mobileCarriers { __typename id code name } }"


ADD_PRODUCT_TO_NISSAN_STORE_CART_OPERATION_ID = (
    "eed0e98dfe2cc937bc49082ee698ec7c5a160f7e1ede1aa0006f79cb5bfdd4af"
)
ADD_PRODUCT_TO_NISSAN_STORE_CART = "mutation AddProductToNissanStoreCart($addProductToNissanStoreCartInput: AddProductToNissanStoreCartInput!) { addProductToNissanStoreCart(input: $addProductToNissanStoreCartInput) { __typename ... on AddProductToNissanStoreCartOutput { cart { __typename id deliveryGroup { __typename id } } product { __typename id name subscription { __typename id sellingModelType pricingTerm { __typename value unit } } } } } }"


CANCEL_PENDING_SUBSCRIPTION_OPERATION_ID = (
    "7c58341746585b1af72ceb9d106da15c99d9660016b35fab59cdf3b6ae27e20f"
)
CANCEL_PENDING_SUBSCRIPTION = "mutation CancelPendingSubscription($cancelPendingSubscriptionInput: CancelPendingSubscriptionInput!) { cancelPendingSubscription(input: $cancelPendingSubscriptionInput) { __typename ... on ResponseStatusType { success } } }"


CANCEL_SUBSCRIPTION_OPERATION_ID = (
    "582a6770133943805e710c65e4b27ade68e9f81530f88b417e2623e9cac277d2"
)
CANCEL_SUBSCRIPTION = "mutation CancelSubscription($cancelSubscriptionInput: CancelSubscriptionInput!) { cancelSubscription(input: $cancelSubscriptionInput) { __typename ... on ResponseStatus { success } ... on CancelSubscriptionSuccessResponse { success subscriptionEndDate } ... on CancelSubscriptionGeneralError { message } } }"


CREATE_NISSAN_STORE_FOD_TRIAL_CHECKOUT_LINK_OPERATION_ID = (
    "9c6c28d802fca574a547c921840ebb9397093a213d6f4dfd05c522e12757b990"
)
CREATE_NISSAN_STORE_FOD_TRIAL_CHECKOUT_LINK = "mutation CreateNissanStoreFODTrialCheckoutLink($vin: String!, $clientOrigin: NissanStoreClientOrigin!) { createNissanStoreFODTrialCheckoutLink(vin: $vin, clientOrigin: $clientOrigin) }"


DIGITAL_WALLET_URL_OPERATION_ID = "6ebdf2e75a646b0905f99afa77af67e9e6b6b58461b0d2bce71be4bc072fd30e"
DIGITAL_WALLET_URL = (
    "query DigitalWalletURL { nissanPay { __typename digitalWallet { __typename url } } }"
)


NISSAN_PAY_OPERATION_ID = "6f08f0f64f7bebe3ce087dcdda08ef0198d3f926dec70c43941dd54e84fc660b"
NISSAN_PAY = "query NissanPay { nissanPay { __typename paymentMethods { __typename ... on NissanPayPaymentMethodCard { __typename paymentProcessor paymentIcon isDefault last4Digits expiryMonth expiryYear status } } digitalWallet { __typename url } } }"


NISSAN_PAY_ORDER_HISTORY_OPERATION_ID = (
    "03eceb4c138de1b971d5c1415b29327cd990c4ba5392a82504aa429ded0c96bb"
)
NISSAN_PAY_ORDER_HISTORY = "query NissanPayOrderHistory($vin: String!, $pageCursor: String) { nissanPay { __typename orderHistory(vin: $vin, pageCursor: $pageCursor) { __typename items { __typename ... on NissanPayEnergyChargeSession { __typename orderDate totalCost address { __typename city country countryCode latitude longitude postalCode state stateCode street } paymentMethod { __typename type processor last4 } cpoBrand sessionType chargeStartTime chargeEndTime chargeDuration connectorType totalEnergy subtotal serviceFeeTotal } } pagination { __typename nextPageCursor totalSize } } } }"


NISSAN_STORE_CHECKOUT_URL_OPERATION_ID = (
    "814f25c745f3e438233e812c89e1a9dc67bdf8c7416b54e983c1e5f9a3872cfe"
)
NISSAN_STORE_CHECKOUT_URL = "query NissanStoreCheckoutURL($vin: String!, $clientOrigin: NissanStoreClientOrigin!) { nissanStoreCheckoutURL(vin: $vin, clientOrigin: $clientOrigin) }"


PRODUCT_CATALOG_OPERATION_ID = "03e4214e129ea35a0a2d8255aaac2481373ef478c611cfb9684e7281d812f30f"
PRODUCT_CATALOG = "query ProductCatalog($productCatalogInput: NSProductCatalogInput!) { productCatalog(productCatalogInput: $productCatalogInput) { __typename ... on NSProductCatalog { packages { __typename shortDescription npTrialDuration productImageUrl longDescription sellingModels { __typename sellingModelPricingTermUnit retailPrice discountedPrice sellingModelType sellingModelId } productId name childProducts { __typename name npCustomerFacing } isFoD promotions { __typename promotionId priority name monthlyPromotionPrice annualPromotionPrice endDate description } } } } }"


UPSERT_NISSAN_PAY_ACCOUNT_OPERATION_ID = (
    "f4483575cf435a5fa6693606a4915b97cb609fe110a74a58dbc162ba41feb0a4"
)
UPSERT_NISSAN_PAY_ACCOUNT = "mutation UpsertNissanPayAccount { upsertNissanPayAccount { __typename ... on UpsertNissanPayAccountSuccessResponse { responseMessage responseCode response customerId } ... on UpsertNissanPayAccountFailureResponse { responseMessage responseCode response } } }"


NCF_CONNECT_ACCOUNT_OPERATION_ID = (
    "eb64b6703fe148c55e26a59b0dc29e2d28e67267a3f064cb48a59064a77b896c"
)
NCF_CONNECT_ACCOUNT = "mutation NCFConnectAccount($vin: String!, $customerType: NCFCustomerType, $accountNumber: String!) { ncfConnectAccount(vin: $vin, customerType: $customerType, accountNumber: $accountNumber) { __typename ... on NCFConnectAccountSuccessResponse { success } ... on NCFConnectAccountCoSignerAlreadyRegisteredErrorResponse { message } ... on NCFConnectAccountInvalidVinAndAccountCombinationErrorResponse { message } ... on NCFConnectAccountInternalErrorResponse { message } ... on NCFConnectAccountPrimaryAlreadyRegisteredErrorResponse { message } } }"


NCF_DISCONNECT_ACCOUNT_OPERATION_ID = (
    "c0e92d64f6cc319f2c804299427bcbf2de2a094f82dd022d515e8bb0d96332d0"
)
NCF_DISCONNECT_ACCOUNT = "mutation NCFDisconnectAccount($accountNumber: String!) { ncfDisconnectAccount(accountNumber: $accountNumber) { __typename ... on NCFDisconnectAccountSuccessResponse { message } ... on NCFDisconnectAccountFailureResponse { message } } }"


NCF_UPDATE_ACCOUNT_OPERATION_ID = "512e60cf7ad47cd898ced786aef9ab42fe1023fa8a8f09fae4f07b0a91eef316"
NCF_UPDATE_ACCOUNT = "mutation NCFUpdateAccount($accountNumber: String!, $address: AddressInput, $phoneNumber: String) { ncfUpdateAccount(accountNumber: $accountNumber, address: $address, phoneNumber: $phoneNumber) { __typename success } }"


NCF_UPDATE_NOTIFICATION_PREFERENCES_OPERATION_ID = (
    "8ff2643cb091a5b5dfddd33452c8d2d124783dfc6f5955d453cbf1b66ec0e417"
)
NCF_UPDATE_NOTIFICATION_PREFERENCES = "mutation NCFUpdateNotificationPreferences($input: NCFUpdateNotificationPreferencesMutationInput!) { ncfUpdateNotificationPreferences(input: $input) { __typename ... on NCFUpdateNotificationPreferencesSuccessResponse { success } ... on NCFUpdateNotificationPreferencesErrorResponse { message } } }"


FINANCIAL_VEHICLES_OPERATION_ID = "0c26aa2fb725bcc6da1c91b0dfe3eee90657faaca9419810dafca51466b2e68b"
FINANCIAL_VEHICLES = "query FinancialVehicles { financialVehicles { __typename vin ... on NCFFinancialVehicle { model year image account { __typename accountNumber upcomingPayment { __typename upcomingPaymentDue dueDate recentPayment recentPaymentDate overdueBalance } customerType contract { __typename maturityDate startDate numberOfPaymentsMade customers { __typename firstName lastName buyerType phoneNumber billingAddress { __typename address city zipCode state } } dealer { __typename name phoneNumber } ... on NCFContractLoan { originalBalance remainingBalance apr principlePaidAmount interestPaidAmount paymentProgressPercentage } ... on NCFContractLease { term paymentsRemaining originalMileage contractedMileage totalMileageAllowance excessMileageChargeAmount dispositionFeeAmount residualValue adjustedPaymentAmount totalPaymentAmount paymentTaxAmount paymentTaxRate paymentProgressPercentage securityDepositAmount } } rules { __typename staticText getPayoffQuote paymentHistory contractDetails progressBarMaturity } } } } }"


GET_ACCOUNT_STATEMENT_PDF_OPERATION_ID = (
    "d0d9a460125763f1a1852344d1c30980d1c8c58b7032a30cfe4926bbd9c3f75a"
)
GET_ACCOUNT_STATEMENT_PDF = "query GetAccountStatementPDF($contractNumber: String!, $documentNumber: String!) { accountStatementPDF(contractNumber: $contractNumber, documentNumber: $documentNumber) { __typename document documentUrl } }"


GET_ACCOUNT_STATEMENTS_OPERATION_ID = (
    "e6f8bbd7df344e1429f53bc161765b7f69f0da026ddf15ea0d4b6ce65a1d8a7d"
)
GET_ACCOUNT_STATEMENTS = "query GetAccountStatements($contractNumber: String!) { accountStatements(contractNumber: $contractNumber) { __typename date documentNumber } }"


GET_CREDIT_OPERATION_ID = "94266501084837bf2d4ef0dca3326b9f2147b9a88902b5e7218e284d19b014c8"
GET_CREDIT = "query GetCredit { vehicles { __typename vin credit { __typename currentQuota creditType creditStatus statusText nextPaymentAmount nextPaymentDate contractNumber term overdueQuotas id balance accountDomiciliation lastUpdate overdueAmount startDate endDate totalOverdueAmount extendedRent supportEmail supportPhoneNumber termsAndConditions endContractEmail creditsPortal } } }"


GET_INVOICE_PDF_OPERATION_ID = "0f581c8c6fc0e1f6b5ed701196184afff1b5bb161d89d7a1ffbfe301fbb3824d"
GET_INVOICE_PDF = "query GetInvoicePDF($contractNumber: String!, $uuid: String!) { invoicePDF(contractNumber: $contractNumber, uuid: $uuid) { __typename uuid file } }"


GET_INVOICES_OPERATION_ID = "e4b0e0348ae8cd5963e937d776663a762b14a449293976bda828735374cd840b"
GET_INVOICES = "query GetInvoices($contractNumber: String!) { invoices(contractNumber: $contractNumber) { __typename date uuid } }"


NCF_ACCOUNT_STATEMENT_OPERATION_ID = (
    "2a82edfc8dbacadf95e6c82b52ce0180b67f5e9baacbf5ef392ebdac36e285b8"
)
NCF_ACCOUNT_STATEMENT = "query NCFAccountStatement($startDate: Date!, $endDate: Date!, $contractType: NCFAccountContractType!) { financialVehicles { __typename ... on NCFFinancialVehicle { account { __typename accountNumber statement(startDate: $startDate, endDate: $endDate, contractType: $contractType) { __typename billingStatements { __typename currentBalanceAmount paymentDueDate financialAccountId statementDate totalAmountDue ... on NCFAccountBillingStatementLease { priorBalanceAmount vehicleYear vehicleModel vehicleMake } } transactions { __typename paymentAmount financialAccountId statementDate sequenceNo ... on NCFAccountTransactionLease { paymentTotalAmount paymentTaxAmount paymentDescription } } } } } } }"


NCF_PAYOUT_QUOTE_OPERATION_ID = "6bf94c15258881030f6ec40d2054288401edf79f617d945e7b27bf8e552ab3e9"
NCF_PAYOUT_QUOTE = "query NCFPayoutQuote($accountNumber: String!, $vin: String!) { ncfPayoutQuote(accountNumber: $accountNumber, vin: $vin) { __typename amount goodThroughDate ... on NCFPayoutQuoteLease { earlyTerminationAmount } } }"


NCF_PREFERENCES_OPERATION_ID = "4484a489220beb655e170a914b0a35ca8255f164809e8e15f3b29a298a5eebe1"
NCF_PREFERENCES = "query NCFPreferences($accountNumber: String!) { ncfPreferences(accountNumber: $accountNumber) { __typename notificationPreferences { __typename isPaperlessStatement isPaymentDueInOneDay isPaymentReceived isPaymentPastDue isStatementAvailable } } }"


NCF_TERMS_AND_CONDITIONS_OPERATION_ID = (
    "f16189ddf5a2c23f7ee3766aa043656a33a302bffe6657759ecc8d8b9b4116a8"
)
NCF_TERMS_AND_CONDITIONS = "query NCFTermsAndConditions { ncfTermsAndConditions }"


PAYMENT_HISTORY_OPERATION_ID = "e269c3294ba09c2c42850aeb06a57ed0681b1f97d492a1424f360b636319bb07"
PAYMENT_HISTORY = "query PaymentHistory($accountNumber: String!, $startDate: DateTime!, $endDate: DateTime!) { paymentHistory(accountNumber: $accountNumber, startDate: $startDate, endDate: $endDate) { __typename type description effectiveDate processDate totalPaymentAmount miscellaneousFees baseRentAmount taxAmount lateFees adminFees registrationFees ... on NCFPaymentHistoryTransactionLoan { principleAmount interestAmount } } }"


ALL_DEALERS_OPERATION_ID = "581b6c84a95b602859bc103577eb32e43e0a4cbbef84bb3c09940dd5d0b1dd2b"
ALL_DEALERS = "query AllDealers($vin: String, $pageSize: Int) { dealers(vin: $vin, pageSize: $pageSize) { __typename dealerId dealerName dealerAddressLine1 } }"


CANCEL_SERVICE_APPOINTMENT_OPERATION_ID = (
    "02cf1da9ff930c6352ef4e30309db2a8c4f1e84ab3f265952d85eec590b4bd39"
)
CANCEL_SERVICE_APPOINTMENT = "mutation CancelServiceAppointment($appointmentId: String!, $dealerId: String!, $vin: String) { cancelServiceAppointment(appointmentId: $appointmentId, dealerId: $dealerId, vin: $vin) { __typename success } }"


CREATE_SERVICE_APPOINTMENT_OPERATION_ID = (
    "980f2a99cdde6b924e005c338dcc6185f873242f457a0b2fe42fd8d3b00f173d"
)
CREATE_SERVICE_APPOINTMENT = "mutation CreateServiceAppointment($appointment: ServiceAppointmentInput!) { createServiceAppointment(appointment: $appointment) { __typename ... on ServiceAppointment { appointmentId } } }"


DEALERS_OPERATION_ID = "99bcf20cccacbd902e4f112827461c5f7dcca0c3b011f3260dcc95c531f4238f"
DEALERS = "query Dealers($zip: String!) { dealers(searchTerm: $zip) { __typename dealerId dealerName dealerAddressLine1 dealerAddressLine2 dealerCityName dealerStateCode dealerCountry dealerZip dealerLatitude dealerLongitude dealerPhoneNumber dealerServicePhone dealerServiceHours dealerOnlineSchedulingMobileUrl nativeServiceBooking languagesSpoken } }"


DEALERS_BY_SEARCH_OPERATION_ID = "c4bd356f59315ac2ef1d68fedfe7d578dfd1945386f0aa7ed4bb8f3ca0561e5d"
DEALERS_BY_SEARCH = "query DealersBySearch($vin: String, $serviceCode: ServiceCodeEnum, $radius: Int, $latitude: Float, $longitude: Float) { dealers(vin: $vin, serviceCode: $serviceCode, radius: $radius, latitude: $latitude, longitude: $longitude) { __typename dealerId dealerName isDealerPreferred dealerAddressLine1 dealerAddressLine2 dealerLatitude dealerLongitude dealerZip dealerCountry dealerStateCode nativeServiceBooking dealerOnlineSchedulingMobileUrl dealerCityName dealerPhoneNumber dealerServicePhone dealerWebsite languagesSpoken dealerEmailAddress dealerServiceHours dealerServicesSchedules { __typename name schedules { __typename dayOfWeek endTime opened startTime } } } }"


DEALS_AND_IMAGES_BY_DEALER_ID_OPERATION_ID = (
    "52f73c33747c221c3a5de53bf8f19152e9827cc029a837f2de747e05fc4e26e5"
)
DEALS_AND_IMAGES_BY_DEALER_ID = "query DealsAndImagesByDealerId($dealerId: String!) { dealsByDealerId(dealerId: $dealerId) { __typename coupon { __typename couponId couponTitle standardDisclaimer } } dealsImagesByDealerId(dealerId: $dealerId) { __typename coupons { __typename couponId couponImageUrl } } }"


GENERATE_ALL_VISITS_OPERATION_ID = (
    "6a4012bcf0ec70ac7d3a36b5b178600b4c5651a2c8105cb019921db11c36b9cb"
)
GENERATE_ALL_VISITS = "query GenerateAllVisits($vin: String!, $mileage: MS_MileageInputType!, $severityId: ID!, $pastVisits: Int!, $futureVisits: Int!) { viewer(Mileage: $mileage, VIN: $vin, SeverityID: $severityId) { __typename ...MaintenanceVisitsViewer } }  fragment MaintenanceVisitsViewer on MS_Viewer { __typename Schedule { __typename Visits(pastVisits: $pastVisits, futureVisits: $futureVisits) { __typename Alignment Interval { __typename Month Year Next DistanceMiles DistanceKMs } ServiceOccurrences { __typename ServiceComponent { __typename ServiceComponentName ServiceCategory { __typename ServiceCategoryName } } ServiceType { __typename ServiceTypeName ServiceTypeGroup { __typename ServiceTypeGroupName } } } } } }"


GENERATE_NEXT_VISIT_OPERATION_ID = (
    "dcef3f6fdab4037776eb0887d24210c2e55113dd5b078578293c0f727b1424e8"
)
GENERATE_NEXT_VISIT = "query GenerateNextVisit($vin: String!, $mileage: MS_MileageInputType!, $severityId: ID!, $pastVisits: Int!, $futureVisits: Int!) { viewer(Mileage: $mileage, VIN: $vin, SeverityID: $severityId) { __typename ...MaintenanceVisitsViewer } }  fragment MaintenanceVisitsViewer on MS_Viewer { __typename Schedule { __typename Visits(pastVisits: $pastVisits, futureVisits: $futureVisits) { __typename Alignment Interval { __typename Month Year Next DistanceMiles DistanceKMs } ServiceOccurrences { __typename ServiceComponent { __typename ServiceComponentName ServiceCategory { __typename ServiceCategoryName } } ServiceType { __typename ServiceTypeName ServiceTypeGroup { __typename ServiceTypeGroupName } } } } } }"


GENERATE_NEXT_VISIT_NO_SEVERITY_OPERATION_ID = (
    "c53205b1dd6493a9c7813171c72985d5cb080f12bc2c598a48efb00f95f6fb92"
)
GENERATE_NEXT_VISIT_NO_SEVERITY = "query GenerateNextVisitNoSeverity($vin: String!, $mileage: MS_MileageInputType!, $severityId: ID!, $pastVisits: Int!, $futureVisits: Int!) { viewer(Mileage: $mileage, VIN: $vin, SeverityID: $severityId) { __typename ...MaintenanceVisitsViewer } }  fragment MaintenanceVisitsViewer on MS_Viewer { __typename Schedule { __typename Visits(pastVisits: $pastVisits, futureVisits: $futureVisits) { __typename Alignment Interval { __typename Month Year Next DistanceMiles DistanceKMs } ServiceOccurrences { __typename ServiceComponent { __typename ServiceComponentName ServiceCategory { __typename ServiceCategoryName } } ServiceType { __typename ServiceTypeName ServiceTypeGroup { __typename ServiceTypeGroupName } } } } } }"


GET_DEALER_BY_ID_OPERATION_ID = "eb2c4869c9e7332631a50a1720e871dc20c66f1f28cd7bdf48c36f4005b003ff"
GET_DEALER_BY_ID = "query GetDealerById($dealerId: String!) { dealer(dealerId: $dealerId) { __typename isDealerPreferred dealerId dealerAddressLine1 dealerLatitude dealerLongitude dealerName dealerWebsite dealerPhoneNumber dealerEmailAddress nativeServiceBooking dealerServicesSchedules { __typename code name schedules { __typename dayOfWeek opened startTime endTime } } } }"


SERVICE_ADVISORS_OPERATION_ID = "dc0c2a11cf2f930d82387960dbbd9ca2de0cb71e72874f35a78de66e5ea44d9d"
SERVICE_ADVISORS = "query ServiceAdvisors($dealerId: String!, $serviceOperationIds: [String!]!, $vin: String) { serviceAdvisors(dealerId: $dealerId, serviceOperationIds: $serviceOperationIds, vin: $vin) { __typename advisorId name jobTitle email imageUrl } }"


SERVICE_APPOINTMENT_TIME_SLOTS_OPERATION_ID = (
    "f480da9f36ebfcf7303cf64a43fa317019f79316589173f889adddd25563e644"
)
SERVICE_APPOINTMENT_TIME_SLOTS = "query ServiceAppointmentTimeSlots($dealerId: String!, $serviceOperationIds: [String!]!, $startDate: DateTime!, $advisorId: String, $transportationCode: String, $locationType: LocationTypeEnum, $vin: String) { serviceAppointmentTimeSlots(dealerId: $dealerId, serviceOperationIds: $serviceOperationIds, startDate: $startDate, advisorId: $advisorId, transportationCode: $transportationCode, locationType: $locationType, vin: $vin) { __typename isOpen date timeslots { __typename time } } }"


SERVICE_APPOINTMENTS_OPERATION_ID = (
    "e096a72fdf7c1e4751265df4abc9715e97cd0efa0ce990288f26b26fb70fa77b"
)
SERVICE_APPOINTMENTS = "query ServiceAppointments($vin: String!, $startDate: DateTime, $endDate: DateTime) { serviceAppointments(vin: $vin, startDate: $startDate, endDate: $endDate) { __typename appointmentId appointmentDate dealerId isEditable dealership { __typename dealerName dealerAddressLine1 dealerAddressLine2 dealerCityName dealerStateCode dealerPhoneNumber } pickUpAddress { __typename address1 address2 city state postalCode country neighbourhood } dropOffAddress { __typename address1 address2 city state postalCode country } transport { __typename code name isValet isLoanerAvailable } customer { __typename contactMethod { __typename type value } } serviceOperations { __typename opCodeDescription opCodeID customerComments serviceCategoryName serviceOperationsDescription } advisor { __typename name advisorId jobTitle email imageUrl } additionalComments } }"


SERVICE_CATEGORIES_OPERATION_ID = "7e1c8de493a29b1adeedba76185abd9fc6a75e33be48526d5c764e0780248e36"
SERVICE_CATEGORIES = "query ServiceCategories { serviceCategories { __typename serviceCategoryId serviceCategoryName serviceCategoryDescription serviceOperations { __typename opCodeID opCodeDescription } } }"


SERVICE_OPERATIONS_OPERATION_ID = "0b070e2e51e0fb5143aec45d1b128c7fe4dc85a633a7e92ebaac758ed4e4a2e1"
SERVICE_OPERATIONS = "query ServiceOperations($vin: String!, $dealerId: String!) { serviceOperations(vin: $vin, dealerId: $dealerId) { __typename opCodeID opCodeDescription customerComments serviceOperationsDescription package maintenance validation price laborHours discounts { __typename code description price } } }"


SERVICE_OPERATIONS_BY_MILEAGE_OPERATION_ID = (
    "35d58f1328e5fa4e15722fbe3131841850530d23c1a2cad34447ae5819b502f7"
)
SERVICE_OPERATIONS_BY_MILEAGE = "query ServiceOperationsByMileage($vin: String!, $dealerId: String!, $mileage: Int!) { serviceOperationsByMileage(vin: $vin, dealerId: $dealerId, mileage: $mileage) { __typename servicesAtClosestIntervals { __typename intervalMileage serviceOperations { __typename opCodeID opCodeDescription customerComments serviceOperationsDescription package maintenance validation price laborHours discounts { __typename code description price } } } } }"


TRANSPORTATION_OPTIONS_OPERATION_ID = (
    "dfb82c466e1a2597905a7e83ad944b8d7b7aba30774ec2ee6cbe941ac822e101"
)
TRANSPORTATION_OPTIONS = "query TransportationOptions($dealerId: String!, $serviceOperationIds: [String!]!, $vin: String) { transportationOptions(dealerId: $dealerId, serviceOperationIds: $serviceOperationIds, vin: $vin) { __typename code name isValet isLoanerAvailable } }"


UPDATE_SERVICE_APPOINTMENT_OPERATION_ID = (
    "10ea93855682f0dc2d4ea2a50799e6e3086bc24a61ee60c915f1c443f2d1e356"
)
UPDATE_SERVICE_APPOINTMENT = "mutation UpdateServiceAppointment($appointmentId: String!, $appointment: ServiceAppointmentInput!) { updateServiceAppointment(appointmentId: $appointmentId, appointment: $appointment) { __typename ... on ServiceAppointment { dealerId appointmentId appointmentDate additionalComments pickUpAddress { __typename address1 address2 city state postalCode country district streetNumber } transport { __typename name } type vehicle { __typename vin } } ... on ServiceAppointmentError { message error } } }"


UPDATE_VEHICLE_PREFERRED_DEALER_OPERATION_ID = (
    "ee96579c755162d75f970f3e33d67e58bf8b2e79a36c37c653d24731653cc33d"
)
UPDATE_VEHICLE_PREFERRED_DEALER = "mutation UpdateVehiclePreferredDealer($vin: String!, $preferredDealerId: String!) { updateVehicle(vin: $vin, preferredDealerId: $preferredDealerId) { __typename ... on UpdateVehicleSuccessResponse { preferredDealer } ... on RequiresAtLeastOneArgumentError { message } ... on InvalidVINError { message } ... on VINNotFoundError { message } ... on UpdateVehicleGeneralError { message } } }"


CANCEL_SECOND_DELIVERY_APPOINTMENT_OPERATION_ID = (
    "8038b57ab8afc28fb2f5c2153bcc89dea2650492101ce5817d08e0b613114668"
)
CANCEL_SECOND_DELIVERY_APPOINTMENT = "mutation CancelSecondDeliveryAppointment($activityId: Int!) { cancelSecondDeliveryAppointment(activityId: $activityId) { __typename ... on CancelSecondDeliveryAppointmentSuccessResponse { success } ... on CancelSecondDeliveryAppointmentUnknownErrorResponse { message } } }"


CREATE_SECOND_DELIVERY_APPOINTMENT_OPERATION_ID = (
    "b6698d3dc4e338707998f4c9d7b2afa600b7d4980d05be50cd91f72c2ea71ee6"
)
CREATE_SECOND_DELIVERY_APPOINTMENT = "mutation CreateSecondDeliveryAppointment($vin: String!, $address: AddressInput!, $contactInformation: SecondDeliveryContactInformationInput!, $timeSlotId: Int!, $redeliveryNotes: String, $featureNotes: String, $mode: SecondDeliveryAppointmentModeEnum) { createSecondDeliveryAppointment(vin: $vin, address: $address, contactInformation: $contactInformation, timeSlotId: $timeSlotId, redeliveryNotes: $redeliveryNotes, featureNotes: $featureNotes, mode: $mode) { __typename ... on CreateSecondDeliveryAppointmentSuccessResponse { success } ... on CreateSecondDeliveryInvalidTimeSlotErrorResponse { message } ... on CreateSecondDeliveryAppointmentUnknownErrorResponse { message } } }"


SECOND_DELIVERY_APPOINTMENT_OPERATION_ID = (
    "ca4319223c37ad3874b942484c301bf4b3b93171ff58bd43da2ab242a23af8df"
)
SECOND_DELIVERY_APPOINTMENT = "query SecondDeliveryAppointment($vin: String!) { vehicle(vin: $vin) { __typename secondDelivery { __typename appointment { __typename ... on SecondDeliveryExistingBookedAppointment { id activityId beginsAt address { __typename address1 address2 city state postalCode country } contact { __typename firstName lastName phoneNumber email } redeliveryNotes featureNotes hub { __typename id timezone dealer { __typename code address { __typename coordinates { __typename latitude longitude } address1 address2 state city country id postalCode } } } mode } ... on SecondDeliveryBookedAppointmentNotExistError { message } ... on SecondDeliveryForbiddenError { message redactedEmail redactedPhoneNumber appointment { __typename id accessToken status } } } } } }"


SECOND_DELIVERY_APPOINTMENTS_AT_HOME_OPERATION_ID = (
    "e2d81521613aa8074f420a5f861e0d99891d9499bf968b6115a85220a72f7a0c"
)
SECOND_DELIVERY_APPOINTMENTS_AT_HOME = "query SecondDeliveryAppointmentsAtHome($vin: String!, $address: AddressInput!, $hubId: String!, $start: DateTime!, $end: DateTime!) { vehicle(vin: $vin) { __typename secondDelivery { __typename appointments(start: $start, end: $end) { __typename atHome(address: $address, hubId: $hubId) { __typename ... on SecondDeliveryAppointmentTimeSlotsSuccessResponse { hub { __typename id timezone } slotsByDate { __typename date timeslots { __typename time id } } } ... on SecondDeliveryAppointmentTimeSlotsErrorAddressNotServicedResponse { message } } } } } }"


SECOND_DELIVERY_APPOINTMENTS_AT_HUB_OPERATION_ID = (
    "285d5991246c2008726e4ed4e5a2b12003da5dd7fd09121379fb6cec4527ab40"
)
SECOND_DELIVERY_APPOINTMENTS_AT_HUB = "query SecondDeliveryAppointmentsAtHub($hubId: String!, $zipCode: String!, $start: DateTime!, $end: DateTime!, $vin: String!) { vehicle(vin: $vin) { __typename secondDelivery { __typename appointments(start: $start, end: $end) { __typename atHub(hubId: $hubId, zipCode: $zipCode) { __typename ... on SecondDeliveryAppointmentTimeSlotsSuccessResponse { hub { __typename id timezone } slotsByDate { __typename date timeslots { __typename time id } } } ... on SecondDeliveryAppointmentTimeSlotsErrorAddressNotServicedResponse { message } } } } } }"


SECOND_DELIVERY_APPOINTMENTS_AT_VIRTUAL_OPERATION_ID = (
    "5a24913a76195ffd03ee01cc8b41932f19f48610e3b114c27c0959f4541b3366"
)
SECOND_DELIVERY_APPOINTMENTS_AT_VIRTUAL = "query SecondDeliveryAppointmentsAtVirtual($hubId: String!, $zipCode: String!, $start: DateTime!, $end: DateTime!, $vin: String!) { vehicle(vin: $vin) { __typename secondDelivery { __typename appointments(start: $start, end: $end) { __typename atVirtual(hubId: $hubId, zipCode: $zipCode) { __typename ... on SecondDeliveryAppointmentTimeSlotsSuccessResponse { hub { __typename id timezone } slotsByDate { __typename date timeslots { __typename time id } } } ... on SecondDeliveryAppointmentTimeSlotsErrorAddressNotServicedResponse { message } } } } } }"


SECOND_DELIVERY_ELIGIBILITY_OPERATION_ID = (
    "a19cdb3243dd2c8ae4c78fef51a829517988ac12ba1f3e4dd295e782f1bfcfae"
)
SECOND_DELIVERY_ELIGIBILITY = "query SecondDeliveryEligibility($vin: String!) { vehicle(vin: $vin) { __typename secondDelivery { __typename eligibility { __typename ... on SecondDeliveryEligibilityResponseRDRRecordFound { hub { __typename id timezone dealer { __typename code address { __typename address1 address2 state city id postalCode coordinates { __typename latitude longitude } } } } leadCar { __typename trim deleted interiorColor retailSalesDate plate brand year model mileage leadId exteriorColor name vin id } redeliveryLeadId daysSinceRetailSalesDate } ... on SecondDeliveryEligibilityResponseAppointmentBooked { appointment { __typename status accessToken id } } ... on SecondDeliveryEligibilityResponseAppointmentCompleted { appointment { __typename status accessToken id } } ... on SecondDeliveryEligibilityResponseNonParticipatingDealer { message } ... on SecondDeliveryEligibilityResponseVinNotFound { message } } cta { __typename marketingMessage { __typename versionToDisplay displayMarketingMessageThresholdInDays remindMeLaterThresholdInDays } discover { __typename prioritized } daysSincePurchased } } } }"


SECOND_DELIVERY_SEND_AUTH_CODE_OPERATION_ID = (
    "fcada57a54859a26e4e8dcad4ae4a3d6e4282a5d7a62e0c433a18dc205c86204"
)
SECOND_DELIVERY_SEND_AUTH_CODE = "mutation SecondDeliverySendAuthCode($appointmentId: Int!, $accessToken: String!, $sendViaEmail: Boolean!, $sendViaSMS: Boolean!) { secondDeliverySendAuthCode(appointmentId: $appointmentId, accessToken: $accessToken, sendViaEmail: $sendViaEmail, sendViaSMS: $sendViaSMS) { __typename ... on SecondDeliverySendAuthCodeSuccessResponse { success } ... on SecondDeliverySendAuthCodeErrorInvalidAccessTokenResponse { message } } }"


SECOND_DELIVERY_VERIFY_AUTH_CODE_OPERATION_ID = (
    "011c0bc00940b689bc42b3c30a96bc755632cd12cefc1bbbe62db9abee8baa9e"
)
SECOND_DELIVERY_VERIFY_AUTH_CODE = "mutation SecondDeliveryVerifyAuthCode($appointmentId: Int!, $accessToken: String!, $authCode: String!) { secondDeliveryVerifyAuthCode(appointmentId: $appointmentId, accessToken: $accessToken, authCode: $authCode) { __typename ... on SecondDeliveryVerifyAuthCodeSuccessResponse { success } ... on SecondDeliveryVerifyAuthCodeErrorInvalidAuthResponse { message } } }"


UPDATE_SECOND_DELIVERY_APPOINTMENT_OPERATION_ID = (
    "af55dd2d886a10cb014a2187786513b1c7398c72c8e0048c1cf2355b5b04529e"
)
UPDATE_SECOND_DELIVERY_APPOINTMENT = "mutation UpdateSecondDeliveryAppointment($vin: String!, $activityId: Int!, $address: AddressInput!, $contactInformation: SecondDeliveryContactInformationInput!, $timeSlotId: Int!, $redeliveryNotes: String, $featureNotes: String) { updateSecondDeliveryAppointment(vin: $vin, activityId: $activityId, address: $address, contactInformation: $contactInformation, timeSlotId: $timeSlotId, redeliveryNotes: $redeliveryNotes, featureNotes: $featureNotes) { __typename ... on UpdateSecondDeliveryAppointmentSuccessResponse { success } ... on UpdateSecondDeliveryUpdateAppointmentTooSoonErrorResponse { message } ... on UpdateSecondDeliveryAppointmentUnknownErrorResponse { message } } }"


VALIDATE_SECOND_DELIVERY_ADDRESS_OPERATION_ID = (
    "dfe7c26961f631dd97c91be4b03d896db2691978b64f130d306ab5e0bb7fca12"
)
VALIDATE_SECOND_DELIVERY_ADDRESS = "query ValidateSecondDeliveryAddress($vin: String!, $address: AddressInput!) { vehicle(vin: $vin) { __typename secondDelivery { __typename validateAddress(address: $address) { __typename ... on ValidSecondDeliveryAddress { valid } ... on InvalidSecondDeliveryAddress { valid dealerAddress { __typename address1 address2 city state postalCode country } } } } } }"


ADD_VEHICLE_INSURANCE_OPERATION_ID = (
    "c8a675f1bbfc0b0dd24aa9df7b1f7226baf678b0ef4bd9b41dae463104220ed8"
)
ADD_VEHICLE_INSURANCE = "mutation AddVehicleInsurance($input: AddVehicleInsuranceInput!) { addVehicleInsurance(input: $input) { __typename ... on AddVehicleInsuranceSuccess { success } ... on AddVehicleInsuranceGeneralError { message } } }"


GET_VEHICLE_INSURANCE_OPERATION_ID = (
    "98d754f8f84559168c53b6c10eed74518518f7fcbcbcc724c19a9540059ae045"
)
GET_VEHICLE_INSURANCE = "query GetVehicleInsurance($vin: String!) { vehicle(vin: $vin) { __typename insurance { __typename id policyNumber expirationDate status insurer { __typename id name contacts { __typename location phoneNumber } } } } }"


INSURERS_OPERATION_ID = "2da75bceb5084402739f948c14cc97a94ef50b9ed3541de666efc7f34f83f83f"
INSURERS = "query Insurers { insurers { __typename name id contacts { __typename location phoneNumber } } }"


UPDATE_VEHICLE_INSURANCE_OPERATION_ID = (
    "22e782bf419449844d927d69e0ebd38f7dfe52215ed063e0cb235146d08341a9"
)
UPDATE_VEHICLE_INSURANCE = "mutation UpdateVehicleInsurance($input: UpdateVehicleInsuranceInput!) { updateVehicleInsurance(input: $input) { __typename ... on UpdateVehicleInsuranceSuccess { success } ... on UpdateVehicleInsuranceGeneralError { message } } }"


COLLISION_CENTERS_OPERATION_ID = "b25799de489658f0d5a885c3d2ba31797db31166c9b37082f06e1daa39b9b27c"
COLLISION_CENTERS = "query CollisionCenters($input: CollisionCenterInput!) { collisionCenters(input: $input) { __typename id name address { __typename address1 address2 city state postalCode country } distance { __typename value unit driveTime } phones { __typename isPrimary number } emails website properties { __typename nissanCertified evCertified p1669718Status relevanceScore smartFilterQualified participantProfileStatus nissanGTR typeFacility } } }"


CREATE_COLLISION_REPORT_OPERATION_ID = (
    "3f4166b52642a9c8045bb9de06031ebe984e25c3f66f0bd38ebdf552f1ea6bfa"
)
CREATE_COLLISION_REPORT = "mutation CreateCollisionReport($input: CreateCollisionReportInput!) { createCollisionReport(input: $input) { __typename ... on CreateCollisionReportSuccess { collisionId } ... on CreateCollisionReportError { message } } }"


CREATE_COLLISION_REPORT_PDF_OPERATION_ID = (
    "19ca3ecdbedb59fb22a511c38b2515e6a2f3d342fd2a05905a72d74dfa75aee8"
)
CREATE_COLLISION_REPORT_PDF = "mutation CreateCollisionReportPDF($input: CreateCollisionReportPDFInput!) { createCollisionReportPDF(input: $input) { __typename ... on CreateCollisionReportPDFSuccess { pdfUrl } ... on CreateCollisionReportPDFError { message } } }"


DELETE_PHOTO_FOR_COLLISION_REPORT_OPERATION_ID = (
    "c00cb1ae4ed0e9c46ddb6a9513265c5dc8c2f982ee4a74f7d97ac9e309fa107c"
)
DELETE_PHOTO_FOR_COLLISION_REPORT = "mutation DeletePhotoForCollisionReport($input: DeletePhotoForCollisionReportInput!) { deletePhotoForCollisionReport(input: $input) { __typename ... on DeletePhotoForCollisionReportSuccess { success } ... on DeletePhotoForCollisionReportError { message } } }"


UPLOAD_PHOTO_FOR_COLLISION_REPORT_OPERATION_ID = (
    "3a98f3817495f4fc58c78d4a3127f53582c255f1aeb17b92998ffceb9537057e"
)
UPLOAD_PHOTO_FOR_COLLISION_REPORT = "mutation UploadPhotoForCollisionReport($input: UploadPhotoForCollisionReportInput!) { uploadPhotoForCollisionReport(input: $input) { __typename ... on UploadPhotoForCollisionReportSuccess { success } ... on UploadPhotoForCollisionReportError { message } } }"
