from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway


# --- Enums
class CategoryEnum(StrEnum):
    ANALYTICS = 'analytics'
    MARKETING = 'marketing'
    FUNCTIONAL = 'functional'

class LifeTimeTypeEnum(StrEnum):
    TEMPORARY = 'temporary'
    DAYS = 'days'
    MINUTES = 'minutes'

class TypeEnum(StrEnum):
    COOKIE = 'cookie'
    PIXEL = 'pixel'
    LOCALSTORAGE = 'localStorage'


# --- DTOs
class DescriptionCookiesModel(BaseModel):
    lang: str = Field(..., min_length=3, max_length=3, description="Language code")
    body: str = Field(..., description="...")

class CookiesModel(BaseModel):
    category: CategoryEnum | None = Field(None, description="Category of the cookie")
    description: List[DescriptionCookiesModel] | None = Field(None, description="Cookie description for each language")
    name: str | None = Field(None, description="Name of the cookie")
    type: TypeEnum | None = Field(None, description="Type of the cookie")
    lifeTimeType: LifeTimeTypeEnum | None = Field(None, description="Cookie lifetime mode")
    lifeTime: StrictInt | None = Field(None, description="Cookie lifetime")

class PostCookiesModel(CookiesModel):
    id: int | None = Field(None, ge=1, description="Snippet")
    snippetId: StrictInt = Field(..., ge=1, description="Id of the snippet code")
    deliverer: str = Field(..., min_length=1, max_length=128, description="Name of the cookie vendor")

class PutCookiesModel(CookiesModel):
    id: StrictInt = Field(..., ge=1, description="Snippet")
    snippetId: StrictInt | None = Field(None, ge=1, description="Id of the snippet code")
    deliverer: str | None = Field(None, min_length=1, max_length=128, description="Name of the cookie vendor")

class PostCmsSnippetsCookiesParamsModel(BaseModel):
    cookies: List[PostCookiesModel] = Field(..., min_length=1, max_length=100, description="...") # type: ignore

class PutCmsSnippetsCookiesParamsModel(BaseModel):
    cookies: List[PutCookiesModel] = Field(..., min_length=1, max_length=100, description="...") # type: ignore


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    This call returns all cookie definitions related to code snippets
    DOCS_URL: https://idosell.readme.io/reference/snippetscookiesget-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/cookies')

    id: Optional[List[int]] = Field(None, min_length=1, description="List of identifiers for specific cookies") # type: ignore

class Post(AppendableGateway):
    """
    Use this operation to create a cookie definition for a code snippet
    DOCS_URL: https://idosell.readme.io/reference/snippetscookiespost-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/cookies')

    params: PostCmsSnippetsCookiesParamsModel = Field(..., description="...")

class Put(AppendableGateway):
    """
    Use this operation to update a cookie definition for a code snippet
    DOCS_URL: https://idosell.readme.io/reference/snippetscookiesput-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/cookies')

    params: PutCmsSnippetsCookiesParamsModel = Field(..., description="...")

class Delete(Gateway):
    """
    This call is used to remove campaign cookies
    DOCS_URL: https://idosell.readme.io/reference/snippetscookiesdelete-1
    """

    _method: str = PrivateAttr(default='DELETE')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/snippets/cookies')

    id: List[int] = Field(..., description="List of cookie identifiers")
