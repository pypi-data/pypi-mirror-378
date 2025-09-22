from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import BooleanStrLongEnum, BooleanStrShortEnum, PageableCamelGateway
from src.idosell.cms._common import ClientTypeEnum
from src.idosell.crm._common import ClientRegistrationDateModel


# --- Enums
class ClientAffiliateProgramEnum(StrEnum):
    YES_VOUCHER = 'yes_voucher' # when customers are in a loyalty program and have only used vouchers,
    YES_VOUCHER_CASH = 'yes_voucher_cash' # when customers are in a loyalty program and have only used vouchers or cash deposits,
    YES_CLIENTS = 'yes_clients'
    YES_ORDERS = 'yes_orders' # when customers are in the loyalty program and have made at least one order,
    NO = 'no' # when customers are in the loyalty program,
    BANNED = 'banned' # when customers are blocked.

class ClientHasLoyaltyCardEnum(StrEnum):
    YES_ACTIVE = 'yes_active'
    YES_NOT_ACTIVE = 'yes_not_active'
    NO = 'no'

class SearchByShopEnum(StrEnum):
    ONE_OF_SELECTED = 'one_of_selected' # searches for customers assigned to at least one shop present in shopsList.
    EXACTLY_SELECTED = 'exactly_selected' # searches for customers assigned to all shops present in shopsList.


# --- DTOs
class ClientLastLoginDateModel(BaseModel):
    clientLastLoginDateBegin: str = Field(..., description="Start date (YYYY-MM-DD)")
    clientLastLoginDateEnd: str = Field(..., description="End date (YYYY-MM-DD)")

class ClientLoyaltyCardModel(BaseModel):
    clientHasLoyaltyCard: ClientHasLoyaltyCardEnum = Field(..., description="Does the customer have a loyalty card")
    clientLoyaltyCardId: StrictInt | None = Field(None, ge=1, description="Customer loyalty card ID, omitted when has_loyalty_card = no")
    clientLoyaltyCardNumber: str | None = Field(None, description="Customer loyalty card number, omitted when has_loyalty_card = no")

class NewsletterEmailApprovalsDataModel(BaseModel):
    inNewsletterEmailApproval: BooleanStrShortEnum = Field(..., description="Permission to E-mail Newsletter")
    shopId: StrictInt = Field(..., description="Shop Id")

class NewsletterSmsApprovalsDataModel(BaseModel):
    inNewsletterSmsApproval: BooleanStrShortEnum = Field(..., description="Permission to E-mail Newsletter")
    shopId: StrictInt = Field(..., description="Shop Id")

class OrderSerialNumberRangeModel(BaseModel):
    ordersSerialNumberBegin: str = Field(..., description="Starting number of serial numbers range for sought products")
    ordersSerialNumberEnd: str = Field(..., description="Ending number for serial number range")

class OrderAddDateModel(BaseModel):
    ordersAddDateBegin: str = Field(..., description="Start date (YYYY-MM-DD)")
    ordersAddDateEnd: str = Field(..., description="End date (YYYY-MM-DD)")

class OrderModel(BaseModel):
    clientHasOrders: BooleanStrLongEnum = Field(..., description="Has the customer made an order")
    ordersMinimalValue: float | None = Field(None, description="Minimum order value, omitted when hasOrders = no")
    ordersSerialNumberRange: OrderSerialNumberRangeModel | None = Field(None, description="Data for serial number range")
    ordersAddDate: OrderAddDateModel | None = Field(None, description="Date range of orders made by customers, omitted when hasOrders = no")

class PostParamsSearchModel(BaseModel):
    clientLogin: str | None = Field(None, description="Customer's login")
    clientIsWholesaler: BooleanStrLongEnum | None = Field(None, description="Determines, whether client is a wholesaler")
    clientCountryId: str | None = Field(None, description="Country ID in accordance with ISO-3166")
    langId: str | None = Field(None, description="Language ID")
    clientCustomerServiceRepresentativeLogin: str | None = Field(None, description="Customer service representative")
    clientDiscountGroupNumber: StrictInt | None = Field(None, description="Customer group number")
    clientRegistrationDate: ClientRegistrationDateModel | None = Field(None, description="Date range of customer registrations")
    clientLastLoginDate: ClientLastLoginDateModel | None = Field(None, description="Date of last customer login (YYYY-MM-DD)")
    clientType: ClientTypeEnum | None = Field(None, description="Customer type")
    clientAffiliateProgram: List[ClientAffiliateProgramEnum] | None = Field(None, description="Information about the loyalty program")
    newsletterEmailApproval: str | None = Field(None, description="Permission to E-mail Newsletter")
    newsletterSmsApproval: str | None = Field(None, description="Permission to SMS Newsletter")
    searchByShops: SearchByShopEnum | None = Field(None, description="Shops")
    clientLoyaltyCard: ClientLoyaltyCardModel | None = Field(None, description="Loyalty cards")
    clientCodeExternal: str | None = Field(None, description="External system code")
    clientCodesExternal: List[str] | None = Field(None, description="External system codes list")
    clientFirstName: str | None = Field(None, description="Customer's first name")
    clientLastName: str | None = Field(None, description="Customer's last name")
    clientNip: str | None = Field(None, description="Customer Tax no")
    clientFirm: str | None = Field(None, description="Customer's company name")
    clientEmail: str | None = Field(None, description="E-mail address")
    newsletterEmailApprovalsData: List[NewsletterEmailApprovalsDataModel] | None = Field(None, description="List of shops where a customer agreed or didn't agree to receive email newsletter")
    newsletterSmsApprovalsData: List[NewsletterSmsApprovalsDataModel] | None = Field(None, description="List of shops where a customer agreed or didn't agree to receive sms newsletter")
    clientLoyaltyCardNumber: str | None = Field(None, description="Customer loyalty card number, omitted when has_loyalty_card = no")
    orders: OrderModel | None = Field(None, description="Orders")
    returnElements: List[str] | None = Field(None, description="Elements to be returned by the endpoint. By default all elements are returned")
    settingsExactSearch: bool | None = Field(None, description="Determines, if data - that will be returned - will be exactly as entered values, or values should be fragment of customer data")


# --- ENDPOINTS
class Search(PageableCamelGateway):
    """
    The method allows to download information about customers from the CRM module assigned to stores to which the user has rights
    DOCS_URL: https://idosell.readme.io/reference/clientscrmsearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/crm/search')

    params: PostParamsSearchModel | None = Field(None, description="...")
