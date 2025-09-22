from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway
from src.idosell.pim.products._common import ItemsParametersModel, SettingsParametersPutModel, TextIdsParametersSearchModel


# --- DTOs
class DeletePimProductsParametersParamsModel(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="Parameter identifiers") # type: ignore

class SearchPimProductsParametersParamsModel(BaseModel):
    ids: List[int] | None = Field(None, min_length=1, description="List of identifiers") # type: ignore
    textIds: List[TextIdsParametersSearchModel] | None = Field(None, min_length=1, description="Element text ID - can be entered instead of 'id'") # type: ignore
    languagesIds: List[str] | None = Field(None, min_length=1, description="List of languages") # type: ignore
    parameterValueIds: bool | None = Field(None, description="Whether to return a list of parameter value IDs")


# --- ENDPOINTS
class Delete(Gateway):
    """
    The method allows you to delete parameters and their values (for parameters that are not pinned to any product)
    DOCS_URL: https://idosell.readme.io/reference/productsparametersdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/parameters/delete')

    params: DeletePimProductsParametersParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Method that enables adding and editing of sections and parameters, modifying their values and setting their order.
    DOCS_URL: https://idosell.readme.io/reference/productsparametersput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/parameters')

    items: List[ItemsParametersModel] = Field(..., min_length=1, description="Sections, parameters or valued to add or edit") # type: ignore
    settings: SettingsParametersPutModel = Field(..., description="Settings")

class Search(PageableCamelGateway):
    """
    Method that enables adding and editing of sections and parameters, modifying their values and setting their order
    DOCS_URL: https://idosell.readme.io/reference/productsparameterssearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/parameters/search')

    params: SearchPimProductsParametersParamsModel | None = Field(None, description="Optional search parameters")
