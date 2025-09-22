from __future__ import annotations
from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, StrictInt

from src.idosell._common import BooleanStrShortEnum, ElementNameSearchEnum, ErrorsModel, PayerAddressBaseModel, SortDirectionSearchEnum


# --- Orders Enums
class ApiFlagEnum(StrEnum):
    NONE = 'none'
    REGISTERED = 'registered'
    REALIZED = 'realized'
    REGISTERED_POS = 'registered_pos'
    REALIZED_POS = 'realized_pos'
    REGISTRATION_FAULT = 'registration_fault'

class ApplicationTypeEnum(StrEnum):
    SUBIEKTGT = 'SubiektGT'
    RACHMISTRZ = 'Rachmistrz'
    WFIRMA = 'wFirma'

class AuctionsServicesNamesEnum(StrEnum):
    ALLEGRO = 'allegro' # Allegro.pl,
    TESTWEBAPI = 'testwebapi' # Allegro.pl test site,
    EBAY = 'ebay' # eBay.

class ClientRequestInvoiceEnum(StrEnum):
    Y = 'y'
    E = 'e' # yes (electronic invoicing )
    N = 'n'

class ClientRequestInvoiceSearchUnfinishedEnum(StrEnum):
    INVOICE = 'invoice' # yes (paper invoicing)
    E_INVOICE = 'e_invoice' # yes (electronic invoicing)
    N = 'no' # no

class ClientsSearchTypeEnum(StrEnum):
    ID = 'id'
    LOGIN = 'login'
    CODEEXTERN = 'codeExtern'

class ClientSearchingModeEnum(StrEnum):
    BILLING_DATA = 'billing_data'
    DELIVERY_DATA = 'delivery_data'
    BILLING_DELIVERY_DATA = 'billing_delivery_data'

class DocumentTypeOrdersGetEnum(StrEnum):
    SALES_CONFIRMATION = 'sales_confirmation'
    VAT_INVOICE = 'vat_invoice'
    CORRECTIVE_VAT_INVOICE = 'corrective_vat_invoice'
    ADVANCE_VAT_INVOICE = 'advance_vat_invoice'
    FINAL_ADVANCE_VAT_INVOICE = 'final_advance_vat_invoice'
    PRO_FORMA_INVOICE = 'pro_forma_invoice'
    ADVANCE_PRO_FORMA_INVOICE = 'advance_pro_forma_invoice'
    FINAL_ADVANCE_PRO_FORMA_INVOICE = 'final_advance_pro_forma_invoice'
    DELIVERY_NOTE = 'delivery_note'
    FISCAL_RECEIPT = 'fiscal_receipt'
    FISCAL_INVOICE = 'fiscal_invoice'
    OTHER = 'other'

class DocumentTypePostEnum(StrEnum):
    VAT_INVOICE = 'vat_invoice'
    FISCAL_INVOICE = 'fiscal_invoice'
    CORRECTIVE_VAT_INVOICE = 'corrective_vat_invoice'
    FISCAL_RECEIPT = 'fiscal_receipt'
    SALES_CONFIRMATION ='sales_confirmation'

class DocumentTypeEppEnum(StrEnum):
    ALL = 'all'
    STOCKS = 'stocks'
    INVOICE = 'invoice'
    PAYMENTS = 'payments'

class DocumentTypeJpkEnum(StrEnum):
    JPK_FA = 'JPK_FA'
    JPK_MAG = 'JPK_MAG'
    JPK_VAT = 'JPK_VAT'

class DropshippingOrderStatusEnum(StrEnum):
    ALL = 'all' # all,
    FINISHED = 'finished' # sent,
    CANCELED = 'canceled' # canceled,
    NOTCANCELED = 'notCanceled' # failed to cancel.

class ElementNameOrdersBySearchUnfinshedEnum(StrEnum):
    ID = 'id' # product ID,
    SN = 'sn' # Order serial number,
    ORDER_TIME = 'order_time' # time of order,
    STATUS = 'status' # Order status,
    ORDER_SOURCE = 'order_source' # Order source,
    ORDER_COST = 'order_cost' # Order amount,
    DISCOUNT_CODE = 'discount_code' # Discount code,
    READY_TO_SEND_DATE = 'ready_to_send_date' # Ready to ship.

