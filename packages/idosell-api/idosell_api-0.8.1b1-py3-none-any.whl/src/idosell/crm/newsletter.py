from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr

from src.idosell._common import PageableSnakeGateway
from src.idosell.crm._common import DateModel, ShopsModel


# --- DTOs
class SearchEmailCrmNewsletterParamsModel(BaseModel):
    shops: List[ShopsModel] | None = Field(None, min_length=1, description="Store ID (list, min 1)")
    language: str | None = Field(None, min_length=1, description="Customer language ID (non-empty)")
    date: DateModel | None = Field(None, description="Date range")
    return_elements: Optional[List[str]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned")

class SearchSmsCrmNewsletterParamsModel(BaseModel):
    shops: List[ShopsModel] | None = Field(None, min_length=1, description="Store ID (list, min 1)")
    language: str | None = Field(None, min_length=1, description="Customer language ID (non-empty)")
    date: DateModel | None = Field(None, description="Date range")
    return_elements: Optional[List[str]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned")


# --- ENDPOINTS
class SearchEmail(PageableSnakeGateway):
    """
    Method that enables extracting a list of customer accounts that agreed / did not agree to receiving email newsletters
    DOCS_URL: https://idosell.readme.io/reference/clientsnewsletteremailsearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/newsletter/email/search')

    params: SearchEmailCrmNewsletterParamsModel = Field(..., description="Parameters transmitted to method")

class SearchSms(PageableSnakeGateway):
    """
    Method that enables extracting a list of customer accounts that agreed / did not agree to receiving text message newsletters
    DOCS_URL: https://idosell.readme.io/reference/clientsnewslettersmssearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/newsletter/sms/search')

    params: SearchSmsCrmNewsletterParamsModel = Field(..., description="Parameters transmitted to method")
