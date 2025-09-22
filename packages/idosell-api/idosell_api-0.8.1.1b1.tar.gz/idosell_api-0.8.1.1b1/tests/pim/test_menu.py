import pytest
from pydantic import ValidationError

from src.idosell.pim.menu import (
    # DTOs
    PutFilterPimMenuParamsModel,
    # Endpoints
    GetFilter, PutFilter, Delete, Get, Post, Put, PutSort
)
from src.idosell.pim._common import (
    MenuFiltersActivePutFilterModel, MenuListDeleteModel,
    MenuListPostModel, MenuListPutModel, MenuListPutSortModel,
    SettingsModel, SettingsPutSortModel,
    MenuFilterDisplayEnum, MenuFilterValueSortEnum
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for DTOs
class TestPutFilterPimMenuParamsModel:
    def test_valid(self):
        dto = PutFilterPimMenuParamsModel(
            shopId=1,
            languageId="eng",
            productMenuTreeId=1,
            productMenuNodeId=1,
            filterForMenuNodeIsDefault=BooleanStrShortEnum.YES,
                menuFiltersActive=MenuFiltersActivePutFilterModel(
                    menuFilterId="filter1",
                    menuFilterName="Color",
                    menuFilterDisplay=MenuFilterDisplayEnum.NAME,
                    menuFilterValueSort=MenuFilterValueSortEnum.PRIORITY,
                    menuFilterDefaultEnabled=BooleanStrShortEnum.YES
                )
        )
        assert dto.shopId == 1
        assert dto.languageId == "eng"
        assert dto.productMenuTreeId == 1
        assert dto.productMenuNodeId == 1
        assert dto.filterForMenuNodeIsDefault == BooleanStrShortEnum.YES
        assert dto.menuFiltersActive.menuFilterId == "filter1"

    def test_empty_strings_allowed(self):
        # Test that empty languageId and filterId are allowed (actual model behavior)
        dto = PutFilterPimMenuParamsModel(
            shopId=1,
            languageId="",
            productMenuTreeId=1,
            productMenuNodeId=1,
            filterForMenuNodeIsDefault=BooleanStrShortEnum.YES,
            menuFiltersActive=MenuFiltersActivePutFilterModel(
                menuFilterId="",
                menuFilterName="Color",
                menuFilterDisplay=MenuFilterDisplayEnum.NAME,
                menuFilterValueSort=MenuFilterValueSortEnum.PRIORITY,
                menuFilterDefaultEnabled=BooleanStrShortEnum.YES
            )
        )
        assert dto.languageId == ""
        assert dto.menuFiltersActive.menuFilterId == ""


# --- Tests for Endpoints
class TestGetFilter:
    def test_instantiate_minimal(self):
        dto = GetFilter()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/menu/filter'
        assert dto.shopId is None
        assert dto.languageId is None
        assert dto.productMenuTreeId is None
        assert dto.productMenuNodeId is None

    def test_instantiate_with_all_params(self):
        dto = GetFilter(
            shopId=1,
            languageId="eng",
            productMenuTreeId=1,
            productMenuNodeId=1
        )
        assert dto.shopId == 1
        assert dto.languageId == "eng"
        assert dto.productMenuTreeId == 1
        assert dto.productMenuNodeId == 1

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(shopId=0)

    def test_invalid_product_menu_tree_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(productMenuTreeId=0)

    def test_invalid_product_menu_node_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(productMenuNodeId=0)

class TestPutFilter:
    def test_instantiate_minimal(self):
        dto = PutFilter(
            params=PutFilterPimMenuParamsModel(
                shopId=1,
                languageId="eng",
                productMenuTreeId=1,
                productMenuNodeId=1,
                filterForMenuNodeIsDefault=BooleanStrShortEnum.YES,
                menuFiltersActive=MenuFiltersActivePutFilterModel(
                    menuFilterId="filter1",
                    menuFilterName="Color",
                    menuFilterDisplay=MenuFilterDisplayEnum.NAME,
                    menuFilterValueSort=MenuFilterValueSortEnum.PRIORITY,
                    menuFilterDefaultEnabled=BooleanStrShortEnum.YES
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/menu/filter'
        assert dto.params.shopId == 1
        assert dto.params.languageId == "eng"
        assert dto.params.productMenuTreeId == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutFilter()


class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            menu_list=[],
            settings=SettingsModel(textid_separator="")
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/menu/menu/delete'
        assert dto.menu_list == []
        assert dto.settings.textid_separator == ""

    def test_instantiate_with_menu_list(self):
        dto = Delete(
            menu_list=[
                MenuListDeleteModel(
                    shop_id=1,
                    menu_id=1,
                    item_id=1,
                    item_textid=r"item1\item2\item3"
                )
            ],
            settings=SettingsModel(textid_separator="\\")
        )
        assert len(dto.menu_list) == 1
        assert dto.menu_list[0].shop_id == 1
        assert dto.settings.textid_separator == "\\"

class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/menu/menu'
        assert dto.shop_id is None
        assert dto.menu_id is None
        assert dto.lang_id is None
        assert dto.node_id is None
        assert dto.level is None
        assert dto.textid_separator is None

    def test_instantiate_with_all_params(self):
        dto = Get(
            shop_id=1,
            menu_id=1,
            lang_id="eng",
            node_id=1,
            level=2,
            textid_separator="\\"
        )
        assert dto.shop_id == 1
        assert dto.menu_id == 1
        assert dto.lang_id == "eng"
        assert dto.node_id == 1
        assert dto.level == 2
        assert dto.textid_separator == "\\"

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            Get(shop_id=0)

    def test_invalid_menu_id_zero(self):
        with pytest.raises(ValidationError):
            Get(menu_id=0)

    def test_invalid_node_id_zero(self):
        with pytest.raises(ValidationError):
            Get(node_id=0)

    def test_level_zero_allowed(self):
        # Test that level=0 is allowed (ge=0 constraint allows 0)
        dto = Get(level=0)
        assert dto.level == 0

    def test_invalid_level_negative(self):
        # Test that negative level values are not allowed
        with pytest.raises(ValidationError):
            Get(level=-1)

class TestPost:
    def test_instantiate_minimal(self):
        dto = Post(
            menu_list=[],
            settings=SettingsModel(textid_separator="")
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/menu/menu'
        assert dto.menu_list == []
        assert dto.settings.textid_separator == ""

    def test_instantiate_with_menu_list(self):
        dto = Post(
            menu_list=[
                MenuListPostModel(
                    shop_id=1,
                    menu_id=1,
                    parent_id="0",
                    parent_textid=r"item1\item2",
                    lang_data=[]
                )
            ],
            settings=SettingsModel(textid_separator="\\")
        )
        assert len(dto.menu_list) == 1
        assert dto.menu_list[0].shop_id == 1
        assert dto.settings.textid_separator == "\\"

class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            menu_list=[],
            settings=SettingsModel(textid_separator="")
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/menu/menu'
        assert dto.menu_list == []
        assert dto.settings.textid_separator == ""

    def test_instantiate_with_menu_list(self):
        dto = Put(
            menu_list=[
                MenuListPutModel(
                    shop_id=1,
                    menu_id=1,
                    item_id="1",
                    item_textid=r"item1\item2\item3",
                    lang_data=[]
                )
            ],
            settings=SettingsModel(textid_separator="\\")
        )
        assert len(dto.menu_list) == 1
        assert dto.menu_list[0].shop_id == 1
        assert dto.settings.textid_separator == "\\"

class TestPutSort:
    def test_instantiate_minimal(self):
        dto = PutSort(
            menu_list=MenuListPutSortModel(
                shop_id=1,
                menu_id=1,
                lang_id="eng",
                parent_id=1,
                parent_textid=r"item1\item2",
                recursive=BooleanStrShortEnum.YES
            ),
            settings=SettingsPutSortModel(textid_separator="")
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/menu/sort'
        assert dto.menu_list.shop_id == 1
        assert dto.settings.textid_separator == ""

    def test_instantiate_with_all_params(self):
        dto = PutSort(
            menu_list=MenuListPutSortModel(
                shop_id=1,
                menu_id=1,
                lang_id="eng",
                parent_id=1,
                parent_textid=r"item1\item2",
                recursive=BooleanStrShortEnum.YES
            ),
            settings=SettingsPutSortModel(textid_separator="\\")
        )
        assert dto.menu_list.shop_id == 1
        assert dto.menu_list.menu_id == 1
        assert dto.settings.textid_separator == "\\"
