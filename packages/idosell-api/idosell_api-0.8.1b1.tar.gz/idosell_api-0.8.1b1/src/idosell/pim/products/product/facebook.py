from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway


# --- DTOs
class DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(BaseModel):
    facebookCatalogId: StrictInt = Field(..., ge=1, description="You can read the Facebook Catalog ID in the Marketing & Integrations/Facebook/Facebook Product Catalog admin panel")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    products: List[int] = Field(..., min_length=1, description="Products list") # type: ignore

class PostToFacebookCatalogPimProductsProductFacebookParamsModel(BaseModel):
    facebookCatalogId: StrictInt = Field(..., description="You can read the Facebook Catalog ID in the Marketing & Integrations/Facebook/Facebook Product Catalog admin panel")
    shopId: StrictInt = Field(..., description="Shop Id")
    products: List[int] = Field(..., min_length=1, description="Products list") # type: ignore


# --- ENDPOINTS
class DeleteToFacebookCatalog(Gateway):
    """
    The method allows you to add products to the Facebook catalog
    DOCS_URL: https://idosell.readme.io/reference/productsproductstofacebookcatalogdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/productsToFacebookCatalog/delete')

    params: DeleteToFacebookCatalogPimProductsProductFacebookParamsModel = Field(..., description="Parameters transmitted to method")

class GetToFacebookCatalog(Gateway):
    """
    The method allows you to retrieve products assigned to the Facebook catalog
    DOCS_URL: https://idosell.readme.io/reference/productsproductstofacebookcatalogget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/productsToFacebookCatalog')

    facebookCatalogId: StrictInt = Field(..., ge=1, description="You can read the Facebook Catalog ID in the Marketing & Integrations/Facebook/Facebook Product Catalog admin panel")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")

class PostToFacebookCatalog(Gateway):
    """
    The method allows you to add products to the Facebook catalog
    DOCS_URL: https://idosell.readme.io/reference/productsproductstofacebookcatalogpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/productsToFacebookCatalog')

    params: PostToFacebookCatalogPimProductsProductFacebookParamsModel = Field(..., description="Parameters transmitted to method")
