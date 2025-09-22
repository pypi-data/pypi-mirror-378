from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt, StrictStr

from src.idosell._common import Gateway, PageableCamelGateway
from src.idosell.wms._common import SuppliersModel


# --- DTOs
class DeleteWmsSuppliersParamsModel(BaseModel):
    ids: List[StrictInt] = Field(..., description="List of ids")

class PutWmsSuppliersParamsModel(BaseModel):
    suppliers: List[SuppliersModel] = Field(..., description="List of suppliers")


# --- ENDPOINTS
class Delete(Gateway):
    """
    Method allows for the removal of suppliers.
    DOCS_URL: https://idosell.readme.io/reference/wmssupplierssuppliersdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/suppliers/suppliers/delete')

    params: DeleteWmsSuppliersParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    The method allows to download a list of suppliers along with information about the number of products assigned to them.
    DOCS_URL: https://idosell.readme.io/reference/wmssupplierssuppliersget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/suppliers/suppliers')

    returnProductsCount: bool | None = Field(None, description="Return quantity of products assigned to supplier")
    names: List[StrictStr] | None = Field(None, min_length=1, description="List of names") # type: ignore
    ids: List[StrictInt] | None = Field(None, min_length=1, description="List of ids") # type: ignore

class Put(Gateway):
    """
    The method allows information about suppliers to be updated, including address details, description, order preparation time or supplier working hours
    DOCS_URL: https://idosell.readme.io/reference/wmssupplierssuppliersput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/suppliers/suppliers')

    params: PutWmsSuppliersParamsModel = Field(..., description="Parameters transmitted to method")
