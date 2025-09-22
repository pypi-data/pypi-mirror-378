from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, IdoSellLanguageId, PageableCamelGateway
from src.idosell.pim.products._common import FiltersActiveSeriesModel, SeriesPutModel


# --- DTOs
class DeletePimProductsSeriesParamsModel(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="IDs") # type: ignore

class PutFilterPimProductsSeriesParamsModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    languageId: IdoSellLanguageId = Field(..., description="Language ID (code in ISO-639-2)")
    serieId: StrictInt = Field(..., ge=1, description="Series Id")
    filterForNodeIsDefault: BooleanStrShortEnum = Field(..., description="...")
    filtersActive: List[FiltersActiveSeriesModel] = Field(..., min_length=1, description="Active filters") # type: ignore

class PutPimProductsSeriesParamsModel(BaseModel):
    series: List[SeriesPutModel] = Field(..., min_length=1, description="Series list") # type: ignore


# --- ENDPOINTS
class Delete(Gateway):
    """
    Method allows you to delete a series of products available in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsseriesdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/series/delete')

    params: DeletePimProductsSeriesParamsModel = Field(..., description="Parameters transmitted to method")

class GetFilter(Gateway):
    """
    Method allows you to retrieve a list of filters for a series of products available in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsseriesfilterget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/series/filter')

    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    languageId: IdoSellLanguageId = Field(..., description="Language ID (code in ISO-639-2)")
    serieId: StrictInt = Field(..., ge=1, description="Series Id")

class PutFilter(AppendableGateway):
    """
    The method allows you to manage the filter settings for the series
    DOCS_URL: https://idosell.readme.io/reference/productsseriesfilterput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/series/filter')

    params: PutFilterPimProductsSeriesParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    Method returns information about the product series available in the IdoSell administration panel.
    DOCS_URL: https://idosell.readme.io/reference/productsseriesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/series')

    return_last_changed_time: str | None = Field(None, min_length=1, description="With 'y' value it returns the last series modification date in YYYY-MM-DD HH:MM:SS format")
    ids: List[int] | None = Field(None, min_length=1, description="IDs") # type: ignore
    names: List[str] | None = Field(None, min_length=1, description="Names") # type: ignore
    languagesIds: List[str] | None = Field(None, min_length=1, description="List of languages") # type: ignore

class Put(AppendableGateway):
    """
    Method allows you to update information about product series available in the IdoSell administration panel.
    DOCS_URL: https://idosell.readme.io/reference/productsseriesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/series')

    params: PutPimProductsSeriesParamsModel = Field(..., description="Parameters transmitted to method")
