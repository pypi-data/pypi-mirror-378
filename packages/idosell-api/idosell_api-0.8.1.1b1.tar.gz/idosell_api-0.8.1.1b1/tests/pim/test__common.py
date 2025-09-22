import pytest
from pydantic import ValidationError

from src.idosell.pim._common import (
    # Enums
    FormatEnum, ItemTypeEnum, HrefTargetEnum, DefaultViewEnum, ActionEnum,
    DisplayAllTypeEnum, MetaRobotsIndexEnum, MetaRobotsFollowEnum,
    MenuFilterValueSortEnum, MenuFilterDisplayEnum, ViewEnum, SortByEnum,
    SortOrderEnum, EntityTypeEnum, DisplayModeEnum, OperationSizesEnum,
    FormatWarrantiesEnum, DataTypeEnum, FieldEnum, OrderEnum, TypeEnum,
    WarrantyTypeEnum,
    # Menu DTOs
    MenuFiltersActivePutFilterModel, MenuListPutSortModel, SettingsPutSortModel,
    SortLangDataModelModel, DisplayLimitLangDataModel, GfxModel, LangDataModel,
    MenuListDeleteModel, MenuListPutModel, MenuListPostModel, SettingsModel,
    # Responsibility DTOs
    EntitiesResponsibilityModel, EntitiesResponsibilityPostModel,
    EntitiesResponsibilityPutModel,
    # Sizecharts DTOs
    ColumnsModel, DescriptionsModel, SizesModel, LanguagesDataModel,
    SizeChartsPutModel,
    # Sizes DTOs
    LangDataSizesModel, SizesPutModel,
    # Warranties DTOs
    LanguagesWarrantiesModel, DescriptionWarrantiesModel, IconSettingsModel,
    LangWarrantiesModel, LangDataWarrantiesModel, ResultsOrderWarrantiesGetModel,
    ShopnameWarrantiesModel, WarrantiesPostModel, WarrantiesPutModel,
)
from src.idosell._common import BooleanStrShortEnum
from src.idosell.pim.products._common import GraphicTypeEnum


# --- Tests for Menu Enums
class TestFormatEnum:
    def test_valid_values(self):
        assert FormatEnum.JPG == 'jpg'
        assert FormatEnum.JPEG == 'jpeg'
        assert FormatEnum.PNG == 'png'
        assert FormatEnum.GIF == 'gif'
        assert FormatEnum.SVG == 'svg'
        assert FormatEnum.WEBP == 'webp'

class TestItemTypeEnum:
    def test_valid_values(self):
        assert ItemTypeEnum.PRODUCTS == 'products'
        assert ItemTypeEnum.NAVIGATION == 'navigation'
        assert ItemTypeEnum.PRODUCTS_WITH_RICH_TEXT == 'products_with_rich_text'
        assert ItemTypeEnum.NAVIGATION_WITH_RICH_TEXT == 'navigation_with_rich_text'
        assert ItemTypeEnum.RICH_TEXT == 'rich_text'
        assert ItemTypeEnum.STATIC == 'static'
        assert ItemTypeEnum.LINK == 'link'

class TestHrefTargetEnum:
    def test_valid_values(self):
        assert HrefTargetEnum.SELF == '_self'
        assert HrefTargetEnum.BLANK == '_blank'

class TestDefaultViewEnum:
    def test_valid_values(self):
        assert DefaultViewEnum.NORMAL == 'normal'
        assert DefaultViewEnum.LIST == 'list'
        assert DefaultViewEnum.GALLERY == 'gallery'

class TestActionEnum:
    def test_valid_values(self):
        assert ActionEnum.EXPAND == 'expand'
        assert ActionEnum.RELOAD == 'reload'

class TestDisplayAllTypeEnum:
    def test_valid_values(self):
        assert DisplayAllTypeEnum.PRODUCTS_LIST == 'products_list'
        assert DisplayAllTypeEnum.NAVIGATION_SITE == 'navigation_site'

class TestMetaRobotsIndexEnum:
    def test_valid_values(self):
        assert MetaRobotsIndexEnum.DEFAULT == 'default'
        assert MetaRobotsIndexEnum.INDEX == 'index'
        assert MetaRobotsIndexEnum.NOINDEX == 'noindex'

