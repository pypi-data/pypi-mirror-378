from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import BooleanStrLongEnum, Gateway, PageableCamelGateway
from src.idosell.crm._common import TradeCreditEnum


# --- Enums
class OperationEnum(StrEnum):
    ADD = 'add'
    REMOVE = 'remove'


# --- DTOs
class ClientLastPurchaseDateProfitPointsModel(BaseModel):
    clientLastPurchaseDateBegin: str = Field(..., description="Start date (YYYY-MM-DD)")
    clientLastPurchaseDateEnd: str = Field(..., description="End date (YYYY-MM-DD)")

class PointsModificationDateModel(BaseModel):
    dateBegin: str = Field(..., description="Modification date from (YYYY-MM-DD HH:mm:ss)")
    dateEnd: str = Field(..., description="Modification date to (YYYY-MM-DD HH:mm:ss)")

class PostCrmProfitpointsParamsModel(BaseModel):
    client_id: StrictInt = Field(..., ge=1, description="...")
    operation: OperationEnum = Field(..., description="Operation: add, remove")
    score: float = Field(..., description="Amount of points to add or subtract")
    note: str = Field(..., description="...")
    order_number: StrictInt = Field(..., ge=1, description="Prepayment ID")


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    Method that enables extracting information about the amount of loyalty points collected by customers in a loyalty program
    DOCS_URL: https://idosell.readme.io/reference/clientsprofitpointsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/profitPoints')

    clientsIds: Optional[List[int]] = Field(default=None, min_length=1, description="Customer numbers (each >=1)")  # type: ignore
    clientTextSearch: Optional[str] = Field(default=None, min_length=1, description="Text search through customer data")
    clientIsActive: Optional[BooleanStrLongEnum] = Field(default=None, description="Active (yes/no)")
    clientHasTradeCredit: Optional[TradeCreditEnum] = Field(default=None, description="Trade credit")
    clientLastPurchaseDate: Optional[ClientLastPurchaseDateProfitPointsModel] = Field(default=None, description="Date of last purchase")
    pointsModificationDate: Optional[PointsModificationDateModel] = Field(default=None, description="Profit points modification date range")
    returnElements: Optional[List[str]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned. Allowed: clientId, clientProfitPoints, clientProfitPointsHistories")  # type: ignore

class Post(Gateway):
    """
    Method that allows for adding loyalty points to the balances of existing customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsprofitpointspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/profitPoints')

    params: PostCrmProfitpointsParamsModel = Field(..., description="Parameters transmitted to method")
