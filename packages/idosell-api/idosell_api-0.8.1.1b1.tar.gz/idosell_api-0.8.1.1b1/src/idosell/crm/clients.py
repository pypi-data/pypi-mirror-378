from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrLongEnum, BooleanStrShortEnum, Gateway, PageableCamelGateway
from src.idosell.crm._common import ClientRegistrationDateModel, ClientTypeEnum, TradeCreditEnum


# --- Enums
class BalanceOperationClientsEnum(StrEnum):
    ADD = 'add'
    REMOVE = 'remove'

class OperationClientsEnum(StrEnum):
    ADD = 'add'
    REMOVE = 'remove'

class ReturnElementsClientsEnum(StrEnum):
    CLIENTID = 'clientId'
    CLIENTSLASTMODIFICATIONDATE = 'clientsLastModificationDate'
    CLIENTLOGIN = 'clientLogin'
    CLIENTEMAIL = 'clientEmail'
    CLIENTTYPE = 'clientType'
    SHOWCLIENTASPARTNER = 'showClientAsPartner'
    BLOCKAUTOMATICALLYASSIGNINGGROUPDISCOUNT = 'blockAutomaticallyAssigningGroupDiscount'
    CLIENTFIRSTNAME = 'clientFirstName'
    CLIENTLASTNAME = 'clientLastName'
    CLIENTBIRTHDATE = 'clientBirthDate'
    CLIENTFIRM = 'clientFirm'
    CLIENTNIP = 'clientNip'
    CLIENTSTREET = 'clientStreet'
    CLIENTZIPCODE = 'clientZipCode'
    CLIENTCITY = 'clientCity'
    CLIENTCOUNTRYID = 'clientCountryId'
    LANGID = 'langId'
    CURRENCYID = 'currencyId'
    CLIENTREGIONID = 'clientRegionId'
    CLIENTISWHOLESALER = 'clientIsWholesaler'
    CLIENTVATPREFERENCES = 'clientVatPreferences'
    CLIENTGROUPDISCOUNTNUMBER = 'clientGroupDiscountNumber'
    CLIENTGROUPDISCOUNTNAME = 'clientGroupDiscountName'
    CLIENTCODEEXTERNAL = 'clientCodeExternal'
    CLIENTPHONE1 = 'clientPhone1'
    CLIENTPHONE2 = 'clientPhone2'
    CLIENTPROVINCEID = 'clientProvinceId'
    NEWSLETTEREMAILAPPROVALSDATA = 'newsletterEmailApprovalsData'
    SHOPS = 'shops'
    CLIENTBALANCES = 'clientBalances'
    CLIENTTRADECREDIT = 'clientTradeCredit'
    CLIENTLOYALTYPOINTS = 'clientLoyaltyPoints'
    OPERATOR = 'operator'
    ISUNREGISTERED = 'isUnregistered'
    AFFILIATELOGIN = 'affiliateLogin'
    AFFILIATEID = 'affiliateId'
    CLIENTREGISTRATIONDATE = 'clientRegistrationDate'
    CLIENTACTIVEINSHOPS = 'clientActiveInShops'


# --- DTOs
class ClientLastPurchaseDateModel(BaseModel):
    clientLastPurchaseDateBegin: str = Field(..., description="Start date (YYYY-MM-DD)")
    clientLastPurchaseDateEnd: str = Field(..., description="End date (YYYY-MM-DD)")

class ClientLastModificationDateModel(BaseModel):
    clientsLastModificationDateBegin: str = Field(..., description="Start date. You can enter both the date in the format YYYY-MM-DD and the date with the time YYYY-MM-DD h:m:s")
    clientsLastModificationDateEnd: str = Field(..., description="End date. You can enter both the date in the format YYYY-MM-DD and the date with the time YYYY-MM-DD h:m:s")

class DeliveryDateModel(BaseModel):
    deliveryDate: str = Field(..., description="Delivery date in format: Y-m-d")
    deliveryHours: List[str] = Field(..., description="Delivery time in format: H:i")

class LastPurchaseDateModel(BaseModel):
    from_: str = Field(..., description="Start date (YYYY-MM-DD)", alias="from")
    to: str = Field(..., description="End date (YYYY-MM-DD)")

class NewsletterEmailApprovalModel(BaseModel):
    approval: BooleanStrShortEnum = Field(..., description="Have customer agreed to a newsletter")
    shop_id: StrictInt = Field(..., ge=1, description="Store ID")

class NewsletterSmsApprovalModel(BaseModel):
    approval: BooleanStrShortEnum = Field(..., description="Have customer agreed to a newsletter")
    shop_id: StrictInt = Field(..., ge=1, description="Store ID")