class TestMetaRobotsFollowEnum:
    def test_valid_values(self):
        assert MetaRobotsFollowEnum.DEFAULT == 'default'
        assert MetaRobotsFollowEnum.FOLLOW == 'follow'
        assert MetaRobotsFollowEnum.NOFOLLOW == 'nofollow'

class TestMenuFilterValueSortEnum:
    def test_valid_values(self):
        assert MenuFilterValueSortEnum.Y == 'y'
        assert MenuFilterValueSortEnum.N == 'n'
        assert MenuFilterValueSortEnum.PRIORITY == 'priority'

class TestMenuFilterDisplayEnum:
    def test_valid_values(self):
        assert MenuFilterDisplayEnum.NAME == 'name'
        assert MenuFilterDisplayEnum.GFX == 'gfx'
        assert MenuFilterDisplayEnum.NAMEGFX == 'namegfx'

class TestViewEnum:
    def test_valid_values(self):
        assert ViewEnum.NORMAL == 'normal'
        assert ViewEnum.LIST == 'list'
        assert ViewEnum.GALLERY == 'gallery'

class TestSortByEnum:
    def test_valid_values(self):
        assert SortByEnum.DATE == 'date'
        assert SortByEnum.PRIORITY == 'priority'
        assert SortByEnum.PRIORITYNAME == 'priorityName'
        assert SortByEnum.NAME == 'name'
        assert SortByEnum.PRICE == 'price'

class TestSortOrderEnum:
    def test_valid_values(self):
        assert SortOrderEnum.ASC == 'asc'
        assert SortOrderEnum.DESC == 'desc'


# --- Tests for Responsibility Enums
class TestEntityTypeEnum:
    def test_valid_values(self):
        assert EntityTypeEnum.PRODUCER == 'producer'
        assert EntityTypeEnum.PERSON == 'person'


# --- Tests for Sizecharts Enums
class TestDisplayModeEnum:
    def test_valid_values(self):
        assert DisplayModeEnum.ALL == 'all'
        assert DisplayModeEnum.SINGLE == 'single'


# --- Tests for Sizes Enums
class TestOperationSizesEnum:
    def test_valid_values(self):
        assert OperationSizesEnum.ADD == 'add'
        assert OperationSizesEnum.EDIT == 'edit'
        assert OperationSizesEnum.DEL == 'del'


# --- Tests for Warranties Enums
class TestFormatWarrantiesEnum:
    def test_valid_values(self):
        assert FormatWarrantiesEnum.JPG == 'jpg'
        assert FormatWarrantiesEnum.GIF == 'gif'
        assert FormatWarrantiesEnum.PNG == 'png'

class TestDataTypeEnum:
    def test_valid_values(self):
        assert DataTypeEnum.URL == 'url'
        assert DataTypeEnum.BASE64 == 'base64'

class TestFieldEnum:
    def test_valid_values(self):
        assert FieldEnum.WARRANTY_ID == 'warranty_id'
        assert FieldEnum.WARRANTY_NAME == 'warranty_name'

class TestOrderEnum:
    def test_valid_values(self):
        assert OrderEnum.ASCENDING == 'ascending'
        assert OrderEnum.DESCENDING == 'descending'

class TestTypeEnum:
    def test_valid_values(self):
        assert TypeEnum.SELLER == 'seller'
        assert TypeEnum.PRODUCER == 'producer'

class TestWarrantyTypeEnum:
    def test_valid_values(self):
        assert WarrantyTypeEnum.SELLER == 'seller'
        assert WarrantyTypeEnum.PRODUCER == 'producer'


# --- Tests for Menu DTOs
class TestMenuFiltersActivePutFilterModel:
    def test_valid(self):
        dto = MenuFiltersActivePutFilterModel(
            menuFilterId="filter1",
            menuFilterName="Color",
            menuFilterDisplay=MenuFilterDisplayEnum.NAME,
            menuFilterValueSort=MenuFilterValueSortEnum.PRIORITY,
            menuFilterDefaultEnabled=BooleanStrShortEnum.YES
        )
        assert dto.menuFilterId == "filter1"
        assert dto.menuFilterDefaultEnabled == BooleanStrShortEnum.YES

