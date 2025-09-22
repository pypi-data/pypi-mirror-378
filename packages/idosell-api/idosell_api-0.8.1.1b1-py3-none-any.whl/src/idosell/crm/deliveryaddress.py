from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway


# --- DTOs
class ClientsPostPutModel(BaseModel):
    clientLogin: str = Field(..., description="Customer's login")
    clientCodeExternal: str = Field(..., description="External system code")
    shopsIds: List[StrictInt] = Field(..., description="List of stores IDs When mask is determined, this parameter is omitted")
    currencyId: str = Field(..., description="Currency ID")
    clientDeliveryAddressFirstName: str = Field(..., description="Recipient's first name")
    clientDeliveryAddressLastName: str = Field(..., description="Recipient's last name")
    clientDeliveryAddressAdditional: str = Field(..., description="Additional information")
    clientDeliveryAddressPhone1: str = Field(..., description="Cell phone")
    clientDeliveryAddressCity: str = Field(..., description="Recipient's city")
    clientDeliveryAddressStreet: str = Field(..., description="Recipient street and number")
    clientDeliveryAddressRegionId: str = Field(..., description="Administrative region code")
    clientDeliveryAddressProvinceId: str = Field(..., description="Administrative region code")
    clientDeliveryAddressZipCode: str = Field(..., description="Recipient's postal code")
    clientDeliveryAddressCountry: str = Field(..., description="Recipient's country")

class ClientsDeliveryAddressPostModel(ClientsPostPutModel):
    pass

class ClientsDeliveryAddressPutModel(ClientsPostPutModel):
    clientDeliveryAddressId: str = Field(..., description="Delivery address ID")

class ClientSettingsDeliveryAddressModel(BaseModel):
    clientSettingSendMail: bool = Field(..., description="Inform the customer about the introduced changes via an e-mail")
    clientSettingSendSms: bool = Field(..., description="Inform the customer about the introduced changes via a text message")

class ClientDeliveryAddressModel(BaseModel):
    clientLogin: str = Field(..., description="Customer's login")
    clientCodeExternal: str = Field(..., description="External system code")
    clientDeliveryAddressId: StrictInt = Field(..., ge=1, description="Delivery address ID")

class DeleteCrmDeliveryaddressParamsModel(BaseModel):
    clients: ClientDeliveryAddressModel = Field(..., description="Customer data")

class PostCrmDeliveryaddressParamsModel(BaseModel):
    clients: List[ClientsDeliveryAddressPostModel] = Field(..., description="Customer data")
    clientsSettings: ClientSettingsDeliveryAddressModel = Field(..., description="Settings")

class PutCrmDeliveryaddressParamsModel(BaseModel):
    clients: List[ClientsDeliveryAddressPutModel] = Field(..., description="Customer data")
    clientsSettings: ClientSettingsDeliveryAddressModel = Field(..., description="Settings")


# --- ENDPOINTS
class Delete(AppendableGateway):
    """
    The method allows you to delete unused delivery addresses for customer accounts in the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientsdeliveryaddressdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/deliveryAddress/delete')

    params: DeleteCrmDeliveryaddressParamsModel = Field(..., description="Parameters transmitted to method")

class Get(Gateway):
    """
    Method that enables extracting information about delivery addresses assigned to existing customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsdeliveryaddressget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/deliveryAddress')

    clientCodesExternal: Optional[List[str]] = Field(default=None, min_length=1, description="External system codes list") # type: ignore
    clientIds: Optional[List[int]] = Field(default=None, min_length=1, description="Customer ID (each >= 1)") # type: ignore
    clientLogins: Optional[List[str]] = Field(default=None, min_length=1, description="Customer's login") # type: ignore

class Post(AppendableGateway):
    """
    Method that enables adding delivery address details to existing customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsdeliveryaddresspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/deliveryAddress')

    params: PostCrmDeliveryaddressParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Method that enables editing the delivery address details for existing customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsdeliveryaddressput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/deliveryAddress')

    params: PutCrmDeliveryaddressParamsModel = Field(..., description="Parameters transmitted to method")