class EmailProcessingConsentEnum(StrEnum):
    YES = 'yes'
    NO = 'no'
    DISABLED = 'disabled'

class EventTypeEnum(StrEnum):
    ORDER = 'order'
    RMA = 'rma'
    RETURN = 'return'

class ExternalStockIdEnum(StrEnum):
    AMAZONDE = 'amazonde'
    AMAZONES = 'amazones'
    AMAZONFR = 'amazonfr'
    AMAZONIT = 'amazonit'
    AMAZONCOUK = 'amazoncouk'
    AMAZONNL = 'amazonnl'
    AMAZONSE = 'amazonse'
    AMAZONCOMTR = 'amazoncomtr'
    AMAZONAE = 'amazonae'
    AMAZONUS = 'amazonus'
    AMAZONPL = 'amazonpl'

class IdentTypeEnum(StrEnum):
    ORDERS_ID = 'orders_id'
    ORDERS_SN = 'orders_sn'

class ImagesTypeEnum(StrEnum):
    PRODUCT = 'product'
    PACKAGE = 'package'

class LoyaltyPointsModeEnum(StrEnum):
    ALL = 'all'
    GIVEN = 'given'
    TAKEN = 'taken'
    GIVEN_OR_TAKEN = 'given_or_taken'
    GIVEN_AND_TAKEN = 'given_and_taken'
    NOT_GIVEN_NOR_TAKEN = 'not_given_nor_taken'

class OpinionsRateEnum(StrEnum):
    POSITIVE = 'positive'
    NEGATIVE = 'negative'

class OrderPaymentTypeEnum(StrEnum):
    CASH_ON_DELIVERY = 'cash_on_delivery'
    PREPAID = 'prepaid'
    TRADECREDIT = 'tradecredit'

class OrderPrepaidStatusEnum(StrEnum):
    UNPAID = 'unpaid' # not paid
    RESTORED = 'restored' # returned
    WAITING = 'waiting' # not registered

class OrdersDateTypeEnum(StrEnum):
    ADD = 'add' # date of order was placed,
    MODIFIED = 'modified' # date of order modification,
    DISPATCH = 'dispatch' # date or order dispatch,
    PAYMENT = 'payment' # date of order payment,
    LAST_PAYMENTS_OPERATION = 'last_payments_operation' # date of last payment operation,
    DECLARED_PAYMENTS = 'declared_payments' # date of last payment.

class OrdersDatesTypesEnum(StrEnum):
    ADD = 'add' # date of order was placed,
    MODIFIED = 'modified' # date of order modification,
    DISPATCH = 'dispatch' # date or order dispatch,
    PAYMENT = 'payment' # date of order payment,
    LAST_PAYMENTS_OPERATION = 'last_payments_operation' # date of last payment operation,
    DECLARED_PAYMENTS = 'declared_payments' # date of last payment.

class OrdersSearchTypeEnum(StrEnum):
    ID = 'id'
    SERIALNUMBER = 'serialNumber'

class OrderSettledAtPriceEnum(StrEnum):
    GROSS = 'gross'
    NET = 'net'
    NET_WITHOUT_VAT = 'net_without_VAT'

class OrderStatusEnum(StrEnum):
    FINISHED_EXT = 'finished_ext'
    FINISHED = 'finished'
    NEW = 'new'
    PAYMENT_WAITING = 'payment_waiting'
    DELIVERY_WAITING = 'delivery_waiting'
    ON_ORDER = 'on_order'
    PACKED = 'packed'
    PACKED_FULFILLMENT = 'packed_fulfillment'
    PACKED_READY = 'packed_ready'
    READY = 'ready'
    WAIT_FOR_DISPATCH = 'wait_for_dispatch'
    SUSPENDED = 'suspended'
    JOINED = 'joined'
    MISSING = 'missing'
    LOST = 'lost'
    FALSE = 'false'
    CANCELED = 'canceled'

class OrdersStatusesEnum(StrEnum):
    NEW = 'new' # not handled
    FINISHED = 'finished' # completed
    FALSE = 'false' # false
    LOST = 'lost' # lost
    ON_ORDER = 'on_order' # in progress
    PACKED = 'packed' # being picked
    READY = 'ready' # ready
    CANCELED = 'canceled' # canceled by customer
    PAYMENT_WAITING = 'payment_waiting' # awaiting payment
    DELIVERY_WAITING = 'delivery_waiting' # awaiting delivery
    SUSPENDED = 'suspended' # on hold
    JOINED = 'joined' # merged
    FINISHED_EXT = 'finished_ext' # handled in FA application