class TestMenuListPutSortModel:
    def test_valid(self):
        dto = MenuListPutSortModel(
            shop_id=1,
            menu_id=1,
            lang_id="eng",
            parent_id=1,
            parent_textid=r"item1\item2",
            recursive=BooleanStrShortEnum.YES
        )
        assert dto.shop_id == 1
        assert dto.lang_id == "eng"

    def test_invalid_menu_id_zero(self):
        with pytest.raises(ValidationError):
            MenuListPutSortModel(
                shop_id=1,
                menu_id=0,
                lang_id="eng",
                parent_id=1,
                parent_textid=r"item1\item2",
                recursive=BooleanStrShortEnum.YES
            )

class TestSettingsPutSortModel:
    def test_valid(self):
        dto = SettingsPutSortModel(textid_separator="\\")
        assert dto.textid_separator == "\\"

class TestSortLangDataModelModel:
    def test_valid(self):
        dto = SortLangDataModelModel(
            view=ViewEnum.NORMAL,
            sort_by=SortByEnum.NAME,
            sort_order=SortOrderEnum.ASC
        )
        assert dto.view == ViewEnum.NORMAL
        assert dto.sort_by == SortByEnum.NAME

class TestDisplayLimitLangDataModel:
    def test_valid(self):
        dto = DisplayLimitLangDataModel(
            view=ViewEnum.LIST,
            limit=10
        )
        assert dto.view == ViewEnum.LIST
        assert dto.limit == 10

    def test_invalid_limit_zero(self):
        with pytest.raises(ValidationError):
            DisplayLimitLangDataModel(
                view=ViewEnum.LIST,
                limit=0
            )

class TestGfxModel:
    def test_valid(self):
        dto = GfxModel(
            base64="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAx EAPwCdABmX/9k=",
            format=FormatEnum.JPG
        )
        assert dto.format == FormatEnum.JPG
        assert dto.base64.startswith("data:image/jpeg")

class TestLangDataModel:
    def test_valid(self):
        dto = LangDataModel(
            lang_id="eng",
            name="Menu Item",
            priority=1,
            description="Description",
            description_bottom="Bottom description",
            link="http://example.com",
            item_type=ItemTypeEnum.PRODUCTS,
            meta_title="Meta Title",
            meta_description="Meta Description",
            meta_keywords="keyword1, keyword2",
            url="http://example.com",
            href_target=HrefTargetEnum.SELF,
            sort=[SortLangDataModelModel(view=ViewEnum.NORMAL, sort_by=SortByEnum.NAME, sort_order=SortOrderEnum.ASC)],
            display_limit=[DisplayLimitLangDataModel(view=ViewEnum.LIST, limit=10)],
            default_view=DefaultViewEnum.NORMAL,
            headline_name="Headline",
            expand=BooleanStrShortEnum.YES,
            hidden=BooleanStrShortEnum.NO,
            action=ActionEnum.EXPAND,
            display_all_type=DisplayAllTypeEnum.PRODUCTS_LIST,
            display_all=BooleanStrShortEnum.YES,
            allow_sort_change=BooleanStrShortEnum.YES,
            allow_limit_change=BooleanStrShortEnum.YES,
            node_gfx=BooleanStrShortEnum.NO,
            gfx_active_type=GraphicTypeEnum.IMG,
            gfx_inactive_type=GraphicTypeEnum.IMG,
            gfx_omo_type=GraphicTypeEnum.IMG,
            gfx_nav=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_active=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_active_desktop=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_active_tablet=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_active_mobile=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_inactive_desktop=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_inactive_tablet=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_inactive_mobile=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_onmouseover=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_omo_desktop=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_omo_tablet=GfxModel(base64="base64data", format=FormatEnum.JPG),
            gfx_omo_mobile=GfxModel(base64="base64data", format=FormatEnum.JPG),
            canonical_to_parent=BooleanStrShortEnum.NO,
            meta_robots_index=MetaRobotsIndexEnum.DEFAULT,
            meta_robots_follow=MetaRobotsFollowEnum.DEFAULT
        )
        assert dto.lang_id == "eng"
        assert dto.name == "Menu Item"

    def test_invalid_priority_zero(self):
        with pytest.raises(ValidationError):
            LangDataModel(
                lang_id="eng",
                name="Menu Item",
                priority=0,
                description="Description",
                description_bottom="Bottom description",
                link="http://example.com",
                item_type=ItemTypeEnum.PRODUCTS,
                meta_title="Meta Title",
                meta_description="Meta Description",
                meta_keywords="keyword1, keyword2",
                url="http://example.com",
                href_target=HrefTargetEnum.SELF,
                sort=[SortLangDataModelModel(view=ViewEnum.NORMAL, sort_by=SortByEnum.NAME, sort_order=SortOrderEnum.ASC)],
                display_limit=[DisplayLimitLangDataModel(view=ViewEnum.LIST, limit=10)],
                default_view=DefaultViewEnum.NORMAL,
                headline_name="Headline",
                expand=BooleanStrShortEnum.YES,
                hidden=BooleanStrShortEnum.NO,
                action=ActionEnum.EXPAND,
                display_all_type=DisplayAllTypeEnum.PRODUCTS_LIST,
                display_all=BooleanStrShortEnum.YES,
                allow_sort_change=BooleanStrShortEnum.YES,
                allow_limit_change=BooleanStrShortEnum.YES,
                node_gfx=BooleanStrShortEnum.NO,
                gfx_active_type=GraphicTypeEnum.IMG,
                gfx_inactive_type=GraphicTypeEnum.IMG,
                gfx_omo_type=GraphicTypeEnum.IMG,
                gfx_nav=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_active=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_active_desktop=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_active_tablet=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_active_mobile=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_inactive_desktop=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_inactive_tablet=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_inactive_mobile=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_onmouseover=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_omo_desktop=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_omo_tablet=GfxModel(base64="base64data", format=FormatEnum.JPG),
                gfx_omo_mobile=GfxModel(base64="base64data", format=FormatEnum.JPG),
                canonical_to_parent=BooleanStrShortEnum.NO,
                meta_robots_index=MetaRobotsIndexEnum.DEFAULT,
                meta_robots_follow=MetaRobotsFollowEnum.DEFAULT
            )

