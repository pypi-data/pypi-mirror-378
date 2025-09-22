from datetime import date
from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, PageableCamelGateway
from src.idosell.cms._common import BodyModel, DisplayBaseModel, PageEnum, SourceModel, ZoneEnum


# --- Enums
class SnippetsTypeEnum(StrEnum):
    HTML = 'html'
    JAVASCRIPT = 'javascript'
    CGI = 'cgi'


# --- DTOs
class DateBeginSnippetsModel(BaseModel):
    defined: BooleanStrShortEnum = Field(..., description="Whether date condition is active")
    date_value: date = Field(..., alias="date", description="Date of snippet activation")
    autoBlock: BooleanStrShortEnum = Field(..., description="Automatic shutdown control")

class DateEndSnippetsModel(BaseModel):
    defined: BooleanStrShortEnum = Field(..., description="Whether date condition is active")
    date_value: date = Field(..., alias="date", description="Date of snippet activation")

class DisplaySnippetsModel(DisplayBaseModel):
    screen: BooleanStrShortEnum = Field(..., description="Display on desktop screens")
    tablet: BooleanStrShortEnum = Field(..., description="Display on mobile tablets")
    phone: BooleanStrShortEnum = Field(..., description="Display on mobile phones")

class PagesSnippetsModel(BaseModel):
    all: BooleanStrShortEnum = Field(..., description="Whether to display to all sites")
    pages: List[PageEnum] = Field(..., description="List of selected pages where snippet shows (works for all=n mode). If passed, the url should be omitted")
    url: List[str] = Field(..., description="List of selected url (works for all=n mode) If passed, pages should be omitted")

class SnippetsModel(BaseModel):
    active: BooleanStrShortEnum | None = Field(None, description="Whether the snippet is active")
    dateBegin: DateBeginSnippetsModel | None = Field(None, description="Filter to control snippet activation")
    dateEnd: DateEndSnippetsModel | None = Field(None, description="Filter to control snippet activation")
    type: SnippetsTypeEnum | None = Field(None, description="Code snippet type")
    useAjax: BooleanStrShortEnum | None = Field(None, description="Whether to load contents asynchronously via XHR request")
    link: str | None = Field(None, description="Url")
    timeout: StrictInt | None = Field(None, ge=1, le=10, description="Content waiting time (timeout) in seconds")
    zone: ZoneEnum | None = Field(None, description="The place where the code snippet is loaded")
    order: StrictInt | None = Field(None, description="The order in which the code snippet will be displayed")
    body: BodyModel | None = Field(None, description="Snippet content for each language")
    display: DisplaySnippetsModel | None = Field(None, description="...")
    pages: PagesSnippetsModel | None = Field(None, description="...")
    sources: SourceModel | None = Field(None, description="Snippet entry source filter")

class PostSnippetsModel(SnippetsModel):
    id: int | None = Field(None, ge=1, description="Id of the code snippet")
    name: str = Field(..., description="The snippet name")
    campaign: StrictInt = Field(..., ge=1, description="Snippet campaign id")

class PutSnippetsModel(SnippetsModel):
    id: StrictInt = Field(..., ge=1, description="Id of the code snippet")
    name: str | None = Field(None, description="The snippet name")
    campaign: StrictInt | None = Field(None, ge=1, description="Snippet campaign id")

class PostCmsSnippetsSnippetsParamsModel(BaseModel):
    snippets: List[PostSnippetsModel] = Field(..., description="...") # array of objects length between 1 and 100

class PutCmsSnippetsSnippetsParamsModel(BaseModel):
    snippets: List[PutSnippetsModel] = Field(..., description="...") # array of objects length between 1 and 100


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    This call returns all snippets
    DOCS_URL: https://idosell.readme.io/reference/snippetssnippetsget-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/snippets')

    campaign: List[int] | None = Field(None, min_length=1, description="List of campaign identifiers") # type: ignore
    id: List[int] | None = Field(None, min_length=1, description="List of identifiers") # type: ignore
    omitDeleted: BooleanStrShortEnum | None = Field(None, description="Whether to skip the return of deleted campaigns")


class Post(AppendableGateway):
    """
    Use this operation to create code snippet
    DOCS_URL: https://idosell.readme.io/reference/snippetssnippetspost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/snippets')

    params: PostCmsSnippetsSnippetsParamsModel = Field(..., description="...")

class Put(AppendableGateway):
    """
    Use this operation to update code snippet
    DOCS_URL: https://idosell.readme.io/reference/snippetssnippetsput-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/snippets')

    params: PutCmsSnippetsSnippetsParamsModel = Field(..., description="...")

class Delete(Gateway):
    """
    This call is used to remove snippets
    DOCS_URL: https://idosell.readme.io/reference/snippetssnippetsdelete-1
    """

    _method: str = PrivateAttr(default='DELETE')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/snippets')

    id: List[int] = Field(..., description="List of identifiers")
