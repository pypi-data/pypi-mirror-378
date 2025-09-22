from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway
from src.idosell.pim.products._common import (
    CollectionIdentModel, ProductsCollectionsDeleteProductsModel, ProductsCollectionsPostModel, ProductsCollectionsPostProductsModel,
    ProductsCollectionsPutProductsModel, ProductsCollectionsPutRenewModel
)


# --- DTOs
class DeleteProductsPimProductsCollectionsParamsModel(BaseModel):
    products: List[ProductsCollectionsDeleteProductsModel] = Field(..., min_length=1, description="Products list") # type: ignore
    collectionId: StrictInt = Field(..., ge=1, description="ID of a collection being modified")

class PostPimProductsCollectionsParamsModel(BaseModel):
    products: List[ProductsCollectionsPostModel] = Field(..., min_length=1, description="Products list") # type: ignore

class PostProductsPimProductsCollectionsParamsModel(BaseModel):
    products: List[ProductsCollectionsPostProductsModel] = Field(..., min_length=1, description="Products list") # type: ignore
    collectionId: StrictInt = Field(..., ge=1, description="ID of a collection being modified")

class PutProductsPimProductsCollectionsParamsModel(BaseModel):
    products: List[ProductsCollectionsPutProductsModel] = Field(..., min_length=1, description="Products list") # type: ignore
    collectionId: StrictInt = Field(..., ge=1, description="ID of a collection being modified")

class PutRenewPimProductsCollectionsParamsModel(BaseModel):
    products: List[ProductsCollectionsPutRenewModel] = Field(..., min_length=1, description="Products list") # type: ignore
    collectionIdent: CollectionIdentModel = Field(..., description="ID of a collection being modified")



# --- ENDPOINTS
class Post(AppendableGateway):
    """
    createCollection method allows to create a new product with a type: collection and to assign existing products as a collection components. Products added via this gate are hidden from the shop customer by default. To change the visibility of created products use the gate setProducts or set it on a product card in the shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productscollectionspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/collections')

    params: PostPimProductsCollectionsParamsModel = Field(..., description="Parameters transmitted to method")

class DeleteProducts(AppendableGateway):
    """
    removeProductsFromCollection method allows to remove indicated collection components
    DOCS_URL: https://idosell.readme.io/reference/productscollectionsproductsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/collections/products/delete')

    params: List[DeleteProductsPimProductsCollectionsParamsModel] = Field(..., description="Parameters transmitted to method")

class PostProducts(AppendableGateway):
    """
    addProductsToCollection method allows to add components to existing collections in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productscollectionsproductspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/collections/products')

    params: PostProductsPimProductsCollectionsParamsModel = Field(..., description="Parameters transmitted to method")

class PutProducts(AppendableGateway):
    """
    setProductsQuantityInCollection method allows to indicate quantity of a collection component
    DOCS_URL: https://idosell.readme.io/reference/productscollectionsproductsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/collections/products')

    params: PutProductsPimProductsCollectionsParamsModel = Field(..., description="Parameters transmitted to method")

class PutRenew(AppendableGateway):
    """
    The renewProductsInCollection method allows you to rebuild existing components of Collections in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productscollectionsrenewput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/collections/renew')

    params: PutRenewPimProductsCollectionsParamsModel = Field(..., description="Parameters transmitted to method")
