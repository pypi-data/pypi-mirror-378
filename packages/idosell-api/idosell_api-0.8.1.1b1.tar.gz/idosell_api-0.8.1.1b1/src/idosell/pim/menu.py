from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway
from src.idosell.pim._common import (
    MenuFiltersActivePutFilterModel, MenuListDeleteModel, MenuListPostModel,
    MenuListPutModel, MenuListPutSortModel, SettingsModel, SettingsPutSortModel
)


# --- DTOs
class PutFilterPimMenuParamsModel(BaseModel):
    shopId: StrictInt = Field(..., description="Shop Id")
    languageId: str = Field(..., description="Language ID (code in ISO-639-2)")
    productMenuTreeId: StrictInt = Field(..., description="Tree menu ID")
    productMenuNodeId: StrictInt = Field(..., description="Menu element ID")
    filterForMenuNodeIsDefault: BooleanStrShortEnum = Field(..., description="Default filter settings")
    menuFiltersActive: MenuFiltersActivePutFilterModel = Field(..., description="Active filters")


# --- ENDPOINTS
class GetFilter(Gateway):
    """
    The method returns information about filter settings in menu nodes.
    DOCS_URL: https://idosell.readme.io/reference/menufilterget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/filter')

    shopId: StrictInt | None = Field(None, ge=1, description="Shop Id")
    languageId: str | None = Field(None, description="Language ID (code in ISO-639-2)")
    productMenuTreeId: StrictInt | None = Field(None, ge=1,description="Tree menu ID")
    productMenuNodeId: StrictInt | None = Field(None, ge=1, description="Menu element ID")

class PutFilter(AppendableGateway):
    """
    The method allows you to manage filter settings in menu nodes.
    DOCS_URL: https://idosell.readme.io/reference/menufilterput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/filter')

    params: PutFilterPimMenuParamsModel = Field(..., description="Parameters transmitted to method")

class Delete(AppendableGateway):
    """
    Method that enables deleting existing menu elements.
    DOCS_URL: https://idosell.readme.io/reference/menumenudeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/menu/delete')

    menu_list: List[MenuListDeleteModel] = Field(..., description="List of menus")
    settings: SettingsModel = Field(..., description="Settings")

class Get(Gateway):
    """
    Method that returns information about menus and menu elements.
    DOCS_URL: https://idosell.readme.io/reference/menumenuget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/menu')

    shop_id: int | None = Field(None, ge=1, description="Shop Id")
    menu_id: int | None = Field(None, ge=1, description="Tree menu ID")
    lang_id: str | None = Field(None, description="Language ID")
    node_id: int | None = Field(None, ge=1, description="Menu node ID")
    level: int | None = Field(None, ge=0, description="Number of levels")
    textid_separator: str | None = Field(None, description="...")

class Post(AppendableGateway):
    """
    Method that enables adding new menu elements.
    DOCS_URL: https://idosell.readme.io/reference/menumenupost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/menu')

    menu_list: List[MenuListPostModel] = Field(..., description="...")
    settings: SettingsModel = Field(..., description="Settings")

class Put(AppendableGateway):
    """
    Method that enables editing existing menu elements.
    DOCS_URL: https://idosell.readme.io/reference/menumenuput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/menu')

    menu_list: List[MenuListPutModel] = Field(..., description="...")
    settings: SettingsModel = Field(..., description="Settings")

class PutSort(AppendableGateway):
    """
    Method that enables sorting of menu elements.
    DOCS_URL: https://idosell.readme.io/reference/menusortput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/menu/sort')

    menu_list: MenuListPutSortModel = Field(..., description="...")
    settings: SettingsPutSortModel = Field(..., description="Settings")
