from __future__ import annotations
from datetime import date, datetime, time
from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway


# --- Enums
class DirectionTypeEnum(StrEnum):
    ASC = 'asc'
    DESC = 'desc'

class OrderByDirectionEnum(StrEnum):
    ASC = 'asc'
    DESC = 'desc'

class OrderByPropertyEnum(StrEnum):
    ID = 'id'
    STATUS = 'status'
    NUMBEROFORDERS = 'numberOfOrders'
    CREATEDATETIME = 'createDateTime'
    UPCOMINGDELIVERYDATE = 'upcomingDeliveryDate'
    NEXTDELIVERYDATE = 'nextDeliveryDate'
    CLIENTBILLINGDATA = 'clientBillingData'

class PriceChangeModeEnum(StrEnum):
    AUTO = 'auto'
    MANUAL = 'manual'

class PropertyTypeEnum(StrEnum):
    ID = 'id'
    PRICE = 'price'
    NETPRICE = 'netPrice'

class SubscriptionsStatusEnum(StrEnum):
    ACTIVE = 'active'
    HOLD = 'hold'
    NONPAYMENT = 'nonpayment'
    FINISHED = 'finished'

class SubscriptionsTypeEnum(StrEnum):
    PERCENTAGE = 'percentage'
    QUOTA = 'quota'


# --- DTOs
class DateTimeModel(BaseModel):
    from_: time = Field(..., description="Time 'from' (RFC, UTC)", alias="from")
    to: time = Field(..., description="Time 'to' (RFC, UTC)")

class DateRangeModel(BaseModel):
    from_: date = Field(..., description="Date 'from' (RFC, UTC)", alias="from")
    to: date = Field(..., description="Date 'to' (RFC, UTC)")

class DateTimeRangeModel(BaseModel):
    from_: datetime = Field(..., description="DateTime 'from' (RFC, UTC)", alias="from")
    to: datetime = Field(..., description="DateTime 'to' (RFC, UTC)")

class ValueModel(BaseModel):
    value: str = Field(..., description="A decimal")

class DeliveryCostModel(BaseModel):
    value: str = Field(..., description="A decimal")

class OrderDeliveryModel(BaseModel):
    courierNote: str = Field(..., description="Note for courier")
    pickupPointId: str = Field(..., description="Pickup point's identifier")
    deliveryFormId: StrictInt = Field(..., ge=1, description="Delivery's form identifier")
    deliveryAddressId: StrictInt = Field(..., ge=1, description="Client's delivery address ID")

class OrderDataModel(BaseModel):
    deliveryCost: DeliveryCostModel = Field(..., description="A representation of a floating-point number with precise accuracy")
    orderDelivery: OrderDeliveryModel = Field(..., description="...")
    payerAddressId: StrictInt = Field(..., ge=1, description="Payer's address identifier")
    noteToStaff: str = Field(..., description="Note to stuff")

class QuantityModel(BaseModel):
    value: str = Field(..., description="A decimal")

class BundledProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="ID of record in database")
    sizeId: str = Field(..., description="ID of size")
    quantity: QuantityModel = Field(..., description="A representation of a floating-point number with precise accuracy")
    bundledProducts: BundledProductsModel | None = Field(None, description="Bundled items")
    comment: str = Field(..., description="Comment for product")
    splitBundleInOrderDocuments: bool = Field(...,  description="Variable that determinates if bundle should be splitted to seperate positions on order documents")

class ProductAddModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="ID of record in database")
    sizeId: str = Field(..., description="ID of size")
    quantity: QuantityModel = Field(..., description="A representation of a floating-point number with precise accuracy")
    bundledProducts: List[BundledProductsModel] = Field(..., description="Bundled items")
    comment: str = Field(..., description="Comment for product")
    splitBundleInOrderDocuments: bool = Field(..., description="Variable that determinates if bundle should be splitted to seperate positions on order documents")

