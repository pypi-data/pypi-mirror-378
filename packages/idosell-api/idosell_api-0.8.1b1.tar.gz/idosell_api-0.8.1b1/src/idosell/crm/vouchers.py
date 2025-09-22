from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AllYNEnum, AppendableGateway, PageableCamelGateway
from src.idosell.crm._common import BalanceModel, BalanceOperationTypeEnum


# --- Enums
class StatusFullEnum(StrEnum):
    ALL = 'all'
    USED = 'used'
    UNUSED = 'unused'
    UNVERFIED = 'unverified'

class StatusEnum(StrEnum):
    USED = 'used'
    UNUSED = 'unused'


# --- DTOs
class VoucherModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Voucher ID")
    number: str = Field(..., description="Number")

class VoucherPostPutBaseModel(BaseModel):
    number: str = Field(..., description="Number")
    name: str = Field(..., description="Name")
    expirationDate: str = Field(..., description="Voucher expiration date")
    balance: BalanceModel = Field(..., description="Voucher balance")
    shops: List[int] = Field(..., description="List of shops the voucher is active in")
    note: str = Field(..., description="...")

class VoucherPostModel(VoucherPostPutBaseModel):
    typeId: StrictInt = Field(..., ge=1, description="Gift voucher type id")

class VoucherPutModel(VoucherPostPutBaseModel):
    id: StrictInt = Field(..., ge=1, description="Voucher ID")
    balanceOperationType: BalanceOperationTypeEnum = Field(..., description="Balance operation type")
    status: StatusEnum = Field(..., description="Status")

class PutBlockCrmVouchersParamsModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Voucher ID")
    number: str = Field(..., min_length=1, description="Number")

class PutUnblockCrmVouchersParamsModel(BaseModel):
    vouchers: List[VoucherModel] = Field(..., min_length=1, description="...") # type: ignore

class DeleteCrmVouchersParamsModel(BaseModel):
    vouchers: List[VoucherModel] = Field(..., min_length=1, description="...") # type: ignore

class PostCrmVouchersParamsModel(BaseModel):
    vouchers: List[VoucherPostModel] = Field(..., min_length=1, description="...") # type: ignore

class PutCrmVouchersParamsModel(BaseModel):
    vouchers: List[VoucherPutModel] = Field(..., min_length=1, description="...") # type: ignore


# --- ENDPOINTS
class PutBlock(AppendableGateway):
    """
    Enables gift voucer blocking
    DOCS_URL: https://idosell.readme.io/reference/vouchersblockput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/block')

    params: PutBlockCrmVouchersParamsModel = Field(..., description="Parameters transmitted to method")

class GetTypes(PageableCamelGateway):
    """
    Allows for downloading all discount code campaigns defined in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/voucherstypesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/types')

class PutUnblock(AppendableGateway):
    """
    Enables gift vouchers unblocking
    DOCS_URL: https://idosell.readme.io/reference/vouchersunblockput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/unblock')

    params: PutUnblockCrmVouchersParamsModel = Field(..., description="Parameters transmitted to method")

class Delete(AppendableGateway):
    """
    Enables deleting a single or a list of gift vouchers
    DOCS_URL: https://idosell.readme.io/reference/vouchersvouchersdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/vouchers/delete')

    params: DeleteCrmVouchersParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    Enables searching for vouchers and retrieving information about indicated vouchers
    DOCS_URL: https://idosell.readme.io/reference/vouchersvouchersget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/vouchers')

    vouchers: Optional[List[VoucherModel]] = Field(default=None, min_length=1, description="List of vouchers to search (min 1)")  # type: ignore
    voucherTypeId: Optional[StrictInt] = Field(default=None, ge=1, description="Discount code campaign ID (>=1)")
    name: Optional[str] = Field(default=None, min_length=1, description="Name (non-empty)")
    status: Optional[StatusFullEnum] = Field(default=None, description="Status")
    generetedFromAffiliateProgram: Optional[AllYNEnum] = Field(default=None, description="Generated in the affiliate program (y/n)")
    noteContain: Optional[str] = Field(default=None, min_length=1, description="Notes contain (non-empty)")
    balanceFrom: Optional[float] = Field(default=None, ge=0, description="Value from (>=0)")
    balanceTo: Optional[float] = Field(default=None, ge=0, description="Value to (>=0)")
    expirationDateFrom: Optional[str] = Field(default=None, min_length=1, description="Expiration date from (non-empty)")
    expirationDateTo: Optional[str] = Field(default=None, min_length=1, description="Expiration date to (non-empty)")
    issueDateFrom: Optional[str] = Field(default=None, min_length=1, description="Created from (non-empty)")
    issueDateTo: Optional[str] = Field(default=None, min_length=1, description="Created to (non-empty)")
    usageDateFrom: Optional[str] = Field(default=None, min_length=1, description="To be used from (non-empty)")
    usageDateTo: Optional[str] = Field(default=None, min_length=1, description="To be used to (non-empty)")

class Post(AppendableGateway):
    """
    Enables adding new gift vouchers with the selected voucher type
    DOCS_URL: https://idosell.readme.io/reference/vouchersvoucherspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/vouchers')

    params: PostCrmVouchersParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Enables editing gift voucher, e.g. changing its balance, validity date or number (only for unused vouchers)
    DOCS_URL: https://idosell.readme.io/reference/vouchersvouchersput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/vouchers/vouchers')

    params: PutCrmVouchersParamsModel = Field(..., description="Parameters transmitted to method")
