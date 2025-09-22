from typing import List, Any

from src.idosell._common import BooleanStrShortEnum
from src.idosell.pim.products._common import (
    IdentTypeEnum, ViewEnum, SortModeGridEnum, MetaSettingsEnum,
    MetaRobotsSettingsIndexEnum, MetaRobotsSettingsFollowEnum,
    ProducerPostModel, ProducerPutModel, ProductsBundleDeleteProductsModel, ProductIdentTypeCodeExistanceEnum, ProductIdentBundlesModel,
    ProductsCollectionsDeleteProductsModel, ProductsCollectionsPostProductsModel, ProductSizesPostModel, RateEnum,
    ItemsParametersModel, SettingsParametersPutModel, ImagesSettingsModel, SourceTypeEnum, ProductsBundlesPostModel,
    ProductSizesBundlesModel, AddTypeEnum, ProductsBundlesPostProductsModel, ProductSizesBundlesCollectionsModel,
    ProductsPutProductsQuantityModel, ProductPutRenewModel, CategoriesModel, OperationEnum, CollectionIdentModel,
    ProductIdentModel, ProductsDescriptionsModel, GroupsPutSettingsModel, ProductsInOrderModel,
    DisplayInPanelEnum, DisplayOnPageEnum, ProductsImagesSettingsModel, ProductsImagesSourceTypeEnum,
    ProductsImages, ProductImagesModel, MarketingZonesPromotionModel, NewPriceSettingsModel, TypeEnum,
    ModeEnum, BasePricingEnum, CalculationMethodEnum, PromotionElementsModel, ElementTypeEnum,
    ProductsMarketingModel, IdentModel, AssignmentModeEnum, MarketingZonesModel, BooleanStrLongEnum,
    ShopsPutZonesModel, ProductAttachmentPutModel, ErrorsModel, ProductsOmnibusModel, SizesOmnibusModel,
    OmnibusPricesModel, OmnibusPriceManagementEnum, ShopsModel, IconsInputTypeParametersEnum,
    QuestionsPutModel, ProductIdentQuestionsModel, ProductIdentTypeQuestionsEnum,
    ItemTextIdsParametersModel, NamesParametersModel, DescriptionsParametersModel, SearchDescriptionParametersModel,
    CardIconsParametersModel, LinkIconsParametersModel, ContextIdParametersModel, ContextIdParametersEnum,
    ProductsCollectionsPutProductsModel, ProductsCollectionsPutRenewModel, ProductIdentCollectionsModel,
    ProductDescriptionsLangDataModel, ProductDescriptionSectionsModel, ProductAuctionDescriptionsDataModel, DescriptionSectionsModel, SectionModel,
    ProductIconsModel, ProductIconTypeEnum,
    SeriesPutModel, PriceRoundModeEnum, LanguagesConfigurationsModel, ProductsListImagesConfigurationModel,
    ProductCardImagesConfigurationModel, ShopsConfigurationsModel, GraphicTypeEnum,
    FilterActiveModel, FilterDisplayEnum, FilterValueSortEnum
)
from src.idosell.pim.products.brands import (
    Delete as PimProductsBrandsDelete,
    DeletePimProductsBrandsParamsModel,
    GetFilter as PimProductsBrandsGetFilter, Get as PimProductsBrandsGet,
    Post as PimProductsBrandsPost, PutFilter as PimProductsBrandsPutFilter, Put as PimProductsBrandsPut,
    PostPimProductsBrandsParamsModel,
    PutFilterPimProductsBrandsParamsModel, PutPimProductsBrandsParamsModel
)
from src.idosell.pim.products.bundles import (
    DeleteProducts as PimProductsBundlesDeleteProducts,
    DeleteProductsPimProductsBundlesParamsModel,
    PostBundles as PimProductsBundlesPostBundles, PostProducts as PimProductsBundlesPostProducts,
    PutProductsQuantity as PimProductsBundlesPutProductsQuantity, PutRenew as PimProductsBundlesPutRenew,
    PostBundlesPimProductsBundlesParamsModel, PostProductsPimProductsBundlesParamsModel, PutProductsQuantityPimProductsBundlesParamsModel, PutRenewPimProductsBundlesParamsModel
)
from src.idosell.pim.products.categories import (
    Get as PimProductsCategoriesGet, SearchIdosell as PimProductsCategoriesSearchIdosell,
    Put as PimProductsCategoriesPut, SearchIdosellPimProductsCategoriesParamsModel,
    PutPimProductsCategoriesParamsModel
)
from src.idosell.pim.products.collections import (
    DeleteProducts as PimProductsCollectionsDeleteProducts,
    DeleteProductsPimProductsCollectionsParamsModel,
    PostProducts as PimProductsCollectionsPostProducts,
    PutProducts as PimProductsCollectionsPutProducts, PutRenew as PimProductsCollectionsPutRenew,
    PostProductsPimProductsCollectionsParamsModel, PutProductsPimProductsCollectionsParamsModel,
    PutRenewPimProductsCollectionsParamsModel
)
from src.idosell.pim.products.descriptions import Get as PimProductsDescriptionsGet, Put as PimProductsDescriptionsPut, PutPimProductsDescriptionsParamsModel
from src.idosell.pim.products.groups import (
    PutMainProduct as PimProductsGroupsPutMainProduct, PutOrder as PimProductsGroupsPutOrder, PutSettings as PimProductsGroupsPutSettings,
    PutMainProductPimProductsGroupsParamsModel, PutOrderPimProductsGroupsParamsModel, PutSettingsPimProductsGroupsParamsModel
)
from src.idosell.pim.products.images import (
    Delete as PimProductsImagesDelete, DeletePimProductsImagesParamsModel,
    Put as PimProductsImagesPut, PutPimProductsImagesParamsModel
)
from src.idosell.pim.products.marketing import (
    GetAllFacebookCatalogIds as PimProductsMarketingGetAllFacebookCatalogIds, GetPromotion as PimProductsMarketingGetPromotion, GetZones as PimProductsMarketingGetZones,
    PutPromotion as PimProductsMarketingPutPromotion, PutZones as PimProductsMarketingPutZones, PutPromotionPimProductsMarketingParamsModel, PutZonesPimProductsMarketingParamsModel
)
from src.idosell.pim.products.miscs import (
    GetProductsAuctions as PimProductsMiscsGetProductsAuctions, GetProductsCodeExistence as PimProductsMiscsGetProductsCodeExistence,
    GetProductsIdBySizecode as PimProductsMiscsGetProductsIdBySizecode, GetProductsReservations as PimProductsMiscsGetProductsReservations,
    GetProductsSKUbyBarcode as PimProductsMiscsGetProductsSKUbyBarcode,
    PutProductsAttachments as PimProductsMiscsPutProductsAttachments,
    SearchProductsDeliveryTime as PimProductsMiscsSearchProductsDeliveryTime, SearchProductsDeliveryTimePimProductsMiscsParamsModel,
    PutProductsAttachmentsPimProductsMiscsParamsModel
)
from src.idosell.pim.products.parameters import (
    Delete as PimProductsParametersDelete,
    DeletePimProductsParametersParamsModel,
    Put as PimProductsParametersPut,
    Search as PimProductsParametersSearch,
    SearchPimProductsParametersParamsModel
)
from src.idosell.pim.products.omnibus import GetPrices as PimProductsOmnibusGetPrices, PutPrices as PimProductsOmnibusPutPrices, PutPricesPimProductsOmnibusParamsModel
from src.idosell.pim.products.opinions import (
    Delete as PimProductsOpinionsDelete,
    DeletePimProductsOpinionsParamsModel,
    Get as PimProductsOpinionsGet, GetRate as PimProductsOpinionsGetRate,
    # Post as PimProductsOpinionsPost,
    Put as PimProductsOpinionsPut, PutPimProductsOpinionsParamsModel
)
from src.idosell.pim.products.questions import (
    Get as PimProductsQuestionsGet,
    Put as PimProductsQuestionsPut,
    PutPimProductsQuestionsParamsModel
)
from src.idosell.pim.products.series import (
    Delete as PimProductsSeriesDelete,
    DeletePimProductsSeriesParamsModel,
    GetFilter as PimProductsSeriesGetFilter, Get as PimProductsSeriesGet,
    Put as PimProductsSeriesPut,
    PutPimProductsSeriesParamsModel
)
from src.idosell.pim.products.sizes import (
    Delete as PimProductsSizesDelete,
    Get as PimProductsSizesGet,
    Put as PimProductsSizesPut,
    DeleteModeSizesEnum,
    DeletePimProductsSizesParamsModel,
    SizesParamsDeleteModel,
    PutModeSizesEnum,
    SizesProductsDataPutModel,
    IndexesDataSizesPutModel,
    SizeDataModel
)
from src.idosell.pim.products.stocks import (
    ErrorModel,
    Get as PimProductsStocksGet,
    IdentStocksModel,
    Put as PimProductsStocksPut, PutPimProductsStocksParamsModel, PutPimProductsStocksSettingsModel,
    ProductsStocksModel, SizesStocksModel, QuantityStocksModel, StocksModel, QuantityOperationModel, OperationStocksEnum
)
from src.idosell.pim.products.strikethrough import (
    GetPrices as PimProductsStrikethroughGetPrices,
    PutPrices as PimProductsStrikethroughPutPrices, PutPricesPimProductsStrikethroughParamsModel, PutPricesPimProductsStrikethroughSettingsModel,
    CalculateBasePriceSizesStrikethroughEnum, PriceModeStrikethroughEnum, ProductsStrikethroughModel, SizesStrikethroughModel, StpSettingsModel, ShopsStrikethroughModel,
    PriceChangeModeStrikethroughEnum, PriceChangeBasevalueStrikethroughEnum
)
from src.idosell.pim.products.supplier import (
    PutCode as PimProductsSupplierPutCode, PutProductData as PimProductsSupplierPutProductData,
    PutCodePimProductsSupplierParamsModel, PutProductDataPimProductsSupplierParamsModel, ProductsSupplierPutCodeModel, ProductsSupplierPutProductDataModel
)
from src.idosell.pim.products.synchronization import (
    PostFile as PimSynchronizationPostFile, PostFilePimProductsSynchronizationParamsModel,
    PutFinishUpload as PimSynchronizationPutFinishUpload, PutFinishUploadPimProductsSynchronizationParamsModel
)


