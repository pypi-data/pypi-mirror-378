from enum import IntEnum, StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableSnakeGateway


# --- Enums
class ApiFlagReturnsEnum(StrEnum):
    NONE = 'none'
    REGISTERED = 'registered'
    REALIZED = 'realized'
    REGISTERED_POS = 'registered_pos'
    REALIZED_POS = 'realized_pos'

class DatesTypeEnum(StrEnum):
    DATE_ADD = 'date_add'
    DATE_END = 'date_end'

class StatusEnum(IntEnum):
    RETURN_NOT_HANDLED = 1
    RETURN_ACCEPTED = 2
    RETURN_NOT_ACCEPTED = 3
    RETURN_CANCELED_BY_THE_CUSTOMER = 13
    RETURN_CANCELED = 14
    RESEND_THE_ORDER = 15
    ABORT_RESENDING_ORDER = 16
    A_CUSTOMER_GENERATED_A_RETURN_IT_WILL_BE_DELIVERED_PERSONALLY = 17
    A_CUSTOMER_GENERATED_A_RETURN_IT_WILL_BE_SENT_BY_THE_CUSTOMER = 18


# --- DTOs
class DateModel(BaseModel):
    date_begin: str = Field(..., description="Beginning date in YYYY-MM-DD HH:MM:SS format")
    date_end: str = Field(..., description="Ending date in YYYY-MM-DD HH:MM:SS format")
    dates_type: DatesTypeEnum = Field(..., description="...")

class RangeModel(BaseModel):
    date: DateModel = Field(..., description="Date range")

class ProductsReturnsPostModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="...")
    size: str = Field(..., description="...")
    quantity: float = Field(..., description="...")
    price: float = Field(..., description="...")
    serialNumbers: List[str] = Field(..., description="...")
    productOrderAdditional: str = Field(..., description="Additional information")

class ReturnProductsPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="...")
    size: str = Field(..., description="...")
    quantity: float = Field(..., description="...")
    price: float = Field(..., description="Price")
    serialNumbers: List[str] = Field(..., description="...")
    productOrderAdditional: str = Field(..., description="Additional information")

class ReturnsPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="...")
    status: StrictInt = Field(..., ge=1, description="...")
    apiFlag: ApiFlagReturnsEnum = Field(..., description="Flag informing on order registration or completion in external program through API")
    products: List[ReturnProductsPutModel] = Field(..., description="Products list")
    userNote: str = Field(..., description="...")
    clientNote: str = Field(..., description="...")
    tryCorrectInvoice: bool = Field(..., description="...")

class PostOmsReturnsParamsModel(BaseModel):
    order_sn: StrictInt = Field(..., ge=1, description="...")
    stock_id: StrictInt = Field(..., ge=1, description="...")
    products: List[ProductsReturnsPostModel] = Field(..., description="Products list")
    status: StrictInt = Field(..., description="...")
    client_received: bool = Field(..., description="...")
    change_status: bool = Field(..., description="...")
    courier_id: int | str = Field(..., description=".")
    return_operator: str = Field(..., description="...")
    tryCorrectInvoice: bool = Field(..., description="...")
    include_shipping_cost: str = Field(..., description="...")
    additional_payment_cost: str = Field(..., description="...")
    emptyReturn: str = Field(..., description="...")

class PutOmsReturnsParamsModel(BaseModel):
    returns: List[ReturnsPutModel] = Field(..., description="...")

class SerialNumberProductsPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Product ID")
    size: str = Field(..., description="Size ID")
    serialNumbers: List[str] = Field(..., description="...")

class PutSerialNumberOmsReturnsParamsModel(BaseModel):
    return_id: StrictInt = Field(..., ge=1, description="Return number")
    products: List[SerialNumberProductsPutModel] = Field(..., description="Products list")


# --- ENDPOINTS
class Get(PageableSnakeGateway):
    """
    Method that enables getting information about returns issued for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/returnsreturnsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/returns/returns')

    order_sn: StrictInt | None = Field(None, ge=1, description="Search by the order serial number to which a return was added (>=1)")
    return_id: StrictInt | None = Field(None, ge=1, description="Search by return ID (>=1)")
    return_shipping_number: str | None = Field(None, min_length=1, description="Search by a return shipment number from a customer to the shop")
    range: RangeModel | None = Field(None, description="Date range")
    status: StatusEnum | None = Field(None, description="Return status (optional)")
    return_ids: List[StrictInt] | None = Field(None, min_length=1, description="Search by return IDs (list, each >= 1)") # type: ignore
    stock_id: StrictInt | None = Field(None, ge=1, description="Search by ID of a stock to which a return is sent (>=1)")
    bundleAsProducts: bool = Field(False, description="Return a set as its constituent products")

class Post(AppendableGateway):
    """
    ...
    DOCS_URL: https://idosell.readme.io/reference/returnsreturnspost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/returns/returns')

    params: PostOmsReturnsParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    ...
    DOCS_URL: https://idosell.readme.io/reference/returnsreturnsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/returns/returns')

    params: PutOmsReturnsParamsModel = Field(..., description="Parameters transmitted to method")

class PutSerialNumber(AppendableGateway):
    """
    Method that enables setting serial numbers for products included in returns issued for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/returnsserialnumberput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/returns/serialNumber')

    params: PutSerialNumberOmsReturnsParamsModel = Field(..., description="Parameters transmitted to method")

class GetStatuses(Gateway):
    """
    Allows to download all configurable return statuses
    DOCS_URL: https://idosell.readme.io/reference/returnsstatusesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/returns/statuses')
