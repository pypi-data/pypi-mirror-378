from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway


# --- Enums
class DeleteModeSizesEnum(StrEnum):
    DELETE_BY_SIZE = 'delete_by_size'
    DELETE_ALL = 'delete_all'

class PutModeSizesEnum(StrEnum):
    ADD = 'add'
    EDIT = 'edit'
    REPLACE = 'replace'


# --- DTOs
class ProductPricesSizesModel(BaseModel):
    productPriceRetail: float = Field(..., gt=0, description="Retail price")
    productPriceWholesale: float = Field(..., gt=0, description="Wholesale price")
    productSearchPriceMin: float = Field(..., ge=0, description="Minimal price for product")
    productPriceSuggested: float = Field(..., gt=0, description="Recommended retail price")

class SitesDataModel(BaseModel):
    siteId: StrictInt = Field(..., ge=1, description="Page ID")
    productPrices: ProductPricesSizesModel = Field(..., description="...")

class SizeDataModel(BaseModel):
    productWeight: StrictInt = Field(..., gt=0, description="Weight")
    codeProducer: str = Field(..., description="Producer code")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")
    sitesData: List[SitesDataModel] = Field(..., description="Parameters set for shops")

class IndexesDataSizesPutModel(BaseModel):
    sizeIndex: str = Field(..., description="Product index")
    sizeData: SizeDataModel = Field(..., description="Parameters set for sizes")

class SizesParamsDeleteModel(BaseModel):
    sizeId: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")

class DeletePimProductsSizesParamsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    sizes: List[SizesParamsDeleteModel] = Field(..., description="List of sizes")

class SizesModel(BaseModel):
    sizeId: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")
    sizeData: SizeDataModel = Field(..., description="Parameters set for sizes")

class SizesProductsDataPutModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    sizes: List[SizesModel] = Field(..., description="List of sizes")

# --- ENDPOINTS
class Delete(AppendableGateway):
    """
    The method is used to remove sizes
    DOCS_URL: https://idosell.readme.io/reference/productssizesdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/sizes/delete')

    mode: DeleteModeSizesEnum = Field(..., description="Edition mode")
    params: DeletePimProductsSizesParamsModel = Field(..., description="Parameters transmitted to method")
    deleteSizesIndexesData: List[str] = Field(..., min_length=1, description="Product parameters recognized by index") # type: ignore

class Get(Gateway):
    """
    Method that returns information about product sizes configured in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productssizesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/sizes')

    page: StrictInt | None = Field(None, ge=0, description="Page with results number. Numeration starts from 0", alias="result::page")
    pageNumber: StrictInt | None = Field(None, ge=1, le=100, description="Number of results on page. Value from 1 to 100", alias="result::pageNumber")

class Put(AppendableGateway):
    """
    This method allows you to edit the size-dependent data
    DOCS_URL: https://idosell.readme.io/reference/productssizesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/sizes')

    mode: PutModeSizesEnum = Field(..., description="Edition mode")
    sizesProductsData: List[SizesProductsDataPutModel] = Field(..., min_length=1, description="Product parameters recognized by product ID or its sizes") # type: ignore
    indexesData: List[IndexesDataSizesPutModel] = Field(..., min_length=1, description="Product parameters recognized by index") # type: ignore
