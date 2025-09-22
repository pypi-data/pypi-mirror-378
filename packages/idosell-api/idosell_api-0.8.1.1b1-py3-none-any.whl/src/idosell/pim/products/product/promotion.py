from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway


# --- DTOs
class DeleteProductsToPromotionPimProductsProductPromotionParamsModel(BaseModel):
    promotionId: StrictInt = Field(..., ge=1, description="Special offer ID")
    products: List[int] = Field(..., min_length=1, description="Products list") # type: ignore

class PostProductsToPromotionPimProductsProductPromotionParamsModel(BaseModel):
    promotionId: StrictInt = Field(..., description="Special offer ID")
    products: List[int] = Field(..., min_length=1, description="Products list") # type: ignore


# --- ENDPOINTS
class DeleteProductsToPromotion(Gateway):
    """
    The method allows to remove the products from the promotion
    DOCS_URL: https://idosell.readme.io/reference/productsproductstopromotiondeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/productsToPromotion/delete')

    params: DeleteProductsToPromotionPimProductsProductPromotionParamsModel = Field(..., description="Parameters transmitted to method")

class PostProductsToPromotion(Gateway):
    """
    The method allows to add products to an existing special offer
    DOCS_URL: https://idosell.readme.io/reference/productsproductstopromotionpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/productsToPromotion')

    params: PostProductsToPromotionPimProductsProductPromotionParamsModel = Field(..., description="Parameters transmitted to method")