class TestMenuListDeleteModel:
    def test_valid(self):
        dto = MenuListDeleteModel(
            shop_id=1,
            menu_id=1,
            item_id=1,
            item_textid=r"item1\item2\item3"
        )
        assert dto.shop_id == 1
        assert dto.item_id == 1

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            MenuListDeleteModel(
                shop_id=0,
                menu_id=1,
                item_id=1,
                item_textid=r"item1\item2\item3"
            )

class TestMenuListPutModel:
    def test_valid(self):
        dto = MenuListPutModel(
            shop_id=1,
            menu_id=1,
            item_id="1",
            item_textid=r"item1\item2\item3",
            lang_data=[]
        )
        assert dto.shop_id == 1
        assert dto.item_textid == r"item1\item2\item3"

class TestMenuListPostModel:
    def test_valid(self):
        dto = MenuListPostModel(
            shop_id=1,
            menu_id=1,
            parent_id="1",
            parent_textid=r"item1\item2",
            lang_data=[]
        )
        assert dto.shop_id == 1
        assert dto.parent_textid == r"item1\item2"

class TestSettingsModel:
    def test_valid(self):
        dto = SettingsModel(textid_separator="")
        assert dto.textid_separator == ""


# --- Tests for Responsibility DTOs
class TestEntitiesResponsibilityModel:
    def test_valid(self):
        dto = EntitiesResponsibilityModel(
            code="CODE1",
            name="Entity Name",
            mail="entity@example.com",
            street="Main Street",
            number="123",
            subnumber=None,
            zipcode="12345",
            city="City",
            country="US",
            phone=None,
            description=None,
            url=None
        )
        assert dto.code == "CODE1"
        assert dto.mail == "entity@example.com"

class TestEntitiesResponsibilityPostModel:
    def test_valid_with_id(self):
        dto = EntitiesResponsibilityPostModel(
            id=1,
            code="CODE1",
            name="Entity Name",
            mail="entity@example.com",
            street="Main Street",
            number="123",
            subnumber=None,
            zipcode="12345",
            city="City",
            country="US",
            phone=None,
            description=None,
            url=None
        )
        assert dto.id == 1

    def test_valid_without_id(self):
        dto = EntitiesResponsibilityPostModel(
            code="CODE1",
            name="Entity Name",
            mail="entity@example.com",
            street="Main Street",
            number="123",
            subnumber=None,
            zipcode="12345",
            city="City",
            country="US"
        )
        assert dto.code == "CODE1"