class AddProductProductsPostModel(BaseModel):
    subscriptionId: StrictInt = Field(..., ge=1, description="Id of subscription")
    products: List[ProductAddModel] = Field(..., description="Collection of products to edit")

class AddProducts(BaseModel):
    subscriptionId: StrictInt = Field(..., ge=1, description="Id of subscription")
    products: List[AddProductProductsPostModel] = Field(..., min_length=1, description="Collection of products to edit") # type: ignore

class SubscriptionsDeliveryDatesModel(BaseModel):
    subscriptionIds: List[int] = Field(..., min_length=1, description="Subscription ids") # type: ignore
    upcomingDeliveryDate: str = Field(..., min_length=1, description="Settings that determinates if price should be updated automaticly")
    changeNextDeliveryDate: bool | None = Field(None, description="A setting that determines whether to also change the date of the next delivery")

class SubscriptionsAutoPriceModel(BaseModel):
    subscriptionIds: List[int] = Field(..., min_length=1, description="Subscription ids") # type: ignore
    autoPriceUpdate: bool | None = Field(None, description="Settings that determinates if price should be updated automaticly")

class SubscriptionDeleteProducts(BaseModel):
    subscriptionId: StrictInt = Field(..., ge=1, description="Id of subscription")
    idsToDelete: List[int] = Field(..., description="Ids in products table to delete")

class RebatesThresholdModel(BaseModel):
    numberFrom: StrictInt = Field(..., ge=1, description="Number from")
    numberTo: StrictInt = Field(..., ge=1, description="Number to")
    type: SubscriptionsTypeEnum = Field(..., description="Type")
    value: ValueModel = Field(..., description="A representation of a floating-point number with precise accuracy")

class PaymentDataModel(BaseModel):
    externalPaymentId: str = Field(..., description="ID of external payment")
    externalPaymentHandle: str = Field(..., description="Handle for external payment")

class SubscriptionModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Subscription ID")
    externalId: str | None = Field(None, description="Subscription ID for external service")
    status: SubscriptionsStatusEnum | None = Field(None, description="Subscription status")
    subscriptionNote: str | None = Field(None, description="Note to subscription (internal)")
    upcomingDeliveryDate: date | None = Field(None, description="Estimated date of the upcoming delivery")
    priceAutoUpdate: bool | None = Field(None, description="Update price automaticly")
    nextDeliveryDate: date | None = Field(None, description="Estimated date of the next delivery")
    daysInPeriod: StrictInt | None = Field(None, ge=1, description="Setting that change subscription period (in days)")
    sendMailAfterStatusChange: bool | None = Field(None, description="Option allowing sending e-mail after status change")
    sendSMSAfterStatusChange: bool | None = Field(None, description="Optian allowing sending SMS after status change")
    orderData: OrderDataModel | None = Field(None, description="...")
    rebatesThresholds: List[RebatesThresholdModel] | None = Field(None, description="Thresholds rebates for newly created subscription orders")
    paymentData: PaymentDataModel | None = Field(None, description="...")

class SubscriptionsEditRequest(BaseModel):
    subscriptionModels: List[SubscriptionModel] = Field(..., min_length=1, description="Subscription") # type: ignore

class PriceModel(BaseModel):
    value: str = Field(..., description="A decimal")

class NetPriceModel(BaseModel):
    value: str = Field(..., description="A decimal")

class FilterModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Identyfier of action where products are")

class EditProductPostModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID of record in database")
    variantId: StrictInt = Field(..., ge=1, description="The variant ID you want to change to")
    variantSizeId: str = Field(..., description="ID of variant's size")
    quantity: QuantityModel = Field(..., description="A representation of a floating-point number with precise accuracy")
    price: PriceModel = Field(..., description="A representation of a floating-point number with precise accuracy")
    netPrice: NetPriceModel = Field(..., description="A representation of a floating-point number with precise accuracy")
    label: str = Field(..., description="Label to the product")

