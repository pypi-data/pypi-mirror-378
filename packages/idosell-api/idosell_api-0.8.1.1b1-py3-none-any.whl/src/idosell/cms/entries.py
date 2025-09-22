from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway


# --- Enums
class PictureFormatEntriesEnum(StrEnum):
    JPG = 'jpg'
    JPEG = 'jpeg'
    PNG = 'png'
    GIF = 'gif'


# --- DTOs
class LangsEntriesModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    title: str = Field(..., description="Name on the page")
    shortDescription: str = Field(..., description="short description")
    longDescription: str = Field(..., description="Long description")
    blogUrl: str = Field(..., description="Blog post URL")
    newsUrl: str = Field(..., description="News item URL")

class VisibleOnSitesListEntriesModel(BaseModel):
    siteId: str = Field(..., description="Site ID")

class ProductsEntriesModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Merchandise identifier")

class PictureEntriesDataModel(BaseModel):
    pictureBase64: str = Field(..., description="Photo encoded with Base64")
    pictureFormat: PictureFormatEntriesEnum = Field(..., description="Photo format")

class EntitiesModel(BaseModel):
    shopId: StrictInt | None = Field(None, description="Shop Id")
    date: str | None = Field(None, description="Date of creating an entry")
    visible: BooleanStrShortEnum | None = Field(None, description="Entry visibility")
    visibleOnSitesList: List[VisibleOnSitesListEntriesModel] | None = Field(None, description="List of pages on which the entry is to be published")
    products: List[ProductsEntriesModel] | None = Field(None, description="Products list")
    pictureData: PictureEntriesDataModel | None = Field(None, description="Photo")
    langs: List[LangsEntriesModel] | None = Field(None, description="Element including entry content in selected languages")
    titleLinkType: str | None = Field(None, description="Type of title and shortcut linking: fullContentLink - link to the subpage with full content, givenUrlLink - link to the given URL, noLink - static element")
    link: str | None = Field(None, description="Provided URL (for link to specified URL option)")

class DeleteCmsEntriesParamsModel(BaseModel):
    entryId: StrictInt = Field(..., ge=1, description="Entry ID")

class PostCmsEntriesParamsModel(EntitiesModel):
    pass

class PutCmsEntriesParamsModel(EntitiesModel):
    entryId: StrictInt = Field(..., ge=1, description="Entry ID")
    deletePicture: BooleanStrShortEnum = Field(..., description="Determines whether to delete an entry photo")


# --- ENDPOINTS
class Delete(Gateway):
    """
    Enables deleting blog or news entry
    DOCS_URL: https://idosell.readme.io/reference/entriesentriesdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/entries/entries/delete')

    params: DeleteCmsEntriesParamsModel = Field(..., description="...")

class Get(Gateway):
    """
    Enables downloading blog or news entry data
    DOCS_URL: https://idosell.readme.io/reference/entriesentriesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/entries/entries')

    entryId: Optional[StrictInt] = Field(None, ge=1, description="Entry ID")
    langId: Optional[str] = Field(None, min_length=1, description="Language ID")

class Post(AppendableGateway):
    """
    Enables adding blog or news entry
    DOCS_URL: https://idosell.readme.io/reference/entriesentriespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/entries/entries')

    params: PostCmsEntriesParamsModel = Field(..., description="...")

class Put(Gateway):
    """
    Enables changing blog or news entry in the shop
    DOCS_URL: https://idosell.readme.io/reference/entriesentriesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/entries/entries')

    params: PutCmsEntriesParamsModel = Field(..., description="...")

class GetPagesToDisplay(Gateway):
    """
    Allows you to download a list of sites on which a blog entry or a news item can be published
    DOCS_URL: https://idosell.readme.io/reference/entriespagestodisplayget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/entries/pagesToDisplay')

    langId: str | None = Field(None, description="Language ID")

class GetSources(Gateway):
    """
    DOCS: This call returns all entry sources with options
    DOCS_URL: https://idosell.readme.io/reference/entriessourcesget-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/entries/sources')

    type: Optional[List[str]] = Field(None, min_length=1, description="The type of source for which we want to get service identifiers") # type: ignore
