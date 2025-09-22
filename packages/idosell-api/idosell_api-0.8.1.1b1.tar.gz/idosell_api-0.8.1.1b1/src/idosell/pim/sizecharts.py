from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway, Gateway, IdoSellLanguageId, PageableCamelGateway
from src.idosell.pim._common import SizeChartsPutModel


# --- DTOs
class DeletePimSizechartsParamsModel(BaseModel):
    ids: List[int] = Field(..., description="!identyfikatory!#")

class PutPimSizechartsParamsModel(BaseModel):
    sizeCharts: List[SizeChartsPutModel] = Field(..., description="...")


# --- ENDPOINTS
class Delete(Gateway):
    """
    The method allows the removal of size charts
    DOCS_URL: https://idosell.readme.io/reference/sizechartssizechartsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/sizecharts/sizecharts/delete')

    params: DeletePimSizechartsParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    The method allows size charts to be downloaded.
    DOCS_URL: https://idosell.readme.io/reference/sizechartssizechartsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/sizecharts/sizecharts')

    ids: List[int] | None = Field(None, description="IDs")
    names: List[str] | None = Field(None, description="Names of size charts")
    languages: List[IdoSellLanguageId] | None = Field(None, description="List of languages")

class Put(AppendableGateway):
    """
    The method allows the size charts settings to be updated
    DOCS_URL: https://idosell.readme.io/reference/sizechartssizechartsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/sizecharts/sizecharts')

    params: PutPimSizechartsParamsModel = Field(..., description="Parameters transmitted to method")
