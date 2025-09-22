from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, StrictInt, constr

from src.idosell._common import BooleanStrShortEnum


# --- Types
Currency = constr(pattern=r'^[A-Z]{3}$', min_length=3, max_length=3)


# --- Enums
class OperatingModeEnum(StrEnum):
    OPEN_IN = 'open_in'
    CLOSED = 'closed'
    H24 = '24h'

class PaymentFormsEnum(StrEnum):
    CASH = 'cash'
    CARD = 'card'

class ServiceStatusEnum(StrEnum):
    AVAILABLE = 'available'
    OUT_OF_SERVICE = 'out_of_service'

# --- Enums
class CurrencyRateEnum(StrEnum):
    CURRENTDAY = 'currentDay'
    PREVIOUSDAY = 'previousDay'

class MainStockSystemEnum(StrEnum):
    IAI = 'iai'
    OTHER = 'other'

class UserTypeEnum(StrEnum):
    ALL = 'all'
    ACTIVE = 'active'

class SaleDateEnum(StrEnum):
    SALEDATEFROMORDER = 'saleDateFromOrder'
    SALEDATEFROMPAYMENT = 'saleDateFromPayment'
    SALEDATEFROMDOCUMENT = 'saleDateFromDocument'

class StockStateConfigEnum(StrEnum):
    BRIDGE = 'bridge'
    OUTSIDE = 'outside'
    UNCONTROLLED = 'uncontrolled'


# --- Couriers DTOs
class AddressModel(BaseModel):
    street: str = Field(..., description="Address")
    zipCode: str = Field(..., description="ZIP / Post code")
    city: str = Field(..., description="Town / City")
    provinceCode: str = Field(..., description="Administrative region (code in ISO-3166-2)")

class CoordinatesModel(BaseModel):
    longitude: float = Field(..., description="Longitude")
    latitude: float = Field(..., description="Latitude")

class DescriptionsCouriersModel(BaseModel):
    languageId: str = Field(..., description="Language ID (code in ISO-639-2)")
    name: str = Field(..., description="Name of the pickup point")
    description: str = Field(..., description="collection point description ")

class OperatingDaysModel(BaseModel):
    weekday: StrictInt = Field(..., ge=1, le=7, description="Days of the week designation.Day number: 1- Monday, 7 - Sunday")
    opening: str = Field(..., description="collection point opening hours (HH:MM)")
    closing: str = Field(..., description="collection point closing time (HH:MM)")
    operatingMode: OperatingModeEnum = Field(..., description="!trybPracyPunktuDostepneWartosciOpenInOtwartyOdDoClosedZamkniety24hCzynnyCalaDobe!#")

class PickupPointDeleteRequestsPostModel(BaseModel):
    pickupPointId: str = Field(..., description="Collection point ID")
    pickupPointExternalId: str = Field(..., description="external system code")
    courierId: StrictInt = Field(..., description="Courier ID")

class PickupPointsPostModel(BaseModel):
    pickupPointExternalId: str = Field(..., description="external system code")
    courierId: StrictInt = Field(..., description="Courier ID")
    descriptions: List[DescriptionsCouriersModel] = Field(..., description="collection point details")
    paymentForms: List[str] = Field(..., description="Accepted payment types")
    serviceStatus: ServiceStatusEnum = Field(..., description="Collection point activity. Available values: available, outOfService ")
    address: AddressModel = Field(..., description="Pickup point address")
    coordinates: CoordinatesModel = Field(..., description="Geographic coordinates")
    operatingDays: List[OperatingDaysModel] = Field(..., description="Personal collection point work hours")

class PickupPointsPutModel(BaseModel):
    pickupPointId: str = Field(..., description="Collection point ID")
    pickupPointExternalId: str = Field(..., description="External system code")
    courierId: StrictInt = Field(..., ge=1, description="Courier ID")
    descriptions: List[DescriptionsCouriersModel] = Field(..., description="Collection point details")
    paymentForms: List[PaymentFormsEnum] = Field(..., description="Accepted payment types")
    serviceStatus: ServiceStatusEnum = Field(..., description="Collection point activity")
    address: AddressModel = Field(..., description="Pickup point address")
    coordinates: CoordinatesModel = Field(..., description="Geographic coordinates")
    operatingDays: List[OperatingDaysModel] = Field(..., description="Personal collection point work hours")

