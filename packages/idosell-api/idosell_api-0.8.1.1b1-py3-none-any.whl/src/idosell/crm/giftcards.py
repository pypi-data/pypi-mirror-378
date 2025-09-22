from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway, PageableCamelModel
from src.idosell.crm._common import BalanceModel, BalanceOperationTypeEnum


# --- DTOs
class GiftCardDeleteModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Card ID")
    number: str = Field(..., description="Card number")

class GiftCardModel(BaseModel):
    id: StrictInt | None = Field(None, ge=1, description="Card ID")
    number: str | None = Field(None, description="Card number")
    pin: str | None = Field(None, description="Card PIN")

class GiftCardPostPutModel(BaseModel):
    number: str = Field(..., description="Card number")
    pin: str = Field(..., description="Card PIN")
    name: str = Field(..., description="Name of card")
    expirationDate: str = Field(..., description="Card expiration date")
    balanceOperationType: BalanceOperationTypeEnum = Field(..., description="Balance operation type")
    balance: BalanceModel = Field(..., description="Card balance")
    shops: List[int] = Field(..., description="List of shops the card is active in")
    note: str = Field(..., description="...")

class GiftCardPostModel(GiftCardPostPutModel):
    typeId: StrictInt = Field(..., ge=1, description="Gift card type id")

class GiftCardPutModel(GiftCardPostPutModel):
    id: StrictInt = Field(..., ge=1, description="Card ID")

class SearchGiftCardModel(PageableCamelModel):
    giftCardTypeId: StrictInt | None = Field(None, ge=1, description="Gift cards type ID")
    name: str | None = Field(None, description="Name")
    noteContain: str | None = Field(None, description="Notes contain")
    balanceFrom: float | None = Field(None, description="Value from")
    balanceTo: float | None = Field(None, description="Value to")
    expirationDateFrom: str | None = Field(None, description="Expiration date from")
    expirationDateTo: str | None = Field(None, description="Expiration date to")
    issueDateFrom: str | None = Field(None, description="Created from")
    issueDateTo: str | None = Field(None, description="Created to")

class PutBlockCrmGiftcardsParamsModel(BaseModel):
    giftCards: List[GiftCardModel] = Field(..., min_length=1, description="List of gift cards") # type: ignore

class DeleteCrmGiftcardsParamsModel(BaseModel):
    giftCards: List[GiftCardDeleteModel] = Field(..., min_length=1, description="List of gift cards") # type: ignore

class PostCrmGiftcardsParamsModel(BaseModel):
    giftCards: List[GiftCardPostModel] = Field(..., min_length=1, description="List of cards to add") # type: ignore

class PutCrmGiftcardsParamsModel(BaseModel):
    giftCards: List[GiftCardPutModel] = Field(..., min_length=1, description="List of cards to edit") # type: ignore

class SearchCrmGiftcardsParamsModel(BaseModel):
    # search body: either giftCards (list) or searchGiftCards (filter) — require at least one
    giftCards: List[GiftCardModel] | None = Field(default=None, min_length=1, description="List of gift cards")  # type: ignore
    searchGiftCards: SearchGiftCardModel | None = Field(default=None, description="element is an element array of type searchGiftCards")

class PutUnblockCrmGiftcardsParamsModel(BaseModel):
    giftCards: List[GiftCardModel] = Field(..., min_length=1, description="List of gift cards") # type: ignore


# --- ENDPOINTS
class PutBlock(AppendableGateway):
    """
    Enables gift card blocking
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardsblockput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards/block')

    params: PutBlockCrmGiftcardsParamsModel = Field(..., description="Parameters transmitted to method")

class Delete(AppendableGateway):
    """
    Enables deleting a single or a list of gift cards
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards/delete')

    params: DeleteCrmGiftcardsParamsModel = Field(..., description="Parameters transmitted to method")

class Post(AppendableGateway):
    """
    Enables adding new gift cards with the selected card type
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards')

    params: PostCrmGiftcardsParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Enables editing gift parameters, e.g. changing its balance, validity date, number or PIN
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards')

    params: PutCrmGiftcardsParamsModel = Field(..., description="Parameters transmitted to method")

class Search(Gateway):
    """
    Enables searching for gift cards and retrieving information about indicated gift cards
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardssearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards/search')

    params: SearchCrmGiftcardsParamsModel = Field(..., description="Parameters transmitted to method")

class GetTypes(PageableCamelGateway):
    """
    Allows for downloading all types of gift cards defined in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardstypesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards/types')

class PutUnblock(AppendableGateway):
    """
    Enables gift card unblocking
    DOCS_URL: https://idosell.readme.io/reference/clientsgiftcardsunblockput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/giftcards/unblock')

    params: PutUnblockCrmGiftcardsParamsModel = Field(..., description="Parameters transmitted to method")
