from enum import IntEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway


# --- Enums
class FaultCodeEnum(IntEnum):
    OPERATION_WAS_SUCCESSFUL = 0
    LOGIN_FAILURE_INVALID_USERNAME_OR_KEY = 1
    EMPTY_RESULT = 2
    NO_PARAMETERS_WERE_RECEIVED = 3
    SHOP_HAS_BEEN_BLOCKED_DUE_TO_NUMBER_OF_OVERDUE_INVOICES_OWED_TO_IAI_COMPANY = 4


# --- DTOs
class ErrorModel(BaseModel):
    faultCode: FaultCodeEnum = Field(..., description="Error code")
    faultString: str = Field(..., description="Error description")

class MembershipCardsModel(BaseModel):
    ordinal_number: StrictInt = Field(..., ge=1, description="Card ID entered by customer")
    card_type: StrictInt = Field(..., ge=1, description="Card ID")
    number: str = Field(..., description="Loyalty card number")
    pin: StrictInt = Field(..., ge=1, description="Card PIN")
    creation_date: str = Field(..., description="Issue date")
    deactivate: bool = Field(..., description="Determines whether a card should be deactivated")
    set_rebate_group: bool = Field(..., description="Flag that determines whether a discount group should be set")
    errors: ErrorModel = Field(..., description="Error code")

class SettingsModel(BaseModel):
    sendMail: bool = Field(..., description="Inform the customer about the introduced changes via an e-mail")
    sendSms: bool = Field(..., description="Inform the customer about the introduced changes via a text message")

class PutCardsCrmMembershipParamsModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Customer ID")
    login: str = Field(..., min_length=1, description="Customer's login (non-empty)")
    membership_cards: List[MembershipCardsModel] = Field(..., min_length=1, description="Membership cards to assign")  # type: ignore
    settings: SettingsModel = Field(..., description="Settings")


# --- ENDPOINTS
class GetCards(Gateway):
    """
    Method that enables extracting information about loyalty cards available in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientsmembershipcardsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/membershipCards')

    id: Optional[StrictInt] = Field(default=None, ge=1, description="Customer ID (>=1)")
    login: Optional[str] = Field(default=None, min_length=1, description="Customer's login (non-empty)")

class PutCards(AppendableGateway):
    """
    Method that enables assigning loyalty cards to customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsmembershipcardsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/membershipCards')

    params: PutCardsCrmMembershipParamsModel = Field(..., description="Parameters transmitted to method")
