from enum import StrEnum
from typing import List
from pydantic import BaseModel, ConfigDict, Field, StrictInt


# --- Enums
class DateTypeEnum(StrEnum):
    OPEN = 'open'
    MODIFY = 'modify'
    CLOSE = 'close'
    STOCKOPERATION = 'stockOperation'

class DateRangeOpenedDocumentsModel(StrEnum):
    OPEN = 'open'
    MODIFY = 'modify'

class DocumentTypeEnum(StrEnum):
    PZ = 'pz'
    PW = 'pw'
    PX = 'px'
    RX = 'rx'
    RW = 'rw'
    MM = 'mm'

class DocumentTypeFullEnum(StrEnum):
    PZ = 'pz'
    PW = 'pw'
    PX = 'px'
    RX = 'rx'
    RW = 'rw'
    MM = 'mm'
    WZ = 'wz'
    ZW = 'zw'

class StockDocumentStatusEnum(StrEnum):
    OPEN = 'open'
    ON_THE_WAY = 'on_the_way'
    CLOSE = 'close'

class DocumentsWntEnum(StrEnum):
    NATIONAL_VAT_INVOICE = 'national_VAT_invoice'
    OTHER_PURCHASE_DOCUMENT = 'other_purchase_document'
    INVOICE_WITHOUT_VAT = 'invoice_without_VAT'
    IMPORTS_FROM_OUTSIDE_THE_EU = 'imports_from_outside_the_EU'

class DocumentsConfirmedEnum(StrEnum):
    OPEN = 'open'
    ON_THE_WAY = 'on_the_way'

class DocumentsPriceTypeEnum(StrEnum):
    BRUTTO = 'brutto'
    NETTO = 'netto'

class DocumentsQueueTypeEnum(StrEnum):
    FIFO = 'fifo'
    LIFO = 'lifo'

class DocumentsCurrencyForPurchasePriceRateTypeEnum(StrEnum):
    CUSTOM = 'custom'
    CURRENTDAY = 'currentDay'
    CUSTOMDAY = 'customDay'
    PREVIOUSDAY = 'previousDay'

class OpenedDocumentsStatusEnum(StrEnum):
    OPEN = 'open'
    ON_THE_WAY = 'on_the_way'
    ALL = 'all'

class ReturnElementsEnum(StrEnum):
    LOCATIONNAME = 'locationName'
    LOCATIONPATH = 'locationPath'
    LOCATIONCODE = 'locationCode'
    STOCKID = 'stockId'
    PRODUCTS = 'products'


# --- Stocks DTOs
class DateRangeModel(BaseModel):
    dateType: DateTypeEnum = Field(..., description="The type of date by which documents are searched")
    dateBegin: str = Field(..., description="Beginning date in YYYY-MM-DD HH:MM:SS format")
    dateEnd: str = Field(..., description="Ending date in YYYY-MM-DD HH:MM:SS format")

class ProductsDeleteModel(BaseModel):
    product: StrictInt = Field(..., ge=1, description="Stock keeping unit")
    size: str = Field(..., description="Product size ID")

class ProductsModel(BaseModel):
    type: str = Field(..., description="...")
    id: StrictInt = Field(..., description="Document identifier")

class ProductsPostPutModel(BaseModel):
    product: StrictInt = Field(..., ge=1, description="Stock keeping unit")
    size:  str = Field(..., description="Product size ID")
    quantity:  StrictInt = Field(..., ge=1, description="Product quantity")
    productPurchasePrice: float = Field(..., gt=0, description="Cost price")
    locationId: StrictInt = Field(..., description="Warehouse location ID. The list of available warehouse locations can be downloaded via the method #get in gateway Locations")
    locationCode: str = Field(..., description="Storage location code")
    locationTextId: str = Field(..., description="Warehouse location full path. Use a backslash () as a separator, for example: M1\Section name\Location name. The list of available warehouse locations can be downloaded via the method #get in gateway Locations") # type: ignore

# --- Suppliers DTOs
class AverageDeliveryTimeModel(BaseModel):
    value: StrictInt = Field(..., ge=1, description="value")
    unit: str = Field(..., description="Unit")

class OrderCompletionTimeModel(BaseModel):
    value: StrictInt = Field(..., ge=1, description="value")
    unit: str = Field(..., description="Unit")

class WorkDaysModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    day: StrictInt = Field(..., ge=1, description="day")
    type: str = Field(..., description="")
    start_time: str = Field(..., description="from", alias="from")
    end_time: str = Field(..., description="to", alias="to")

class SuppliersModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Id")
    name: str = Field(..., description="Name")
    email: str = Field(..., description="e-mail address. (limit of 50 characters)")
    phone: str = Field(..., description="Phone number. (limit of 20 characters)")
    fax: str = Field(..., description="Fax. (limit of 20 characters)")
    street: str = Field(..., description="Address. (limit of 50 characters)")
    zipCode: str = Field(..., description="ZIP / Post code. (limit of 6 characters)")
    city: str = Field(..., description="Town / City. (limit of 50 characters)")
    country: StrictInt = Field(..., ge=1, description="Region ID")
    taxCode: str = Field(..., description="VAT no.. (limit of 13 characters)")
    averageDeliveryTime: AverageDeliveryTimeModel = Field(..., description="Average delivery time")
    description: str = Field(..., description="Description. (limit of 255 characters)")
    orderCompletionTime: OrderCompletionTimeModel = Field(..., description="Order preparation time for shipment")
    workDays: List[WorkDaysModel] = Field(..., description="Supplier working hours")
