from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway
from src.idosell.pim.products._common import (
    ProductIdentBundlesModel, ProductPutRenewModel, ProductsBundleDeleteProductsModel, ProductsBundlesPostModel,
    ProductsBundlesPostProductsModel, ProductsPutProductsQuantityModel
)


# --- DTOs
class DeleteProductsPimProductsBundlesParamsModel(BaseModel):
    products: List[ProductsBundleDeleteProductsModel] = Field(..., min_length=1, description="Products list") # type: ignore
    bundleIdent: ProductIdentBundlesModel = Field(..., description="Bundle identifier")

class PostBundlesPimProductsBundlesParamsModel(BaseModel):
    products: List[ProductsBundlesPostModel] = Field(..., min_length=1, description="Products list") # type: ignore

class PostProductsPimProductsBundlesParamsModel(BaseModel):
    products: List[ProductsBundlesPostProductsModel] = Field(..., min_length=1, description="Products list") # type: ignore
    bundleIdent: ProductIdentBundlesModel = Field(..., description="Bundle identifier")

class PutProductsQuantityPimProductsBundlesParamsModel(BaseModel):
    products: List[ProductsPutProductsQuantityModel] = Field(..., min_length=1, description="Products list") # type: ignore
    bundleIdent: ProductIdentBundlesModel = Field(..., description="Bundle identifier")

class PutRenewPimProductsBundlesParamsModel(BaseModel):
    products: List[ProductPutRenewModel] = Field(..., min_length=1, description="Products list") # type: ignore
    bundleIdent: ProductIdentBundlesModel = Field(..., description="Bundle identifier")


# --- ENDPOINTS
class PostBundles(AppendableGateway):
    """
    createBundle method allows to create a new product with a type: set and to assign existing products as a set components. Products added via this gate are hidden from the shop customer by default. To change the visibility of created products use the gate setProducts or set it on a product card in the shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsbundlesbundlespost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/bundles/bundles')

    params: PostBundlesPimProductsBundlesParamsModel = Field(..., description="Parameters transmitted to method")

class DeleteProducts(AppendableGateway):
    """
    removeProductsFromBundle method allows to remove indicated set components
    DOCS_URL: https://idosell.readme.io/reference/productsbundlesproductsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/bundles/products/delete')

    params: List[DeleteProductsPimProductsBundlesParamsModel] = Field(..., description="Parameters transmitted to method")

class PostProducts(AppendableGateway):
    """
    addProductsToBundle method allows to add components to existing sets in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsbundlesproductspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/bundles/products')

    params: PostProductsPimProductsBundlesParamsModel = Field(..., description="Parameters transmitted to method")

class PutProductsQuantity(AppendableGateway):
    """
    setProductsQuantityInBundle method allows to indicate quantity of a set component
    DOCS_URL: https://idosell.readme.io/reference/productsbundlesproductsquantityput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/bundles/productsQuantity')

    params: PutProductsQuantityPimProductsBundlesParamsModel = Field(..., description="Parameters transmitted to method")

class PutRenew(AppendableGateway):
    """
    the renewProductsInBundle method allows you to rebuild components of Sets existing in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsbundlesrenewput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/bundles/renew')

    params: PutRenewPimProductsBundlesParamsModel = Field(..., description="Parameters transmitted to method")
