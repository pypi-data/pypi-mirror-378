from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.pim.products._common import IdentTypeEnum, ProductsOmnibusModel


# --- DTOs
class PutPricesPimProductsOmnibusParamsModel(BaseModel):
    products: List[ProductsOmnibusModel] = Field(..., description="Products list")


# --- ENDPOINTS
class GetPrices(Gateway):
    """
    Allows you to download information about the lowest prices before promotions
    DOCS_URL: https://idosell.readme.io/reference/productsomnibuspricesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/omnibusPrices')

    identType: IdentTypeEnum | None = Field(None, description="Identifier type")
    products: List[str] | None = Field(None, min_length=1, max_length=100, description="Products list") # type: ignore

class PutPrices(AppendableGateway):
    """
    Allows for editing product strikethrough price settings
    DOCS_URL: https://idosell.readme.io/reference/productsomnibuspricesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/omnibusPrices')

    params: PutPricesPimProductsOmnibusParamsModel = Field(..., description="Parameters transmitted to method")