class TestEntitiesResponsibilityPutModel:
    def test_valid(self):
        dto = EntitiesResponsibilityPutModel(
            id=1,
            code="CODE1",
            name="Entity Name",
            mail="entity@example.com",
            street="Main Street",
            number="123",
            subnumber=None,
            zipcode="12345",
            city="City",
            country="US",
            phone=None,
            description=None,
            url=None
        )
        assert dto.id == 1

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            EntitiesResponsibilityPutModel(
                id=0,
                code="CODE1",
                name="Entity Name",
                mail="entity@example.com",
                street="Main Street",
                number="123",
                subnumber=None,
                zipcode="12345",
                city="City",
                country="US"
            )


# --- Tests for Sizecharts DTOs
class TestColumnsModel:
    def test_valid(self):
        dto = ColumnsModel(
            columnNumber=1,
            columnTitle="Size"
        )
        assert dto.columnNumber == 1
        assert dto.columnTitle == "Size"

    def test_invalid_column_number_zero(self):
        with pytest.raises(ValidationError):
            ColumnsModel(
                columnNumber=0,
                columnTitle="Size"
            )

class TestDescriptionsModel:
    def test_valid(self):
        dto = DescriptionsModel(
            columnNumber=1,
            value="S"
        )
        assert dto.columnNumber == 1
        assert dto.value == "S"

class TestSizesModel:
    def test_valid(self):
        dto = SizesModel(
            sizeId="S",
            priority=1,
            descriptions=[DescriptionsModel(columnNumber=1, value="Small")]
        )
        assert dto.sizeId == "S"
        assert len(dto.descriptions) == 1

class TestLanguagesDataModel:
    def test_valid(self):
        dto = LanguagesDataModel(
            language="eng",
            columns=[ColumnsModel(columnNumber=1, columnTitle="Size")],
            sizes=[SizesModel(sizeId="S", priority=1, descriptions=[DescriptionsModel(columnNumber=1, value="Small")])]
        )
        assert dto.language == "eng"
        assert len(dto.columns) == 1

class TestSizeChartsPutModel:
    def test_valid(self):
        dto = SizeChartsPutModel(
            id=1,
            nameInPanel="Size Chart 1",
            displayMode=DisplayModeEnum.ALL,
            languagesData=[LanguagesDataModel(
                language="eng",
                columns=[ColumnsModel(columnNumber=1, columnTitle="Size")],
                sizes=[SizesModel(sizeId="S", priority=1, descriptions=[DescriptionsModel(columnNumber=1, value="Small")])]
            )]
        )
        assert dto.id == 1
        assert dto.displayMode == DisplayModeEnum.ALL

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            SizeChartsPutModel(
                id=0,
                nameInPanel="Size Chart 1",
                displayMode=DisplayModeEnum.ALL,
                languagesData=[LanguagesDataModel(
                    language="eng",
                    columns=[ColumnsModel(columnNumber=1, columnTitle="Size")],
                    sizes=[SizesModel(sizeId="S", priority=1, descriptions=[DescriptionsModel(columnNumber=1, value="Small")])]
                )]
            )


# --- Tests for Sizes DTOs
class TestLangDataSizesModel:
    def test_valid(self):
        dto = LangDataSizesModel(
            lang_id="eng",
            name="Small"
        )
        assert dto.lang_id == "eng"
        assert dto.name == "Small"

class TestSizesPutModel:
    def test_valid(self):
        dto = SizesPutModel(
            faultCode=0,
            faultString="OK",
            group_id=1,
            id="S",
            name="Small",
            description="Small size",
            operation=OperationSizesEnum.ADD,
            lang_data=[LangDataSizesModel(lang_id="eng", name="Small")]
        )
        assert dto.group_id == 1
        assert dto.operation == OperationSizesEnum.ADD

    def test_invalid_group_id_zero(self):
        with pytest.raises(ValidationError):
            SizesPutModel(
                faultCode=0,
                faultString="OK",
                group_id=0,
                id="S",
                name="Small",
                description="Small size",
                operation=OperationSizesEnum.ADD,
                lang_data=[LangDataSizesModel(lang_id="eng", name="Small")]
            )