pim_products_delete: List[Any] = [
    PimProductsBrandsDelete(
        params = DeletePimProductsBrandsParamsModel(ids = [1])
    ),
    PimProductsBundlesDeleteProducts(
        params = [DeleteProductsPimProductsBundlesParamsModel(
            products = [ProductsBundleDeleteProductsModel(
                productIdent = ProductIdentBundlesModel(
                    productIdentType = IdentTypeEnum.ID,
                    identValue = '1'
                )
            )],
            bundleIdent = ProductIdentBundlesModel(
                productIdentType = IdentTypeEnum.ID,
                identValue = '1'
            )
        )]
    ),
    PimProductsCollectionsDeleteProducts(
        params = [DeleteProductsPimProductsCollectionsParamsModel(
            products = [ProductsCollectionsDeleteProductsModel(productId= 1)],
            collectionId = 1
        )]
    ),
    PimProductsImagesDelete(
        params = [DeletePimProductsImagesParamsModel(
            deleteAll = False,
            productId = 1,
            shopId = 1,
            productImagesId = ['1']
        )]
    ),
    PimProductsOpinionsDelete(
        params = DeletePimProductsOpinionsParamsModel(id = 1)
    ),
    PimProductsParametersDelete(
        params = DeletePimProductsParametersParamsModel(ids = [1])
    ),
    PimProductsSeriesDelete(
        params = DeletePimProductsSeriesParamsModel(ids = [1])
    ),
    PimProductsSizesDelete(
        mode = DeleteModeSizesEnum.DELETE_BY_SIZE,
        params = DeletePimProductsSizesParamsModel(
            productId = 1,
            sizes = [SizesParamsDeleteModel(sizeId = '1', sizePanelName = 'M')]
        ),
        deleteSizesIndexesData = ['1']
    ),
]


