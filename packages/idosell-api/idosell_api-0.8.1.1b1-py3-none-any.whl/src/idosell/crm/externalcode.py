from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway


# --- DTOs
class PutCrmExternalcodeParamsModel(BaseModel):
    client_id: StrictInt = Field(..., ge=1, description="Client ID (>=1)")
    client_login: str = Field(..., min_length=1, description="Customer's login (non-empty)")
    code_extern: str = Field(..., min_length=1, description="External system code (non-empty)")


# --- ENDPOINTS
class Put(Gateway):
    """
    Method that enables setting external system codes for existing customer accounts
    DOCS_URL: https://idosell.readme.io/reference/clientsexternalcodeput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/externalCode')

    params: PutCrmExternalcodeParamsModel = Field(..., description="Parameters transmitted to method")
