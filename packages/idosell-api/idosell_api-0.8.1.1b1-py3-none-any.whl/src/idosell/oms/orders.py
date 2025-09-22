from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, IdoSellDateTime, OrdersBySearchModel, PageableCamelGateway
from src.idosell.oms._common import (
    ApplicationTypeEnum, CampaignSearchModel, ClientRequestInvoiceEnum, ClientRequestInvoiceSearchUnfinishedEnum, ClientsModel,
    ClientsSearchModel, ClientsSearchUnfinishedModel, DateRangeSearchModel, DevideProductsPutModel, DocumentTypeEppEnum, DocumentTypeJpkEnum, DocumentTypeOrdersGetEnum,
    DocumentTypePostEnum, DocumentsDeleteModel, DocumentsPostModel, DropshippingOrderStatusEnum, ExternalStockIdEnum, IdentTypeEnum,
    ImagesDeleteModel, ImagesImagesPostModel, ImagesOrderModel, ImagesSettingsPostModel, LoyaltyPointsModeEnum, OpinionSearchModel,
    OpinionsRateEnum, OrderBySearchModel, OrderPackagesPostPutModel, OrderPaymentTypeEnum, OrderPrepaidStatusEnum,
    OrderSourceModel, OrderSourceSearchUnfinishedModel, OrderTypeEnum, OrderTypeSearchUnfinishedEnum,
    OrdersBySearchUnfinishedModel, OrdersPostModel, OrdersPutModel, OrdersRangeModel, OrdersSearchModel, OrdersStatusesEnum,
    OrdersStatusesSearchUnfinishedEnum, PackagesSearchModel, PackagesSearchUnfinishedModel, ProductsSearchModel, ProductsSerialNumbersOrdersPutModel,
    ProfitMarginOrdersPutModel, SearchingOperatorTypeMatchEnum, ShippmentStatusEnum, StocksSearachModel
)


# --- DTOs
class PutClientOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")

class PutCourierOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    courierId: StrictInt = Field(..., ge=1, description="Courier ID")
    pickupPointId: str = Field(..., description="Collection point ID")

class PutDeliveryAddressOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    clientDeliveryAddressId: StrictInt = Field(..., ge=1, description="Delivery address ID")
    clientLogin: str = Field(..., description="Customer's login")

class PutDevideOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    products: List[DevideProductsPutModel] = Field(..., description="Products list")
    splitPayments: bool = Field(..., description="Whether to split payments")

class PostDocumentsCreateOmsOrdersParamsModel(BaseModel):
    orderSerialNumbers: List[int] = Field(..., description="...")
    actualize: bool = Field(..., description="...")
    documentType: DocumentTypePostEnum = Field(..., description="Document type")
    documentIssuedDate: str = Field(..., description="Document issued date")
    documentPurchaseDate: str = Field(..., description="Document purchase date")
    printerId: StrictInt = Field(..., description="Printer id")

class PostDocumentsOmsOrdersParamsModel(BaseModel):
    documents: List[DocumentsPostModel] = Field(..., description="List of documents")

class PutHandlerOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    orderOperatorLogin: str = Field(..., description="Order handler")

class DeleteImagesOmsOrdersParamsModel(BaseModel):
    order: ImagesOrderModel = Field(..., description="")
    images: List[ImagesDeleteModel] = Field(..., description="List of attachment IDs to be removed from the details of the selected order")

class PostImagesOmsOrdersParamsModel(BaseModel):
    userName: str = Field(..., description="Login")
    settings: ImagesSettingsPostModel = Field(..., description="...")
    order: ImagesOrderModel = Field(..., description="...")
    images: ImagesImagesPostModel = Field(..., description="List of image attachments")

class SearchOpinionsOmsOrdersParamsModel(BaseModel):
    opinion: OpinionSearchModel | None = Field(None, description="")
    orders: OrdersSearchModel | None = Field(None, description="")
    clients: ClientsSearchModel | None = Field(None, description="")
    dateRange: DateRangeSearchModel | None = Field(None, description="")
    ordersBy: List[OrderBySearchModel] | None = Field(None, description="Possibility of sorting returned list")

class PostOmsOrdersParamsModel(BaseModel):
    orders: OrdersPostModel = Field(..., description="Orders")

class PutOmsOrdersParamsModel(BaseModel):
    orders: OrdersPutModel = Field(..., description="Orders")

