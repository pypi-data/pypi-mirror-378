from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway


# --- Enums
class OperationTagsEnum(StrEnum):
    ADD = 'add'
    SET = 'set'
    SUBSTRACT = 'substract'


# --- DTOs
class ClientTagsModel(BaseModel):
    tagId: StrictInt = Field(..., ge=1, description="Tag ID")
    operation: OperationTagsEnum = Field(..., description="...")
    tagValue: StrictInt = Field(..., ge=1, description="Tag value")

class DeleteClearCrmTagsParamsModel(BaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")

class DeleteCrmTagsParamsModel(BaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")
    tagId: StrictInt = Field(..., ge=1, description="Tag ID")

class PostCrmTagsParamsModel(BaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")
    tagName: str = Field(..., description="Tag name")
    tagValue: StrictInt = Field(..., ge=1, description="Tag value")

class PutCrmTagsParamsModel(BaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")
    clientTags: List[ClientTagsModel] = Field(..., description="...")


# --- ENDPOINTS
class DeleteClear(Gateway):
    """
    Use this method to delete all tags assigned to a customer
    DOCS_URL: https://idosell.readme.io/reference/clientstagscleardeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/tags/clear/delete')

    params: DeleteClearCrmTagsParamsModel = Field(..., description="Parameters transmitted to method")

class Delete(AppendableGateway):
    """
    Use this method to delete selected tags assigned to a customer
    DOCS_URL: https://idosell.readme.io/reference/clientstagsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/tags/delete')

    params: List[DeleteCrmTagsParamsModel] = Field(..., description="Parameters transmitted to method")

class Get(Gateway):
    """
    Use this method to retrieve all tags assigned to a client
    DOCS_URL: https://idosell.readme.io/reference/clientstagsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/tags')

    clientId: Optional[StrictInt] = Field(default=None, ge=1, description="Unique client's number")

class Post(AppendableGateway):
    """
    Use this method to add new tags and their associated values to the client
    DOCS_URL: https://idosell.readme.io/reference/clientstagspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/tags')

    params: PostCrmTagsParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    The method is used to update the value of the tags assigned to the client. A tag with value 0 is detached from the client
    DOCS_URL: https://idosell.readme.io/reference/clientstagsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/tags')

    params: PutCrmTagsParamsModel = Field(..., description="Parameters transmitted to method")