class OrdersStatusesSearchUnfinishedEnum(StrEnum):
    NEW = 'new' # not handled
    ON_ORDER = 'on_order' # in progress
    PACKED = 'packed' # being picked
    PACKED_FULLFILMENT = 'packed_fullfilment' # being picked
    PACKED_READY = 'packed_ready' # packed
    READY = 'ready' # ready
    PAYMENT_WAITING = 'payment_waiting' # awaiting payment
    DELIVERY_WAITING = 'delivery_waiting' # awaiting delivery
    WAIT_FOR_DISPATCH = 'wait_for_dispatch' # awaiting dispatch date
    SUSPENDED = 'suspended' # on hold
    FINISHED_EXT = 'finished_ext' # handled in FA application

class OrderTypeEnum(StrEnum):
    RETAIL = 'reatil' # retail order
    WHOLESALE = 'wholesale' # wholesale order

class OrderTypeSearchUnfinishedEnum(StrEnum):
    RETAIL = 'reatil' # retail order
    WHOLESALE = 'wholesale' # wholesale order
    DROPSHIPPING = 'dropshipping' # order to be handled,
    DELIVERER = 'deliverer' # order sent to the supplier.

class ProductIdentTypeEnum(StrEnum):
    ID = 'id'
    INDEX = 'index'
    CODEEXTERN = 'codeExtern'

class ProductQuantityOperationTypeEnum(StrEnum):
    ADD = 'add'
    SUBTRACT = 'subtract'

class SearchingOperatorTypeMatchEnum(StrEnum):
    NO_ASSIGNMENT = 'no_assignment'
    NO_EMPTY = 'no_empty'
    EMPTY = 'empty'

class ShippmentStatusEnum(StrEnum):
    ALL = 'all'
    RECEIVED = 'received'
    NON_RECEIVED = 'non-received'

class SourceTypeEnum(StrEnum):
    BASE64 = 'base64'
    URL = 'url'

class TypeEnum(StrEnum):
    VAT_INVOICE = 'vat_invoice'
    CORRECTIVE_VAT_INVOICE = 'corrective_vat_invoice'
    OTHER = 'other'


# --- Common DTOs
class ShippingStoreCostsModel(BaseModel):
    amount: float = Field(..., ge=0, description="Value")
    tax: float = Field(..., ge=0, description="Value Added Tax")


# --- Orders DTOs
class AdditionalDataModel(BaseModel):
    documentId: str = Field(..., description="Document number")
    documentIssuedDate: str = Field(..., description="The date document was issued in the ISO-8601 format (YYYY-MM-DD)")

class AuctionsParamsModel(BaseModel):
    auctionsServicesNames: List[AuctionsServicesNamesEnum] = Field(..., description="Auction sites names") # Auction sites listing: "allegro" - Allegro.pl, "testwebapi" - Allegro.pl test site, "ebay" - eBay

class AuctionsAccountsModel(BaseModel):
    auctionsAccountId: StrictInt = Field(..., ge=1, description="Auction service account Id")
    auctionsAccountLogin: str = Field(..., description="External marketplace service account name (which the listing was created from)")

class AuctionsClientsModel(BaseModel):
    auctionClientId: str = Field(..., description="Account ID on auction site")
    auctionClientLogin: str = Field(..., description="Account login on auction site")

class CampaignSearchModel(BaseModel):
    campaignId: StrictInt = Field(..., description="Campaign ID")
    discountCodes: List[str] = Field(..., description="Discount codes")

class ClientDeliveryAddressModel(BaseModel):
    clientDeliveryAddressFirstName: str = Field(..., description="Recipient's first name")
    clientDeliveryAddressLastName: str = Field(..., description="Recipient's last name")
    clientDeliveryAddressAdditional: str = Field(..., description="Additional information")
    clientDeliveryAddressStreet: str = Field(..., description="Recipient street and number")
    clientDeliveryAddressZipCode: str = Field(..., description="Recipient's postal code")
    clientDeliveryAddressCity: str = Field(..., description="Recipient's city")
    clientDeliveryAddressCountry: str = Field(..., description="Recipient's country")
    clientDeliveryAddressPhone: str = Field(..., description="Consignee's phone number")

