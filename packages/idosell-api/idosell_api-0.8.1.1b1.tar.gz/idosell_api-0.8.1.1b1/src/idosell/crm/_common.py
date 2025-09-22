from datetime import date
from enum import StrEnum
from pydantic import BaseModel, Field, StrictInt

from src.idosell._common import BooleanStrShortEnum


# --- Enums
class BalanceOperationTypeEnum(StrEnum):
    ADD = 'add'
    SET = 'set'
    SUBTRACT = 'subtract'

class ClientTypeEnum(StrEnum):
    PERSON = 'person' # if client sex is not determined
    PERSON_MALE = 'person_male' # when client is a male
    PERSON_FEMALE = 'person_female' # when a customer is a woman
    FIRM = 'firm' # when client is company.

class TradeCreditEnum(StrEnum):
    NONZERO = 'nonzero'
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    ZERO = 'zero'


# --- DTOs
class BalanceModel(BaseModel):
    amount: float = Field(..., ge=0, description="Available balance")
    currency: str = Field(..., description="Currency ID")

class ClientRegistrationDateModel(BaseModel):
    clientRegistrationDateBegin: date = Field(..., description="Client Registration Date From")
    clientRegistrationDateEnd: date = Field(..., description="Client Registration Date To")

class DateModel(BaseModel):
    from_: str = Field(..., description="Start date (YYYY-MM-DD HH:MM:SS)", alias="from")
    to: str = Field(..., description="End date (YYYY-MM-DD HH:MM:SS)")

class ShopsModel(BaseModel):
    shop_id: StrictInt = Field(..., ge=1, description="Store ID")
    approval: BooleanStrShortEnum = Field(..., description="Have customer agreed to a newsletter")
    registered: BooleanStrShortEnum = Field(..., description="Is registered: y - only registered customers, n - only non-registered customers, null (argument not sent) - all")