class SubscriptionEditProducts(BaseModel):
    subscriptionId: StrictInt = Field(..., description="Id of subscription")
    products: List[EditProductPostModel] = Field(..., description="Collection of products to edit")

class OrderByModel(BaseModel):
    property: PropertyTypeEnum = Field(..., description="Order by property")
    direction: DirectionTypeEnum = Field(..., description="Order by direction")

class PaginationModel(BaseModel):
    page: StrictInt = Field(..., ge=0, description="Page index (starting from 0)")
    perPage: StrictInt = Field(..., ge=1, description="Number of records per page")


class ItemsListRequestPostModel(BaseModel):
    filter: FilterModel = Field(..., description="...")
    orderBy: OrderByModel = Field(..., description="...")
    pagination: PaginationModel = Field(..., description="...")

class ListViewFetchIdsFilterPostModel(BaseModel):
    ids: List[int] = Field(..., description="Subscription IDs")
    statuses: List[str] = Field(..., description="Subscription statuses")
    clientId: StrictInt = Field(..., ge=1, description="Client ID")
    shopId: StrictInt = Field(..., ge=1, description="Shop ID")
    priceChangeMode: PriceChangeModeEnum = Field(..., description="Price change mode")
    createDateTime: DateTimeRangeModel = Field(..., description="...")
    finishDateTime: DateTimeRangeModel = Field(..., description="...")
    upcomingDeliveryDate: DateRangeModel = Field(..., description="...")
    nextDeliveryDate: DateRangeModel = Field(..., description="...")
    textSearch: str = Field(..., description="Text search phrase")

class ListViewSelectModel(BaseModel):
    productsData: bool = Field(..., description="...")
    rebatesThresholds: bool = Field(..., description="...")
    rebateCode: bool = Field(..., description="...")
    paymentData: bool = Field(..., description="...")
    clientBillingData: bool = Field(..., description="...")
    orderDeliveryAddress: bool = Field(..., description="...")
    courierData: bool = Field(..., description="...")
    payerAddress: bool = Field(..., description="...")

class ListViewFilterModel(BaseModel):
    ids: List[int] = Field(..., description="Subscription IDs")
    statuses: List[str] = Field(..., description="Subscription statuses")
    clientId: StrictInt = Field(..., ge=1, description="Client ID")
    shopId: StrictInt = Field(..., ge=1, description="Client ID")
    priceChangeMode: PriceChangeModeEnum = Field(..., description="Price change mode")
    createDateTime: DateTimeModel = Field(..., description="...")
    finishDateTime: DateTimeModel = Field(..., description="...")
    upcomingDeliveryDate: DateTimeModel = Field(..., description="...")
    nextDeliveryDate: DateTimeModel = Field(..., description="...")
    textSearch: str = Field(..., description="Text search phrase")

class ListViewOrderByModel(BaseModel):
    property: OrderByPropertyEnum = Field(..., description="A property or combination for sorting the results")
    orderByDirection: OrderByDirectionEnum = Field(..., description="Order direction")

class ListViewPaginationModel(BaseModel):
    page: StrictInt = Field(..., ge=0, description="Page index (starting from 0)")
    perPage: StrictInt = Field(..., ge=1, le=1000, description="Number of records per page")

class ListViewListRequestPostModel(BaseModel):
    select: ListViewSelectModel = Field(..., description="...")
    filter: ListViewFilterModel = Field(..., description="Filters that limit the result of a customer query")
    orderBy: ListViewOrderByModel = Field(..., description="Order by settings")
    pagination: ListViewPaginationModel = Field(..., description="Pagination settings")

class SetRebateCodeRequestPostModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="")
    code: str = Field(..., description="")

class UnsetRebateCodeRequestPostModel(BaseModel):
    id: StrictInt = Field(..., description="Subscription ID")

