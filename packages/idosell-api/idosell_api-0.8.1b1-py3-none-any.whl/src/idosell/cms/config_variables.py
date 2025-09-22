from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway, PageableCamelGateway


# --- Enums
class TypeConfigVariablesEnum(StrEnum):
    SNIPPETS_CAMPAIGN = 'snippets_campaign'


# --- DTOs
class PutVariablesModel(BaseModel):
    key: str = Field(..., min_length=1, max_length=255, description="Key of config value")
    value: str | None = Field(None, min_length=0, max_length=255, description="Value of config item")
    type: str = Field(..., description="The type of module for which the configuration is used")
    itemId: StrictInt = Field(..., ge=1, description="Identifier of the item in used module")

class PutCmsConfigVariablesModel(BaseModel):
    variables: List[PutVariablesModel] = Field(..., description="...")


# --- ENDPOINTS
class Get(PageableCamelGateway):
    """
    This call returns config variables for given module (type)
    DOCS_URL: https://idosell.readme.io/reference/configvariablesget-1
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/config/variables')

    type: TypeConfigVariablesEnum = Field(TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN, description="Which component is affected by the configuration")
    item: List[int] | None = Field(None, min_length=1, description="List of item identifiers for given configuration type. Eg. snippet campaign identifiers") # type: ignore
    key: List[str] | None = Field(None, min_length=1, description="List of configuration keys") # type: ignore

class Put(AppendableGateway):
    """
    Use this operation to update snippet campaigns
    DOCS_URL: https://idosell.readme.io/reference/configvariablesput-1
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/config/variables')

    params: PutCmsConfigVariablesModel = Field(..., description="...")

class Delete(Gateway):
    """
    This call is used to remove defined configuration variables
    DOCS_URL: https://idosell.readme.io/reference/configvariablesdelete-1
    """

    _method: str = PrivateAttr(default='DELETE')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/config/variables')

    type: TypeConfigVariablesEnum = Field(..., description="Which component is affected by the configuration")
    item: List[int] | None = Field(None, description="List of item identifiers for given configuration type. Eg. snippet campaign identifiers")
    key: List[str] | None = Field(None, description="List of configuration keys")
