from typing import List, Any

from src.idosell.pim._common import (
    EntityTypeEnum, LangDataModel, MenuListPostModel, SettingsModel, MenuListPutModel,
    MenuListPutSortModel, SettingsPutSortModel, EntitiesResponsibilityPostModel, EntitiesResponsibilityPutModel,
    ItemTypeEnum, HrefTargetEnum, DefaultViewEnum, ActionEnum, DisplayAllTypeEnum,
    MetaRobotsIndexEnum, MetaRobotsFollowEnum, GfxModel, FormatEnum,
    WarrantiesPostModel, TypeEnum, ShopnameWarrantiesModel, LanguagesWarrantiesModel, DescriptionWarrantiesModel,
    MenuFiltersActivePutFilterModel, MenuFilterDisplayEnum, MenuFilterValueSortEnum,
    SizeChartsPutModel, LanguagesDataModel, ColumnsModel, SizesModel, DescriptionsModel, DisplayModeEnum,
    SizesPutModel, LangDataSizesModel, OperationSizesEnum,
    LangDataWarrantiesModel, LangWarrantiesModel, IconSettingsModel, FormatWarrantiesEnum, DataTypeEnum, WarrantiesPutModel,
    SortLangDataModelModel, DisplayLimitLangDataModel, ViewEnum, SortByEnum, SortOrderEnum, MenuListDeleteModel
)

from src.idosell._common import BooleanStrShortEnum
from src.idosell.pim.products._common import GraphicTypeEnum

from src.idosell.pim.menu import (
    Delete as PimMenuDelete, GetFilter as PimMenuGetFilter, Get as PimMenuGet,
    Post as PimMenuPost,
    PutFilter as PimMenuPutFilter, Put as PimMenuPut, PutFilterPimMenuParamsModel, PutSort as PimMenuPutSort
)
from src.idosell.pim.responsibility import (
    DeleteEntities as PimResponsibilityDeleteEntities, GetEntities as PimResponsibilityGetEntities,
    PostEntities as PimResponsibilityPostEntities, PostEntitiesPimResponsabilityParamsModel,
    PutEntities as PimResponsibilityPutEntities, PutEntitiesPimResponsabilityParamsModel
)
from src.idosell.pim.sizecharts import (
    Delete as PimSizechartsDelete, DeletePimSizechartsParamsModel,
    Get as PimSizechartsGet,
    Put as PimSizechartsPut,
    PutPimSizechartsParamsModel
)
from src.idosell.pim.sizes import (
    Get as PimSizesGet,
    Put as PimSizesPut,
    PutPimSizesParamsModel
)
from src.idosell.pim.warranties import (
    Delete as PimWarrantiesDelete, DeletePimWarrantiesParamsModel,
    GetCountTotal as PimWarrantiesGetCountTotal, Get as PimWarrantiesGet,
    Post as PimWarrantiesPost, PostPimWarrantiesParamsModel,
    PutLanguageData as PimWarrantiesPutLanguageData, Put as PimWarrantiesPut, PutLanguageDataPimWarrantiesParamsModel, PutPimWarrantiesParamsModel
)

pim_delete: List[Any] = [
    PimMenuDelete(menu_list=[MenuListDeleteModel(
        shop_id=1,
        menu_id=1,
        item_id=1,
        item_textid='blah'
    )], settings=SettingsModel(textid_separator='')), # type: ignore
    PimResponsibilityDeleteEntities(code=['1'], type=""), # type: ignore
    PimSizechartsDelete(
        params = DeletePimSizechartsParamsModel(ids = [1])
    ),
    PimWarrantiesDelete(
        params = DeletePimWarrantiesParamsModel(warranty_ids = ['1'])
    ),
]

pim_get: List[Any] = [
    PimMenuGetFilter(), # type: ignore
    PimMenuGet(), # type: ignore
    PimResponsibilityGetEntities(), # type: ignore
    PimSizechartsGet(), # type: ignore
    PimSizesGet(), # type: ignore
    PimWarrantiesGetCountTotal(), # type: ignore
    PimWarrantiesGet() # type: ignore
]

