
from enum import StrEnum
from pydantic import BaseModel, Field, StrictInt

from src.idosell._common import AllYNEnum, BooleanStrShortEnum


# --- Enums
class ClientTypeEnum(StrEnum):
    ALL = 'all'
    UNREGISTERED = 'unregistered'
    REGISTERED = 'registered'
    RETAILER = 'retailer'
    WHOLESALER = 'wholesaler'

class PageEnum(StrEnum):
    HOME = 'home'
    BASKET = 'basket'
    CHECKOUT_PAYMENT_DELIVERY = 'checkout_payment_delivery'
    CHECKOUT_CONFIRMATION = 'checkout_confirmation'
    NEW_ORDER_PLACEMENT = 'new_order_placement'
    ORDER_DETAILS = 'order_details'
    NAVIGATION = 'navigation'
    PRODUCT_DETAILS = 'product_details'
    SEARCH_RESULTS = 'search_results'
    AFTER_ORDER_PLACE = 'after_order_place'
    MAILING_SUBSCRIBE = 'mailing_subscribe'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_ERROR = 'payment_error'
    PAYMENT_PENDING = 'payment_pending'
    OTHER_PAGES = 'other_pages'

class ZoneEnum(StrEnum):
    HEAD = 'head'
    BODYBEGIN = 'bodyBegin'
    BODYEND = 'bodyEnd'


# --- Model DTOs
class BodyModel(BaseModel):
    lang: str = Field(..., min_length=3, max_length=3, description="Language code")
    body: str = Field(..., description="...")

class DisplayBaseModel(BaseModel):
    clientType: ClientTypeEnum = Field(..., description="Type of customers to whom to display the snippet")
    newsletter: AllYNEnum = Field(..., description="Whether to display only for newsletter visitors")
    hasOrders: AllYNEnum = Field(..., description="Whether to display the code snippet only for customers who have placed an order")
    useRebateCode: AllYNEnum = Field(..., description="Display only after entering rebate code")

class SourceFilterModel(BaseModel):
    active: BooleanStrShortEnum = Field(..., description="Whether source filter is active")
    id: StrictInt = Field(..., ge=1, description="Id of service of given source")

class SourceModel(BaseModel):
    direct: SourceFilterModel = Field(..., description="...")
    search: SourceFilterModel = Field(..., description="...")
    advert: SourceFilterModel = Field(..., description="...")
    priceComparers: SourceFilterModel = Field(..., description="...")
    affiliate: SourceFilterModel = Field(..., description="...")
    cpa: SourceFilterModel = Field(..., description="...")
    newsletter: SourceFilterModel = Field(..., description="...")
    social: SourceFilterModel = Field(..., description="...")
    page: SourceFilterModel = Field(..., description="...")
