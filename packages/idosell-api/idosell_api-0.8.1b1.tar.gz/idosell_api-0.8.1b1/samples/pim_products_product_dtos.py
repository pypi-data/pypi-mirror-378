from typing import List, Any

from src.idosell._common import BooleanStrShortEnum
from src.idosell.pim.products._common import (
    ProductLongDescriptionsLangDataModel, ProductLongDescriptionsModel
)
from src.idosell.pim.products._common import PriceRoundModeEnum
from src.idosell.pim.products.product._common import (
    AssociatedProductsModel, AvailablePaymentFormsModel, ContextValueEnum, ConverterUnitValueEnum, DispatchSettingsModel, FreeShippingSettingsModel,
    MinQuantityPerOrderModel, ModeEnum, PicturesSettingInputTypeEnum, PriceChangeModeEnum, PriceFormulaModel, ProductAuctionPricesModel, ProductDeliveryTimeChangeModeEnum,
    ProductDeliveryTimeModel, ProductDimensionsModel, ProductNamesLangDataModel, ProductNamesModel, ProductParametersDistinctionChangeModeEnum,
    ProductShopPriceComparisonSitesPricesModel, ProductShopsAttributesModel, ProductSizesModel, ProductStockQuantitiesModel, ProductStocksDataModel,
    ReturnProductSettingsModel, SettingActualizeDelivererModeEnum, SettingCalculateBasePriceSizesEnum, SettingDefaultCategoryModel,
    SettingDefaultSizesGroupModel, SettingModificationTypeEnum, ShippingSettingsModel, ShopsSizeAttributesModel,
    StandardUnitModel, SubscriptionModel, VersionGroupNamesLangDataModel, VersionGroupNamesModel, VersionNamesLangDataModel, VersionNamesModel,
    VersionSettingsCommonModel, ReturnOptionsModel, ProductPriceComparisonSitesPricesModel, ProductComplexNotesEnum,
    ProductDiscountModel, ProductDistinguishedModel, ProductMetaDescriptionsLangDataModel, ProductMetaDescriptionsModel,
    ProductMetaKeywordsLangDataModel, ProductMetaKeywordsModel, ProductMetaTitlesLangDataModel, ProductMetaTitlesModel,
    ProductPromotionModel, ProductSpecialModel, ProductUrlModel, YNSelectedEnum, AttachmentOperationValuesEnum,
    ClearStockQuantitiesModel, PictureSettingsPostModel, PriceComparisonSitesPostModel, ProductDescriptionsLangDataPostModel, ProductDescriptionsModel,
    ProductVersionPostModel, ProductsDeleteModel, ProductsPostModel, ProductsPutModel, ProductNamesInAuctionModel, ProductNamesInPriceComparerModel,
    ProductParamDescriptionsModel, ProductLongDescriptionsInAuctionModel, ProductVersionPutModel, RemoveAllProductsAssignedToMenuModel, VersionParentPutModel,
    VersionParentTypeEnum, ProductPriceVatChangeModeEnum, ProductShopsPricesConfigEnum, ProductPosPricesConfigEnum, ProductTypeEnum,
    ProductAvailabilityManagementTypeEnum, ProducerCodesStandardEnum, SerialNumbersOptionEnum, ProductInExportToStrefaMarekAllegroEnum,
    SettingDeleteIndividualDescriptionsByShopsMaskModel, SettingDeleteIndividualMetaByShopsMaskModel, SettingsPostModel, SettingsPutModel
)
from src.idosell.pim.products.product.facebook import (
    DeleteToFacebookCatalog as PimProductsProductDeleteToFacebookCatalog,
    DeleteToFacebookCatalogPimProductsProductFacebookParamsModel,
    GetToFacebookCatalog as PimProductsProductGetToFacebookCatalog,
    PostToFacebookCatalog as PimProductsProductPostToFacebookCatalog,
    PostToFacebookCatalogPimProductsProductFacebookParamsModel
)
from src.idosell.pim.products.product.product import (
    Delete as PimProductsProductDelete,
    DeletePimProductsProductProductParamsModel,
    Get as PimProductsProductGet,
    Post as PimProductsProductPost,
    PostPimProductsProductProductParamsModel,
    Put as PimProductsProductPut,
    PutPimProductsProductProductParamsModel,
    Search as PimProductsProductSearch,
    SearchPimProductsProductProductParamsModel
)
from src.idosell.pim.products.product.promotion import (
    DeleteProductsToPromotion as PimProductsProductDeleteProductsToPromotion,
    DeleteProductsToPromotionPimProductsProductPromotionParamsModel,
    PostProductsToPromotion as PimProductsProductPostProductsToPromotion,
    PostProductsToPromotionPimProductsProductPromotionParamsModel
)


