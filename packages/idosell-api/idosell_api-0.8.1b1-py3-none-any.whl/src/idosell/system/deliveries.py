from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway, PageableCamelGateway


# --- DTOs
class PostRegionsSystemDeliveriesParamsModel(BaseModel):
    regionName: str = Field(..., min_length=1, max_length=255, description="Name of the region in the panel")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    postCodeFrom: str = Field(..., min_length=1, max_length=32, description="The range of postal codes from %s")
    postCodeTo: str = Field(..., min_length=1, max_length=32, description="The range of postal codes to %s")
    parentRegionId: StrictInt = Field(..., ge=1, description="ID of the country for which the region is being added")

class PutDefaultProfilesSystemDeliveriesParamsModel(BaseModel):
    regionId: StrictInt = Field(..., ge=1, description="Country ID")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    retailProfileId: StrictInt = Field(..., ge=1, description="ID of delivery profile for retail sales")
    wholesaleProfileId: StrictInt = Field(..., ge=1, description="ID of delivery profile for wholesale sales")


# --- ENDPOINTS
class PutDefaultProfiles(Gateway):
    """
    The method allows to set the default delivery profile for the given region
    DOCS_URL: https://idosell.readme.io/reference/deliveriesdefaultprofilesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/deliveries/defaultProfiles')

    params: PutDefaultProfilesSystemDeliveriesParamsModel = Field(..., description="Parameters transmitted to method")

class GetProfiles(PageableCamelGateway):
    """
    Allows to download all of the delivery profiles defined in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/deliveriesprofilesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/deliveries/profiles')

class GetRegions(Gateway):
    """
    The method allows to download a list of regions supporting deliveries
    DOCS_URL: https://idosell.readme.io/reference/deliveriesregionsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/deliveries/regions')

    shopId: Optional[StrictInt] = Field(None, ge=1, description="Shop Id (optional, integer, >= 1)")

class PostRegions(Gateway):
    """
    Allows you to add a region to the indicated country
    DOCS_URL: https://idosell.readme.io/reference/deliveriesregionspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/deliveries/regions')

    params: PostRegionsSystemDeliveriesParamsModel = Field(..., description="Parameters transmitted to method")
