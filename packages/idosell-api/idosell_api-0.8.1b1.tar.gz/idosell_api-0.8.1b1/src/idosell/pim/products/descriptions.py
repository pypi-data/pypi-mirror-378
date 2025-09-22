from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.pim.products._common import IdentTypeEnum, ProductsDescriptionsModel


# --- DTOs
class PutPimProductsDescriptionsParamsModel(BaseModel):
    products: List[ProductsDescriptionsModel] = Field(..., min_length=1, description="Products list") # type: ignore


# --- ENDPOINTS
class Get(Gateway):
    """
    Method that returns text elements for a given product, e.g. product name, long and short description, metadata
    DOCS_URL: https://idosell.readme.io/reference/productsdescriptionsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/descriptions')

    type: IdentTypeEnum = Field(..., description="Identifier type")
    ids: List[int] = Field(..., min_length=1, description="ID value") # type: ignore
    shopId: StrictInt | None = Field(None, ge=1, description="Shop Id")

class Put(AppendableGateway):
    """
    The method allows for setting text elements for a given product, e.g. product name, long and short description, metadata
    DOCS_URL: https://idosell.readme.io/reference/productsdescriptionsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/descriptions')

    params: PutPimProductsDescriptionsParamsModel = Field(..., description="Parameters transmitted to method")