class PostCrmClientsClientsModel(BaseModel):
    login: str = Field(..., description="Customer's login")
    code_extern: str = Field(..., description="External system code")
    email: str = Field(..., description="Customer e-mail address")
    firstname: str = Field(..., description="Customer's first name")
    lastname: str = Field(..., description="Customer's last name")
    street: str = Field(..., description="Address")
    zipcode: str = Field(..., description="Customer's postal code")
    city: str = Field(..., description="Customer's city")
    country_code: str = Field(..., description="Customer country (ISO-3166-1 alpha-2 standard (2 letters))")
    province_code: str = Field(..., description="Administrative region code")
    password: str = Field(..., description="Customer password (min. 8 characters)")
    birth_date: str = Field(..., description="Date of birth")
    phone: str = Field(..., description="Customer phone number")
    company: str = Field(..., description="...")
    vat_number: str = Field(..., description="Customer Tax no")
    wholesaler: bool = Field(False, description="Determines, whether client is a wholesaler")
    client_type: ClientTypeEnum = Field(..., description="Customer type")
    language: str = Field(..., description="Customer language ID")
    shops: List[int] = Field(..., description="Determines, in which store account should be active")
    block_autosigning_to_shops: bool = Field(..., description="Defines availability of log in to other pages than the ones given in the element: shops ")
    currency: str = Field(..., description="Customer default currency (ISO-4217 (3 letters))")
    delivery_dates: List[str] = Field(..., description="...")
    external_balance_value: float = Field(..., description="Customer account balance in external system")
    external_trade_credit_limit_value: float = Field(..., description="Debt limit")
    email_newsletter: BooleanStrShortEnum = Field(..., description="Have customer agreed to a newsletter. List of allowed parameters: 'y' - yes, 'n' - no. The value will be set in all shops in which the customer account is active")
    sms_newsletter: BooleanStrShortEnum = Field(..., description="Have customer agreed to a newsletter. List of allowed parameters: 'y' - yes, 'n' - no. The value will be set in all shops in which the customer account is active")
    client_group: StrictInt = Field(..., ge=1, description="Discount group ID")
    request_reference: str = Field(..., description="Field used for identifying request-response pairs for the endpoint")
    newsletter_email_approvals: List[NewsletterEmailApprovalModel] = Field(..., description="List of shops where a customer agreed or didn't agree to receive email newsletter")
    newsletter_sms_approvals: List[NewsletterSmsApprovalModel] = Field(..., description="List of shops where a customer agreed or didn't agree to receive sms newsletter")
    block_group_auto_assignment: bool = Field(..., description="Block assigning of discount groups automatically based on order history")

class PutCrmClientsClientsModel(BaseModel):
    clientLogin: str = Field(..., description="Customer's login")
    clientEmail: str = Field(..., description="Customer e-mail address")
    clientFirstName: str = Field(..., description="Customer's first name")
    clientLastName: str = Field(..., description="Customer's last name")
    clientStreet: str = Field(..., description="Address")
    clientZipCode: str = Field(..., description="Customer's postal code")
    clientCity: str = Field(..., description="Customer's city")
    clientCountryId: str = Field(..., description="Country ID in accordance with ISO-3166")
    clientProvinceId: str = Field(..., description="Administrative region code")
    clientPassword: str = Field(..., description="Customer password (min. 8 characters)")
    clientBirthDate: str = Field(..., description="Date of birth")
    clientPhone1: str = Field(..., description="Customer phone number")
    clientFirm: str = Field(..., description="...")
    clientNip: str = Field(..., description="Customer Tax no")
    clientIsWholesaler: bool = Field(False, description="Determines, whether client is a wholesaler")
    clientType: ClientTypeEnum = Field(..., description="Customer type")
    langId: str = Field(..., description="Customer language ID")
    blockLoginToOtherShops: bool = Field(..., description="Defines availability of log in to other pages than the ones given in the element: shops ")
    shopsIds: List[int] = Field(..., description="Determines, in which store account should be active")
    currencyId: str = Field(..., description="Currency ID")
    clientCodeExternal: str = Field(..., description="External system code")
    deliveryDates: List[DeliveryDateModel] = Field(..., description="List with delivery dates and times")
    clientBalanceAmountExternal: float = Field(..., description="Customer account balance in external system")
    clientTradeCreditLimitExternal: float = Field(..., description="Debt limit")
    newsletterEmailApproval: bool = Field(..., description="Permission to E-mail Newsletter")
    newsletterSmsApproval: bool = Field(..., description="Permission to SMS Newsletter")
    clientGroupDiscountNumber: StrictInt = Field(..., ge=1, description="Discount group ID")
    requestReference: str = Field(..., description="Field used for identifying request-response pairs for the endpoint")
    newsletterEmailApprovalsData: List[NewsletterEmailApprovalModel] = Field(..., description="List of shops where a customer agreed or didn't agree to receive email newsletter")
    newsletterSmsApprovalsData: List[NewsletterSmsApprovalModel] = Field(..., description="List of shops where a customer agreed or didn't agree to receive sms newsletter")
    clientActive: bool = Field(..., description="Is the customer active")
    numberOfDaysToPay: StrictInt = Field(..., ge=1, description="Number of days to pay for invoice")
    affiliateLogin: str = Field(..., description="ID of a partner who acquired a given customer")
    clientNote: str = Field(..., description="Notes from customer")