pim_products_product_delete: List[Any] = [
    PimProductsProductDelete(
        params = DeletePimProductsProductProductParamsModel(
            products = [ProductsDeleteModel(productId = 1, productSizeCodeExternal = 'abcd')])
    ),
    PimProductsProductDeleteToFacebookCatalog(
        params = DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId = 1,
            shopId = 1,
            products = [1]
        )
    ),
    PimProductsProductDeleteProductsToPromotion(
        params = DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId = 1,
            products = [1]
        )
    ),
]

pim_products_product_get: List[Any] = [
    PimProductsProductGetToFacebookCatalog(
        facebookCatalogId = 1,
        shopId = 1
    ),
    PimProductsProductGet(
        productIds = ['1']
    ),
]

pim_products_product_search: List[Any] = [
    PimProductsProductSearch(
        resultsPage = 0,
        resultsLimit = 10,
        params = SearchPimProductsProductProductParamsModel()  # type: ignore
    ),
]

pim_products_product_post: List[Any] = [
    PimProductsProductPostToFacebookCatalog(
        params = PostToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId = 1,
            shopId = 1,
            products = [1]
        )
    ),
    PimProductsProductPost(
        params = PostPimProductsProductProductParamsModel(
            settings = SettingsPostModel(
                settingAddingCategoryAllowed = BooleanStrShortEnum.NO,
                settingAddingSizeAllowed = BooleanStrShortEnum.NO,
                settingAddingProducerAllowed = BooleanStrShortEnum.NO,
                settingAddingSeriesAllowed = BooleanStrShortEnum.NO,
                settingDefaultCategory = SettingDefaultCategoryModel(
                    categoryId = 1,
                    categoryName = 'Default Category'
                ),
                settingDefaultSizesGroup = SettingDefaultSizesGroupModel(
                    sizesGroupId = 1,
                    sizesGroupName = 'Default Sizes'
                ),
                settingsAddingDefaultShopMaskAllowed = BooleanStrShortEnum.NO,
                settingsAddingManuallySelectedShopMaskAllowed = None,
                settingPriceFormat = None
            ),
            picturesSettings = PictureSettingsPostModel(
                picturesSettingInitialUrlPart = 'http://example.com/',
                picturesSettingInputType = PicturesSettingInputTypeEnum.URL,
                picturesSettingOverwrite = BooleanStrShortEnum.YES,
                picturesSettingScaling = BooleanStrShortEnum.YES
            ),
            products = [ProductsPostModel(
                productDisplayedCode = 'test-displayed-code',
                productTaxCode = 'test-tax-code',
                productInWrapper = 1,
                productSellByRetail = 1.0,
                productSellByWholesale = 1.0,
                categoryIdoSellId = 1,
                categoryIdoSellPath = 'test/category/path',
                categoryId = 1,
                categoryName = 'Test Category',
                producerId = 1,
                producerName = 'Test Producer',
                cnTaricCode = 'test-taric',
                countryOfOrigin = 'US',
                unitId = 1,
                seriesId = 1,
                seriesPanelName = 'Test Series',
                sizesGroupId = 1,
                productVat = 23.0,
                productVatFree = BooleanStrShortEnum.NO,
                productPriceComparisonSitesPrices = [ProductPriceComparisonSitesPricesModel(
                    priceComparisonSiteId = 1,
                    productPriceComparisonSitePrice = 100.0
                )],
                productEnableInPos = BooleanStrShortEnum.YES,
                productAdvancePrice = 10.0,
                productNote = 'Test note',
                shopsMask = 1,
                productComplexNotes = ProductComplexNotesEnum.YES,
                productInExportToPriceComparisonSites = YNSelectedEnum.YES,
                productInExportToAmazonMarketplace = YNSelectedEnum.YES,
                productPromotion = ProductPromotionModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productDiscount = ProductDiscountModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productDistinguished = ProductDistinguishedModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productSpecial = ProductSpecialModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productParametersDistinction = [],
                productLongDescriptions = ProductLongDescriptionsModel(
                    productLongDescriptionsLangData = [
                        ProductLongDescriptionsLangDataModel(
                            langId = 'pl',
                            productLongDescription = 'Test long description'
                        )
                    ]
                ),
                productAuctionDescriptionsData = [],
                productMetaTitles = ProductMetaTitlesModel(
                    productMetaTitlesLangData = [
                        ProductMetaTitlesLangDataModel(
                            langId = 'pl',
                            langName = 'Polski',
                            productMetaTitle = 'Test meta title'
                        )
                    ]
                ),
                productMetaDescriptions = ProductMetaDescriptionsModel(
                    productMetaDescriptionsLangData = [
                        ProductMetaDescriptionsLangDataModel(
                            langId = 'pl',
                            langName = 'Polski',
                            productMetaDescription = 'Test meta description'
                        )
                    ]
                ),
                productMetaKeywords = ProductMetaKeywordsModel(
                    productMetaKeywordsLangData = [
                        ProductMetaKeywordsLangDataModel(
                            langId = 'pl',
                            langName = 'Polski',
                            productMetaKeyword = 'test, keyword'
                        )
                    ]
                ),
                productUrl = ProductUrlModel(
                    productUrlsLangData = []
                ),
                priceComparisonSites = [PriceComparisonSitesPostModel(
                    shopId = 1,
                    priceComparisonSiteId = 1,
                )],
                productId = 1,
                productSizeCodeExternal = 'blah',
                priceChangeMode = PriceChangeModeEnum.AMOUNT_SET,
                priceFormula = None,
                productRetailPrice = 1,
                productWholesalePrice = 1,
                productMinimalPrice = 1,
                productAutomaticCalculationPrice = 1,
                productPosPrice = 1,
                productProfitPoints = 1,
                productWeight = 1,
                productInVisible = BooleanStrShortEnum.NO,
                productInPersistent = BooleanStrShortEnum.NO,
                availableProfile = 1,
                productRebate = 1,
                warrantyId = 1,
                productPriority = 1,
                productIcon = 'test-icon.png',
                productWatermarkId = 1,
                productWatermarkUrl = 'https://example.com/blah.png',
                productPictures = [],
                productDescriptionPictures = [],
                associatedProducts = [AssociatedProductsModel(
                    associatedProductId = 1,
                    associatedProductName = 'Recommended product name',
                    associatedProductCode = 'Recommended product code. External system code'
                )],
                productSizes = [ProductSizesModel(
                    sizeId = 'Size identifier',
                    sizePanelName = 'Size name',
                    productWeight = 1,
                    productWeightNet = 1,
                    productRetailPrice = 1,
                    productWholesalePrice = 1,
                    productMinimalPrice = 1,
                    productAutomaticCalculationPrice = 1,
                    productPosPrice = 1,
                    productAuctionPrices = [ProductAuctionPricesModel(
                        productAuctionId = 1,
                        productAuctionSiteId = 1,
                        productAuctionPrice = 1
                    )],
                    productCode = 'External product system code',
                    productInPersistent = BooleanStrShortEnum.NO,
                    productStocksData = ProductStocksDataModel(
                        productStockQuantities = [ProductStockQuantitiesModel(
                            stockId = 1,
                            productSizeQuantity = 1, # TODO can be 0?
                            productSizeQuantityToAdd = 1, # TODO can be 0?
                            productSizeQuantityToSubstract = 1 # TODO can be 0?
                        )]
                    ),
                    shopsSizeAttributes = [ShopsSizeAttributesModel(
                        shopId = 1,
                        productRetailPrice = 1,
                        productWholesalePrice = 1,
                        productMinimalPrice = 1,
                        productAutomaticCalculationPrice = 1
                    )]
                )],
                productShopsAttributes = [ProductShopsAttributesModel(
                    shopId = 1,
                    productShopPriceComparisonSitesPrices = [ProductShopPriceComparisonSitesPricesModel(
                        priceComparisonSiteId = 1,
                        productPriceComparisonSitePercentDiff = 1
                    )]
                )],
                subscription = [SubscriptionModel(
                    shopId = 1,
                    enabled = False,
                    daysInPeriod = [1],
                    unitsNumberRetail = 1,
                    unitsNumberWholesale = 1
                )],
                productNames = ProductNamesModel(
                    productNamesLangData = [ProductNamesLangDataModel(
                        langId = 'pl',
                        productName = 'Product name'
                    )]
                ),
                productDescriptions = ProductDescriptionsModel(
                    productDescriptionsLangData = [ProductDescriptionsLangDataPostModel(
                        langId = 'pl',
                        productDescription = 'Short product description'
                    )]
                ),
                productVersion = ProductVersionPostModel(
                    versionParentId = 1,
                    versionPriority = 1,
                    versionSettings = VersionSettingsCommonModel(
                        versionDisplayAllInShop = BooleanStrShortEnum.NO,
                        versionCommonCode = BooleanStrShortEnum.NO,
                        versionCommonProducer = BooleanStrShortEnum.NO,
                        versionCommonNote = BooleanStrShortEnum.NO,
                        versionCommonWarranty = BooleanStrShortEnum.NO,
                        versionCommonSeries = BooleanStrShortEnum.NO,
                        versionCommonCategory = BooleanStrShortEnum.NO,
                        versionCommonPrice = BooleanStrShortEnum.NO,
                        versionCommonAdvance = BooleanStrShortEnum.NO,
                        versionCommonRebate = BooleanStrShortEnum.NO,
                        versionCommonVat = BooleanStrShortEnum.NO,
                        versionCommonProfitPoints = BooleanStrShortEnum.NO,
                        versionCommonPromotion = BooleanStrShortEnum.NO,
                        versionCommonAssociated = BooleanStrShortEnum.NO,
                        versionCommonVisibility = BooleanStrShortEnum.NO,
                        versionCommonPriority = BooleanStrShortEnum.NO,
                        versionCommonShops = BooleanStrShortEnum.NO,
                        versionCommonSizes = BooleanStrShortEnum.NO,
                        versionCommonWeight = BooleanStrShortEnum.NO,
                        versionCommonDictionary = BooleanStrShortEnum.NO,
                        versionCommonName = BooleanStrShortEnum.NO,
                        versionCommonDescription = BooleanStrShortEnum.NO,
                        versionCommonLongDescription = BooleanStrShortEnum.NO,
                        versionCommonIcon = BooleanStrShortEnum.NO,
                        versionCommonPhotos = BooleanStrShortEnum.NO,
                        versionCommonAvailableProfile = BooleanStrShortEnum.NO,
                        versionCommonComplexNotes = BooleanStrShortEnum.NO,
                        versionCommonSumInBasket = BooleanStrShortEnum.NO,
                        versionCommonAuctionsPrice = BooleanStrShortEnum.NO,
                        versionCommonDiscount = BooleanStrShortEnum.NO,
                        versionCommonDistinguished = BooleanStrShortEnum.NO,
                        versionCommonSpecial = BooleanStrShortEnum.NO,
                        versionCommonTraits = BooleanStrShortEnum.NO,
                        versionCommonPersistent = BooleanStrShortEnum.NO,
                        versionCommonUnit = BooleanStrShortEnum.NO
                    ),
                    versionNames = VersionNamesModel(
                        versionNamesLangData = [VersionNamesLangDataModel(
                            langId = 'pl',
                            versionName = 'Name of the parameter value, e.g. orange, green, red'
                        )]
                    ),
                    versionGroupNames = VersionGroupNamesModel(
                        versionGroupNamesLangData = [VersionGroupNamesLangDataModel(
                            langId = 'pl',
                            versionGroupName = 'Parameter name, e.g. color, width'
                        )]
                    )
                ),
                currencyId = 'currencyId',
                delivererId = 1,
                productParametersDistinctionChangeMode = ProductParametersDistinctionChangeModeEnum.ADD,
                productDeliveryTime = ProductDeliveryTimeModel(
                    productDeliveryTimeChangeMode = ProductDeliveryTimeChangeModeEnum.PRODUCT,
                    productDeliveryTimeValue = 1
                ),
                productSumInBasket = BooleanStrShortEnum.NO,
                dispatchSettings = DispatchSettingsModel(
                    enabled = False,
                    shippingSettings = ShippingSettingsModel(
                        codDisabled = True,
                        dvpOnly = True,
                        atypicalSize = False,
                        insuranceOnly = False,
                        excludeSmileService = True,
                        disallowedCouriers = [1]

                    ),
                    freeShippingSettings = FreeShippingSettingsModel(
                        mode = ModeEnum.NO,
                        availablePaymentForms = AvailablePaymentFormsModel(
                            prepaid = False,
                            cashOnDelivery = True,
                            tradeCredit = False
                        ),
                        availableCouriers = [1],
                        availableRegions = [1]
                    ),
                    returnProductSettings = ReturnProductSettingsModel(
                        returnOptions = ReturnOptionsModel(
                            enabled = False,
                            firm = False,
                            hurt = False,
                            detalist = False
                        ),
                        byOwnService = False,
                        byInPostSzybkieZwrotyByIAI = False
                    )
                ),
                standardUnit = StandardUnitModel(
                    contextValue = ContextValueEnum.CONTEXT_STD_UNIT_WEIGHT,
                    standardUnitValue = 1,
                    converterUnitValue = ConverterUnitValueEnum.VAL0
                ),
                minQuantityPerOrder = MinQuantityPerOrderModel(
                    minQuantityPerOrderRetail = 1,
                    minQuantityPerOrderWholesale = 1
                ),
                productDimensions = ProductDimensionsModel(
                    productWidth = 1,
                    productHeight = 1,
                    productLength = 1
                ),
                responsibleProducerCode = 'responsibleProducerCode',
                responsiblePersonCode = 'responsiblePersonCode'
            )]
        )
    ),
    PimProductsProductPostProductsToPromotion(
        params = PostProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId = 1,
            products = [1]
        )
    )
]

