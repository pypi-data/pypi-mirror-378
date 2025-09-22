from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway
from src.idosell.pim.products._common import (
    IdentTypeEnum, ProductAttachmentPutModel, ProductIdBySizeCodeEnum, ProductIdentTypeCodeExistanceEnum,
    ProductsDeliveryTimeProductsSearchModel
)


# --- DTOs
class PutProductsAttachmentsPimProductsMiscsParamsModel(BaseModel):
    productsAttachments: List[ProductAttachmentPutModel] = Field(..., min_length=1, description="List of product attachments") # type: ignore

class SearchProductsDeliveryTimePimProductsMiscsParamsModel(BaseModel):
    stockId: StrictInt | None = Field(None, ge=1, description="Stock ID")
    isCollectionInPerson: bool | None = Field(None, description="Should products be prepared for personal collection?")
    products: List[ProductsDeliveryTimeProductsSearchModel] | None = Field(None, min_length=1, description="Products list") # type: ignore


# --- ENDPOINTS
class GetProductsAuctions(PageableCamelGateway):
    """
    Allows for downloading information about auctions and auction categories to which the product has been assigned (for a maximum of 100 products in one request)
    DOCS_URL: https://idosell.readme.io/reference/productsauctionsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/auctions')

    identType: IdentTypeEnum | None = Field(None, description="Product identifier type")
    products: List[str] | None = Field(None, min_length=1, max_length=100, description="Products list") # type: ignore
    auctionSites: List[str] | None = Field(None, description="Array of auction site IDs")

class GetProductsCodeExistence(Gateway):
    """
    The method allows to check if a product with the given identification code (panel ID, IAI code, manufacturer code, external system code) exists in the panel
    DOCS_URL: https://idosell.readme.io/reference/productscodeexistenceget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/codeExistence')

    identType: ProductIdentTypeCodeExistanceEnum | None = Field(None, description="Identifier type")
    products: List[str] | None = Field(None, min_length=1, description="Products list") # type: ignore
    delivererId: str | None = Field(None, min_length=1, description="Supplier ID")

class GetProductsIdBySizecode(Gateway):
    """
    Method that returns information about product IDs, as well as size IDs and names, based on the provided product external system codes.
    DOCS_URL: https://idosell.readme.io/reference/productsidbysizecodeget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/idBySizecode')

    codes: List[str] | None = Field(None, min_length=1, description="Search codes") # type: ignore
    type: ProductIdBySizeCodeEnum | None = Field(None, description="Type of codes")

class GetProductsReservations(Gateway):
    """
    It allows to download information about product reservations in orders (for up to 100 products in one request).
    DOCS_URL: https://idosell.readme.io/reference/productsreservationsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/reservations')

    identType: IdentTypeEnum | None = Field(None, description="Identifier type")
    products: List[str] | None = Field(None, min_length=1, max_length=100, description="Products list") # type: ignore

class GetProductsSKUbyBarcode(Gateway):
    """
    The method allows to download, among others, information on identifiers, names and size codes, their available stock quantity and locations in the warehouse based on scanned bar codes.
    DOCS_URL: https://idosell.readme.io/reference/productsskubybarcodeget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/SKUbyBarcode')

    productIndices: List[str] | None = Field(None, min_length=1, description="List of sought products by indexes") # type: ignore
    searchOnlyInCodeIai: bool | None = Field(None, description="Search for products only by IAI code")

class PostProductsRestore(Gateway):
    """
    The method is used to restore deleted products
    DOCS_URL: https://idosell.readme.io/reference/productsrestorepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/restore')

    productId: StrictInt = Field(..., ge=1, description="Product IAI code")

class PutProductsAttachments(AppendableGateway):
    """
    Method that enables adding and editing product attachments
    DOCS_URL: https://idosell.readme.io/reference/productsattachmentsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/attachments')

    params: PutProductsAttachmentsPimProductsMiscsParamsModel = Field(..., description="Parameters transmitted to method")

class SearchProductsDeliveryTime(AppendableGateway):
    """
    The method returns the time needed to prepare the product for shipment
    DOCS_URL: https://idosell.readme.io/reference/productsdeliverytimesearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/deliveryTime/search')

    params: SearchProductsDeliveryTimePimProductsMiscsParamsModel = Field(..., description="Parameters transmitted to method")
