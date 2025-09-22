from enum import IntEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway


# --- RMA Enums
class StatusIdEnum(IntEnum):
    COMPLAINT_IS_BEING_CONSIDERED_PRODUCT_WAS_SENT_FOR_TESTIN = 4
    COMPLAINT_IS_BEING_CONSIDERED_PRODUCT_SENT_TO_THE_PRODUCE = 5
    COMPLAINT_IS_BEING_CONSIDERED_REPAIR_IN_PROGRES = 6
    COMPLAINT_DIDNT_ARRIV = 14
    COMPLAINT_NOT_CONFIRMED_BY_THE_SHOP_SERVIC = 15
    THE_COMPLAINT_HAS_BEEN_CANCELLE = 17
    COMPLAINT_CANCELED_BY_THE_CUSTOME = 18
    COMPLAINT_CONFIRME = 19
    COMPLAINT_NOT_HANDLE = 20
    COMPLAINT_REJECTED_NO_FAULT_WAS_FOUN = 22
    COMPLAINT_REJECTED_THE_WARRANTY_PERIOD_HAS_EXPIRED = 23
    COMPLAINT_REJECTED_DEFECT_CAUSED_BY_IMPROPER_US = 24
    COMPLAINT_IS_BEING_CONSIDERED_REPAIR_COMPLETE = 28
    COMPLAINT_IS_BEING_CONSIDERED_THE_COMPLAINT_REQUIRES_ADDITIONAL_INFORMATION_FROM_THE_CUSTOMER = 29


# --- DTOs
class RmaDateModel(BaseModel):
    dateFrom: str = Field(..., description="Starting date in the YYYY-MM-DD format")
    dateTo:  str = Field(..., description="End date in the YYYY-MM-DD format")

class RmaChatModel(BaseModel):
    message: str = Field(..., description="Message content")

class RmasModel(BaseModel):
    rmaId: StrictInt = Field(..., description="Complaint id")
    rmaStatusId: StatusIdEnum = Field(..., description="Claim status")
    rmaChat: List[RmaChatModel] = Field(..., description="Customer correspondence")

class PutOmsRmaParamsModel(BaseModel):
    rmas: List[RmasModel] = Field(..., description="Complaints")


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    This get method allows you to retrieve data about existing claims
    DOCS_URL: https://idosell.readme.io/reference/rmarmaget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/rma/rma')

    rmaIds: List[StrictInt] | None = Field(None, min_length=1, description="List of RMA IDs (optional, list must contain at least one element, each >= 1)") # type: ignore
    stockId: StrictInt | None = Field(None, ge=1, description="Stock ID (optional, >= 1)")
    operatorLogin: str | None = Field(None, min_length=1, description="Login of the user handling the complaint (optional)")
    clientId: StrictInt | None = Field(None, ge=1, description="Unique client's number (optional, >= 1)")
    creationDate: RmaDateModel | None = Field(None, description="Complaint creation date in the YYYY-MM-DD format (optional)")
    modificationDate: RmaDateModel | None = Field(None, description="Complaint modification date in the YYYY-MM-DD format (optional)")
    endDate: RmaDateModel | None = Field(None, description="Complaint closing date in the YYYY-MM-DD format (optional)")

class Put(AppendableGateway):
    """
    This update method allows to update the data in existing complaints
    DOCS_URL: https://idosell.readme.io/reference/rmarmaput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/rma/rma')

    params: PutOmsRmaParamsModel = Field(..., description="Parameters transmitted to method")

class GetStatuses(Gateway):
    """
    Allows to download all possible complaint statuses
    DOCS_URL: https://idosell.readme.io/reference/rmastatusesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/rma/statuses')
