from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt, StrictStr

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, PageableCamelGateway, PageableSnakeGateway
from src.idosell.wms._common import (
    DateRangeModel, DateRangeOpenedDocumentsModel, DocumentTypeEnum, DocumentTypeFullEnum, DocumentsConfirmedEnum,
    DocumentsCurrencyForPurchasePriceRateTypeEnum, DocumentsPriceTypeEnum, DocumentsQueueTypeEnum, DocumentsWntEnum,
    OpenedDocumentsStatusEnum, ProductsDeleteModel, ProductsPostPutModel, StockDocumentStatusEnum
)


# --- DTOs
class DeleteDocumentsWmsStocksParamsModel(BaseModel):
    type: DocumentTypeEnum = Field(..., description="Document identifier")
    id: int | str = Field(..., description="Document identifier")

class DeleteProductsWmsStocksParamsModel(BaseModel):
    products: List[ProductsDeleteModel] = Field(..., description="List of products")
    type: DocumentTypeEnum = Field(..., description="...")
    id: StrictInt = Field(..., description="Document identifier")

class PostDocumentsWmsStocksParamsModel(BaseModel):
    type: DocumentTypeEnum = Field(..., description="...")
    stockId: int | str = Field(..., ge=1, description="Target warehouse ID. The list of available warehouses can be downloaded via the method #get in gateway SystemConfig")
    stockDocumentNumber: StrictStr = Field(..., min_length=1, description="Document number")
    stockSourceId: int | str = Field(..., ge=1, description="Source warehouse ID. The list of available warehouses can be downloaded via the method #get in gateway SystemConfig")
    note: StrictStr | None = Field(..., min_length=1, description="...")
    productsInPreorder: BooleanStrShortEnum = Field(..., description="")
    delivererId: StrictInt = Field(..., ge=1, description="Supplier ID")
    wnt: DocumentsWntEnum = Field(..., description="Type of purchase document")
    saleDocumentCreationDate: str = Field(..., description="Issue date of purchase document. Correct format is yyyy-mm-dd, e.g. 2007-12-31.")
    deliveryOnTheWayPlannedDeliveryDate: str = Field(..., description="Planned date of acceptance of delivery. Correct format is yyyy-mm-dd, e.g. 2007-12-31. Requires parameter: 'confirmed=on_the_way'")
    confirmed: DocumentsConfirmedEnum = Field(..., description="Planned date of acceptance of delivery. Correct format is yyyy-mm-dd, e.g. 2007-12-31. Requires parameter: 'confirmed=on_the_way'")
    currencyForPurchasePrice: StrictStr = Field(..., min_length=1, description="Purchase price currency, e.g. PLN, USD, GBP")
    priceType: DocumentsPriceTypeEnum = Field(..., description="Settlement by prices")
    queueType: DocumentsQueueTypeEnum = Field(..., description="Methods of stock level correction")

class PostProductsWmsStocksParamsModel(BaseModel):
    products: List[ProductsPostPutModel] = Field(..., description="Products list")
    id: StrictInt | None = Field(None, description="Document identifier")
    type: DocumentTypeEnum | None = Field(None, description="...")

class PutCloseWmsStocksParamsModel(BaseModel):
    type: DocumentTypeEnum = Field(..., description="...")
    id: StrictInt = Field(..., description="Document identifier")

class PutDocumentsWmsStocksParamsModel(BaseModel):
    stockDocumentId: StrictInt = Field(..., description="Document identifier")
    stockDocumentType: DocumentTypeEnum = Field(..., description="Document type")
    stockDocumentNumber: StrictStr = Field(..., min_length=1, description="Number of purchase document")
    stockId: StrictInt = Field(..., ge=1, description="Source warehouse ID. The list of available warehouses can be downloaded via the method #get in gateway SystemConfig")
    stockSourceId: StrictInt = Field(..., ge=1, description="Source warehouse ID. The list of available warehouses can be downloaded via the method #get in gateway SystemConfig")
    note: StrictStr | None = Field(..., min_length=1, description="...")
    productsInPreorder: BooleanStrShortEnum = Field(..., description="Products available in presales")
    delivererId: StrictInt = Field(..., description="Supplier ID")
    wnt: DocumentsWntEnum = Field(..., description="Type of purchase document")
    saleDocumentCreationDate: str = Field(..., description="Issue date of purchase document. Correct format is yyyy-mm-dd, e.g. 2007-12-31.")
    deliveryOnTheWayPlannedDeliveryDate: str = Field(..., description="Planned date of acceptance of delivery. Correct format is yyyy-mm-dd, e.g. 2007-12-31. Requires parameter: 'confirmed=on_the_way'")
    confirmed: DocumentsConfirmedEnum = Field(..., description="Document status")
    currencyForPurchasePrice: StrictStr = Field(..., min_length=1, description="Purchase price currency, e.g. PLN, USD, GBP")
    currencyForPurchasePriceRate: float = Field(..., description="Currency exchange rate (Currency conversion)")
    currencyForPurchasePriceRateType: DocumentsCurrencyForPurchasePriceRateTypeEnum = Field(..., description="Type of currency rate")
    currencyForPurchasePriceRateDate: str = Field(..., description="Currency rate of the day. Correct format is yyyy-mm-dd, e.g. 2007-12-31.")
    priceType: DocumentsPriceTypeEnum = Field(..., description="Settlement by prices")
    queueType: DocumentsQueueTypeEnum = Field(..., description="Methods of stock level correction")
    verificationDate: str = Field(..., description="Verification date")
    verificationUser: str = Field(..., description="Users verification")

