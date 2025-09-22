from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, PageableCamelGateway
from src.idosell.pim.products._common import (
    ClientsOpinionsModel, DateRangeGetModel, OpinionGetModel, OpinionsPostModel, OrdersByGetModel,
    ProductsOpinionsGetModel, RateEnum, ScoreNegativeGetModel, ScorePositiveGetModel
)


# --- DTOs
class DeletePimProductsOpinionsParamsModel(BaseModel):
    id: StrictInt = Field(..., gt=0, description="ID of the opinion to delete")

class PostPimProductsOpinionsParamsModel(BaseModel):
    opinions: OpinionsPostModel = Field(..., description="List of reviews")

class PutPimProductsOpinionsParamsModel(BaseModel):
    id: StrictInt = Field(..., description="...")
    confirmed: BooleanStrShortEnum = Field(..., description="...")
    rating: StrictInt | None = Field(None, ge=1, le=5, description="...")
    content: str = Field(..., description="...")
    language: str = Field(..., description="Customer language ID")
    shopAnswer: str = Field(..., description="Reply to an opinion")
    picture: str = Field(..., description="...")
    opinionConfirmedByPurchase: bool = Field(..., description="Opinion confirmed with purchase")


# --- ENDPOINTS
class Delete(Gateway):
    """
    The method allows to delete the feedback about the commodity from the panel.
    DOCS_URL: https://idosell.readme.io/reference/productsopinionsopinionsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/opinions/opinions/delete')

    params: DeletePimProductsOpinionsParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    The method allows for downloading information about reviews issued for products available in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsopinionsopinionsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/opinions/opinions')

    opinion: OpinionGetModel | None = Field(None, description="Review identification")
    products: ProductsOpinionsGetModel | None = Field(None, description="Products list")
    clients: ClientsOpinionsModel | None = Field(None, description="Customer data")
    scorePositive: ScorePositiveGetModel | None = Field(None, description="Review positive score data")
    scoreNegative: ScoreNegativeGetModel | None = Field(None, description="Review negative score data")
    dateRange: DateRangeGetModel | None = Field(None, description="Date range")
    ordersBy: List[OrdersByGetModel] | None = Field(None, min_length=1, max_length=5, description="Possibility of sorting returned list") # type: ignore

class Post(AppendableGateway):
    """
    The method allows for adding reviews of products available in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsopinionsopinionspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/opinions/opinions')

    params: PostPimProductsOpinionsParamsModel = Field(..., description="Parameters transmitted to method")

class Put(Gateway):
    """
    The method allows to edit opinions about goods available in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsopinionsopinionsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/opinions/opinions')

    params: PutPimProductsOpinionsParamsModel = Field(..., description="Parameters transmitted to method")

class GetRate(Gateway):
    """
    Evaluation of the usefulness of opinions issued for products.
    DOCS_URL: https://idosell.readme.io/reference/productsopinionsrateget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/opinions/rate')

    id: StrictInt = Field(..., gt=0, description="...")
    operation: RateEnum = Field(..., description="...")