class ClientWithoutAccountDataModel(BaseModel):
    clientFirstName: str = Field(..., description="Customer's first name")
    clientLastName: str = Field(..., description="Customer's last name")
    clientFirm: str = Field(..., description="Customer's company name")
    clientNip: str = Field(..., description="Customer Tax no")
    clientStreet: str = Field(..., description="Street and number")
    clientZipCode: str = Field(..., description="Customer's postal code")
    clientCity: str = Field(..., description="Customer's city")
    clientCountry: str = Field(..., description="Customer's country")
    clientEmail: str = Field(..., description="E-mail address")
    clientPhone1: str = Field(..., description="Cell phone")
    clientPhone2: str = Field(..., description="Land line")
    langId: str = Field(..., description="Language ID")

class ClientsModel(BaseModel):
    clientLogin: str = Field(..., description="Customer's login")
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")
    clientFirstName: str = Field(..., description="Customer's first name")
    clientLastName: str = Field(..., description="Customer's last name")
    clientCity: str = Field(..., description="Customer's city")
    clientEmail: str = Field(..., description="E-mail address")
    clientHasTaxNumber: BooleanStrShortEnum = Field(..., description="Parameter can be used to search for orders assigned to customer with VAT number")
    clientSearchingMode: ClientSearchingModeEnum = Field(..., description="Parameter allows to choose, by which data orders should be searched")
    clientFirm: str = Field(..., description="Customer's company name")
    clientNip: str = Field(..., description="Customer Tax no")
    clientCountryId: str = Field(..., description="Country ID in accordance with ISO-3166")
    clientCountryName: str = Field(..., description="Region name takes priority over clientCountryId")

class ClientsSearchModel(BaseModel):
    type: ClientsSearchTypeEnum = Field(..., description="...")
    value: str = Field(..., description="...")

class ClientsSearchUnfinishedModel(BaseModel):
    clientLogin: str = Field(..., description="Customer's login")
    clientFirstName: str = Field(..., description="Customer's first name")
    clientLastName: str = Field(..., description="Customer's last name")
    clientCity: str = Field(..., description="Customer's city")
    clientEmail: str = Field(..., description="E-mail address")
    clientHasTaxNumber: BooleanStrShortEnum = Field(..., description="Parameter can be used to search for orders assigned to customer with VAT number")
    clientSearchingMode: ClientSearchingModeEnum = Field(..., description="Parameter allows to choose, by which data orders should be searched")
    clientFirm: str = Field(..., description="Customer's company name")
    clientCountryId: str = Field(..., description="Country ID in accordance with ISO-3166")
    clientCountryName: str = Field(..., description="Region name takes priority over clientCountryId")

class DateRangeSearchModel(BaseModel):
    begin: str = Field(..., description="")
    end: str = Field(..., description="")

class DeliveryPackageParametersModel(BaseModel):
    productWeight: StrictInt = Field(..., gt=0, description="Product weight (g)")
    packagingWeight: StrictInt = Field(..., gt=0, description="Packaging weight (g)")

class DevideProductsPutModel(BaseModel):
    basketPosition: StrictInt = Field(..., description="Item in basket")
    quantity: float = Field(..., gt=0, description="Quantity")

class DiscountCodeModel(BaseModel):
    name: str = Field(..., description="Name")

class DocumentsDeleteModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    id: StrictInt = Field(..., ge=1, description="Document identifier")

class DocumentsPostModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    name: str = Field(..., description="File name")
    pdfBase64: str = Field(...,  description="BMP, PNG, JPG, JPEG, GIF or PDF files in Base64 encoding algorithm")
    type: TypeEnum = Field(..., description="Document type")
    returnedInOrderDetails: BooleanStrShortEnum = Field(..., description="Is it to be shown to the customer in the order view")
    additionalData: AdditionalDataModel | None = Field(None, description="Additional information")


class ImagesDeleteModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Attachment ID")

class ImagesOrderModel(BaseModel):
    orderId: str = Field(..., description="Order ID")
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")