pim_products_get: List[Any] = [
    PimProductsBrandsGetFilter(
        shopId = 1,
        languageId = 'pol',
        producerId = 1
    ),
    PimProductsBrandsGet(), # type: ignore
    PimProductsCategoriesGet(), # type: ignore
    PimProductsDescriptionsGet(
        type = IdentTypeEnum.ID,
        ids = [1]
    ), # type: ignore
    PimProductsMarketingGetAllFacebookCatalogIds(
        shopId = 1
    ),
    PimProductsMarketingGetPromotion(), # type: ignore
    PimProductsMarketingGetZones(), # type: ignore
    PimProductsMiscsGetProductsAuctions(), # type: ignore
    PimProductsMiscsGetProductsCodeExistence(
        identType = ProductIdentTypeCodeExistanceEnum.ID
    ), # type: ignore
    PimProductsMiscsGetProductsIdBySizecode(), # type: ignore
    PimProductsMiscsGetProductsReservations(), # type: ignore
    PimProductsMiscsGetProductsSKUbyBarcode(), # type: ignore
    PimProductsOmnibusGetPrices(), # type: ignore
    PimProductsOpinionsGet(), # type: ignore
    PimProductsOpinionsGetRate(
        id = 1,
        operation = RateEnum.POSITIVE
    ),
    PimProductsQuestionsGet(), # type: ignore
    PimProductsSeriesGetFilter(
        shopId = 1,
        languageId = 'pol',
        serieId = 1
    ),
    PimProductsSeriesGet(), # type: ignore
    PimProductsSizesGet(), # type: ignore
    PimProductsStocksGet(), # type: ignore
    PimProductsStrikethroughGetPrices(), # type: ignore
]