class SearchOmsOrdersParamsModel(BaseModel):
    orderPrepaidStatus: OrderPrepaidStatusEnum | None = Field(None, description="Prepayment status")
    ordersStatuses: OrdersStatusesEnum | None = Field(None, description="Order status")
    shippmentStatus: ShippmentStatusEnum | None = Field(None, description="None")
    couriersName: List[str] | None = Field(None, description="Shipping companies (packages deliverers)")
    couriersId: List[int] | None = Field(None, description="Courier service identifiers")
    orderPaymentType: OrderPaymentTypeEnum | None = Field(None, description="Order payment method")
    withMissingSalesDocuments: List[str] | None = Field(None, description="None")
    orderType: OrderTypeEnum | None = Field(None, description="Order type")
    dropshippingOrderStatus: DropshippingOrderStatusEnum | None = Field(None, description="None")
    ordersIds: List[str] | None = Field(None, description="Orders IDs")
    ordersSerialNumbers: List[int] | None = Field(None, description="Order serial numbers")
    clients: List[ClientsModel] | None = Field(None, description="Customer data")
    ordersRange: OrdersRangeModel | None = Field(None, description="Ranges of dates or serial numbers")
    orderSource: OrderSourceModel | None = Field(None, description="Order source data")
    products: List[ProductsSearchModel] | None = Field(None, description="Products list")
    clientRequestInvoice: ClientRequestInvoiceEnum | None = Field(None, description="Customer asked for invoice")
    packages: PackagesSearchModel | None = Field(None, description="Information on consignments")
    stocks: List[StocksSearachModel] | None = Field(None, description="Stock quantities data")
    campaign: CampaignSearchModel | None = Field(None, description="Used discount codes data")
    loyaltyPointsMode: LoyaltyPointsModeEnum | None = Field(None, description="Loyalty points")
    orderOperatorLogin: str | None = Field(None, description="Order handler")
    orderPackingPersonLogin: str | None = Field(None, description="Order picker")
    ordersBy: List[OrdersBySearchModel] | None = Field(None, description="Possibility of sorting returned list")
    searchingOperatorTypeMatch: SearchingOperatorTypeMatchEnum | None = Field(None, description="Method of searching orders by handler")
    ordersDelayed: BooleanStrShortEnum | None = Field(None, description="Orders with the exceeded date of shipment")
    showBundles: bool | None = Field(None, description="Combine the components of the set into one item")
    orderExternalId: str | None = Field(None, description="The order ID of the external service")
    orderCurrency: str | None = Field(None, description="Order currency")

class PostPackagesOmsOrdersParamsModel(BaseModel):
    orderPackages: OrderPackagesPostPutModel = Field(..., description="List of parcels assigned to the order Maximum default number: 100 parcels")

class PutPackagesOmsOrdersParamsModel(BaseModel):
    orderPackages: OrderPackagesPostPutModel = Field(..., description="List of parcels assigned to the order Maximum default number: 100 parcels")

class PutPickupPointOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: int | str = Field(..., description="Order serial number")
    pickupPointId: int | str = Field(..., description="Collection point ID")

class PutProductsSerialNumbersOmsOrdersParamsModel(BaseModel):
    orders: List[ProductsSerialNumbersOrdersPutModel] = Field(..., description="Orders")

class PutProfitMarginOmsOrdersParamsModel(BaseModel):
    orders: List[ProfitMarginOrdersPutModel] = Field(..., description="Orders")

class PutShippingCostsOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., description="Order serial number")
    deliveryCost: float = Field(..., description="Delivery cost")
    orderDeliveryVat: float = Field(..., description="Delivery VAT")