class ImagesImagesPostModel(BaseModel):
    type: ImagesTypeEnum = Field(..., description="Type. Available values: product - Product photo, package - Package photo")
    source: str = Field(..., description="Attachment source data, depending on the source type selected in the settings. BMP, PNG, JPG, JPEG, GIF or PDF files in Base64 encoding algorithm")
    name: str = Field(..., description="Name")

class ImagesSettingsPostModel(BaseModel):
    sourceType: SourceTypeEnum = Field(..., description="Source type. Available values: base64 - Attachment data encoded using the base64 algorithm, url - Attachment file link")

class OpinionSearchModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="...")
    language: str = Field(..., description="Customer language ID")
    confirmed: bool = Field(..., description="...")
    host: str = Field(..., description="...")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")

class OrdersSearchModel(BaseModel):
    type: OrdersSearchTypeEnum = Field(..., description="...")
    value: str = Field(..., description="...")

class OrderBySearchModel(BaseModel):
    elementName: ElementNameSearchEnum = Field(..., description="Field name by which a list will be sorted")
    sortDirection: SortDirectionSearchEnum = Field(..., description="Determines sorting direction")

class OrderPackagesPostPutModel(BaseModel):
    eventId: str = Field(..., description="Id")
    eventType: EventTypeEnum = Field(..., description="Type")
    packages: List[PackagesPostPutModel] = Field(..., description="Information on consignments")

class OrderProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    sizeId: str = Field(..., description="Size identifier")
    productSerialNumbers: List[str] = Field(..., description="Serial numbers")

class OrderSourceModel(BaseModel):
    # Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up. https://idosell.readme.io/reference/ordersorderssearchpost
    shopsMask: StrictInt = Field(..., description="Bit mask of shop IDs")
    shopsIds: List[int] = Field(..., description="List of stores IDs When mask is determined, this parameter is omitted")
    auctionsParams: AuctionsParamsModel = Field(..., description="Object used for order searching based on auctions' parameters")
    auctionsItemsIds: List[int] = Field(..., description="Auctions' numbers")
    auctionsAccounts: List[AuctionsAccountsModel] = Field(..., description="Auction sites accounts' data")
    auctionsClients: List[AuctionsClientsModel] = Field(..., description="Client's account on auction site data")

class OrderSourceSearchUnfinishedModel(BaseModel):
    # Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up. https://idosell.readme.io/reference/ordersorderssearchpost
    shopsMask: StrictInt = Field(..., description="Bit mask of shop IDs")
    shopsIds: List[int] = Field(..., description="List of stores IDs When mask is determined, this parameter is omitted")
    auctionsParams: AuctionsParamsModel = Field(..., description="Object used for order searching based on auctions' parameters")
    auctionsItemsIds: List[int] = Field(..., description="Auctions' numbers")
    auctionsAccounts: List[AuctionsAccountsModel] = Field(..., description="Auction sites accounts' data")
    auctionsClients: List[AuctionsClientsModel] = Field(..., description="Client's account on auction site data")

class OrdersDateRangeModel(BaseModel):
    ordersDateType: OrdersDateTypeEnum = Field(..., description="Type of date according to the orders are searched")
    ordersDatesTypes: List[OrdersDatesTypesEnum] = Field(..., description="Date chart according to which orders are searched")

class OrdersPostModel(BaseModel):
    orderType: OrderTypeEnum = Field(..., description="")
    shopId: StrictInt = Field(..., description="")
    stockId: StrictInt = Field(..., description="")
    orderPaymentType: OrderPaymentTypeEnum = Field(..., description="")
    currencyId: str = Field(..., description="")
    clientWithoutAccount: BooleanStrShortEnum = Field(..., description="")
    clientWithoutAccountData: ClientWithoutAccountDataModel = Field(..., description="")
    clientLogin: str = Field(..., description="")
    clientNoteToOrder: str = Field(..., description="")
    clientNoteToCourier: str = Field(..., description="")
    affiliateId: StrictInt = Field(..., description="")
    courierId: StrictInt = Field(..., description="")
    pickupPointId: str = Field(..., description="")
    deliveryCost: float = Field(..., description="")
    clientDeliveryAddress: ClientDeliveryAddressModel = Field(..., description="")
    payerAddress: PayerAddressModel = Field(..., description="")
    products: ProductsModel = Field(..., description="")
    orderRebateValue: float = Field(..., description="")
    orderOperatorLogin: str = Field(..., description="")
    ignoreBridge: bool = Field(..., description="")
    settings: SettingsModel = Field(..., description="")
    orderSettledAtPrice: OrderSettledAtPriceEnum = Field(..., description="")
    clientRequestInvoice: ClientRequestInvoiceEnum = Field(..., description="")
    billingCurrency: str = Field(..., description="")
    billingCurrencyRate: float = Field(..., description="")
    purchaseDate: str = Field(..., description="Sale date. ISO-8602 format")

