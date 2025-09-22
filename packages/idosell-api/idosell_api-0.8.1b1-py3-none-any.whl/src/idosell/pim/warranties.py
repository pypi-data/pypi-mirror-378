from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway, Gateway, PageableSnakeGateway
from src.idosell.pim._common import LangDataWarrantiesModel, ResultsOrderWarrantiesGetModel, WarrantiesPostModel, WarrantiesPutModel


# --- DTOs
class DeletePimWarrantiesParamsModel(BaseModel):
    warranty_ids: List[str] = Field(..., description="...")

class PostPimWarrantiesParamsModel(BaseModel):
    warranties: List[WarrantiesPostModel] = Field(..., description="...")

class PutLanguageDataPimWarrantiesParamsModel(BaseModel):
    lang_data: LangDataWarrantiesModel = Field(..., description="...")

class PutPimWarrantiesParamsModel(BaseModel):
    warranties: List[WarrantiesPutModel] = Field(..., description="...")


# --- ENDPOINTS
class GetCountTotal(Gateway):
    """
    Method that enables getting the number of product guarantees available in the administration panel.
    DOCS_URL: https://idosell.readme.io/reference/warrantiescounttotalget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/warranties/countTotal')

    warranty_ids: List[str] | None = Field(None, description="...")

class PutLanguageData(AppendableGateway):
    """
    Method that enables editing product warranty language settings
    DOCS_URL: https://idosell.readme.io/reference/warrantieslanguagedataput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/warranties/languageData')

    params: PutLanguageDataPimWarrantiesParamsModel = Field(..., description="Parameters transmitted to method")

class Delete(Gateway):
    """
    Method that enables deleting product warranties from the administration panel
    DOCS_URL: https://idosell.readme.io/reference/warrantieswarrantiesdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/warranties/warranties/delete')

    params: DeletePimWarrantiesParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableSnakeGateway):
    """
    Method that enables getting a list of product warranties available in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/warrantieswarrantiesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/warranties/warranties')

    warranty_ids: List[str] | None = Field(None, description="...")
    resultsOrder: ResultsOrderWarrantiesGetModel | None = Field(None, description="...")

class Post(AppendableGateway):
    """
    Method that enables adding product warranties to the administration panel
    DOCS_URL: https://idosell.readme.io/reference/warrantieswarrantiespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/warranties/warranties')

    params: PostPimWarrantiesParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Method that enables editing product warranties available in the administration panel.
    DOCS_URL: https://idosell.readme.io/reference/warrantieswarrantiesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/warranties/warranties')

    params: PutPimWarrantiesParamsModel = Field(..., description="Parameters transmitted to method")