class PostBalanceCrmClientsParamsModel(BaseModel):
    clientId: StrictInt = Field(..., ge=1, description="Unique client's number")
    operation: OperationClientsEnum = Field(..., description="Operation")
    balance: float = Field(..., description="Value to add or remove from balance")
    currency: str = Field(..., description="Currency of operation")
    note: str = Field(..., description="Note")
    prepaidId: StrictInt = Field(..., ge=1, description="Order payment identifier")

class PostCrmClientsParamsModel(BaseModel):
    clients: List[PostCrmClientsClientsModel] = Field(..., description="Customer data")

class PutCrmClientsParamsModel(BaseModel):
    clients: List[PutCrmClientsClientsModel] = Field(..., description="Customer data")

class SettingsPostModel(BaseModel):
    send_mail: bool = Field(False, description="Inform the customer with an email about the newly created account")
    send_sms: bool = Field(False, description="Inform the customer with a text message about the newly created account")

class SettingsPostPutModel(BaseModel):
    clientSettingSendMail: bool = Field(False, description="Inform the customer about the introduced changes via an e-mail")
    clientSettingSendSms: bool = Field(False, description="Inform the customer about the introduced changes via a text message")


# --- ENDPOINTS
class GetBalance(PageableCamelGateway):
    """
    Method that enables extracting customer balance information from existing customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsbalanceget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/balance')

    clientNumbers: Optional[List[int]] = Field(default=None, min_length=1, description="Customer Id (list, each >=1)") # type: ignore
    textSearch: Optional[str] = Field(default=None, min_length=1, description="Text search through customer data")
    active: Optional[BooleanStrLongEnum] = Field(default=None, description="Active (yes/no)")
    hasTradeCredit: Optional[TradeCreditEnum] = Field(default=None, description="Trade credit")
    lastPurchaseDate: Optional[LastPurchaseDateModel] = Field(default=None, description="Start and end date (YYYY-MM-DD)")
    returnElements: Optional[List[str]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned. Allowed: clientId, clientBalance, clientBalanceHistory") # type: ignore

class PostBalance(Gateway):
    """
    Method that allows for customer account balance operations
    DOCS_URL: https://idosell.readme.io/reference/clientsbalancepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/balance')

    params: PostBalanceCrmClientsParamsModel = Field(..., description="Parameters transmitted to method")
    settings: SettingsPostPutModel = Field(..., description="Settings")

class Get(PageableCamelGateway):
    """
    Method that enables extracting customer account details
    DOCS_URL: https://idosell.readme.io/reference/clientsclientsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/clients')

    clientsIds: Optional[List[int]] = Field(default=None, min_length=1, description="Customer numbers (each >=1)") # type: ignore
    clientCodesExternal: Optional[List[str]] = Field(default=None, min_length=1, description="External system codes list (non-empty strings)") # type: ignore
    clientTextSearch: Optional[str] = Field(default=None, min_length=1, description="Text search through customer data")
    clientIsActive: Optional[BooleanStrLongEnum] = Field(default=None, description="Active (yes/no)")
    clientHasTradeCredit: Optional[TradeCreditEnum] = Field(default=None, description="Trade credit")
    clientLastPurchaseDate: Optional[ClientLastPurchaseDateModel] = Field(default=None, description="Date of last purchase")
    clientsLastModificationDate: Optional[ClientLastModificationDateModel] = Field(default=None, description="Last modification date")
    returnElements: Optional[List[str]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned") # type: ignore
    clientRegistrationDate: Optional[ClientRegistrationDateModel] = Field(default=None, description="Client Registration Date")
    shopId: Optional[str] = Field(default=None, min_length=1, description="The ID of the shop, that client is assigned to")

class Post(AppendableGateway):
    """
    Method that enables adding new customer accounts to the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientsclientspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/clients')

    params: PostCrmClientsParamsModel = Field(..., description="Parameters transmitted to method")
    settings: SettingsPostModel = Field(..., description="Settings")

class Put(AppendableGateway):
    """
    Method enables modifying existing customer account data
    DOCS_URL: https://idosell.readme.io/reference/clientsclientsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/clients')

    params: PutCrmClientsParamsModel = Field(..., description="Parameters transmitted to method")
    clientsSettings: SettingsPostPutModel = Field(..., description="Settings")