class OrdersPutModel(BaseModel):
    orderId: str = Field(..., description="Order ID")
    orderSerialNumber: StrictInt = Field(..., description="Order serial number")
    orderStatus: OrderStatusEnum = Field(..., description="Order status")
    apiFlag: ApiFlagEnum = Field(..., description="Flag informing on order registration or completion in external program through API")
    apiNoteToOrder: str = Field(..., description="API note added to order")
    clientNoteToOrder: str = Field(..., description="Customer comments on order")
    clientNoteToCourier: str = Field(..., description="Customer remarks for courier")
    orderNote: str = Field(..., description="Note to the order")
    products: ProductsPutModel = Field(..., description="Products list")
    orderPaymentType: OrderPaymentTypeEnum = Field(..., description="Order payment method")
    orderSettledAtPrice: OrderSettledAtPriceEnum = Field(..., description="Settlement by prices")
    ignoreBridge: bool = Field(..., description="Omits collecting orders via IAI Bridge")
    settings: SettingsPutModel = Field(..., description="Settings")
    emailProcessingConsent: EmailProcessingConsentEnum = Field(..., description="Consent to send data to cooperating services")
    clientRequestInvoice: ClientRequestInvoiceEnum = Field(..., description="Customer asked for invoice")
    billingCurrency: str = Field(..., description="Order settlement currency")
    billingCurrencyRate: float = Field(..., description="Panel billing currency exchange rate in relation to billing currency in the shop")
    purchaseDate: str = Field(..., description="Sale date. ISO-8602 format")
    estimatedDeliveryDate: str = Field(..., description="Estimated date of shipment of the order in format Y-m-d H:i")

class OrdersSerialNumberRangeModel(BaseModel):
    ordersSerialNumberBegin: StrictInt = Field(..., ge=1, description="Starting number of serial numbers range for sought products")
    ordersSerialNumberEnd: StrictInt = Field(..., ge=1, description="Ending number for serial number range")

class OrdersRangeModel(BaseModel):
    ordersDateRange: OrdersDateRangeModel = Field(..., description="Data for date range")
    ordersSerialNumberRange: OrdersSerialNumberRangeModel = Field(..., description="Data for serial number range")

class OrdersBySearchUnfinishedModel(BaseModel):
    elementName: ElementNameOrdersBySearchUnfinshedEnum = Field(..., description="Field name by which a list will be sorted")
    sortDirection: SortDirectionSearchEnum = Field(..., description="Determines sorting direction")

class PackagesPostPutModel(BaseModel):
    deliveryPackageId: StrictInt = Field(..., ge=1, description="Shipment ID")
    courierId: str = Field(..., description="Courier ID")
    deliveryPackageNumber: str = Field(..., description="Package number")
    deliveryShippingNumber: str = Field(..., description="Consignment number")
    deliveryPackageParameters: DeliveryPackageParametersModel = Field(..., description="Package parameters")
    shippingStoreCosts: ShippingStoreCostsModel = Field(..., description="Cost for shop")

class PackagesSearchModel(BaseModel):
    packagesNumbers: List[str] = Field(..., description="Consignments numbers")
    orderHasPackageNumbers: BooleanStrShortEnum = Field(..., description="Does order have consignment number assigned")
    hasMultiPackages: BooleanStrShortEnum = Field(..., description="Multipack order")

class PackagesSearchUnfinishedModel(BaseModel):
    packagesNumbers: List[str] = Field(..., description="Consignments numbers")
    orderHasPackageNumbers: BooleanStrShortEnum = Field(..., description="Does order have consignment number assigned")

class ParameterValuesModel(BaseModel):
    valueId: str = Field(..., description="...")