# --- System DTOs
class BlockIfIncorrectStockQuantitiesModel(BaseModel):
    finished: BooleanStrShortEnum = Field(..., description="y/n")

class CurrenciesModel(BaseModel):
    id: Currency = Field(..., description="Currency code in ISO-4217 (3 letters)")
    rate: float = Field(..., le=10000, description="Currency exchange rate. Maximal value is 10000")
    scale: StrictInt = Field(..., ge=1, description="Currency smaller unit")

class DescriptionsSystemModel(BaseModel):
    language: str = Field(..., description="ISO-639-3")
    nameSingular: str = Field(..., max_length=30, description="Name (singular) (limit of 30 characters)")
    namePlural: str = Field(..., max_length=30, description="Name (plural) (limit of 30 characters)")
    nameFractions: str = Field(..., description="Name (by fractions) (limit of 30 characters)")

class RestrictionsModel(BaseModel):
    blockIfIncorrectStockQuantities: BlockIfIncorrectStockQuantitiesModel = Field(..., description="Block the ability of selecting a status, if there are products in the warehouse from which the order is being processed, with insufficient stock level")

class OrdersModel(BaseModel):
    alwaysAllowSentStatus: BooleanStrShortEnum = Field(..., description="Allow the status to be changed to 'Shipped' even if the order payments and stock levels do not match")
    restrictions: RestrictionsModel = Field(..., description="Order management restrictions")

class TaxSettingsModel(BaseModel):
    saleDatePrepaid: SaleDateEnum = Field(..., description="Sales date settings on sales documents for prepaid orders")
    saleDateCashOnDelivery: SaleDateEnum = Field(..., description="Sales date settings on sales documents for orders paid with cash on delivery")
    saleDateTradeCredit: SaleDateEnum = Field(..., description="Sales date settings on sales documents for orders paid with trade credit")
    currencyRate: CurrencyRateEnum = Field(..., description="Configuration of default currency rate for orders")

class ShopsModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    salesDocumentsAreCreatedByClient: BooleanStrShortEnum = Field(..., description="Sales documents in third party application")

class PanelSettingsModel(BaseModel):
    mainStockSystem: MainStockSystemEnum = Field(..., description="The main warehouse and sales system")
    stockStateConfig: StockStateConfigEnum = Field(..., description="Stock quantities in third party application")
    taxSettings: TaxSettingsModel = Field(..., description="Fiscal and settlement settings")
    shops: List[ShopsModel] = Field(..., description="...")

class RestictionModel(BaseModel):
    blockIfIncorrectStockQuantities: BlockIfIncorrectStockQuantitiesModel = Field(..., description="Block the ability of selecting a status, if there are products in the warehouse from which the order is being processed, with insufficient stock level")

class UnitDescriptionModel(BaseModel):
    language: str = Field(..., max_length=30, description="ISO-639-3")
    nameSingular: str = Field(..., max_length=30, description="Name (singular) (limit of 30 characters)")
    namePlural: str = Field(..., max_length=30, description="Name (plural) (limit of 30 characters)")
    nameFractions: str = Field(..., max_length=30, description="Name (plural) (limit of 30 characters)")

class UnitsModel(BaseModel):
    id: StrictInt = Field(..., description="!IdentyfikatorJednostki!#")
    nameInPanel: str = Field(..., max_length=30, description="Name in panel (limit of 30 characters)")
    precisionUnit: StrictInt = Field(..., description="Accuracy (number of places after comma)")
    visible: bool =  Field(..., description="Visibility")
    descriptions: List[DescriptionsSystemModel] = Field(..., description="Unit names")
