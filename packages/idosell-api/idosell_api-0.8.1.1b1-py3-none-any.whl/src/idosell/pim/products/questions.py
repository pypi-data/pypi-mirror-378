from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.pim.products._common import QuestionsPutModel


# --- DTOs
class PutPimProductsQuestionsParamsModel(BaseModel):
    questions: List[QuestionsPutModel] = Field(..., description="Question Board")


# --- ENDPOINTS
class Get(Gateway):
    """
    The method allows you to download a list of questions to products available in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsquestionsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/questions')

    id: StrictInt | None = Field(None, ge=1, description="Question ID")
    productId: StrictInt | None = Field(None, ge=1, description="Product IAI code")

class Put(AppendableGateway):
    """
    The method allows you to add and edit questions to products available in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsquestionsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/questions')

    params: PutPimProductsQuestionsParamsModel = Field(..., description="Parameters transmitted to method")
