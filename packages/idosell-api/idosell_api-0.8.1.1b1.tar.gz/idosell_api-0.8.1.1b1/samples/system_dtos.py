from typing import List, Any

from src.idosell._common import BooleanStrShortEnum
from src.idosell.system._common import (
    AddressModel, CoordinatesModel, CurrenciesModel, CurrencyRateEnum, DescriptionsCouriersModel, DescriptionsSystemModel, MainStockSystemEnum, OperatingDaysModel,
    OperatingModeEnum, PaymentFormsEnum, PickupPointDeleteRequestsPostModel,
    PickupPointsPostModel, PickupPointsPutModel, ServiceStatusEnum, PanelSettingsModel, ShopsModel,
    StockStateConfigEnum, TaxSettingsModel, SaleDateEnum, RestrictionsModel, BlockIfIncorrectStockQuantitiesModel, OrdersModel, UnitsModel
)
from src.idosell.system.couriers import (
    DeletePickupPoint as SystemCouriersDeletePickupPoint,
    DeletePickupPointSystemCouriersParamsModel,
    Get as SystemCouriersGet, GetAssignedToShippingProfiles as SystemCouriersGetAssignedToShippingProfiles,
    GetPickupPoints as SystemCouriersGetPickupPoints,
    PostPickupPoints as SystemCouriersPostPickupPoints,
    PutPickupPoints as SystemCouriersPutPickupPoints,
    PostPickupPointsSystemCouriersParamsModel,
    PutPickupPointsSystemCouriersParamsModel
)
from src.idosell.system.deliveries import (
    GetProfiles as SystemDeliveriesGetProfiles, GetRegions as SystemDeliveriesGetRegions,
    PostRegions as SystemDeliveriesPostRegions,
    PutDefaultProfiles as SystemDeliveriesPutDefaultProfiles,
    PostRegionsSystemDeliveriesParamsModel, PutDefaultProfilesSystemDeliveriesParamsModel
)
from src.idosell.system.shops import GetCurrencies as SystemShopsGetCurrencies, GetLanguages as SystemShopsGetLanguages
from src.idosell.system.system import (
    GetCurrencies as SystemSystemGetCurrencies, GetConfig as SystemSystemGetConfig, GetProcessesAutomation as SystemSystemGetProcessesAutomation,
    GetServerLoad as SystemSystemGetServerLoad, GetServerTime as SystemSystemGetServerTime, GetShopsData as SystemSystemGetShopsData,
    GetUnits as SystemSystemGetUnits, GetUsers as SystemSystemGetUsers,
    PutConfig as SystemSystemPutConfig, PutCurrencies as SystemSystemPutCurrencies, PutProcessesAutomation as SystemSystemPutProcessesAutomation, PutUnits as SystemSystemPutUnits,
    PutConfigSystemSystemParamsModel, PutProcessesAutomationSystemSystemParamsModel, PutUnitsSystemSystemParamsModel
)

system_delete: List[Any] = [
    SystemCouriersDeletePickupPoint(
        params = DeletePickupPointSystemCouriersParamsModel(
            pickupPointDeleteRequests = [PickupPointDeleteRequestsPostModel(
                pickupPointId = 'blah',
                pickupPointExternalId = 'blah',
                courierId = 1
            )]
        )
    ),
]

system_get: List[Any] = [
    SystemCouriersGetAssignedToShippingProfiles(), # type: ignore
    SystemCouriersGet(countryCode = 'pl'), # type: ignore
    SystemCouriersGetPickupPoints(courierId = 1), # type: ignore
    SystemDeliveriesGetProfiles(), # type: ignore
    SystemDeliveriesGetRegions(), # type: ignore
    SystemShopsGetCurrencies(), # type: ignore
    SystemShopsGetLanguages(), # type: ignore
    SystemSystemGetConfig(), # type: ignore
    SystemSystemGetCurrencies(symbol = 'PLN', date="2025-08-26"), # type: ignore
    SystemSystemGetProcessesAutomation(), # type: ignore
    SystemSystemGetServerLoad(), # type: ignore
    SystemSystemGetServerTime(), # type: ignore
    SystemSystemGetShopsData(), # type: ignore
    SystemSystemGetUnits(), # type: ignore
    SystemSystemGetUsers(), # type: ignore
]