pim_post: List[Any] = [
    PimMenuPost(
        menu_list = [MenuListPostModel(
            shop_id = 1,
            menu_id = 1,
            parent_id = 'blah',
            parent_textid = 'blah',
            lang_data = [LangDataModel(
                lang_id="pl",
                name="Test Menu",
                priority=1,
                description="Test description",
                description_bottom="Test description bottom",
                link="",
                item_type=ItemTypeEnum.PRODUCTS,
                meta_title="Test Meta Title",
                meta_description="Test Meta Description",
                meta_keywords="test keywords",
                url="https://example.com",
                href_target=HrefTargetEnum.BLANK,
                sort=[SortLangDataModelModel(view=ViewEnum.NORMAL, sort_by=SortByEnum.NAME, sort_order=SortOrderEnum.ASC)],
                display_limit=[DisplayLimitLangDataModel(view=ViewEnum.NORMAL, limit=10)],
                default_view=DefaultViewEnum.NORMAL,
                headline_name="",
                expand=BooleanStrShortEnum.NO,
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
                gfx_nav=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active_desktop=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active_tablet=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active_mobile=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_inactive_desktop=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_inactive_tablet=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_inactive_mobile=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_onmouseover=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_omo_desktop=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_omo_tablet=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_omo_mobile=GfxModel(base64="test", format=FormatEnum.PNG),
                canonical_to_parent=BooleanStrShortEnum.NO,
                meta_robots_index=MetaRobotsIndexEnum.DEFAULT,
                meta_robots_follow=MetaRobotsFollowEnum.DEFAULT
            )]
        )],
        settings = SettingsModel(textid_separator = '')
    ),
    PimResponsibilityPostEntities(
        params = PostEntitiesPimResponsabilityParamsModel(
            entities = [EntitiesResponsibilityPostModel(
                id = 1,
                code = "TEST_PRODUCER",
                name = "Test Producer",
                mail = "test@example.com",
                street = "Test Street",
                number = "123",
                subnumber = None,
                zipcode = "00-000",
                city = "Test City",
                country = "PL",
                phone = None,
                description = None,
                url = None
            )],
            type = EntityTypeEnum.PRODUCER
        )
    ),
    PimWarrantiesPost(
        params = PostPimWarrantiesParamsModel(
            warranties = [
                WarrantiesPostModel(
                    name = "Test Warranty",
                    type = TypeEnum.SELLER,
                    period = 12,
                    shopname = ShopnameWarrantiesModel(
                        languages = [
                            LanguagesWarrantiesModel(
                                language_id = "pl",
                                language_name = "Polski",
                                value = "Gwarancja testowa"
                            )
                        ]
                    ),
                    description = DescriptionWarrantiesModel(
                        languages = [
                            LanguagesWarrantiesModel(
                                language_id = "pl",
                                language_name = "Polski",
                                value = "Opis gwarancji testowej"
                            )
                        ]
                    )
                )
            ]
        )
    )
]

