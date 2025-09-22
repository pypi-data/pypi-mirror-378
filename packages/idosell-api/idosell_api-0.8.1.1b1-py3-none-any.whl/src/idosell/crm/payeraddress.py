from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, PageableCamelGateway, PayerAddressBaseModel


# DTOs
class PayerModel(BaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")
    payerAddressId: StrictInt = Field(..., ge=1, description="Buyer's address id")

class PostPayersModel(PayerAddressBaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")

class PutPayersModel(PayerAddressBaseModel):
    clientId: str = Field(..., description="Unique client's number")
    payerAddressId: str = Field(..., description="Buyer's address id")

class DeleteParamsPayersAddressModel(BaseModel):
    payers: List[PayerModel] = Field(..., description="List of payer addresses to delete")

class PostParamsPayersAddressModel(BaseModel):
    payers: List[PostPayersModel] = Field(..., description="...")

class PutParamsPayersAddressModel(BaseModel):
    payers: List[PutPayersModel] = Field(..., description="...")


# --- ENDPOINTS
class Delete(AppendableGateway):
    """
    The method allows you to delete unused buyer addresses for customer accounts in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientspayeraddressdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/payerAddress/delete')

    params: DeleteParamsPayersAddressModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    The method allows to retrieve buyer's addresses from sales documents, for existing customer accounts in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientspayeraddressget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/payerAddress')

    clientId: Optional[str] = Field(default=None, min_length=1, description="Unique client's number")

class Post(AppendableGateway):
    """
    The method allows to add buyer's addresses to sales documents, for existing customer accounts in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientspayeraddresspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/payerAddress')

    params: PostParamsPayersAddressModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    The method allows to modify buyer's addresses in sales documents, for existing customer accounts in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientspayeraddressput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/payerAddress')

    params: PutParamsPayersAddressModel = Field(..., description="Parameters transmitted to method")
