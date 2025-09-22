from enum import StrEnum
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway, PageableCamelGateway


# --- Enums
class SourceTypeAllEnum(StrEnum):
    ORDER = 'order'
    RETURN = 'return'
    RMA = 'rma'
    ALL = 'all'

class RefundsSourceTypeEnum(StrEnum):
    RETURN = 'return'
    RMA = 'rma'

class SourceTypeWithOrderEnum(StrEnum):
    ORDER = 'order'
    RETURN = 'return'
    RMA = 'rma'


# --- DTOs
class RefundDetailsPostModel(BaseModel):
    paymentFormId: StrictInt = Field(..., ge=1, description="Payment method ID")
    paymentSystem: StrictInt = Field(..., ge=1, description="Payment system ID")
    account: str = Field(..., description="Account number")
    clientAccount: str = Field(..., description="Client account number")

class PostAddAutomaticOmsRefundsParamsModel(BaseModel):
    sourceType: RefundsSourceTypeEnum = Field(..., description="...")
    sourceId: StrictInt = Field(..., ge=1, description="Source ID")

class PostAddAutomaticForOrderOmsRefundsParamsModel(BaseModel):
    sourceId: StrictInt = Field(..., ge=1, description="Source ID")
    refundValue: float = Field(..., description="Amount")
    paymentId: StrictInt = Field(..., ge=1, description="Payment ID")
    refundCurrency: str = Field(..., description="Payment currency")

class PostAddManualOmsRefundsParamsModel(BaseModel):
    sourceType: SourceTypeWithOrderEnum = Field(..., description="")
    sourceId: int | str = Field(..., ge=1, description="Source ID")
    refundValue: float = Field(..., description="Amount")
    refundCurrency: str = Field(..., description="Payment currency")
    refundDetails: RefundDetailsPostModel = Field(..., description="")

class PutCancelRefundOmsRefundsParamsModel(BaseModel):
    sourceType: SourceTypeWithOrderEnum = Field(..., description="...")
    sourceId: StrictInt = Field(..., ge=1, description="Source ID")
    paymentId: str = Field(..., description="Payment ID")

class PutConfirmOmsRefundsParamsModel(BaseModel):
    sourceType: SourceTypeWithOrderEnum = Field(..., description="...")
    sourceId: StrictInt = Field(..., ge=1, description="Source ID")
    paymentId: str = Field(..., description="Payment ID")

class PutOmsRefundsParamsModel(BaseModel):
    sourceType: SourceTypeWithOrderEnum = Field(..., description="...")
    sourceId: StrictInt = Field(..., ge=1, description="Source ID")
    paymentId: str = Field(..., description="Payment ID")
    refundValue: float = Field(..., description="Amount")
    refundCurrency: str = Field(..., description="Payment currency")


# --- ENDPOINTS
class PostAddAutomatic(Gateway):
    """
    Method allows you to add automatic refund of payments for returns and rma
    DOCS_URL: https://idosell.readme.io/reference/refundsaddautomaticrefund-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/addAutomaticRefund')

    params: PostAddAutomaticOmsRefundsParamsModel = Field(..., description="Parameters transmitted to method")

class PostAddAutomaticForOrder(Gateway):
    """
    Method allows you to add automatic refund for order
    DOCS_URL: https://idosell.readme.io/reference/refundsaddautomaticrefundfororder-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/addAutomaticRefundForOrder')

    params: PostAddAutomaticForOrderOmsRefundsParamsModel = Field(..., description="Parameters transmitted to method")

class PostAddManual(Gateway):
    """
    Method allows you to add manual refund for return and rma
    DOCS_URL: https://idosell.readme.io/reference/refundsaddmanualrefund-1
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/addManualRefund')

    params: PostAddManualOmsRefundsParamsModel = Field(..., description="Parameters transmitted to method")

class PutCancelRefund(Gateway):
    """
    Method allows you to cancel refund
    DOCS_URL: https://idosell.readme.io/reference/refundscancelrefund-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/cancelRefund')

    params: PutCancelRefundOmsRefundsParamsModel = Field(..., description="Parameters transmitted to method")

class PutConfirm(Gateway):
    """
    Method allows you to confirm refund
    DOCS_URL: https://idosell.readme.io/reference/refundsconfirmrefund-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/confirmRefund')

    params: PutConfirmOmsRefundsParamsModel = Field(..., description="Parameters transmitted to method")

class GetPossibleAuto(Gateway):
    """
    Method returns Automatic refunds possible
    DOCS_URL: https://idosell.readme.io/reference/refundsgetpossibleautorefunds-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/getPossibleAutoRefunds')

    sourceId: StrictInt = Field(..., ge=1, description="Source ID")
    sourceType: SourceTypeWithOrderEnum = Field(..., description="Source type")

class GetStatus(Gateway):
    """
    Method returns refund status
    DOCS_URL: https://idosell.readme.io/reference/refundsgetrefundstatus-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/getRefundStatus')

    sourceId: StrictInt = Field(..., ge=1, description="Source ID")
    paymentId: StrictInt = Field(..., ge=1, description="Payment ID")
    sourceType: SourceTypeWithOrderEnum = Field(..., description="Source type")

class GetRetrieveList(PageableCamelGateway):
    """
    Method returns a list of incomplete refunds
    DOCS_URL: https://idosell.readme.io/reference/refundsretrieverefundslist-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/retrieveRefundsList')

    sourceType: SourceTypeAllEnum = Field(..., description="Source type")

class PutUpdate(Gateway):
    """
    Method allows you to update refund
    DOCS_URL: https://idosell.readme.io/reference/refundsupdaterefund-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/refunds/updateRefund')

    params: PutOmsRefundsParamsModel = Field(..., description="Parameters transmitted to method")