class SubscriptionsStatusModel(BaseModel):
    subscriptionIds: List[int] = Field(..., description="Subscription ids")
    subscriptionStatus: SubscriptionsStatusEnum = Field(..., description="Status to set")
    sendMailAfterStatusChange: bool = Field(..., description="Option allowing sending e-mail after status change")
    sendSMSAfterStatusChange: bool = Field(..., description="Optian allowing sending SMS after status change")


# --- ENDPOINTS
class PostAddProduct(Gateway):
    """
    The method allowing adding products to subscription
    DOCS_URL: https://idosell.readme.io/reference/subscriptionsaddproductpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/addProduct')

    addProducts: AddProducts = Field(..., description="...")

class PostChangeDeliveryDates(Gateway):
    """
    The method allowing to change subscriptions delivery dates
    DOCS_URL: https://idosell.readme.io/reference/subscriptionschangedeliverydatespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/changeDeliveryDates')

    subscriptionsDeliveryDatesModel: SubscriptionsDeliveryDatesModel = Field(..., description="...")

class PostChangePriceAutoUpdate(Gateway):
    """
    The method allowing to change subscriptions price auto update setting
    DOCS_URL: https://idosell.readme.io/reference/subscriptionschangepriceautoupdatepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/changePriceAutoUpdate')

    subscriptionsAutoPriceModel: SubscriptionsAutoPriceModel = Field(..., description="...")

class PostChangeStatus(Gateway):
    """
    The method allowing to change subscriptions status
    DOCS_URL: https://idosell.readme.io/reference/subscriptionschangestatuspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/changeStatus')

    subscriptionsStatusModel: SubscriptionsStatusModel = Field(..., description="...")

class DeleteProduct(Gateway):
    """
    The method allowing for products in subscription removeing
    DOCS_URL: https://idosell.readme.io/reference/subscriptionsdeleteproductpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/deleteProduct')

    subscriptionDeleteProducts: SubscriptionDeleteProducts = Field(..., description="...")

class PostEdit(Gateway):
    """
    The method allowing for subscription editing
    DOCS_URL: https://idosell.readme.io/reference/subscriptionseditpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/edit')

    subscriptionsEditRequest: SubscriptionsEditRequest = Field(..., description="Subscriptions model")

class PostEditProduct(Gateway):
    """
    The method allowing for products in subscription editing
    DOCS_URL: https://idosell.readme.io/reference/subscriptionseditproductpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/editProduct')

    subscriptionEditProducts: SubscriptionEditProducts = Field(..., description="...")

class PostItemsList(Gateway):
    """
    List of items assigned to subscription
    DOCS_URL: https://idosell.readme.io/reference/subscriptionsitemslistpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/items/list')

    request: ItemsListRequestPostModel = Field(..., description="...")

class PostListViewFetchIds(Gateway):
    """
    List of subscriptions ID's of the store
    DOCS_URL: https://idosell.readme.io/reference/subscriptionslistviewfetchidspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/listView/fetchIds')

    filter: ListViewFetchIdsFilterPostModel = Field(..., description="Filters that limit the result of a customer query")

class PostListViewList(Gateway):
    """
    List of subscriptions of the store. Allows you to download data for editing and basic statistics
    DOCS_URL: https://idosell.readme.io/reference/subscriptionslistviewlistpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/listView/list')

    request: ListViewListRequestPostModel = Field(..., description="Object describing the request for a list of Subscriptions")

class PostSetRebateCode(Gateway):
    """
    The method for set rebate code
    DOCS_URL: https://idosell.readme.io/reference/subscriptionssetrebatecodepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/setRebateCode')

    request: SetRebateCodeRequestPostModel = Field(..., description="Object with discount code data to set")

class PostUnsetRebateCode(Gateway):
    """
    The method for set rebate code
    DOCS_URL: https://idosell.readme.io/reference/subscriptionsunsetrebatecodepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/subscriptions/unsetRebateCode')

    request: UnsetRebateCodeRequestPostModel = Field(..., description="Object with request witch unset rebate code")