class PutProductsWmsStocksParamsModel(BaseModel):
    products: List[ProductsPostPutModel] = Field(..., description="Products list")
    type: DocumentTypeEnum = Field(..., description="...")
    id: StrictInt = Field(..., ge=1, description="Document identifier")

class PutAcceptMMWmsStocksParamsModel(BaseModel):
    id: StrictInt = Field(..., description="Document identifier")

class PutRejectMMWmsStocksParamsModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Document identifier")


# --- ENDPOINTS
class PutAcceptMM(Gateway):
    """
    The method enables the MM document to be received at the target warehouse
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsacceptmmput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/acceptMM')

    params: PutAcceptMMWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class PutClose(Gateway):
    """
    Method that enables closing warehouse documents
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentscloseput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/close')

    params: PutCloseWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class DeleteDocuments(Gateway):
    """
    Method that enables deleting open warehouse documents.
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsdocumentsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/documents/delete')

    params: DeleteDocumentsWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class GetDocuments(PageableCamelGateway):
    """
    The method allows for downloading a list of warehouse documents
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsdocumentsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/documents')

    stockDocumentType: DocumentTypeFullEnum | None = Field(None, description="Document type")
    stockDocumentStatus: StockDocumentStatusEnum | None = Field(None, description="Document type")
    stockDocumentsIds: List[int] | None = Field(None, description="Document identifier")
    stockDocumentsNumbers: List[StrictStr] | None = Field(None, description="Document number")
    productsInPreorder: BooleanStrShortEnum | None = Field(None, description="Products available in presales")
    dateRange: DateRangeModel | None = Field(None, description="Date range")

class PostDocuments(Gateway):
    """
    Method that enables warehouse document creation
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsdocumentspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/documents')

    params: PostDocumentsWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class PutDocuments(Gateway):
    """
    The method allows for warehouse documents edit
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsdocumentsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/documents')

    params: PutDocumentsWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class GetOpenedDocuments(PageableCamelGateway):
    """
    Method that enables getting a list of open warehouse documents
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsopeneddocumentsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/openedDocuments')

    type: DocumentTypeEnum | None = Field(None, description="...")
    status: OpenedDocumentsStatusEnum | None = Field(None, description="...")
    stockId: StrictInt | None = Field(None, ge=1, description="Target warehouse ID. The list of available warehouses can be downloaded via the method #get in gateway SystemConfig")
    stockSourceId: StrictInt | None = Field(None, ge=1, description="Source warehouse ID. The list of available warehouses can be downloaded via the method #get in gateway SystemConfig")
    dateRange: DateRangeOpenedDocumentsModel | None = Field(None, description="Date range")

class DeleteProducts(AppendableGateway):
    """
    Method that enables deleting products from warehouse documents
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsproductsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/products/delete')

    params: DeleteProductsWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class GetProducts(PageableSnakeGateway):
    """
    Method that enables getting a list of products present on a warehouse document
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsproductsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/products')

    type: DocumentTypeFullEnum | None = Field(None, description="...")
    id: StrictInt | None = Field(None, ge=1, description="Document identifier")

class PostProducts(AppendableGateway):
    """
    Method that enables adding products to warehouse documents.
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsproductspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/products')

    params: PostProductsWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class PutProducts(AppendableGateway):
    """
    Method that enables, amongst others, editing the quantity of a given product on a warehouse document
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsproductsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/products')

    params: PutProductsWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")

class PutRejectMM(Gateway):
    """
    The method allows to withdraw the MM document to the source warehouse
    DOCS_URL: https://idosell.readme.io/reference/wmsstocksdocumentsrejectmmput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/stocksdocuments/rejectMM')

    params: PutRejectMMWmsStocksParamsModel = Field(..., description="Parameters transmitted to method")
