from enum import StrEnum
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import BooleanStrLongEnum, Gateway, PageableCamelGateway


# --- Payments Enums
class EventSourceTypeEnum(StrEnum):
    ORDER = 'order'
    RETURN = 'return'
    RMA = 'rma'

class PaymentsTypeEnum(StrEnum):
    PAYMENT = 'payment'
    ADVANCE = 'advance'
    REPAYMENT = 'repayment'
    FEE = 'fee'

class SourceTypePaymentsEnum(StrEnum):
    ORDER = 'order'
    RETURN = 'return'


# --- DTOs
class OtherPostModel(BaseModel):
    system: StrictInt = Field(..., ge=1, description="Payment system")
    number: str = Field(..., description="Number")
    month: float = Field(..., description="Month")
    year: StrictInt = Field(..., ge=1, description="Year")
    securityCode: str = Field(..., description="Security code")
    name: str = Field(..., description="Name")

class OtherPutModel(BaseModel):
    system: StrictInt = Field(..., ge=1, description="Payment system")

class ParamsPaymentsPutModel(BaseModel):
    sourceType: EventSourceTypeEnum = Field(..., description="Defines payment category. For the payments regarding returns, enter 'return'")
    paymentNumber: str = Field(..., description="Payment number - [order no.]-[payment no.], i.e. 1234-1")
    accountingDate: str = Field(..., description="Registering date")

class SettingsPaymentsPutModel(BaseModel):
    sendMail: bool = Field(..., description="Indicates if a customer should be informed about allocating the payment by email")
    sendSms: bool = Field(..., description="ndicates if a customer should be informed about allocating the payment by SMS")

class PostCancelOmsPaymentsParamsModel(BaseModel):
    sourceType: EventSourceTypeEnum = Field(..., description="Defines payment category. For the payments regarding returns, enter 'return'")
    paymentNumber: str = Field(..., description="Payment number - [order no.]-[payment no.], i.e. 1234-1")

class PostCashbackOmsPaymentsParamsModel(BaseModel):
    sourceType: SourceTypePaymentsEnum = Field(..., description="Defines payment category. For the payments regarding returns, enter 'return'")
    paymentNumber: str = Field(..., description="Payment number - [order no.]-[payment no.], i.e. 1234-1")
    value: float = Field(..., description="Refund value")

class PostOmsPaymentsParamsModel(BaseModel):
    sourceId: StrictInt = Field(..., description="Source ID")
    sourceType: EventSourceTypeEnum = Field(..., description="Source type")
    value: float = Field(..., description="Payment amount")
    account: str = Field(..., description="Number of a bank account to which a payment is sent")
    type: PaymentsTypeEnum = Field(..., description="...")
    paymentFormId: StrictInt = Field(..., description="Form of payment ID")
    paymentVoucherKey: str = Field(..., description="Gift card or voucher number")
    giftCardPIN: StrictInt = Field(..., ge=1, description="Gift card PIN")
    externalPaymentId: str = Field(..., description="Transaction ID in external service")

class PutOmsPaymentsParamsModel(BaseModel):
    sourceType: EventSourceTypeEnum = Field(..., description="Source type")
    paymentNumber: str = Field(..., description="Payment number - [order no.]-[payment no.], i.e. 1234-1")
    paymentFormId: StrictInt = Field(..., ge=1, description="Payment method ID. Check getPaymentForms")
    value: float = Field(..., description="Payment amount")
    accountingDate: str = Field(..., description="Registering date")
    account: str = Field(..., description="Number of a bank account to which a payment is sent")
    clientAccount: str = Field(..., description="Data of customer account in store")
    other: OtherPutModel = Field(..., description="...")
    externalPaymentId: str = Field(..., description="Transaction ID in external service")

class PostRepaymentOmsPaymentsParamsModel(BaseModel):
    sourceId: StrictInt = Field(..., description="Returns ID")
    source_type: str = Field(..., description="Defines payment category. For the payments regarding returns, enter 'return'")
    value: float = Field(..., description="Refund value")
    payment_form_id: StrictInt = Field(..., description="Payment method ID. Check getPaymentForms")
    account: str = Field(..., description="Number of a bank account to which a payment is sent")
    client_account: str = Field(..., description="Customer account")
    other: OtherPostModel = Field(..., description="...")


# --- ENDPOINTS
class PostCancel(Gateway):
    """
    Method that enables cancelling payments for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentscancelpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/cancel')

    params: PostCancelOmsPaymentsParamsModel = Field(..., description="Parameters transmitted to method")

class PostCashback(Gateway):
    """
    The method allows to send refund requests (so called cashback) for payments managed by external payment systems which have such option available
    DOCS_URL: https://idosell.readme.io/reference/paymentscashbackpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/cashback')

    params: PostCashbackOmsPaymentsParamsModel = Field(..., description="Parameters transmitted to method")

class PutConfirm(Gateway):
    """
    Method that enables accepting payments for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentsconfirmput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/confirm')

    params: ParamsPaymentsPutModel = Field(..., description="Parameters transmitted to method")
    settings: SettingsPaymentsPutModel = Field(..., description="Settings")

class GetForms(Gateway):
    """
    Method that enables getting information about payment methods available in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentsformsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/forms')

    activeOnly: BooleanStrLongEnum | None = Field(None, description="Return only active forms of payment")

class Get(Gateway):
    """
    Method that enables getting information about payments for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentspaymentsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/payments')

    paymentNumber: str = Field(..., min_length=1, description="Payment number consists of: source ID (order / return ID) and the payment ordinal number, e.g. 1234-1")
    sourceType: EventSourceTypeEnum = Field(..., description="Source type")

class Post(Gateway):
    """
    Method that enables adding payments to orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentspaymentspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/payments')

    params: PostOmsPaymentsParamsModel = Field(..., description="Parameters transmitted to method")

class Put(Gateway):
    """
    Method that enables editing payments for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentspaymentsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/payments')

    params: PutOmsPaymentsParamsModel = Field(..., description="Parameters transmitted to method")

class GetProfiles(PageableCamelGateway):
    """
    Allows to download all of the payment profiles defined in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentsprofilesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/profiles')

class PostRepayment(Gateway):
    """
    Method that enables adding withdrawals for orders in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/paymentsrepaymentpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/payments/repayment')

    params: PostRepaymentOmsPaymentsParamsModel = Field(..., description="Parameters transmitted to method")