pim_put: List[Any] = [
    PimMenuPutFilter(
        params = PutFilterPimMenuParamsModel(
            shopId=1,
            languageId="pl",
            productMenuTreeId=1,
            productMenuNodeId=1,
            filterForMenuNodeIsDefault=BooleanStrShortEnum.YES,
            menuFiltersActive=MenuFiltersActivePutFilterModel(
                menuFilterId="1",
                menuFilterName="Test Filter",
                menuFilterDisplay=MenuFilterDisplayEnum.NAME,
                menuFilterValueSort=MenuFilterValueSortEnum.Y,
                menuFilterDefaultEnabled=BooleanStrShortEnum.YES
            )
        )
    ),
    PimMenuPut(
        menu_list = [MenuListPutModel(
            shop_id=1,
            menu_id=1,
            item_id="1",
            item_textid="test",
            lang_data=[LangDataModel(
                lang_id="pl",
                name="Test Menu",
                priority=1,
                description="Test description",
                description_bottom="Test description bottom",
                link="",
                item_type=ItemTypeEnum.PRODUCTS,
                meta_title="Test Meta Title",
                meta_description="Test Meta Description",
                meta_keywords="test keywords",
                url="https://example.com",
                href_target=HrefTargetEnum.BLANK,
                sort=[SortLangDataModelModel(view=ViewEnum.NORMAL, sort_by=SortByEnum.NAME, sort_order=SortOrderEnum.ASC)],
                display_limit=[DisplayLimitLangDataModel(view=ViewEnum.NORMAL, limit=10)],
                default_view=DefaultViewEnum.NORMAL,
                headline_name="",
                expand=BooleanStrShortEnum.NO,
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
                gfx_nav=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active_desktop=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active_tablet=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_active_mobile=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_inactive_desktop=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_inactive_tablet=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_inactive_mobile=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_onmouseover=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_omo_desktop=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_omo_tablet=GfxModel(base64="test", format=FormatEnum.PNG),
                gfx_omo_mobile=GfxModel(base64="test", format=FormatEnum.PNG),
                canonical_to_parent=BooleanStrShortEnum.NO,
                meta_robots_index=MetaRobotsIndexEnum.DEFAULT,
                meta_robots_follow=MetaRobotsFollowEnum.DEFAULT
            )]
        )],
        settings = SettingsModel(textid_separator="")
    ),
    PimMenuPutSort(
        menu_list = MenuListPutSortModel(
            shop_id=1,
            menu_id=1,
            lang_id="pl",
            parent_id=1,
            parent_textid="test",
            recursive=BooleanStrShortEnum.YES
        ),
        settings = SettingsPutSortModel(textid_separator="")
    ),
    PimResponsibilityPutEntities(
        params = PutEntitiesPimResponsabilityParamsModel(
            entities = [EntitiesResponsibilityPutModel(
                id = 1,
                code = "TEST_PRODUCER",
                name = "Test Producer",
                mail = "test@example.com",
                street = "Test Street",
                number = "123",
                subnumber = None,
                zipcode = "00-000",
                city = "Test City",
                country = "PL",
                phone = None,
                description = None,
                url = None
            )],
            type = EntityTypeEnum.PRODUCER
        )
    ),
    PimSizechartsPut(
        params = PutPimSizechartsParamsModel(
            sizeCharts = [SizeChartsPutModel(
                id = 1,
                nameInPanel = "Test Size Chart",
                displayMode = DisplayModeEnum.ALL,
                languagesData = [LanguagesDataModel(
                    language = "pl",
                    columns = [ColumnsModel(
                        columnNumber = 1,
                        columnTitle = "Size"
                    )],
                    sizes = [SizesModel(
                        sizeId = "S",
                        priority = 1,
                        descriptions = [DescriptionsModel(
                            columnNumber = 1,
                            value = "Small"
                        )]
                    )]
                )]
            )]
        )
    ),
    PimSizesPut(
        params = PutPimSizesParamsModel(
            sizes = [SizesPutModel(
                faultCode = 0,
                faultString = "",
                group_id = 1,
                id = "S",
                name = "Small",
                description = "Small size",
                operation = OperationSizesEnum.ADD,
                lang_data = [LangDataSizesModel(
                    lang_id = "pl",
                    name = "Mały"
                )]
            )]
        )
    ),
    PimWarrantiesPutLanguageData(
        params = PutLanguageDataPimWarrantiesParamsModel(
            lang_data = LangDataWarrantiesModel(
                warranty_id = "1",
                lang = [LangWarrantiesModel(
                    lang_id = "pl",
                    name = "Test Warranty",
                    icon = "test",
                    icon_settings = IconSettingsModel(
                        format = FormatWarrantiesEnum.PNG,
                        data_type = DataTypeEnum.BASE64
                    ),
                    description = "Test description"
                )]
            )
        )
    ),
    PimWarrantiesPut(
        params = PutPimWarrantiesParamsModel(
            warranties = [WarrantiesPutModel(
                id = "1",
                name = "Test Warranty",
                type = TypeEnum.SELLER,
                period = 12
            )]
        )
    ),
]
