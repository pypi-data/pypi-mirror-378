from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway
from src.idosell.system._common import PickupPointDeleteRequestsPostModel, PickupPointsPostModel, PickupPointsPutModel


# --- DTOs
class DeletePickupPointSystemCouriersParamsModel(BaseModel):
    pickupPointDeleteRequests: List[PickupPointDeleteRequestsPostModel] = Field(..., description="List of pickupPoints to delete")

class PostPickupPointsSystemCouriersParamsModel(BaseModel):
    pickupPoints: List[PickupPointsPostModel] = Field(..., min_length=1, description="List of pickup points") # type: ignore

class PutPickupPointsSystemCouriersParamsModel(BaseModel):
    pickupPoints: List[PickupPointsPutModel] = Field(..., min_length=1, description="List of pickup points") # type: ignore


# --- ENDPOINTS
class GetAssignedToShippingProfiles(Gateway):
    """
    Retrieves information about assigned couriers to delivery profiles
    DOCS_URL: https://idosell.readme.io/reference/couriersassignedtoshippingprofilesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/couriers/assignedToShippingProfiles')

class Get(PageableCamelGateway):
    """
    Method that returns all couriers available for a given country. It also returns information whether the courier service handles personal collections
    DOCS_URL: https://idosell.readme.io/reference/courierscouriersget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/couriers/couriers')

    countryCode: str = Field(..., min_length=2, max_length=2, pattern=r'^[A-Za-z]{2}$', description="Country code in ISO-3166-1 alpha-2 format (2 letters)")  # type: ignore

class DeletePickupPoint(AppendableGateway):
    """
    The method enables cancelling personal collection points within your own collection points chain. It does not allow for modifying integrated couriers collection points
    DOCS_URL: https://idosell.readme.io/reference/courierspickuppointsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/couriers/pickupPoints/delete')

    params: DeletePickupPointSystemCouriersParamsModel = Field(..., description="Parameters transmitted to method")

class GetPickupPoints(PageableCamelGateway):
    """
    The method returns personal collection points within its own network of collection points and for integrated couriers
    DOCS_URL: https://idosell.readme.io/reference/courierspickuppointsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/couriers/pickupPoints')

    courierId: StrictInt = Field(..., ge=1, description="Courier ID")
    pickupPointId: Optional[str] = Field(None, min_length=1, description="Collection point ID")
    pickupPointExternalId: Optional[str] = Field(None, min_length=1, description="External system code")

class PostPickupPoints(AppendableGateway):
    """
    The method enables adding personal collection points within your own collection points chain. It does not allow for modifying integrated couriers collection points.
    DOCS_URL: https://idosell.readme.io/reference/courierspickuppointspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/couriers/pickupPoints')

    params: PostPickupPointsSystemCouriersParamsModel = Field(..., description="Parameters transmitted to method")

class PutPickupPoints(AppendableGateway):
    """
    The method enables updating personal collection points within your own collection points chain. It does not allow for modifying integrated couriers collection points
    DOCS_URL: https://idosell.readme.io/reference/courierspickuppointsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/couriers/pickupPoints')

    params: PutPickupPointsSystemCouriersParamsModel = Field(..., description="Parameters transmitted to method")