class SearchUnfinishedOmsOrdersParamsModel(BaseModel):
    orderPrepaidStatus: OrderPrepaidStatusEnum | None = Field(None, description="Prepayment status")
    ordersStatuses: OrdersStatusesSearchUnfinishedEnum | None = Field(None, description="Order status")
    couriersName: List[str] | None = Field(None, description="Shipping companies (packages deliverers)")
    orderPaymentType: OrderPaymentTypeEnum | None = Field(None, description="Order payment method")
    orderType: OrderTypeSearchUnfinishedEnum | None = Field(None, description="Order type")
    dropshippingOrderStatus: DropshippingOrderStatusEnum | None = Field(None, description="Dropshipping order status in the supplier's system")
    ordersIds: List[str] | None = Field(None, description="Orders IDs")
    ordersSerialNumbers: List[int] | None = Field(None, description="Order serial numbers")
    clients: List[ClientsSearchUnfinishedModel] | None = Field(None, description="Customer data")
    ordersRange: OrdersRangeModel | None = Field(None, description="Ranges of dates or serial numbers")
    orderSource: OrderSourceSearchUnfinishedModel | None = Field(None, description="Bit mask of shop IDs")
    products: List[ProductsSearchModel] | None = Field(None, description="Products list")
    clientRequestInvoice: ClientRequestInvoiceSearchUnfinishedEnum | None = Field(None, description="Customer asked for invoice")
    packages: PackagesSearchUnfinishedModel | None = Field(None, description="Information on consignments")
    stocks: List[StocksSearachModel] | None = Field(None, description="Stock quantities data")
    campaign: CampaignSearchModel | None = Field(None, description="Used discount codes data")
    loyaltyPointsMode: LoyaltyPointsModeEnum | None = Field(None, description="Loyalty points")
    orderOperatorLogin: str | None = Field(None, description="Order handler")
    orderPackingPersonLogin: str | None = Field(None, description="Order picker")
    ordersBy: List[OrdersBySearchUnfinishedModel] | None = Field(None, description="Possibility of sorting returned list")
    searchingOperatorTypeMatch: SearchingOperatorTypeMatchEnum | None = Field(None, description="Method of searching orders by handler")
    ordersDelayed: BooleanStrShortEnum | None = Field(None, description="Orders with the exceeded date of shipment")

class PutWarehouseOmsOrdersParamsModel(BaseModel):
    orderSerialNumber: StrictInt = Field(..., description="Order serial number")
    stockId: StrictInt = Field(..., description="Stock ID")
    orderOperatorLogin: str = Field(..., description="Order handler")
    externalStockId: ExternalStockIdEnum = Field(..., description="External warehouse ID (if required)")


# --- ENDPOINTS
class GetAnalytics(Gateway):
    """
    The method is used to retrieve information about the margins of the goods of the order
    DOCS_URL: https://idosell.readme.io/reference/ordersanalyticsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/analytics')

    orderSerialNumber: List[int] | None = Field(None, min_length=1, description="Array of order serial numbers (items must be >= 1)") # type: ignore

class GetAuctionDetails(Gateway):
    """
    Method that enables getting information about external listings assigned to orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersauctiondetailsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/auctionDetails')

    identType: IdentTypeEnum | None = Field(None, description="Identifier type")
    orders: List[str] | None = Field(None, min_length=1, description="Orders Id values") # type: ignore

class PutClient(Gateway):
    """
    ...
    DOCS_URL: https://idosell.readme.io/reference/ordersclientput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/client')

    params: PutClientOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class PutCourier(Gateway):
    """
    Method that enables changing the courier handling the shipment for an order
    DOCS_URL: https://idosell.readme.io/reference/orderscourierput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/courier')

    params: PutCourierOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class DeleteDocumentsOmsOrdersParamsModel(BaseModel):
    documents: List[DocumentsDeleteModel] = Field(..., description="List of documents")