# --- Tests for Warranties DTOs
class TestLanguagesWarrantiesModel:
    def test_valid(self):
        dto = LanguagesWarrantiesModel(
            language_id="eng",
            language_name="English",
            value="2 years"
        )
        assert dto.language_id == "eng"
        assert dto.value == "2 years"

class TestDescriptionWarrantiesModel:
    def test_valid(self):
        dto = DescriptionWarrantiesModel(
            languages=[LanguagesWarrantiesModel(language_id="eng", language_name="English", value="2 years warranty")]
        )
        assert len(dto.languages) == 1

class TestIconSettingsModel:
    def test_valid(self):
        dto = IconSettingsModel(
            format=FormatWarrantiesEnum.JPG,
            data_type=DataTypeEnum.BASE64
        )
        assert dto.format == FormatWarrantiesEnum.JPG
        assert dto.data_type == DataTypeEnum.BASE64

class TestLangWarrantiesModel:
    def test_valid(self):
        dto = LangWarrantiesModel(
            lang_id="eng",
            name="Warranty Name",
            icon="base64icon",
            icon_settings=IconSettingsModel(format=FormatWarrantiesEnum.JPG, data_type=DataTypeEnum.BASE64),
            description="Warranty description"
        )
        assert dto.lang_id == "eng"
        assert dto.icon == "base64icon"

class TestLangDataWarrantiesModel:
    def test_valid_with_str_id(self):
        dto = LangDataWarrantiesModel(
            warranty_id="warranty1",
            lang=[LangWarrantiesModel(
                lang_id="eng",
                name="Warranty Name",
                icon="base64icon",
                icon_settings=IconSettingsModel(format=FormatWarrantiesEnum.JPG, data_type=DataTypeEnum.BASE64),
                description="Warranty description"
            )]
        )
        assert dto.warranty_id == "warranty1"

    def test_valid_with_int_id(self):
        dto = LangDataWarrantiesModel(
            warranty_id=123,
            lang=[LangWarrantiesModel(
                lang_id="eng",
                name="Warranty Name",
                icon="base64icon",
                icon_settings=IconSettingsModel(format=FormatWarrantiesEnum.JPG, data_type=DataTypeEnum.BASE64),
                description="Warranty description"
            )]
        )
        assert dto.warranty_id == 123

class TestResultsOrderWarrantiesGetModel:
    def test_valid(self):
        dto = ResultsOrderWarrantiesGetModel(
            field=FieldEnum.WARRANTY_NAME,
            order=OrderEnum.ASCENDING
        )
        assert dto.field == FieldEnum.WARRANTY_NAME
        assert dto.order == OrderEnum.ASCENDING

class TestShopnameWarrantiesModel:
    def test_valid(self):
        dto = ShopnameWarrantiesModel(
            languages=[LanguagesWarrantiesModel(language_id="eng", language_name="English", value="2 years")]
        )
        assert len(dto.languages) == 1

class TestWarrantiesPostModel:
    def test_valid(self):
        dto = WarrantiesPostModel(
            name="Warranty 1",
            type=TypeEnum.SELLER,
            period=24,
            shopname=ShopnameWarrantiesModel(languages=[LanguagesWarrantiesModel(language_id="eng", language_name="English", value="2 years")]),
            description=DescriptionWarrantiesModel(languages=[LanguagesWarrantiesModel(language_id="eng", language_name="English", value="Full warranty coverage")])
        )
        assert dto.name == "Warranty 1"
        assert dto.type == TypeEnum.SELLER
        assert dto.period == 24

class TestWarrantiesPutModel:
    def test_valid_with_str_id(self):
        dto = WarrantiesPutModel(
            id="warranty1",
            name="Warranty 1",
            type=TypeEnum.SELLER,
            period=24
        )
        assert dto.id == "warranty1"
        assert dto.period == 24

    def test_valid_with_int_id(self):
        dto = WarrantiesPutModel(
            id=123,
            name="Warranty 1",
            type=TypeEnum.SELLER,
            period=24
        )
        assert dto.id == 123

    def test_invalid_period_negative(self):
        with pytest.raises(ValidationError):
            WarrantiesPutModel(
                id="warranty1",
                name="Warranty 1",
                type=TypeEnum.SELLER,
                period=-1
            )