system_post: List[Any] = [
    SystemCouriersPostPickupPoints(
        params = PostPickupPointsSystemCouriersParamsModel(
            pickupPoints = [PickupPointsPostModel(
                pickupPointExternalId = 'blah',
                courierId = 1,
                descriptions = [DescriptionsCouriersModel(
                    languageId = 'pl',
                    name = 'Name of the pickup point',
                    description = 'collection point description'
                )],
                paymentForms = ['cash'],
                serviceStatus = ServiceStatusEnum(ServiceStatusEnum.OUT_OF_SERVICE),
                address = AddressModel(
                    street = 'street',
                    zipCode = 'zipCode',
                    city = 'city',
                    provinceCode = 'provinceCode'
                ),
                coordinates = CoordinatesModel(
                    longitude = 0,
                    latitude = 0
                ),
                operatingDays = [OperatingDaysModel(
                    weekday = 1,
                    opening = '08:00',
                    closing = '21:00',
                    operatingMode = OperatingModeEnum.OPEN_IN
                )]
            )]
        )
    ),
    SystemDeliveriesPostRegions(
        params = PostRegionsSystemDeliveriesParamsModel(
            regionName = 'Test Region',
            shopId = 1,
            postCodeFrom = 'postCodeFrom',
            postCodeTo = 'postCodeTo',
            parentRegionId = 1
        )
    ),
]

system_put: List[Any] = [
        SystemCouriersPutPickupPoints(
        params = PutPickupPointsSystemCouriersParamsModel(
            pickupPoints = [PickupPointsPutModel(
                pickupPointId = 'some_id',
                pickupPointExternalId = 'blah',
                courierId = 1,
                descriptions = [DescriptionsCouriersModel(
                    languageId = 'pl',
                    name = 'Name of the pickup point',
                    description = 'collection point description'
                )],
                paymentForms = [PaymentFormsEnum.CASH],
                serviceStatus = ServiceStatusEnum(ServiceStatusEnum.OUT_OF_SERVICE),
                address = AddressModel(
                    street = 'street',
                    zipCode = 'zipCode',
                    city = 'city',
                    provinceCode = 'provinceCode'
                ),
                coordinates = CoordinatesModel(
                    longitude = 0,
                    latitude = 0
                ),
                operatingDays = [OperatingDaysModel(
                    weekday = 1,
                    opening = '08:00',
                    closing = '21:00',
                    operatingMode = OperatingModeEnum.OPEN_IN
                )]
            )]
        )
    ),
    SystemDeliveriesPutDefaultProfiles(
        params = PutDefaultProfilesSystemDeliveriesParamsModel(
            regionId = 1,
            shopId = 1,
            retailProfileId = 1,
            wholesaleProfileId = 1
        )
    ),
    SystemSystemPutConfig(
        params = PutConfigSystemSystemParamsModel(
            panelSettings = PanelSettingsModel(
                mainStockSystem = MainStockSystemEnum.OTHER,
                stockStateConfig = StockStateConfigEnum.OUTSIDE,
                taxSettings = TaxSettingsModel(
                    saleDatePrepaid = SaleDateEnum.SALEDATEFROMORDER,
                    saleDateCashOnDelivery = SaleDateEnum.SALEDATEFROMPAYMENT,
                    saleDateTradeCredit = SaleDateEnum.SALEDATEFROMDOCUMENT,
                    currencyRate = CurrencyRateEnum.CURRENTDAY
                ),
                shops = [ShopsModel(
                    shopId = 1,
                    salesDocumentsAreCreatedByClient = BooleanStrShortEnum.NO
                )]
            )
        )
    ),
    SystemSystemPutCurrencies(
        currencies = [CurrenciesModel(
            id = 'PLN',
            rate = 1.0,
            scale = 1
        )]
    ),
    SystemSystemPutProcessesAutomation(
        params = PutProcessesAutomationSystemSystemParamsModel(
            shopId = 1,
            orders = OrdersModel(
                alwaysAllowSentStatus = BooleanStrShortEnum.NO,
                restrictions = RestrictionsModel(
                    blockIfIncorrectStockQuantities = BlockIfIncorrectStockQuantitiesModel(
                        finished = BooleanStrShortEnum.NO
                    )
                )
            )
        )
    ),
    SystemSystemPutUnits(
        params = PutUnitsSystemSystemParamsModel(
            units = [UnitsModel(
                id = 1,
                nameInPanel = 'Unit',
                precisionUnit = 1,
                visible = False,
                descriptions = [DescriptionsSystemModel(
                    language = 'pol',
                    nameSingular = 'Polish',
                    namePlural = 'Polish',
                    nameFractions = 'Polish'
                )]
            )]
        )
    ),
]