class PutDeliveryAddress(Gateway):
    """
    Method that enables editing the delivery address details for an order in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersdeliveryaddressput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/deliveryAddress')

    params: PutDeliveryAddressOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class PutDevide(AppendableGateway):
    """
    Method for division order
    DOCS_URL: https://idosell.readme.io/reference/ordersdevideput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/devide')

    params: PutDevideOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class PostDocumentsCreate(Gateway):
    """
    The method allows to generate documents to the order in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersdocumentscreatepost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/documents/create')

    params: PostDocumentsCreateOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class DeleteDocuments(AppendableGateway):
    """
    The method allows to delete documents added to the order in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersdocumentsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/documents/delete')

    params: DeleteDocumentsOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetDocuments(Gateway):
    """
    Method that enables extracting information about documents issued for orders in the administration panel.
    DOCS_URL: https://idosell.readme.io/reference/ordersdocumentsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/documents')

    orderSerialNumber: List[str] = Field(..., min_length=1, description="Order serial number (at least 1)") # type: ignore
    documentType: DocumentTypeOrdersGetEnum = Field(..., min_length=1, description="Document type")
    returnElements: List[str] | None = Field(None, description="Elements returned by api")

class PostDocuments(AppendableGateway):
    """
    The method allows to add TIFF, BMP, PNG, JPG, JPEG, GIF or PDF documents to the order in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersdocumentspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/documents')

    params: PostDocumentsOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetExportdocumentsEPP(Gateway):
    """
    This method returns sales and warehouse documents in the universal EDI (Electronic Data Interchange) format
    DOCS_URL: https://idosell.readme.io/reference/ordersexportdocumentseppget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/exportdocuments/EPP')

    dateBegin: IdoSellDateTime = Field(..., description="Beginning date in YYYY-MM-DD HH:MM:SS format")
    dateEnd: IdoSellDateTime = Field(..., description="Ending date in YYYY-MM-DD HH:MM:SS format")
    applicationType: ApplicationTypeEnum = Field(..., description="...")
    stocks: List[int] | None = Field(None, min_length=1, description="Stock ID (required only when selecting particular stocks)") # type: ignore
    documentType: DocumentTypeEppEnum = Field(..., description="Document type")
    invoiceFirstGeneratedDate: StrictInt | None = Field(None, ge=1, description="Date the document was first generated")

class GetExportdocumentsJPK(Gateway):
    """
    Method returns sales and warehouse documents in universal JPK format
    DOCS_URL: https://idosell.readme.io/reference/ordersexportdocumentsjpkget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/exportdocuments/JPK')

    documentType: DocumentTypeJpkEnum | None = Field(None, description="Document type")
    fileId: StrictInt | None = Field(None, ge=1, description="JPK file identifier to download")
    documentVersion: StrictInt | None = Field(None, ge=1, description="JPK format version. If empty, takes the latest version number")
    schemaVersion: str | None = Field(None, description="Schema version")
    dateBegin: IdoSellDateTime | None = Field(None, description="Beginning date in YYYY-MM-DD HH:MM:SS format. (JPK_FA, JPK_MAG)")
    dateEnd: IdoSellDateTime | None = Field(None, description="Ending date in YYYY-MM-DD HH:MM:SS format. (JPK_FA, JPK_MAG)")
    month: StrictInt | None = Field(None, ge=1, le=12, description="Billing month for which to generate the document. (JPK_VAT)")
    year: StrictInt | None = Field(None, ge=1, description="Billing year for which to generate the document. (JPK_VAT)")
    currency: str | None = Field(None, min_length=3, max_length=3, description="Currency symbol in ISO-4217 (3 letters)")
    shop: List[int] | None = Field(None, min_length=1, description="Store ID only required if a specific store is selected") # type: ignore
    stockId: List[int] | None = Field(None, min_length=1, description="Stock ID") # type: ignore
    forceBackgroundGenerate: bool | None = Field(None, description="Forces the file to be generated by background tasks. The file will be generated later. Then, after it is generated, you will be able to download the given file using the returned ID. The file will be available 24h after the task is completed")

class GetHandler(Gateway):
    """
    Method that enables getting information about the handler currently assigned to an order
    DOCS_URL: https://idosell.readme.io/reference/ordershandlerget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/handler')

    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")

class PutHandler(Gateway):
    """
    Method that enabled assigning a handler to an order
    DOCS_URL: https://idosell.readme.io/reference/ordershandlerput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/handler')

    params: PutHandlerOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetHistory(Gateway):
    """
    Method allows to retrieve orders history from the IdoSell Shop panel
    DOCS_URL: https://idosell.readme.io/reference/ordershistoryget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/history')

    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")

class DeleteImages(AppendableGateway):
    """
    Method allows to remove image attachments from the details of the specified order
    DOCS_URL: https://idosell.readme.io/reference/ordersimagesdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/images/delete')

    params: DeleteImagesOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetImages(Gateway):
    """
    Method allows downloading image attachment data from the details of the specified order
    DOCS_URL: https://idosell.readme.io/reference/ordersimagesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/images')

    imageId: StrictInt = Field(..., ge=1, description="Attachment ID (Photos)")
    orderSerialNumber: StrictInt | None = Field(None, ge=1, description="Order serial number")

class PostImages(AppendableGateway):
    """
    Method allows to add image attachments to the details of the specified order
    DOCS_URL: https://idosell.readme.io/reference/ordersimagespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/images')

    params: PostImagesOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetLabels(Gateway):
    """
    The method is used to generate parcels and printouts for a courier
    DOCS_URL: https://idosell.readme.io/reference/orderslabelsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/labels')

    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")

class SearchOpinions(PageableCamelGateway):
    """
    The method allows for downloading information about reviews issued for orders available in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersopinionssearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/opinions/search')

    params: SearchOpinionsOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetOpinionsRate(Gateway):
    """
    Evaluation of the usefulness of opinions issued for orders
    DOCS_URL: https://idosell.readme.io/reference/ordersopinionsrateget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/opinionsRate')

    id: StrictInt = Field(..., ge=1, description="...")
    operation: OpinionsRateEnum = Field(..., description="...")

class Get(Gateway):
    """
    Method that enables extracting information about orders present in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersordersget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/orders')

    ordersIds: List[str] | None = Field(None, min_length=1, description="Orders IDs") # type: ignore
    ordersSerialNumbers: List[int] | None = Field(None, min_length=1, description="Order serial numbers. You can transfer a maximum of 100 items") # type: ignore
    orderExternalId: str | None = Field(None, min_length=1, description="The order ID of the external service. You can transfer a maximum of 100 items in one request") # type: ignore

