from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway
from src.idosell.pim.products._common import GroupsPutSettingsModel, ProductIdentModel, ProductsInOrderModel


# --- DTOs
class PutMainProductPimProductsGroupsParamsModel(BaseModel):
    groups: List[ProductIdentModel] = Field(..., min_length=1, description="List of product identifiers") # type: ignore

class PutOrderPimProductsGroupsParamsModel(BaseModel):
    groups: List[ProductsInOrderModel] = Field(..., min_length=1, description="Groups with products and order priorities") # type: ignore

class PutSettingsPimProductsGroupsParamsModel(BaseModel):
    groups: List[GroupsPutSettingsModel] = Field(..., min_length=1, description="Groups display settings") # type: ignore


# --- ENDPOINTS
class PutMainProduct(AppendableGateway):
    """
    The method allows you to change the main product in a group of products
    DOCS_URL: https://idosell.readme.io/reference/productsgroupsmainproductput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/groups/mainProduct')

    params: PutMainProductPimProductsGroupsParamsModel = Field(..., description="Parameters transmitted to method")

class PutOrder(AppendableGateway):
    """
    The method allows you to change the order of products in a group of products
    DOCS_URL: https://idosell.readme.io/reference/productsgroupsorderput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/groups/order')

    params: PutOrderPimProductsGroupsParamsModel = Field(..., description="Parameters transmitted to method")

class PutSettings(AppendableGateway):
    """
    The method allows you to change the settings for displaying products to a group of products
    DOCS_URL: https://idosell.readme.io/reference/productsgroupssettingsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/groups/settings')

    params: PutSettingsPimProductsGroupsParamsModel = Field(..., description="Parameters transmitted to method")