pim_products_post: List[Any] = [
    PimProductsBrandsPost(
        params = PostPimProductsBrandsParamsModel(producers=[ProducerPostModel(
            nameInPanel="Test Producer",
            imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.BASE64),
            languagesConfigurations=[LanguagesConfigurationsModel(
                productsListImagesConfiguration=ProductsListImagesConfigurationModel(
                    graphicType=GraphicTypeEnum.IMG,
                    singleGraphic='test',
                    pcGraphic='test',
                    tabletGraphic='test',
                    phoneGraphic='test'
                ),
                productCardImagesConfiguration=ProductCardImagesConfigurationModel(
                    graphicType=GraphicTypeEnum.IMG,
                    singleGraphic='test',
                    pcGraphic='test',
                    tabletGraphic='test',
                    phoneGraphic='test'
                ),
                languageId='pol',
                shopsConfigurations=[ShopsConfigurationsModel(
                    name='Test Shop',
                    descriptionTop='Test description top',
                    descriptionBottom='Test description bottom',
                    headerName='Test Header',
                    shopId=1,
                    view=ViewEnum.DEFAULT,
                    enableSort=True,
                    enableChangeDisplayCount=True,
                    numberOfProductsGrid=16,
                    sortModeGrid=SortModeGridEnum.D_RELEVANCE,
                    metaSettings=MetaSettingsEnum.AUTO,
                    metaTitle=None,
                    metaDescription=None,
                    metaKeywords=None,
                    metaRobotsSettingsIndex=MetaRobotsSettingsIndexEnum.AUTO,
                    metaRobotsSettingsFollow=MetaRobotsSettingsFollowEnum.AUTO
                )]
            )]
        )])
    ),
    PimProductsBundlesPostBundles(
        params = PostBundlesPimProductsBundlesParamsModel(
            products = [ProductsBundlesPostModel(
                productIdent = ProductIdentBundlesModel(
                    productIdentType = IdentTypeEnum.ID,
                    identValue = '1'
                ),
                productSizes = ProductSizesBundlesModel(
                    size = 'M',
                    sizePanelName = 'M'
                ),
                addType = AddTypeEnum.ALLSIZES,
                quantity = 1.0
            )]
        )
    ),
    PimProductsBundlesPostProducts(
        params = PostProductsPimProductsBundlesParamsModel(
            products = [ProductsBundlesPostProductsModel(
                productIdent = ProductIdentBundlesModel(
                    productIdentType = IdentTypeEnum.ID,
                    identValue = '1'
                ),
                productSizes = ProductSizesBundlesCollectionsModel(
                    size = 'M',
                    sizePanelName = 'M'
                ),
                addType = AddTypeEnum.ALLSIZES,
                quantity = 1.0
            )],
            bundleIdent = ProductIdentBundlesModel(
                productIdentType = IdentTypeEnum.ID,
                identValue = '1'
            )
    )
),
    PimProductsCollectionsPostProducts(
        params = PostProductsPimProductsCollectionsParamsModel(
            products = [ProductsCollectionsPostProductsModel(
                productId = 1,
                productSizes = [ProductSizesPostModel(size = 'M')],
                addType = AddTypeEnum.ALLSIZES,
                quantity = 1
            )],
            collectionId = 1
        )
),
    PimSynchronizationPostFile(
        params = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId = 1,
            packageId = 1,
            fileType = "full",
            md5Content = "d41d8cd98f00b204e9800998ecf8427e",
            fileContent = "dGVzdA==",
            offerName = "test_offer"
        )
    ),
]