class Post(AppendableGateway):
    """
    Method that is used for adding new retail or wholesale orders to a shop in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersorderspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/orders')

    params: PostOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Method that enables editing an order in the administration panel. It allows, for example, to change the products included in the order or change its status
    DOCS_URL: https://idosell.readme.io/reference/ordersordersput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/orders')

    params: PutOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class Search(PageableCamelGateway):
    """
    Method that enables extracting information about orders present in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersorderssearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/orders/search')

    params: SearchOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetPackages(Gateway):
    """
    Method that enables getting a list of parcels assigned to an order
    DOCS_URL: https://idosell.readme.io/reference/orderspackagesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/packages')

    deliveryPackageNumbers: List[str] | None = Field(None, min_length=1, description="Consignments numbers") # type: ignore
    orderNumbers: List[int] | None = Field(None, min_length=1, description="Order serial numbers") # type: ignore
    returnNumbers: List[int] | None= Field(None, min_length=1, description="Returns numbers") # type: ignore
    rmaNumbers: List[int] | None = Field(None, min_length=1, description="RMA numbers") # type: ignore
    returnLabels: bool | None = Field(None, description="Return parcel labels")

class PostPackages(AppendableGateway):
    """
    Method that enables editing parcels already assigned to an order
    DOCS_URL: https://idosell.readme.io/reference/orderspackagespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/packages')

    params: PostPackagesOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class PutPackages(AppendableGateway):
    """
    Method that enables editing parcels already assigned to an order
    DOCS_URL: https://idosell.readme.io/reference/orderspackagesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/packages')

    params: PutPackagesOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class PutPickupPoint(Gateway):
    """
    The method allows to change the collection point in the order
    DOCS_URL: https://idosell.readme.io/reference/orderspickuppointput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/pickupPoint')

    params: PutPickupPointOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetPrinterDocuments(Gateway):
    """
    Method that enables getting a VAT invoice issued for an order added to the administration panel by the IAI POS application
    DOCS_URL: https://idosell.readme.io/reference/ordersprinterdocumentsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/printerDocuments')

    user: str = Field(..., min_length=1, description="...")
    printScenarioAction: str = Field(..., min_length=1, description="...")
    objectNumber: str = Field(..., min_length=1, description="...")
    objectType: str = Field(..., min_length=1, description="...")
    printerAccessKey: str = Field(..., min_length=1, description="...")
    skipNotGeneratedDocument: bool | None = Field(None, description="...")

class PutProductsSerialNumbers(AppendableGateway):
    """
    Method that enables adding serial numbers to products in an order
    DOCS_URL: https://idosell.readme.io/reference/ordersproductsserialnumbersput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/productsSerialNumbers')

    params: PutProductsSerialNumbersOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class PutProfitMargin(AppendableGateway):
    """
    Method that enables setting price margins for products in an order
    DOCS_URL: https://idosell.readme.io/reference/ordersprofitmarginput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/profitMargin')

    params: PutProfitMarginOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetProfitability(Gateway):
    """
    The method is used to retrieve information about the profitability of an order
    DOCS_URL: https://idosell.readme.io/reference/ordersprofitabilityget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/profitability')

    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")

class PutShippingCosts(Gateway):
    """
    Method that enables editing the delivery costs for an order in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/ordersshippingcostsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/shippingCosts')

    params: PutShippingCostsOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class SearchUnfinished(PageableCamelGateway):
    """
    It allows you to download information about unclosed orders located in the store's administration panel. Orders with a status of false and lost are considered closed. Orders with a status of false and lost are considered closed
    DOCS_URL: https://idosell.readme.io/reference/ordersunfinishedsearchpost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/unfinished/search')

    params: SearchUnfinishedOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")

class GetWarehouse(Gateway):
    """
    Method that enables getting information about which warehouse an order is being handled from
    DOCS_URL: https://idosell.readme.io/reference/orderswarehouseget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/warehouse')

    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")

class PutWarehouse(Gateway):
    """
    Method that enables setting which warehouse an order is handled from
    DOCS_URL: https://idosell.readme.io/reference/orderswarehouseput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/orders/warehouse')

    params: PutWarehouseOmsOrdersParamsModel = Field(..., description="Parameters transmitted to method")