pim_products_product_put: List[Any] = [
    PimProductsProductPut(
        params = PutPimProductsProductProductParamsModel(
            settings = SettingsPutModel(
                settingModificationType = SettingModificationTypeEnum.ALL,
                settingPriceFormat = None,
                settingTextIdSeparator = None,
                settingCalculateBasePriceSizes = SettingCalculateBasePriceSizesEnum.ALL,
                settingAddingCategoryAllowed = BooleanStrShortEnum.YES,
                settingAddingSizeAllowed = BooleanStrShortEnum.YES,
                settingAddingProducerAllowed = BooleanStrShortEnum.YES,
                settingAddingSeriesAllowed = BooleanStrShortEnum.YES,
                settingAddingSizeschartAllowed = BooleanStrShortEnum.NO,
                settingDefaultCategory = SettingDefaultCategoryModel(
                    categoryId = 1,
                    categoryName = 'Default'
                ),
                settingDefaultSizesGroup = SettingDefaultSizesGroupModel(
                    sizesGroupId = 1,
                    sizesGroupName = 'Default Sizes'
                ),
                settingIgnoreRetailPricesInCaseOfPromotion = BooleanStrShortEnum.NO,
                returnPromotionStatus = BooleanStrShortEnum.NO,
                settingsRestoreDeletedProducts = BooleanStrShortEnum.NO,
                settingsAddingDefaultShopMaskAllowed = BooleanStrShortEnum.NO,
                settingsAddingManuallySelectedShopMaskAllowed = None,
                settingAddingSupplierAllowed = BooleanStrShortEnum.NO,
                settingActualizeDelivererMode = SettingActualizeDelivererModeEnum.ALWAYS,
                settingDeleteIndividualDescriptionsByShopsMask = SettingDeleteIndividualDescriptionsByShopsMaskModel(
                    shopsMask = 0
                ),
                settingDeleteIndividualMetaByShopsMask = SettingDeleteIndividualMetaByShopsMaskModel(
                    shopsMask = 0
                ),
                settingsSkipDuplicatedProducers = False
            ),
            picturesSettings = None,
            products = [ProductsPutModel(
                productDisplayedCode = 'test-put-code',
                productTaxCode = 'test-tax-code',
                productInWrapper = 1,
                productSellByRetail = 1.0,
                productSellByWholesale = 1.0,
                categoryIdoSellId = 1,
                categoryIdoSellPath = 'test/category/path',
                categoryId = 1,
                categoryName = 'Test Category',
                producerId = 1,
                producerName = 'Test Producer',
                cnTaricCode = 'test-taric',
                countryOfOrigin = 'US',
                unitId = 1,
                seriesId = 1,
                seriesPanelName = 'Test Series',
                sizesGroupId = 1,
                productVat = 23.0,
                productVatFree = BooleanStrShortEnum.NO,
                productPriceComparisonSitesPrices = [],
                productEnableInPos = BooleanStrShortEnum.YES,
                productAdvancePrice = 10.0,
                productNote = 'Test note',
                shopsMask = 1,
                productComplexNotes = ProductComplexNotesEnum.YES,
                productInExportToPriceComparisonSites = YNSelectedEnum.YES,
                productInExportToAmazonMarketplace = YNSelectedEnum.YES,
                productPromotion = ProductPromotionModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productDiscount = ProductDiscountModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productDistinguished = ProductDistinguishedModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productSpecial = ProductSpecialModel(
                    promoteInEnabled = BooleanStrShortEnum.NO,
                    promoteItemNormalPrice = 100.0,
                    promoteItemWholesaleNormalPrice = 90.0,
                    promoteItemEndingDate = '2025-12-31'
                ),
                productParametersDistinction = [],
                productLongDescriptions = ProductLongDescriptionsModel(
                    productLongDescriptionsLangData = []
                ),
                productAuctionDescriptionsData = [],
                productMetaTitles = ProductMetaTitlesModel(
                    productMetaTitlesLangData = []
                ),
                productMetaDescriptions = ProductMetaDescriptionsModel(
                    productMetaDescriptionsLangData = []
                ),
                productMetaKeywords = ProductMetaKeywordsModel(
                    productMetaKeywordsLangData = []
                ),
                productUrl = ProductUrlModel(
                    productUrlsLangData = []
                ),
                priceComparisonSites = [],
                productId = 1,
                productIndex = '1',
                productSizeCodeExternal = 'test-external-code',
                productSizeCodeProducer = 'test-producer-code',
                sizesGroupName = 'Default Sizes',
                priceChangeMode = PriceChangeModeEnum.AMOUNT_SET,
                productRetailPrice = 100.0,
                productRetailPriceNet = 80.0,
                productWholesalePrice = 90.0,
                productWholesalePriceNet = 72.0,
                productMinimalPrice = 80.0,
                productMinimalPriceNet = 64.0,
                productAutomaticCalculationPrice = 70.0,
                productAutomaticCalculationPriceNet = 56.0,
                productPosPrice = 60.0,
                productPosPriceNet = 48.0,
                # productProfitPoints = 0.0,
                productWeight = 1000,
                productInVisible = BooleanStrShortEnum.NO,
                # productInPersistent = BooleanStrShortEnum.NO,
                availableProfile = 1,
                productRebate = 1,
                warrantyId = 1,
                productPriority = 1,
                productIconLink = 'test-icon.png',
                productPictures = [],
                # productDescriptionPictures = [],
                associatedProducts = [],
                productSizes = [],
                productShopsAttributes = [],
                subscription = [],
                productNames = ProductNamesModel(
                    productNamesLangData = []
                ),
                productNamesInAuction = ProductNamesInAuctionModel(
                    productNamesInAuctionLangData = []
                ),
                productNamesInPriceComparer = ProductNamesInPriceComparerModel(
                    productNamesInPriceComparerLangData = []
                ),
                productParamDescriptions = ProductParamDescriptionsModel(
                    productParamDescriptionsLangData = []
                ),
                productLongDescriptionsInAuction = ProductLongDescriptionsInAuctionModel(
                    langId = 'pl',
                    productLongDescriptionsInAuction = '...'
                ),
                productVersion = ProductVersionPutModel(
                    versionParent = VersionParentPutModel(
                        versionParentId = '1',
                        versionParentType = VersionParentTypeEnum.ID
                    ),
                    versionPriority = 1,
                    versionSettings = VersionSettingsCommonModel(
                        versionDisplayAllInShop = BooleanStrShortEnum.NO,
                        versionCommonCode = BooleanStrShortEnum.NO,
                        versionCommonProducer = BooleanStrShortEnum.NO,
                        versionCommonNote = BooleanStrShortEnum.NO,
                        versionCommonWarranty = BooleanStrShortEnum.NO,
                        versionCommonSeries = BooleanStrShortEnum.NO,
                        versionCommonCategory = BooleanStrShortEnum.NO,
                        versionCommonPrice = BooleanStrShortEnum.NO,
                        versionCommonAdvance = BooleanStrShortEnum.NO,
                        versionCommonRebate = BooleanStrShortEnum.NO,
                        versionCommonVat = BooleanStrShortEnum.NO,
                        versionCommonProfitPoints = BooleanStrShortEnum.NO,
                        versionCommonPromotion = BooleanStrShortEnum.NO,
                        versionCommonAssociated = BooleanStrShortEnum.NO,
                        versionCommonVisibility = BooleanStrShortEnum.NO,
                        versionCommonPriority = BooleanStrShortEnum.NO,
                        versionCommonShops = BooleanStrShortEnum.NO,
                        versionCommonSizes = BooleanStrShortEnum.NO,
                        versionCommonWeight = BooleanStrShortEnum.NO,
                        versionCommonDictionary = BooleanStrShortEnum.NO,
                        versionCommonName = BooleanStrShortEnum.NO,
                        versionCommonDescription = BooleanStrShortEnum.NO,
                        versionCommonLongDescription = BooleanStrShortEnum.NO,
                        versionCommonIcon = BooleanStrShortEnum.NO,
                        versionCommonPhotos = BooleanStrShortEnum.NO,
                        versionCommonAvailableProfile = BooleanStrShortEnum.NO,
                        versionCommonComplexNotes = BooleanStrShortEnum.NO,
                        versionCommonSumInBasket = BooleanStrShortEnum.NO,
                        versionCommonAuctionsPrice = BooleanStrShortEnum.NO,
                        versionCommonDiscount = BooleanStrShortEnum.NO,
                        versionCommonDistinguished = BooleanStrShortEnum.NO,
                        versionCommonSpecial = BooleanStrShortEnum.NO,
                        versionCommonTraits = BooleanStrShortEnum.NO,
                        versionCommonPersistent = BooleanStrShortEnum.NO,
                        versionCommonUnit = BooleanStrShortEnum.NO
                    ),
                    versionNames = VersionNamesModel(
                        versionNamesLangData = []
                    ),
                    versionGroupNames = VersionGroupNamesModel(
                        versionGroupNamesLangData = []
                    )
                ),
                currencyId = 'PLN',
                delivererId = 1,
                delivererName = 'Test Deliverer',
                productCurrenciesShops = [],
                productParametersDistinctionChangeMode = ProductParametersDistinctionChangeModeEnum.ADD,
                productDeliveryTime = ProductDeliveryTimeModel(
                    productDeliveryTimeChangeMode = ProductDeliveryTimeChangeModeEnum.PRODUCT,
                    productDeliveryTimeValue = 1
                ),
                productParameters = [],
                clearProductParameters = False,
                changeParametersDistinction = [],
                productPriceVatChangeMode = ProductPriceVatChangeModeEnum.CHANGE_GROSS,
                productMenuItems = [],
                removeAllProductsAssignedToMenu = RemoveAllProductsAssignedToMenuModel(
                    shopId = 1,
                    menuId = 1
                ),
                productSumInBasket = BooleanStrShortEnum.NO,
                productShopsPricesConfig = ProductShopsPricesConfigEnum.SAME_PRICES,
                productPosPricesConfig = ProductPosPricesConfigEnum.POS_EQUALS_RETAIL,
                productType = ProductTypeEnum.PRODUCT_ITEM,
                priceRoundMode = PriceRoundModeEnum.NONE,
                productAvailabilityManagementType = ProductAvailabilityManagementTypeEnum.STOCK,
                removeChooseSizesValues = [],
                removeAllUnusedProductSizes = False,
                producerCodesStandard = ProducerCodesStandardEnum.AUTO,
                javaScriptInTheItemCard = [],
                serialNumbersOption = SerialNumbersOptionEnum.NA,
                dispatchSettings = DispatchSettingsModel(
                    enabled = False,
                    shippingSettings = ShippingSettingsModel(
                        codDisabled = False,
                        dvpOnly = False,
                        atypicalSize = False,
                        insuranceOnly = False,
                        excludeSmileService = False,
                        disallowedCouriers = []
                    ),
                    freeShippingSettings = FreeShippingSettingsModel(
                        mode = ModeEnum.NO,
                        availablePaymentForms = AvailablePaymentFormsModel(
                            prepaid = False,
                            cashOnDelivery = True,
                            tradeCredit = False
                        ),
                        availableCouriers = [],
                        availableRegions = []
                    ),
                    returnProductSettings = ReturnProductSettingsModel(
                        returnOptions = ReturnOptionsModel(
                            enabled = False,
                            firm = False,
                            hurt = False,
                            detalist = False
                        ),
                        byOwnService = False,
                        byInPostSzybkieZwrotyByIAI = False
                    )
                ),
                standardUnit = StandardUnitModel(
                    contextValue = ContextValueEnum.CONTEXT_STD_UNIT_WEIGHT,
                    standardUnitValue = 1,
                    converterUnitValue = ConverterUnitValueEnum.VAL0
                ),
                minQuantityPerOrder = MinQuantityPerOrderModel(
                    minQuantityPerOrderRetail = 1,
                    minQuantityPerOrderWholesale = 1
                ),
                dynamicPricingEnabled = 'false',
                productDimensions = ProductDimensionsModel(
                    productWidth = 10,
                    productHeight = 10,
                    productLength = 10
                ),
                clearStockQuantities = ClearStockQuantitiesModel(
                    clearAllStockQuantities = False,
                    stocksListToClear = [1]
                ),
                productSuggestedPrice = 0.0,
                productSuggestedPriceNet = 0.0,
                productStrikethroughRetailPrice = 0.0,
                productStrikethroughRetailPriceNet = 0.0,
                productStrikethroughWholesalePrice = 0.0,
                productStrikethroughWholesalePriceNet = 0.0,
                productHotspotsZones = [],
                priceInPoints = [],
                loyaltyPoints = [],
                exportToAmazonExportAllSizes = BooleanStrShortEnum.NO,
                exportAmazonUpdateStocks = BooleanStrShortEnum.NO,
                productInExportToStrefaMarekAllegro = ProductInExportToStrefaMarekAllegroEnum.NO,
                productInExportToSmaPreset = 0,
                warrantyName = 'Test Warranty',
                priceFormula = PriceFormulaModel(
                    priceFormulaParameters = 'Formula parameters for calculating price',
                    priceFormulaFunction = 'Formula function for calculating price'
                ),
                sizeChartId = 1,
                sizeChartName = 'Test Size Chart',
                productPriorityInMenuNodes = [],
                productAuctionIconLink = 'test-auction-icon.png',
                productGroupIconLink = 'test-group-icon.png',
                productPicturesReplace = [],
                parametersConfigurable = [],
                attachments = [],
                removeAttachments = [],
                virtualAttachmentsToRemove = False,
                virtualAttachments = [],
                attachmentOperationValues = AttachmentOperationValuesEnum.ADD,
                responsibleProducerCode = 'RP001',
                responsiblePersonCode = '12345'
            )]
        )
    )
]
