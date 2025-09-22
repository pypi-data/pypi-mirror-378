from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt, model_validator

from src.idosell._common import Gateway, PageableCamelGateway


# --- Enums
class ReturnElementsEnum(StrEnum):
    GROUPNUMBER = 'groupNumber'
    GROUPCOMBINED = 'groupCombined'
    GROUPTYPE = 'groupType'
    GROUPREBATE = 'groupRebate'
    GROUPNAME = 'groupName'


# --- DTOs
class CategoriesModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID")
    price: float = Field(..., gt=0, description="Price")
    currency: str = Field(..., description="Currency")

class ProductsDiscountsModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID")
    price: float = Field(..., gt=0, description="Price")
    currency: str = Field(..., description="Currency")

class ProducersModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID")
    price: float = Field(..., gt=0, description="Price")
    currency: str = Field(..., description="Currency")

class SeriesModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID")
    price: float = Field(..., gt=0, description="Price")
    currency: str = Field(..., description="Currency")

class MenuItems(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID")
    price: float = Field(..., gt=0, description="Price")
    currency: str = Field(..., description="Currency")

class MenuItemsModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="ID")
    price: float = Field(..., ge=0, description="Price")
    currency: str = Field(..., description="Currency")

class DeleteGroupsCrmDiscountsParamsModel(BaseModel):
    discountGroupId: StrictInt = Field(..., ge=1, description="Discount group ID")

class PostGroupsCrmDiscountsParamsModel(BaseModel):
    discountGroupName: str = Field(..., description="Discount group name")

class PutGroupsCrmDiscountsParamsModel(BaseModel):
    discountGroupId: StrictInt = Field(..., ge=1, description="Discount group ID")
    discountGroupName: str = Field(..., description="Discount group name")

class DeleteGroupsProductsCrmDiscountsParamsModel(BaseModel):
    discountGroupId: StrictInt | None = Field(None, ge=1, description="Discount group ID")
    products: List[int] | None = Field(None, description="Products list")
    producers: List[int] | None = Field(None, description="Brands")
    series: List[int] | None = Field(None, description="Series")
    categories: List[int] | None = Field(None, description="List of categories in which sought products are present")
    menuItems: List[int] | None = Field(None, description="Menu elements")

    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        """Validate that at least one field is provided for the delete operation."""
        fields_to_check = [self.discountGroupId, self.products, self.producers, self.series, self.categories, self.menuItems]
        if not any(field is not None for field in fields_to_check):
            raise ValueError("At least one field must be provided")
        return self

class PutGroupsProductsCrmDiscountsParamsModel(BaseModel):
    discountGroupId: StrictInt = Field(..., ge=1, description="Discount group ID")
    products: List[ProductsDiscountsModel] = Field(..., description="Products list")
    producers: List[ProducersModel] = Field(..., description="Brands")
    series: List[SeriesModel] = Field(..., description="Series")
    categories: List[CategoriesModel] = Field(..., description="List of categories in which sought products are present")
    menuItems: List[MenuItemsModel] = Field(..., description="Menu elements")


# --- ENDPOINTS
class GetGroupsClients(Gateway):
    """
    Returns the list of customer IDs assigned to an indicated discount group. In order to assign a discount group, use setClients method in API Clients
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupsclientsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups/clients')

    discountGroupId: StrictInt = Field(..., ge=1, description="Discount group ID")

class DeleteGroups(Gateway):
    """
    Allows to remove a discount group. The condition for conducting this process is no customers assigned to the indicated group. In order to check the assigned customers use getClientsAssignedToDiscountGroup method
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups/delete')

    params: DeleteGroupsCrmDiscountsParamsModel = Field(..., description="Parameters transmitted to method")

class GetGroups(PageableCamelGateway):
    """
    Method that enables extracting information about discount groups configured in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups')

    groupNumbers: Optional[List[int]] = Field(default=None, min_length=1, description="List of group numbers (each >=1)")  # type: ignore
    returnElements: Optional[List[ReturnElementsEnum]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned")  # type: ignore

class PostGroups(Gateway):
    """
    Allows to add a new discount group in the administration panel. The discount group is added by default with the setting "Discount for products - yes, but different for indicated groups"
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups')

    params: PostGroupsCrmDiscountsParamsModel = Field(..., description="Parameters transmitted to method")

class PutGroups(Gateway):
    """
    Allows to change a discount group name
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups')

    params: PutGroupsCrmDiscountsParamsModel = Field(..., description="Parameters transmitted to method")

class DeleteGroupsProducts(Gateway):
    """
    The method allows the removal of products from a discount group
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupsproductsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups/products/delete')

    params: DeleteGroupsProductsCrmDiscountsParamsModel = Field(..., description="Parameters transmitted to method")

class PutGroupsProducts(Gateway):
    """
    The method allows products to be added to a discount group and their price to be specified in the discount group
    DOCS_URL: https://idosell.readme.io/reference/discountsgroupsproductsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/groups/products')

    params: PutGroupsProductsCrmDiscountsParamsModel = Field(..., description="Parameters transmitted to method")

class PutRebatesBlockCard(Gateway):
    """
    Allows to block an indicated discount card, eg. when it is assumed that its number has been made available publicly. The blocked card can be unblocked with the method unblockRebateCard
    DOCS_URL: https://idosell.readme.io/reference/discountsrebatesblockcardput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/rebates/blockCard')

    card_number: str = Field(..., description="Card number")

class DeleteRebatesCard(Gateway):
    """
    Method allows to quickly delete all the discount codes, which have never been used by customers, from an indicated rebate campaign. Codes which have been used at least once, will not be deleted
    DOCS_URL: https://idosell.readme.io/reference/discountsrebatescarddeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/rebates/card/delete')

    campaign_id: StrictInt = Field(..., ge=1, description="Campaign ID")

class PostRebatesCard(Gateway):
    """
    Allows to upload new card numbers to already existing discount card types in the administration panel. Cards uploaded such way retrieve settings, regarding the discount amount, from the type of cards to which they are uploaded. Every card can also have individual, independent discount settings which can be set in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/discountsrebatescardpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/rebates/card')

    campaign_id: StrictInt = Field(..., ge=1, description="Campaign ID")
    card_number: str = Field(..., description="Card number")

class DeleteRebatesCode(Gateway):
    """
    Allows to quickly delete all the discount codes, which have never been used by customers, from an indicated rebate campaign. Codes which have been used at least once, will not be deleted
    DOCS_URL: https://idosell.readme.io/reference/discountsrebatescodedeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/rebates/code/delete')

    campaign_id: StrictInt = Field(..., ge=1, description="Campaign ID")

class PostRebatesCode(Gateway):
    """
    Allows to upload new code numbers to already existing rebate campaigns in the administration panel. The codes uploaded in such way retrieve settings, regarding the discount amount, from a campaign to which they are uploaded. Each discount code can also have individual, independent discount settings which can be set in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/discountsrebatescodepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/rebates/code')

    campaign_id: StrictInt = Field(..., ge=1, description="Campaign ID")
    code_number: str = Field(..., description="Code")

class PutRebatesUnblockCard(Gateway):
    """
    unblockRebateCard method - allows to unblock discount cards. Block cards with the blockRebateCard method
    DOCS_URL: https://idosell.readme.io/reference/discountsrebatesunblockcardput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/discounts/rebates/unblockCard')

    card_number: str = Field(..., description="Card number")
