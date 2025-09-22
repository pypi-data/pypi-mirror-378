from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.pim._common import SizesPutModel


# --- DTOs
class PutPimSizesParamsModel(BaseModel):
    sizes: List[SizesPutModel] = Field(..., description="Size table")


# --- ENDPOINTS
class Get(Gateway):
    """
    Method that returns information about product sizes configured in the administration panel. List of size groups (with sizes that belong to particular group) is returned as a result
    DOCS_URL: https://idosell.readme.io/reference/sizessizesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/sizes/sizes')

    return_last_changed_time: str | None = Field(None, description="When the value is 'y', the last size modification date is returned, formatted as YYYY-MM-DD HH-MM-SS")

class Put(AppendableGateway):
    """
    Method that enables creating, deleting and editing product sizes in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/sizessizesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/sizes/sizes')

    params: PutPimSizesParamsModel = Field(..., description="Parameters transmitted to method")