pim_products_put: List[Any] = [
    PimProductsBrandsPutFilter(
        params = PutFilterPimProductsBrandsParamsModel(
            shopId = 1,
            languageId = "pol",
            producerId = 1,
            filterForNodeIsDefault = BooleanStrShortEnum.NO,
            filtersActive = [FilterActiveModel(
                filterId = "test_filter",
                filterName = "Test Filter",
                filterDisplay = FilterDisplayEnum.NAME,
                filterValueSort = FilterValueSortEnum.YES,
                filterDefaultEnabled = BooleanStrShortEnum.YES
            )]
        )
    ),
    PimProductsBrandsPut(
        params = PutPimProductsBrandsParamsModel(producers=[ProducerPutModel(
            id=1,
            nameInPanel="Test Producer",
            imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.BASE64),
            languagesConfigurations=[LanguagesConfigurationsModel(
                productsListImagesConfiguration=ProductsListImagesConfigurationModel(
                    graphicType=GraphicTypeEnum.IMG,
                    singleGraphic='test',
                    pcGraphic='test',
                    tabletGraphic='test',
                    phoneGraphic='test'
                ),
                productCardImagesConfiguration=ProductCardImagesConfigurationModel(
                    graphicType=GraphicTypeEnum.IMG,
                    singleGraphic='test',
                    pcGraphic='test',
                    tabletGraphic='test',
                    phoneGraphic='test'
                ),
                languageId='pol',
                shopsConfigurations=[ShopsConfigurationsModel(
                    name='Test Shop',
                    descriptionTop='Test description top',
                    descriptionBottom='Test description bottom',
                    headerName='Test Header',
                    shopId=1,
                    view=ViewEnum.DEFAULT,
                    enableSort=True,
                    enableChangeDisplayCount=True,
                    numberOfProductsGrid=16,
                    sortModeGrid=SortModeGridEnum.D_RELEVANCE,
                    metaSettings=MetaSettingsEnum.AUTO,
                    metaTitle=None,
                    metaDescription=None,
                    metaKeywords=None,
                    metaRobotsSettingsIndex=MetaRobotsSettingsIndexEnum.AUTO,
                    metaRobotsSettingsFollow=MetaRobotsSettingsFollowEnum.AUTO
                )]
            )]
        )])
    ),
    PimProductsBundlesPutProductsQuantity(
        params = PutProductsQuantityPimProductsBundlesParamsModel(
            products=[ProductsPutProductsQuantityModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue='1'
                ),
                quantity=1.0
            )],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue='1'
            )
        )
    ),
    PimProductsBundlesPutRenew(
        params = PutRenewPimProductsBundlesParamsModel(
            products=[ProductPutRenewModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue='1'
                ),
                productSizes=[ProductSizesBundlesCollectionsModel(
                    size='M',
                    sizePanelName='M'
                )],
                addType=AddTypeEnum.ALLSIZES,
                quantity=1
            )],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue='1'
            )
        )
    ),
    PimProductsCategoriesPut(
        params = PutPimProductsCategoriesParamsModel(
            categories=[CategoriesModel(
                id=2,
                parent_id=1,
                priority=1,
                operation=OperationEnum.ADD
            )]
        )
    ),
    PimProductsCollectionsPutProducts(
        params = PutProductsPimProductsCollectionsParamsModel(
            products = [
                ProductsCollectionsPutProductsModel(
                    productId = 1,
                    quantity = 5
                )
            ],
            collectionId = 1
        )
    ),
    PimProductsCollectionsPutRenew(
        params = PutRenewPimProductsCollectionsParamsModel(
            products = [
                ProductsCollectionsPutRenewModel(
                    productIdent = ProductIdentCollectionsModel(
                        productId = '1',
                        productIdentType = IdentTypeEnum.ID
                    ),
                    productSizes = [
                        ProductSizesBundlesCollectionsModel(
                            size = 'M',
                            sizePanelName = 'M'
                        )
                    ],
                    addType = AddTypeEnum.ALLSIZES,
                    quantity = 5
                )
            ],
            collectionIdent = CollectionIdentModel(
                collectionId = '1',
                collectionIdentType = IdentTypeEnum.ID
            )
        )
    ),
    PimProductsDescriptionsPut(
        params = PutPimProductsDescriptionsParamsModel(
            products = [ProductsDescriptionsModel(
                productIdent = ProductIdentModel(
                    identValue = '1',
                    productIdentType = IdentTypeEnum.ID
                ),
                productDescriptionsLangData = [
                    ProductDescriptionsLangDataModel(
                        langId = 'pol',
                        shopId = 1,
                        productName = 'Test Product',
                        productAuctionName = 'Test Auction Product',
                        productPriceComparerName = 'Test Price Comparer',
                        productDescription = 'Test short description',
                        productLongDescription = 'Test long description',
                        productDescriptionSections = ProductDescriptionSectionsModel(
                            descriptionSections = [
                                DescriptionSectionsModel(
                                    section_1=SectionModel(type=TypeEnum.TEXT, content="Test section content"),
                                    section_2=SectionModel(type=TypeEnum.TEXT, content="Test section 2 content")
                                )
                            ]
                        ),
                        productAuctionLongDescription = 'Test auction long description',
                        productMetaTitle = 'Test Meta Title',
                        productMetaDescription = 'Test Meta Description',
                        productMetaKeywords = 'test, product, keywords'
                    )
                ],
                productAuctionDescriptionsData = [
                    ProductAuctionDescriptionsDataModel(
                        productAuctionId = 'test_auction_id',
                        productAuctionSiteId = 'test_site_id',
                        productAuctionName = 'Test Auction Product',
                        productAuctionAdditionalName = 'Test Additional Name',
                        productAuctionDescription = 'Test auction description'
                    )
                ]
            )]
        )
    ),
    PimProductsGroupsPutMainProduct(
        params = PutMainProductPimProductsGroupsParamsModel(
            groups = [ProductIdentModel(
                identValue = '1',
                productIdentType = IdentTypeEnum.ID
            )]
        )
    ),
    PimProductsGroupsPutOrder(
        params = PutOrderPimProductsGroupsParamsModel(
            groups = [ProductsInOrderModel(
                productIdent = ProductIdentModel(
                    identValue = '1',
                    productIdentType = IdentTypeEnum.ID
                ),
                priority = 1
            )]
        )
    ),
    PimProductsGroupsPutSettings(
        params = PutSettingsPimProductsGroupsParamsModel(
            groups = [GroupsPutSettingsModel(
                productIdent = ProductIdentModel(
                    identValue = '1',
                    productIdentType = IdentTypeEnum.ID
                ),
                displayInPanel = DisplayInPanelEnum.ALL,
                displayOnPage = DisplayOnPageEnum.ALL,
                specifiedProductIdent = ProductIdentModel(
                    identValue = '1',
                    productIdentType = IdentTypeEnum.ID
                )
            )]
        )
    ),
    PimProductsImagesPut(
        params = PutPimProductsImagesParamsModel(
            productsImagesSettings=ProductsImagesSettingsModel(
                productsImagesSourceType=ProductsImagesSourceTypeEnum.BASE64,
                productsImagesApplyMacro=False
            ),
            productsImages=[
                ProductsImages(
                    productIdent=ProductIdentModel(
                        identValue='1',
                        productIdentType=IdentTypeEnum.ID
                    ),
                    shopId=1,
                    otherShopsForPic=[],
                    productImages=[
                        ProductImagesModel(
                            productImageSource='base64encodedimage',
                            productImageNumber=1,
                            productImagePriority=1,
                            deleteProductImage=False
                        )
                    ],
                    productIcons=[
                        ProductIconsModel(
                            productIconSource='test-icon.png',
                            deleteProductIcon=False,
                            productIconType=ProductIconTypeEnum.SHOP
                        )
                    ],
                    productImagesSettings=ProductsImagesSettingsModel(
                        productsImagesSourceType=ProductsImagesSourceTypeEnum.BASE64,
                        productsImagesApplyMacro=False
                    )
                )
            ]
        )
    ),
    PimProductsMarketingPutPromotion(
        params = PutPromotionPimProductsMarketingParamsModel(
            promotionId='1',
            promotionName='Test Promotion',
            shopsIds=[1],
            marketingZones=MarketingZonesPromotionModel(
                promotion=BooleanStrShortEnum.YES,
                discount=BooleanStrShortEnum.NO,
                distinguished=BooleanStrShortEnum.NO,
                special=BooleanStrShortEnum.NO,
                new=BooleanStrShortEnum.NO
            ),
            newPriceSettings=NewPriceSettingsModel(
                type=TypeEnum.TEXT,
                discountValue=10.0,
                currencyId='PLN',
                mode=ModeEnum.PERCENT_DIFF,
                endValue='0.00'
            ),
            startDate='2025-01-01 00:00:00',
            endDate='2025-12-31 23:59:59',
            changeProductsToVisibleWhileStarting=BooleanStrShortEnum.NO,
            removeProductsAfterStockLevelRunsDown=BooleanStrShortEnum.NO,
            removeProductsAfterOwnStockLevelRunsDown=BooleanStrShortEnum.NO,
            reduceBasingPrice=BasePricingEnum.GROSS,
            calculationMethod=CalculationMethodEnum.SUM,
            removeAllPromotionElements=BooleanStrShortEnum.NO,
            promotionElements=[
                PromotionElementsModel(
                    elementType=ElementTypeEnum.PRODUCT,
                    elementId='1'
                )
            ]
        )
    ),
    PimProductsMarketingPutZones(
        params = PutZonesPimProductsMarketingParamsModel(
            products=[
                ProductsMarketingModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.ID,
                        value='1'
                    ),
                    assignment_mode=AssignmentModeEnum.AUTO,
                    marketing_zones=MarketingZonesModel(
                        promotion=BooleanStrLongEnum.YES,
                        discount=BooleanStrLongEnum.NO,
                        distinguished=BooleanStrLongEnum.NO,
                        special=BooleanStrLongEnum.NO
                    )
                )
            ],
            assignment_mode=AssignmentModeEnum.AUTO,
            marketing_zones=MarketingZonesModel(
                promotion=BooleanStrLongEnum.YES,
                discount=BooleanStrLongEnum.NO,
                distinguished=BooleanStrLongEnum.NO,
                special=BooleanStrLongEnum.NO
            ),
            shops=[
                ShopsPutZonesModel(
                    shop_id=1,
                    assignment_mode=AssignmentModeEnum.AUTO,
                    marketing_zones=MarketingZonesModel(
                        promotion=BooleanStrLongEnum.YES,
                        discount=BooleanStrLongEnum.NO,
                        distinguished=BooleanStrLongEnum.NO,
                        special=BooleanStrLongEnum.NO
                    )
                )
            ]
        )
    ),
    PimProductsMiscsPutProductsAttachments(
        params = PutProductsAttachmentsPimProductsMiscsParamsModel(
            productsAttachments=[
                ProductAttachmentPutModel(
                    productIdent=ProductIdentModel(
                        identValue='1',
                        productIdentType=IdentTypeEnum.ID
                    ),
                    attachments=[],
                    virtualAttachments=[],
                    errors=ErrorsModel(
                        faultCode=0,
                        faultString=''
                    ),
                    attachmentsErrorsOccurred=False,
                    virtualAttachmentsErrorsOccurred=False
                )
            ]
        )
    ),
    PimProductsOmnibusPutPrices(
        params = PutPricesPimProductsOmnibusParamsModel(
            products=[
                ProductsOmnibusModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.ID,
                        value='1'
                    ),
                    sizes=[
                        SizesOmnibusModel(
                            ident=IdentModel(
                                type=IdentTypeEnum.ID,
                                value='1'
                            ),
                            omnibusPrices=OmnibusPricesModel(
                                omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                                omnibusPriceRetail=100.0,
                                omnibusPriceWholesale=90.0
                            ),
                            shops=[
                                ShopsModel(
                                    shopId=1,
                                    omnibusPrices=OmnibusPricesModel(
                                        omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                                        omnibusPriceRetail=100.0,
                                        omnibusPriceWholesale=90.0
                                    )
                                )
                            ]
                        )
                    ],
                    omnibusPrices=OmnibusPricesModel(
                        omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                        omnibusPriceRetail=100.0,
                        omnibusPriceWholesale=90.0
                    ),
                    shops=[
                        ShopsModel(
                            shopId=1,
                            omnibusPrices=OmnibusPricesModel(
                                omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                                omnibusPriceRetail=100.0,
                                omnibusPriceWholesale=90.0
                            )
                        )
                    ]
                )
            ]
        )
    ),
    PimProductsOpinionsPut(
        params = PutPimProductsOpinionsParamsModel(
            id=1,
            confirmed=BooleanStrShortEnum.YES,
            rating=5,
            content='Great product!',
            language='pol',
            shopAnswer='Thank you!',
            picture='',
            opinionConfirmedByPurchase=True
        )
    ),
    PimProductsParametersPut(
        items = [ItemsParametersModel(
            id=1,
            item_text_ids=[
                ItemTextIdsParametersModel(
                    lang_id='pol',
                    value='test_item_text_id'
                )
            ],
            names=[
                NamesParametersModel(
                    lang_id='pol',
                    value='Test Parameter'
                )
            ],
            descriptions=[
                DescriptionsParametersModel(
                    lang_id='pol',
                    value='Test parameter description'
                )
            ],
            search_description=[
                SearchDescriptionParametersModel(
                    lang_id='pol',
                    value='Test search description',
                    shop_id=1
                )
            ],
            card_icons=[
                CardIconsParametersModel(
                    lang_id='pol',
                    value='test_icon',
                    shop_id=1
                )
            ],
            link_icons=[
                LinkIconsParametersModel(
                    lang_id='pol',
                    value='test_link_icon',
                    shop_id=1
                )
            ],
            context_id=ContextIdParametersModel(
                context_id=ContextIdParametersEnum.CONTEXT_COLOR,
                context_value_id='red'
            ),
            context_value_id='red'
        )],
        settings = SettingsParametersPutModel(
            icons_input_type=IconsInputTypeParametersEnum.BASE64
        )
    ),
    PimProductsQuestionsPut(
        params = PutPimProductsQuestionsParamsModel(
            questions=[
                QuestionsPutModel(
                    id=1,
                    lang='pol',
                    question='base64question',
                    answer='base64answer',
                    dateAdd='2025-01-01',
                    host='example.com',
                    author='Test User',
                    productIdent=ProductIdentQuestionsModel(
                        productId='1',
                        productIdentType=ProductIdentTypeQuestionsEnum.ID
                    ),
                    visible=BooleanStrShortEnum.YES,
                    priority=1,
                    confirmed=BooleanStrShortEnum.YES,
                    shopId=1,
                    answerDate='2025-01-01',
                    answerAuthor='Test Admin'
                )
            ]
        )
    ),
    PimProductsSeriesPut(
        params = PutPimProductsSeriesParamsModel(
            series=[SeriesPutModel(
                id=1,
                nameInPanel="Test Series",
                shopsConfigurations=[]
            )]
        )
    ),
    PimProductsSizesPut(
        mode = PutModeSizesEnum.ADD,
        sizesProductsData = [SizesProductsDataPutModel(
            productId=1,
            sizes=[]
        )],
        indexesData = [IndexesDataSizesPutModel(
            sizeIndex='1',
            sizeData=SizeDataModel(
                productWeight=1,
                codeProducer='test',
                productSizeCodeExternal='test',
                sitesData=[]
            )
        )]
    ),
    PimProductsStocksPut(
        params = PutPimProductsStocksParamsModel(products=[ProductsStocksModel(
            ident=IdentStocksModel(identType=IdentTypeEnum.ID, identValue='1'),
            sizes=[SizesStocksModel(
                ident=IdentStocksModel(identType=IdentTypeEnum.ID, identValue='1'),
                quantity=QuantityStocksModel(stocks=[StocksModel(
                    stock_id=1,
                    quantity_operation=QuantityOperationModel(operation=OperationStocksEnum.SET, quantity=10.0),
                    location_id=1,
                    location_text_id='test',
                    location_code='test',
                    additionalLocations=[]
                )])
            )],
            settings=PutPimProductsStocksSettingsModel(
                productIndent=IdentStocksModel(identType=IdentTypeEnum.ID, identValue='1'),
                sizesIndent=IdentStocksModel(identType=IdentTypeEnum.ID, identValue='1')
            ),
            error=ErrorModel(faultCode=0, faultString='')
        )]),
        settings = PutPimProductsStocksSettingsModel(
            productIndent = IdentStocksModel(identType = IdentTypeEnum.ID, identValue = '1'),
            sizesIndent = IdentStocksModel(identType = IdentTypeEnum.ID, identValue = '1')
        )
    ),
    PimProductsStrikethroughPutPrices(
        params = PutPricesPimProductsStrikethroughParamsModel(products=[ProductsStrikethroughModel(
            ident=IdentModel(type=IdentTypeEnum.ID, value='1'),
            sizes=[SizesStrikethroughModel(
                ident=IdentModel(type=IdentTypeEnum.ID, value='1'),
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=9.0
                ),
                shops=[ShopsStrikethroughModel(
                    shop_id=1,
                    stp_settings=StpSettingsModel(
                        price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                        price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                        retail_price_change_value=10.0,
                        wholesale_price_change_value=9.0
                    )
                )]
            )],
            stp_settings=StpSettingsModel(
                price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                retail_price_change_value=10.0,
                wholesale_price_change_value=9.0
            ),
            shops=[ShopsStrikethroughModel(
                shop_id=1,
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=9.0
                )
            )]
        )]),
        settings = PutPricesPimProductsStrikethroughSettingsModel(
            calculate_base_price_sizes = CalculateBasePriceSizesStrikethroughEnum.ALL,
            price_mode = PriceModeStrikethroughEnum.GROSS,
            price_round_mode = PriceRoundModeEnum.NONE
        )
    ),
    PimProductsSupplierPutCode(
        params = PutCodePimProductsSupplierParamsModel(products=[ProductsSupplierPutCodeModel(
            productId=1,
            productDeliverers=[]
        )])
    ),
    PimProductsSupplierPutProductData(
        params = PutProductDataPimProductsSupplierParamsModel(products=[ProductsSupplierPutProductDataModel(
            productId=1,
            productDeliverers=[]
        )])
    ),
    PimSynchronizationPutFinishUpload(
        params = PutFinishUploadPimProductsSynchronizationParamsModel(
            synchronizationId=1,
            packageId=1,
            filesInPackage=1,
            verifyFiles=False
        )
    ),
]

pim_products_search: List[Any] = [
    PimProductsCategoriesSearchIdosell(
        params = SearchIdosellPimProductsCategoriesParamsModel(
            languagesIds = None,
            categoriesIdoSellIds = None,
            categoriesIdoSellNames = None,
            categoriesIdoSellPaths = None
        ),
        resultsPage = 1,
        resultsLimit = 1
    ),
    PimProductsMiscsSearchProductsDeliveryTime(
        params = SearchProductsDeliveryTimePimProductsMiscsParamsModel(
            stockId = None,
            isCollectionInPerson = None,
            products = None
        )
    ),
    PimProductsParametersSearch(
        params = SearchPimProductsParametersParamsModel(
            ids = None,
            textIds = None,
            languagesIds = None,
            parameterValueIds = None
        ),
        resultsPage = 1,
        resultsLimit = 1
    ),
]
