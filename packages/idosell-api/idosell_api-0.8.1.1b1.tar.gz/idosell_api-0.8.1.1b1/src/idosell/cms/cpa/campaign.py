from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, PageableCamelGateway


# --- DTOs
class CampaignModel(BaseModel):
    description: str | None = Field(None, description="Snippet campaign internal description")
    shop: List[StrictInt] | None = Field(None, min_length=1, description="Shop ids where code snippets are active") # type: ignore
    active: BooleanStrShortEnum | None = Field(None, description="Whether the snippet is active")

class PostCampaignModel(CampaignModel):
    id: int | None = Field(None, description="Snippet campaign id")
    name: str = Field(..., description="Snippet campaign name")

class PutCampaignModel(CampaignModel):
    id: StrictInt = Field(..., ge=1, description="Snippet campaign id")
    name: str | None = Field(None, description="Snippet campaign name")

class PostCmsCpaCampaignParamsModel(BaseModel):
    campaigns: List[PostCampaignModel] = Field(..., min_length=1, max_length=100, description="...") # type: ignore

class PutCmsCpaCampaignParamsModel(BaseModel):
    campaigns: List[PutCampaignModel] = Field(..., min_length=1, max_length=100, description="...") # type: ignore


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    This call returns all CPA campaigns
    DOCS_URL: https://idosell.readme.io/reference/cpacampaignget-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/campaign')

    shopId: Optional[List[Annotated[int, Field(ge=1)]]] = Field(default=None, min_length=1, description="List of shop identifiers")  # type: ignore
    id: Optional[List[Annotated[int, Field(ge=1)]]] = Field(default=None, min_length=1, description="List of identifiers")  # type: ignore

class Post(AppendableGateway):
    """
    Use this operation to create cpa campaigns
    DOCS_URL: https://idosell.readme.io/reference/cpacampaignpost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/campaign')

    params: PostCmsCpaCampaignParamsModel = Field(..., description="...")

class Put(AppendableGateway):
    """
    Use this operation to update CPA campaigns
    DOCS_URL: https://idosell.readme.io/reference/cpacampaignput-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/campaign')

    params: PutCmsCpaCampaignParamsModel = Field(..., description="...")

class Delete(Gateway):
    """
    This call is used to remove CPA program campaign
    DOCS_URL: https://idosell.readme.io/reference/cpacampaigndelete-1
    """

    _method: str = PrivateAttr(default='DELETE')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/campaign')

    id: List[int] = Field(..., description="List of identifiers")