class PayerAddressModel(PayerAddressBaseModel):
    payerAddressId: StrictInt = Field(..., ge=1, description="Buyer's address id")

class ProductBundleItemsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    sizeId: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")
    productIndex: str = Field(..., description="One of the unique, indexed product codes (IAI code / External system code / Producer code)")

class PriceFormulaParametersModel(BaseModel):
    parameterId: str = Field(..., description="Parameter ID")
    parameterValue: str = Field(..., description="...")
    parameterValues: List[ParameterValuesModel] = Field(..., description="Parameter values")

class ProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    sizeId: str = Field(..., description="Size identifier")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")
    stockId: StrictInt = Field(..., description="Stock ID")
    productQuantity: float = Field(..., description="Product quantity")
    productRetailPrice: float = Field(..., description="Gross price")
    productFree: bool = Field(..., description="Free product")
    forceLoyaltyPoints: float = Field(..., description="...")
    productVat: float = Field(..., description="Value of VAT")
    productVatFree: BooleanStrShortEnum = Field(..., description="Is product VAT free")
    discountCode: DiscountCodeModel = Field(..., description="Information on used discount code")
    remarksToProduct: str = Field(..., description="Client's remarks on product")
    label: str = Field(..., description="Label for grouping products")
    productBundleItems: ProductBundleItemsModel = Field(..., description="List of components if a products is a set or collection")

class ProductsPutModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    sizeId: str = Field(..., description="Size identifier")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")
    basketPosition: StrictInt = Field(..., description="Item in basket")
    stockId: StrictInt = Field(..., description="Stock ID")
    productFree: bool = Field(..., description="Free product")
    forceLoyaltyPoints: float = Field(..., description="...")
    productQuantity: float = Field(..., description="Product quantity")
    productQuantityOperationType: ProductQuantityOperationTypeEnum = Field(..., description="Type of operation performed on product linked to current order")
    productRetailPrice: float = Field(..., description="Gross price")
    productVat: float = Field(..., description="Value of VAT")
    productVatFree: BooleanStrShortEnum = Field(..., description="Is product VAT free")
    remarksToProduct: str = Field(..., description="Client's remarks on product")
    label: str = Field(..., description="Label for grouping products")
    productBundleItems: ProductBundleItemsModel = Field(..., description="List of components if a products is a set or collection")
    priceFormulaParameters: List[PriceFormulaParametersModel] = Field(..., description="Information about the selected parameters in the configurator")

class ProductsSerialNumbersOrdersPutModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    orderProducts: List[OrderProductsModel] = Field(..., description="Products list")

class ProductIdentModel(BaseModel):
    identValue: str = Field(..., description="ID value")
    productIdentType: ProductIdentTypeEnum = Field(..., description="Identifier type")

class ProductsProfitMarginOrdersPutModel(BaseModel):
    productIdent: ProductIdentModel = Field(..., description="...")
    sizeId: str = Field(..., description="Size identifier")
    productProfitMargin: float = Field(..., description="Product profit margin gross")
    productProfitMarginNet: float = Field(..., description="Product profit margin net")
    errors: ErrorsModel | None = Field(None, description="Information on error that occurred during gate call")

class ProfitMarginOrdersPutModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    products: List[ProductsProfitMarginOrdersPutModel] = Field(..., description="Products list")
    errors: ErrorsModel | None = Field(None, description="Information on error that occurred during gate call")
    isProductsErrors: bool = Field(..., description="Flag marking errors in the result")

class ProductsSearchModel(BaseModel):
    productId: StrictInt = Field(..., description="Product IAI code")
    productName: str = Field(..., description="Product name")
    sizeId: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")

class SettingsModel(BaseModel):
    settingSendMail: bool = Field(..., description="Send an email with order placement confirmation")
    settingSendSMS: bool = Field(..., description="Send a text message with order placement confirmation")

class SettingsPutModel(BaseModel):
    dontSendMail: BooleanStrShortEnum = Field(..., description="Blocks the sending of emails")
    dontSendSMS: BooleanStrShortEnum = Field(..., description="Blocks the sending of sms messages")

class StocksSearachModel(BaseModel):
    stockId: StrictInt = Field(..., ge=1, description="Stock ID")
