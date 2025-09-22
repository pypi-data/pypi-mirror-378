from typing import List
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import AppendableGateway
from src.idosell.pim.products._common import ProductsSupplierPutCodeModel, ProductsSupplierPutProductDataModel


# --- DTOs
class PutCodePimProductsSupplierParamsModel(BaseModel):
    products: List[ProductsSupplierPutCodeModel] = Field(..., min_length=1, description="Products list") # type: ignore

class PutProductDataPimProductsSupplierParamsModel(BaseModel):
    products: List[ProductsSupplierPutProductDataModel] = Field(..., min_length=1, description="Products list") # type: ignore


# --- ENDPOINTS
class PutCode(AppendableGateway):
    """
    The method allows to edit supplier data in the IdoSell Shop administration panel.
    DOCS_URL: https://idosell.readme.io/reference/productssuppliercodeput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/supplierCode')

    params: PutCodePimProductsSupplierParamsModel = Field(..., description="Parameters transmitted to method")

class PutProductData(AppendableGateway):
    """
    The method allows you to edit the commodity data related to its suppliers.
    DOCS_URL: https://idosell.readme.io/reference/productssupplierproductdataput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/supplierProductData')

    params: PutProductDataPimProductsSupplierParamsModel = Field(..., description="Parameters transmitted to method")
