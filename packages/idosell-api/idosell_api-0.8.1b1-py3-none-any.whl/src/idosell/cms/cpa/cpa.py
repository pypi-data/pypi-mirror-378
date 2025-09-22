from enum import StrEnum
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, PageableCamelGateway
from src.idosell.cms._common import BodyModel, DisplayBaseModel, PageEnum, SourceModel, ZoneEnum


# --- Enums
class PageSettingsModeEnum(StrEnum):
    ADVANCED = 'advanced'
    SIMPLE = 'simple'

class SourceEnum(StrEnum):
    COOKIE = 'cookie'
    SESSION = 'session'


# --- CPA DTOs
class DisplayModel(DisplayBaseModel):
    pass

class PageModel(BaseModel):
    active: BooleanStrShortEnum = Field(..., description="...")
    page: PageEnum = Field(..., description="...")
    zone: ZoneEnum = Field(..., description="The place where the cpa code is loaded. (For 'all' mode)")
    body: List[BodyModel] = Field(..., description="...")

class PageSettingsModel(BaseModel):
    mode: PageSettingsModeEnum = Field(..., description="Whether to display to all sites")
    zone: ZoneEnum | None = Field(None, description="The place where the cpa code is loaded. (For 'all' mode)")
    body: List[BodyModel] | None = Field(None, description="Snippet content for each language. (For 'all' mode)")
    pages: List[PageModel] | None = Field(None, description="Page setting for advance mode")

class VariableModel(BaseModel):
    name: str = Field(..., max_length=150, description="...")
    source: SourceEnum = Field(..., description="...")

class CpaModel(BaseModel):
    active: BooleanStrShortEnum | None = Field(None, description="Whether the CPA program is active")
    pageSettings: PageSettingsModel | None = Field(None, description="CPA program page settings simple or advanced, depending on the mode")
    display: DisplayModel | None = Field(None, description="...")
    sources: SourceModel | None = Field(None, description="Snippet entry source filter")
    variables: List[VariableModel] | None = Field(None, description="List of variables that can be used in a body template")

class PostCpaModel(CpaModel):
    id: int | None = Field(None, description="Id of the CPA program")
    name: str = Field(..., description="The CPA program name")
    campaign: StrictInt = Field(..., ge=1, description="CPA campaign id")

class PutCpaModel(CpaModel):
    id: StrictInt = Field(..., ge=1, description="Id of the CPA program")
    name: str | None = Field(None, description="The CPA program name")
    campaign: StrictInt | None = Field(None, ge=1, description="CPA campaign id")

class PostCmsCpaCpaParamsModel(BaseModel):
    cpa: List[PostCpaModel] = Field(..., min_length=1, max_length=100, description="...") # type: ignore

class PutCmsCpaCpaParamsModel(BaseModel):
    cpa: List[PutCpaModel] = Field(..., min_length=1, max_length=100, description="...") # type: ignore


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    This call returns all cpa programs
    DOCS_URL: https://idosell.readme.io/reference/cpacpaget-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/cpa')

    campaign: Optional[List[Annotated[int, Field(ge=1)]]] = Field(default=None, min_length=1, description="List of campaign identifiers") # type: ignore
    id: Optional[List[Annotated[int, Field(ge=1)]]] = Field(default=None, min_length=1, description="List of identifiers") # type: ignore

class Post(AppendableGateway):
    """
    Use this operation to create code snippet
    DOCS_URL: https://idosell.readme.io/reference/cpacpapost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/cpa')

    params: PostCmsCpaCpaParamsModel = Field(..., description="...")

class Put(AppendableGateway):
    """
    Use this operation to update code snippet
    DOCS_URL: https://idosell.readme.io/reference/cpacpaput-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/cpa')

    params: PutCmsCpaCpaParamsModel = Field(..., description="...")

class Delete(Gateway):
    """
    This call is used to remove CPA programs
    DOCS_URL: https://idosell.readme.io/reference/cpacpadelete-1
    """

    _method: str = PrivateAttr(default='DELETE')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/cpa/cpa')

    id: List[int] = Field(..., description="List of identifiers")
