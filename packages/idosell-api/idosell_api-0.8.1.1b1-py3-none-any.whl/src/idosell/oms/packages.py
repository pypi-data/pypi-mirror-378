from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.oms._common import ShippingStoreCostsModel


# --- Enums
class EventOrderTypeEnum(StrEnum):
    ORDER = 'order'
    RETURN = 'return'
    RMA = 'rma'


# --- DTOs
class EventsSearchModel(BaseModel):
    eventType: EventOrderTypeEnum = Field(..., description="Type")
    eventsIds: List[int] = Field(..., description="IDs")

class ParcelParametersModel(BaseModel):
    id: str = Field(..., description="Configuration option identifier for the shipment")
    value: str = Field(..., description="The value of the configuration option for the shipment")

class ParcelParametersByPackagesModel(BaseModel):
    packageId: str = Field(..., description="Package ID in system")
    parcelParameters: List[ParcelParametersModel] = Field(..., description="Shipment configuration options available for a given courier")

class PackagesPackagesModel(BaseModel):
    packageId: StrictInt = Field(..., ge=1, description="Package ID in system")
    delivery: StrictInt = Field(..., ge=1, description="Courier Id")
    packageNumber: str = Field(..., description="Number of the parcel in the shipmnet given by the courier. Returned only if the courier supports parcel numbers")
    shippingNumber: str = Field(..., description="Shipment number provided by the courier. Returned only if the courier supports tracking numbers")
    packageParameters: str = Field(..., description="Package parameters (this option is temporarily unavailable)")
    shippingStoreCosts: ShippingStoreCostsModel = Field(..., description="Cost for shop")

class OrderPackagesPackagesPostModel(BaseModel):
    eventId: StrictInt = Field(..., description="Id")
    eventType: EventOrderTypeEnum = Field(..., description="")
    parcelParameters: List[ParcelParametersModel] = Field(..., description="Shipment configuration options available for a given courier")
    parcelParametersByPackages: List[ParcelParametersByPackagesModel] = Field(..., description="Shipment configuration options available for Inpost Smile courier")

class OrderPackagesPackagesPutModel(BaseModel):
    orderId: str = Field(..., description="Order ID")
    orderType: EventOrderTypeEnum = Field(..., description="Order type")
    packages: List[PackagesPackagesModel] = Field(..., description="Information on consignments")

class PostLabelsOmsPackagesParamsModel(BaseModel):
    eventId: StrictInt = Field(..., description="Id")
    eventType: EventOrderTypeEnum = Field(..., description="Type")
    parcelParameters: List[ParcelParametersModel] = Field(..., description="Shipment configuration options available for a given courier")
    parcelParametersByPackages: List[ParcelParametersByPackagesModel] = Field(..., description="Shipment configuration options available for Inpost Smile courier")

class PostOmsPackagesParamsModel(BaseModel):
    orderPackages: List[OrderPackagesPackagesPostModel] = Field(..., min_length=1, max_length=100, description="List of parcels assigned to the order Maximum default number: 100 parcels")

class PutOmsPackagesParamsModel(BaseModel):
    orderPackages: List[OrderPackagesPackagesPutModel] = Field(..., min_length=1, max_length=100, description="List of parcels assigned to the order Maximum default number: 100 parcels")

class SearchOmsPackagesParamsModel(BaseModel):
    deliveryPackageNumbers: List[str] | None = Field(None, min_length=1, description="Consignments numbers") # type: ignore
    events: List[EventsSearchModel] | None = Field(None, min_length=1, description="Element, package is assigned to") # type: ignore
    returnLabels: bool | None = Field(None, description="Return parcel labels")


# --- ENDPOINTS
class GetLabels(Gateway):
    """
    The method allows you to download labels for the courier from orders, complaints and returns
    DOCS_URL: https://idosell.readme.io/reference/packageslabelsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/packages/labels')

    eventId: StrictInt = Field(..., ge=1, description="Id")
    eventType: EventOrderTypeEnum = Field(..., description="Event type")

class PostLabels(AppendableGateway):
    """
    The method is used to generate shipments and printouts for the courier in orders, complaints and returns. When generating a label with a default courier configuration, it is not necessary to complete the shipment configuration options. To generate a custom label, you must additionally forward the shipment configuration options available to the courier in a given event (parcelParameters node). Completable configuration options can be checked using the getPackages method
    DOCS_URL: https://idosell.readme.io/reference/packageslabelspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/packages/labels')

    params: PostLabelsOmsPackagesParamsModel = Field(..., description="Parameters transmitted to method")

class Post(AppendableGateway):
    """
    Method that enables adding parcels to an order
    DOCS_URL: https://idosell.readme.io/reference/packagespackagespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/packages/packages')

    params: PostOmsPackagesParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Method that enables editing parcels already assigned to an order
    DOCS_URL: https://idosell.readme.io/reference/packagespackagesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/packages/packages')

    params: PutOmsPackagesParamsModel = Field(..., description="Parameters transmitted to method")

class Search(Gateway):
    """
    Method that enables getting a list of parcels assigned to an order
    DOCS_URL: https://idosell.readme.io/reference/packagespackagessearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/packages/packages/search')

    params: SearchOmsPackagesParamsModel = Field(..., description="Parameters transmitted to method")
