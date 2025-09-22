from enum import IntEnum, StrEnum
from typing import List
from pydantic import BaseModel, Field, StrictInt, model_validator

from src.idosell._common import BooleanStrLongEnum, BooleanStrShortEnum
from src.idosell.pim.products._common import (
    AttachmentFileTypeEnum, AttachmentNameModel, DocumentTypesModel, PriceRoundModeEnum, ProductLongDescriptionsModel,
    ProductAuctionDescriptionsDataModel, VirtualAttachmentsBaseModel
)


# --- Enums
class AttachmentOperationValuesEnum(StrEnum):
    ADD = 'add'
    EDIT = 'edit'
    REMOVE = 'remove'

class ContextValueEnum(StrEnum):
    CONTEXT_STD_UNIT_WEIGHT = 'CONTEXT_STD_UNIT_WEIGHT' # #!WagaTowaruWGramach!#,
    CONTEXT_STD_UNIT_WEIGHT_SI = 'CONTEXT_STD_UNIT_WEIGHT_SI' # Product weight in kilograms
    CONTEXT_STD_UNIT_VOLUME = 'CONTEXT_STD_UNIT_VOLUME' # A product's value in milliliters
    CONTEXT_STD_UNIT_VOLUME_SI = 'CONTEXT_STD_UNIT_VOLUME_SI' # A product's value in liters
    CONTEXT_STD_UNIT_LENGTH = 'CONTEXT_STD_UNIT_LENGTH' # Length of product in meters
    CONTEXT_STD_UNIT_AREA_M2 = 'CONTEXT_STD_UNIT_AREA_M2' # Area of product in square meters
    CONTEXT_STD_UNIT_VOLUME_M3 = 'CONTEXT_STD_UNIT_VOLUME_M3' # The volume of products in cubic meters
    CONTEXT_STD_UNIT_QUANTITY_PACKAGE = 'CONTEXT_STD_UNIT_QUANTITY_PACKAGE' # Number of pieces per pack for standard unit

class ConverterUnitValueEnum(StrEnum):
    VAL0 = '0' # default (taken from the category),
    VAL1 = '1' # price per gram/milliliter/meter
    VAL10 = '10' # price per 10 grams/10 milliliters/10 meters
    VAL100 = '100' # price per 100 grams/100 milliliters/100 meters
    VAL1000 = '1000' # price per liter/kilogram/kilometer

class ModeEnum(StrEnum):
    NO = 'no'
    ONLYPRODUCT = 'onlyProduct'
    WHOLEBASKET = 'wholeBasket'

class ProductInExportToStrefaMarekAllegroEnum(StrEnum):
    NO = 'no' # product invisible in the export to Strefa Marek Allegro
    YES = 'yes' # product visible in the export to Strefa Marek Allegro

class ProductAvailabilityManagementTypeEnum(StrEnum):
    STOCK = 'stock' # by means of stock management tools
    MANUAL = 'manual' # manually.

class PicturesSettingDeleteIconEnum(StrEnum):
    AUCTIONS = 'auctions'
    DEFAULT = 'default'
    VERSIONS = 'versions'

class PicturesSettingCreateIconFromPictureEnum(StrEnum):
    AUCTIONS = 'auctions'
    DEFAULT = 'default'
    VERSIONS = 'versions'

class PicturesSettingRestoreOriginalIconsEnum(StrEnum):
    ALL = 'all'
    AUCTIONS = 'auctions'
    DEFAULT = 'default'
    VERSIONS = 'versions'

class PicturesSettingDeleteOriginalIconsEnum(StrEnum):
    ALL = 'all'
    AUCTIONS = 'auctions'
    DEFAULT = 'default'
    VERSIONS = 'versions'

class PicturesSettingInputTypeEnum(StrEnum):
    BASE64 = 'base64'
    URL = 'url'

class PriceChangeModeEnum(StrEnum):
    AMOUNT_SET = 'amount_set' # sets product prices to desired value (default mode)
    AMOUNT_DIFF = 'amount_diff' # sets sum difference between prices set (adds or subtracts entered sum from the current price)
    PERCENT_DIFF = 'percent_diff' # sets percentage difference between prices set (adds or subtracts entered percent from the current price)

class ProductDeliveryTimeChangeModeEnum(StrEnum):
    PRODUCT = 'product' # sets own product delivery time
    DELIVERER = 'deliverer' # sets product delivery time exactly the same as deliverer's

class ProductParametersDistinctionChangeModeEnum(StrEnum):
    ADD = 'add' # adds properties to already existent ones
    DELETE = 'delete' # removes properties of already existent ones
    DELETE_GROUP = 'delete_group' # removes properties from selected group
    REPLACE = 'replace' # overwrites properties already existent with new ones (default mode)

class ProducerCodesStandardEnum(StrEnum):
    AUTO = 'auto' # Choose automatically
    GTIN14 = 'GTIN14' # GTIN-14
    GTIN13 = 'GTIN13' # GTIN-13 (EAN-13)
    ISBN13 ='ISBN13' # GTIN-13 (ISBN-13)
    GTIN12 = 'GTIN12' # GTIN-12 (UPC-A)
    ISBN10 = 'ISBN10' #  ISBN-10
    GTIN8 = 'GTIN8' # GTIN-8 (EAN-8)
    UPCE = 'UPCE' # UPC-E
    MPN ='MPN' # MPN
    OTHER = 'other' # Other

class ProductComplexNotesEnum(IntEnum):
    NO = 0
    YES = 1

class ProductPosPricesConfigEnum(StrEnum):
    POS_EQUALS_RETAIL = 'pos_equals_retail' # sets POS price the same as retail price. Possible to set only if the "shops_prices_config" parameter is set to jest same_prices or there is only one shop in panel
    POS_NOTEQUALS_RETAIL = 'pos_notequals_retail' # Price for POS different than retail price
    NOT_AVAILABLE_IN_POS = 'not_available_in_pos' # Product not available for POS sales
    SIZES_POS_PRICE_AS_BASE_PRICE = 'sizes_pos_price_as_base_price' # Remove prices for sizes and set a sale price which equals a basic price

class ProductTypeEnum(StrEnum):
    PRODUCT_ITEM  = 'product_item' # Goods
    PRODUCT_FREE = 'product_free' # Free product
    PRODUCT_PACKAGING = 'product_packaging' # packaging
    PRODUCT_BUNDLE = 'product_bundle' # set
    PRODUCT_COLLECTION = 'product_collection' # collection
    PRODUCT_SERVICE = 'product_service' # service
    PRODUCT_VIRTUAL = 'product_virtual' # virtual product
    PRODUCT_CONFIGURABLE = 'product_configurable' # configurable product

class ProductShopsPricesConfigEnum(StrEnum):
    SAME_PRICES = 'same_prices' # prices in each shop are the same
    DIFFERENT_PRICES = 'different_prices' # prices in each shop are different

class ProductPriceVatChangeModeEnum(StrEnum):
    CHANGE_GROSS = 'change_gross' # changes the product gross price, leaving the net price unchanged
    CHANGE_NET = 'change_net' #- changes the net price, leaving the gross price unchanged (default mode)

class SerialNumbersOptionEnum(StrEnum):
    NA = 'na' # not used
    OPTIONAL = 'optional' # Optional
    REQUIRED = 'required' # required

class SettingActualizeDelivererModeEnum(StrEnum):
    ALWAYS = 'always' # (default value). - update in any case
    IFNECESSARY = 'ifNecessary' # update when no supplier is assigned to the product
    NONE = 'none' # supplier update disabled

class SettingCalculateBasePriceSizesEnum(StrEnum):
    ALL = 'all' # Product price calculated basing on prices of all sizes
    AVAILABLE = 'available' # Product price calculated basing on prices of sizes with stock levels

class SettingModificationTypeEnum(StrEnum):
    ALL = 'all' # (default value). - allows adding new products. If the product of entered ID or external product system code cannot be found in system, the product will be added as a new one
    EDIT = 'edit' # doesn't allow adding new products. In this mode only editing the already existing products is possible. If the product of entered ID or external product system code cannot be found in shop, gate will return error and the product will not be added to shop
    ADD = 'add' # In this mode you can only add products

class YNSelectedEnum(StrEnum):
    YES = 'y' # Visible
    SELECTED = 'selected' # yes (selected)
    NO = 'n' # invisible

class ProductMenuOperationEnum(StrEnum):
    ADD_PRODUCT = 'add_product' # assigns a product to the menu element
    DELETE_PRODUCT = 'delete_product' # removes a product from the menu element

class ProductParameterDescriptionTypeEnum(StrEnum):
    DISTINCTION = 'distinction' # Set as distinguished on product card, list of products (distinguished)
    PROJECTOR_HIDE = 'projector_hide' # Set as hidden on list of parameters on product card
    GROUP_DISTINCTION = 'group_distinction' # Set as parameter differentiating products in group (nieaktywne)
    AUCTION_TEMPLATE_HIDE = 'auction_template_hide' # Hidden for a variable [iai:product_parameters] in auction templates

class ProductParameterOperationEnum(StrEnum):
    ADD_PARAMETER = 'add_parameter' # assigning element to product
    DELETE_PARAMETER = 'delete_parameter' # removing element from product

class VersionParentTypeEnum(StrEnum):
    ID = 'id'
    CODEEXTERN = 'codeExtern'
    CODEPRODUCER = 'codeProducer'

class AttachmentEnableEnum(StrEnum):
    ALL = 'all'
    ONLY_LOGGED = 'only_logged'
    ORDERED = 'ordered'
    WHOLESALER = 'wholesaler'
    WHOLESALER_OR_ORDERED = 'wholesaler_or_ordered'
    WHOLESALER_AND_ORDERED ='wholesaler_and_ordered'

class PriceConfigurableTypeEnum(StrEnum):
    DISABLE = 'disable' # Deletion,
    INPUT = 'input' # Text field,
    RADIO = 'radio' # Single-choice field,
    CHECKBOX = 'checkbox' # Checkbox type multiple choice list,
    SELECT = 'select' # Drop-down single choice list.

class ModifierTypeEnum(StrEnum):
    AMOUNT = 'amount' # in value,
    PERCENT = 'percent' # percentage

class LoyaltyPointsTypeEnum(StrEnum):
    AWARDCLIENT = 'awardClient'
    CHARGECLIENT = 'chargeClient'
    BOTH = 'both'

class LoyaltyPointsClientsTypeEnum(StrEnum):
    BOTH = 'both'
    RETAILERS = 'retailers'
    WHOLESALERS = 'wholesalers'

class LoyaltyPointsOperationEnum(StrEnum):
    AWARDCLIENT = 'awardClient'
    CHARGECLIENT = 'chargeClient'
    BOTH = 'both'

class PriceInPointsClientsEnum(StrEnum):
    RETAILERS = 'retailers' # Prices will be changed for retail customers,
    WHOLESALERS = 'wholesalers' # Prices will be changed for wholesale customers,
    BOTH = 'both' # Prices will be changed for both retail and wholesale customers,
    NOBODY = 'nobody' # This option is available only for setting determining, which customers can buy for points. Using this value turns off possibility of granting points or buying for points for both retail and wholesale customers.

class PriceInPointsOperationEnum(StrEnum):
    CLIENTS_COST = 'clients_cost' # Clients who are allowed to buy selected products for points,
    CLIENTS_AWARD = 'clients_award' # Clients can be awarded with points for buying selected products,
    COUNT_COST = 'count_cost' # Number of points for which the selected products will be sold,
    COUNT_AWARD = 'count_award' # Number of points clients will be rewarded for buying selected products.

class ProductDateModeSearchEnum(StrEnum):
    ADDED = 'added' # #!dataDodaniaProduktu!#,
    FINISHED= 'finished' #date of running out of product,
    RESUMED= 'resumed' #date of resuming product,
    MODIFIED= 'modified' #date of last modification of product,
    QUANTITY_CHANGED= 'quantity_changed' #date of last product stock quantity modification,
    PRICE_CHANGED= 'price_changed' #date of last price change,
    MODIFIED_AND_QUANTITY_CHANGED= 'modified_and_quantity_changed' #date of last modification and stock quantity change.

class ReturnElementsSearchEnum(StrEnum):
    LANG_DATA = 'lang_data'
    ADDING_TIME = 'adding_time'
    DELETED = 'deleted'
    CODE = 'code'
    NOTE = 'note'
    TAXCODE = 'taxcode'
    INWRAPPER = 'inwrapper'
    SELLBY_RETAIL = 'sellby_retail'
    SELLBY_WHOLESALE = 'sellby_wholesale'
    PRODUCER_ID = 'producer_id'
    PRODUCER_NAME = 'producer_name'
    IAICATEGORYID = 'iaiCategoryId'
    IAICATEGORYNAME = 'iaiCategoryName'
    IAICATEGORYPATH = 'iaiCategoryPath'
    CATEGORY_ID = 'category_id'
    CATEGORY_NAME = 'category_name'
    SIZE_GROUP_ID = 'size_group_id'
    MODIFICATION_TIME = 'modification_time'
    CURRENCY = 'currency'
    CURRENCY_SHOP = 'currency_shop'
    BESTSELLER = 'bestseller'
    NEW_PRODUCT = 'new_product'
    RETAIL_PRICE = 'retail_price'
    WHOLESALE_PRICE = 'wholesale_price'
    MINIMAL_PRICE = 'minimal_price'
    AUTOMATIC_CALCULATION_PRICE = 'automatic_calculation_price'
    POS_PRICE = 'pos_price'
    STRIKETHROUGH_RETAIL_PRICE = 'strikethrough_retail_price'
    STRIKETHROUGH_WHOLESALE_PRICE = 'strikethrough_wholesale_price'
    LAST_PURCHASE_PRICE = 'last_purchase_price'
    PURCHASE_PRICE_NET_AVERAGE = 'purchase_price_net_average'
    PURCHASE_PRICE_NET_LAST = 'purchase_price_net_last'
    PURCHASE_PRICE_GROSS_AVERAGE = 'purchase_price_gross_average'
    PURCHASE_PRICE_GROSS_LAST = 'purchase_price_gross_last'
    VAT = 'vat'
    VAT_FREE = 'vat_free'
    REBATE = 'rebate'
    HOTSPOTS_ZONES = 'hotspots_zones'
    PROFIT_POINTS = 'profit_points'
    POINTS = 'points'
    WEIGHT = 'weight'
    EXPORT_TO_PRICECOMPARERS = 'export_to_pricecomparers'
    EXPORT_TO_AMAZON_MARKETPLACE = 'export_to_amazon_marketplace'
    ENABLE_IN_POS = 'enable_in_pos'
    COMPLEX_NOTES = 'complex_notes'
    AVAILABLE_PROFILE = 'available_profile'
    TRAITS = 'traits'
    PARAMETERS = 'parameters'
    VERSION_DATA = 'version_data'
    ADVANCE = 'advance'
    PROMOTION = 'promotion'
    DISCOUNT = 'discount'
    DISTINGUISHED = 'distinguished'
    SPECIAL = 'special'
    VISIBLE = 'visible'
    PERSISTENT = 'persistent'
    PRIORITY = 'priority'
    SHOPS_MASK = 'shops_mask'
    ICON = 'icon'
    ICON_FOR_AUCTIONS = 'icon_for_auctions'
    ICON_FOR_GROUP = 'icon_for_group'
    PICTURES = 'pictures'
    UNIT = 'unit'
    WARRANTY = 'warranty'
    SERIES = 'series'
    PRODUCTS_ASSOCIATED = 'products_associated'
    SHOPS = 'shops'
    QUANTITIES = 'quantities'
    SIZES_ATTRIBUTES = 'sizes_attributes'
    SHOPS_ATTRIBUTES = 'shops_attributes'
    AUCTION_PRICES = 'auction_prices'
    PRICE_COMPARERS_PRICES = 'price_comparers_prices'
    DELIVERER = 'deliverer'
    SIZES = 'sizes'
    SIZE_GROUP_NAME = 'size_group_name'
    PICTURES_COUNT = 'pictures_count'
    PRODUCT_TYPE = 'product_type'
    PRICE_CHANGED_TIME = 'price_changed_time'
    QUANTITY_CHANGED_TIME = 'quantity_changed_time'
    DELIVERER_NAME = 'deliverer_name'
    AVAILABLE_PROFILE_NAME = 'available_profile_name'
    AVAILABILITY_MANAGEMENT_TYPE = 'availability_management_type'
    SUM_IN_BASKET = 'sum_in_basket'
    MENU = 'menu'
    AUCTION_SETTINGS = 'auction_settings'
    BUNDLE = 'bundle'
    SIZESCHART_ID = 'sizeschart_id'
    SIZESCHART_NAME = 'sizeschart_name'
    SERIALNUMBERS = 'serialnumbers'
    PRODUCER_CODES_STANDARD = 'producer_codes_standard'
    JAVASCRIPTINTHEITEMCARD = 'javaScriptInTheItemCard'
    PRODUCTAUCTIONDESCRIPTIONSDATA = 'productAuctionDescriptionsData'
    PRICEFORMULA = 'priceFormula'
    PRODUCTINDIVIDUALDESCRIPTIONSDATA = 'productIndividualDescriptionsData'
    PRODUCTINDIVIDUALURLSDATA = 'productIndividualUrlsData'
    PRODUCTSERVICESDESCRIPTIONSDATA = 'productServicesDescriptionsData'
    CNTARICCODE = 'cnTaricCode'
    PRODUCTISGRATIS = 'productIsGratis'
    DIMENSIONS = 'dimensions'
    RESPONSIBLEPRODUCERCODE = 'responsibleProducerCode'
    RESPONSIBLEPERSONCODE = 'responsiblePersonCode'

class ModeSearchEnum(StrEnum):
    NO = 'no'
    ONLYPRODUCT = 'onlyProduct'
    WHOLEBASKET = 'wholeBasket'

class ProductInExportToPriceComparisonSitesSearchEnum(StrEnum):
    YES = 'y' # Visible
    SELECTED = 'selected' # Selected
    ASSIGN_SELECTED = 'assign_selected' # Enable the visibility of the product in the export to price comparison sites passed in the priceComparisonSites node. Price comparison sites previously assigned to the commodity will be retained
    UNASSIGN_SELECTED = 'unassign_selected' # Disable product visibility in exports to price comparison sites passed in the priceComparisonSites node
    NO = 'n' # invisible

class ProductSearchPriceModeEnum(StrEnum):
    RETAIL_PRICE = 'retail_price' # Retail price of the product
    WHOLESALE_PRICE = 'wholesale_price' # Wholesale price of the product
    MINIMAL_PRICE = 'minimal_price' # Product minimal price
    POS_PRICE = 'pos_price' # price for POS
    LAST_PURCHASE_PRICE = 'last_purchase_price' # Last purchase price

class ReturnProductsSearchEnum(StrEnum):
    ACTIVE = 'active'
    DELETED = 'deleted'
    IN_TRASH = 'in_trash'

class ReturnProductsVersionsSearchEnum(StrEnum):
    VERSION_ALL = 'version_all' # returns all variants
    VERSION_MAIN = 'version_main' # - returns only main variant

class SearchModeInShopsEnum(StrEnum):
    IN_ONE_OF_SELECTED = 'in_one_of_selected' # in one of indicated stores
    IN_ALL_OF_SELECTED = 'in_all_of_selected' # in all indicated stores


# --- Models
class AssociatedProductsModel(BaseModel):
    associatedProductId: StrictInt = Field(..., ge=1, description="Recommended product ID")
    associatedProductName: str = Field(..., description="Recommended product name")
    associatedProductCode: str = Field(..., description="Recommended product code. External system code")

class AvailablePaymentFormsModel(BaseModel):
    prepaid: bool = Field(..., description="Prepayment")
    cashOnDelivery: bool = Field(..., description="Cash on delivery")
    tradeCredit: bool = Field(..., description="Trade credit")

class MinQuantityPerOrderModel(BaseModel):
    minQuantityPerOrderRetail: float = Field(..., gt=0, description="Minimum number of products in a retail order")
    minQuantityPerOrderWholesale: float = Field(..., gt=0, description="Minimum number of products in a wholesale order")

class PriceFormulaModel(BaseModel):
    priceFormulaParameters: str = Field(..., description="Formula parameters for calculating price")
    priceFormulaFunction: str = Field(..., description="Formula function for calculating price")

# --- Product lang related
class ProductUrlsLangDataModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    langId: str = Field(..., description="Language ID")
    url: str = Field(..., description="...")

class ProductUrlModel(BaseModel):
    productUrlsLangData: List[ProductUrlsLangDataModel] = Field(..., description="...")

class ProductDeliveryTimeModel(BaseModel):
    productDeliveryTimeChangeMode: ProductDeliveryTimeChangeModeEnum = Field(..., description="Operation type")
    productDeliveryTimeValue: StrictInt = Field(..., ge=0, le=999, description="The amount of time it takes to get goods from the supplier to the store. The maximum time is 99 for the unit 'days' or 999 for the unit 'hours' and 'minutes'")

    @model_validator(mode='after')
    def validate_delivery_time(self):
        """Validate delivery time constraints based on mode."""
        if self.productDeliveryTimeChangeMode == ProductDeliveryTimeChangeModeEnum.PRODUCT:
            if self.productDeliveryTimeValue < 0 or self.productDeliveryTimeValue > 999:
                raise ValueError("Delivery time value must be between 0 and 999")
        return self

class ProductDimensionsModel(BaseModel):
    productWidth: float = Field(..., gt=0, description="The width of a product in centimeters")
    productHeight: float = Field(..., gt=0, description="Height of a product in centimeters")
    productLength: float = Field(..., gt=0, description="The length of a product in centimeters")

class ProductDiscountModel(BaseModel):
    promoteInEnabled: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if the promotion should be active")
    promoteItemNormalPrice: float = Field(..., description="Strikethrough price")
    promoteItemWholesaleNormalPrice: float = Field(..., description="Strikethrough wholesale price")
    promoteItemEndingDate: str = Field(..., description="Switching off date")

class ProductDistinguishedModel(BaseModel):
    promoteInEnabled: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if the promotion should be active")
    promoteItemNormalPrice: float = Field(..., description="Strikethrough price")
    promoteItemWholesaleNormalPrice: float = Field(..., description="Strikethrough wholesale price")
    promoteItemEndingDate: str = Field(..., description="Switching off date")

class ProductParametersDistinctionModel(BaseModel):
    parameterId: StrictInt = Field(..., ge=1, description="Parameter ID")
    parameterName: str = Field(..., description="Parameter name")
    parameterValueId: StrictInt = Field(..., ge=1, description="Parameter value ID")
    parameterValueName: str = Field(..., description="Attributes group name")

class ProductPriceComparisonSitesPricesModel(BaseModel):
    priceComparisonSiteId: StrictInt = Field(..., ge=1, description="Price comparison website ID")
    productPriceComparisonSitePrice: float = Field(..., description="Price for a price comparison website in a shop")

class ProductPromotionModel(BaseModel):
    promoteInEnabled: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if the promotion should be active")
    promoteItemNormalPrice: float = Field(..., description="Strikethrough price")
    promoteItemWholesaleNormalPrice: float = Field(..., description="Strikethrough wholesale price")
    promoteItemEndingDate: str = Field(..., description="Switching off date")

class ProductSpecialModel(BaseModel):
    promoteInEnabled: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if the promotion should be active")
    promoteItemNormalPrice: float = Field(..., description="Strikethrough price")
    promoteItemWholesaleNormalPrice: float = Field(..., description="Strikethrough wholesale price")
    promoteItemEndingDate: str = Field(..., description="Switching off date")

class ProductMetaTitlesLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    langName: str = Field(..., description="Language name")
    productMetaTitle: str = Field(..., description="Product meta title")

class ProductMetaTitlesModel(BaseModel):
    productMetaTitlesLangData: List[ProductMetaTitlesLangDataModel] = Field(..., description="...")

class ProductMetaDescriptionsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    langName: str = Field(..., description="Language name")
    productMetaDescription: str = Field(..., description="Product meta description")

class ProductMetaDescriptionsModel(BaseModel):
    productMetaDescriptionsLangData: List[ProductMetaDescriptionsLangDataModel] = Field(..., description="...")

# --- Meta related
class ProductMetaKeywordsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    langName: str = Field(..., description="Language name")
    productMetaKeyword: str = Field(..., description="Product meta keywords")

class ProductMetaKeywordsModel(BaseModel):
    productMetaKeywordsLangData: List[ProductMetaKeywordsLangDataModel] = Field(..., description="...")

class ProductsBaseModel(BaseModel):
    productDisplayedCode: str = Field(..., description="External product system code")
    productTaxCode: str = Field(..., description="PKWiU [PCPandS]")
    productInWrapper: StrictInt = Field(..., ge=1, description="Number of items in package data")
    productSellByRetail: float = Field(..., gt=0, description="Sold at - for retailers")
    productSellByWholesale: float = Field(..., gt=0, description="Sold at - for wholesalers")
    categoryIdoSellId: StrictInt = Field(..., ge=1, description="IdoSell Category ID")
    categoryIdoSellPath: str = Field(..., description="IdoSell Category pathname")
    categoryId: StrictInt = Field(..., ge=1, description="Category Id")
    categoryName: str = Field(..., description="Category name")
    producerId: StrictInt = Field(..., ge=1, description="Brand Id")
    producerName: str = Field(..., description="Brand name")
    cnTaricCode: str = Field(..., description="CN/TARIC")
    countryOfOrigin: str = Field(..., description="Country of origin. Country code in the ISO-3166-1 alpha-2 standard (2 letters)")
    unitId: StrictInt = Field(..., ge=1, description="Product unit of measure ID")
    seriesId: StrictInt = Field(..., ge=1, description="ID of series, to which product belongs")
    seriesPanelName: str = Field(..., description="Name of series, to which the product belongs, visible in panel")
    # WARNING: Changing sizesGroupId has critical business implications:
    # - Changes zero ALL stock quantities in ALL stocks
    # - Changes only allowed if product is NOT in unhandled orders or auction listings
    # - This field change should be used with extreme caution
    sizesGroupId: StrictInt = Field(..., ge=1, description="Size group ID. Change of one size group to another results in zeroing all stock quantities in all stocks. Change of size group can be made, if product is not present in any unhandled orders nor listed on auctions")
    productVat: float = Field(..., gt=0, description="Value of VAT")
    productVatFree: BooleanStrShortEnum = Field(..., description="Is product VAT free")
    productPriceComparisonSitesPrices: List[ProductPriceComparisonSitesPricesModel] = Field(..., description="Different prices for price comparison websites")
    productEnableInPos: BooleanStrShortEnum = Field(..., description="Object determines if the product is available in POS sale")
    productAdvancePrice: float = Field(..., ge=0, description="Required advance payment in percents")
    productNote: str = Field(..., description="Annotation")
    shopsMask: int | None = Field(None, description="Bit mask of shop IDs. Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up")
    productComplexNotes: ProductComplexNotesEnum = Field(..., description="Complex rating")
    productInExportToPriceComparisonSites: YNSelectedEnum = Field(..., description="Product visibility in export to price comparison and marketplaces")
    productInExportToAmazonMarketplace: YNSelectedEnum = Field(..., description="Visibility of an item in an export to Amazon Marketplace")
    productPromotion: ProductPromotionModel = Field(..., description="Reduced price")
    productDiscount: ProductDiscountModel = Field(..., description="Discount for shop")
    productDistinguished: ProductDistinguishedModel = Field(..., description="Distinguished product in store")
    productSpecial: ProductSpecialModel = Field(..., description="Special product in store")
    productParametersDistinction: List[ProductParametersDistinctionModel] = Field(..., description="Parameters (distinguished)")
    productLongDescriptions: ProductLongDescriptionsModel = Field(..., description="Long product description")
    productAuctionDescriptionsData: List[ProductAuctionDescriptionsDataModel] = Field(..., description="Product data for auction services")
    productMetaTitles: ProductMetaTitlesModel = Field(..., description="Product meta title")
    productMetaDescriptions: ProductMetaDescriptionsModel = Field(..., description="Product meta description")
    productMetaKeywords: ProductMetaKeywordsModel = Field(..., description="Product meta keywords")
    productUrl: ProductUrlModel = Field(..., description="!AdresURLDlaTowaru!#")

class StandardUnitModel(BaseModel):
    contextValue: ContextValueEnum = Field(..., description="Possible special contexts corresponding to standard units")
    standardUnitValue: float = Field(..., gt=0, description="Total length/volume/area/weight of product")
    converterUnitValue: ConverterUnitValueEnum = Field(..., description="Price converter per unit")

class SettingDefaultCategoryModel(BaseModel):
    categoryId: StrictInt = Field(..., ge=1, description="Category id")
    categoryName: str = Field(..., description="Category name")

class SettingDefaultSizesGroupModel(BaseModel):
    sizesGroupId: StrictInt = Field(..., ge=1, description="Size group ID. Change of one size group to another results in zeroing all stock quantities in all stocks. Change of size group can be made, if product is not present in any unhandled orders nor listed on auctions")
    sizesGroupName: str = Field(..., description="Size group name")

class SubscriptionModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    enabled: bool = Field(False, description="Is subscription enabled for product")
    daysInPeriod: List[int] = Field(..., description="Days in period")
    unitsNumberRetail: float = Field(..., gt=0, description="Sold at - for retailers")
    unitsNumberWholesale: float = Field(..., gt=0, description="Sold at - for wholesalers")


# --- Versions related
class VersionNamesLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    versionName: str = Field(..., description="Name of the parameter value, e.g. orange, green, red")

class VersionNamesModel(BaseModel):
    versionNamesLangData: List[VersionNamesLangDataModel] = Field(..., description="Array of languages, values are displayed in")

class VersionGroupNamesLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    versionGroupName: str = Field(..., description="Parameter name, e.g. color, width")

class VersionGroupNamesModel(BaseModel):
    versionGroupNamesLangData: List[VersionGroupNamesLangDataModel] = Field(..., description="Parameter name")

class VersionSettingsBaseModel(BaseModel):
    versionDisplayAllInShop: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Show in shop")
    versionCommonCode: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same code")
    versionCommonProducer: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same brand")
    versionCommonNote: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same annotation")
    versionCommonWarranty: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same warranty")
    versionCommonSeries: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same series")
    versionCommonCategory: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same category")
    versionCommonPrice: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same price")
    versionCommonAdvance: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Same advance")
    versionCommonRebate: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Same quantity discount")
    versionCommonVat: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same VAT rate")
    versionCommonProfitPoints: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same loyalty points")
    versionCommonPromotion: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same promotion")
    versionCommonAssociated: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same related product")
    versionCommonVisibility: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same visibility")
    versionCommonPriority: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same priority")
    versionCommonShops: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same shops")
    versionCommonSizes: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same sizes")
    versionCommonWeight: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same weight")
    versionCommonDictionary: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same parameters")
    versionCommonName: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same name")
    versionCommonDescription: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same short description")
    versionCommonLongDescription: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same long description")
    versionCommonIcon: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same icon")
    versionCommonPhotos: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same large photos")
    versionCommonAvailableProfile: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same availability profile")
    versionCommonComplexNotes: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same complex rating")
    versionCommonSumInBasket: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Do You wish to sum up the products in the basket as a one order?")

class VersionSettingsCommonModel(VersionSettingsBaseModel):
    versionCommonAuctionsPrice: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Same price for auction services")
    versionCommonDiscount: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same loyalty discount")
    versionCommonDistinguished: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same privileged products")
    versionCommonSpecial: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same for special")
    versionCommonTraits: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="DEPRECATED")
    versionCommonPersistent: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Same display when not in stock")
    versionCommonUnit: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The same unit of measure")

# --- Product Shops related
class ProductShopPriceComparisonSitesPricesModel(BaseModel):
    priceComparisonSiteId: StrictInt = Field(..., ge=1, description="Price comparison website ID")
    productPriceComparisonSitePercentDiff: float = Field(..., gt=0, description="Percentage difference between the price comparison website and the shop")

class ProductShopsAttributesModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    productShopPriceComparisonSitesPrices: List[ProductShopPriceComparisonSitesPricesModel] = Field(..., description="Information about prices for price comparison websites dependent on a shop")

# --- Product Stocks related
class ProductStockQuantitiesModel(BaseModel):
    stockId: StrictInt = Field(..., ge=1, description="Stock ID")
    productSizeQuantity: StrictInt = Field(..., ge=0, description="Product stock quantity")
    productSizeQuantityToAdd: StrictInt = Field(..., ge=0, description="Product quantity to add up")
    productSizeQuantityToSubstract: StrictInt = Field(..., ge=0, description="Product quantity to subtract")

class ProductStocksDataModel(BaseModel):
    productStockQuantities: List[ProductStockQuantitiesModel] = Field(..., description="Object contains information on product quantity")

# --- Product Sizes related
class ProductAuctionPricesModel(BaseModel):
    productAuctionId: StrictInt = Field(..., ge=1, description="Auction system ID")
    productAuctionSiteId: StrictInt = Field(..., ge=1, description="Auction site ID")
    productAuctionPrice: float = Field(..., gt=0, description="Price for auction site")

class ShopsSizeAttributesModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    productRetailPrice: float = Field(..., gt=0, description="Gross price")
    productWholesalePrice: float = Field(..., gt=0, description="Wholesale price")
    productMinimalPrice: float = Field(..., gt=0, description="Minimal price")
    productAutomaticCalculationPrice: float = Field(..., gt=0, description="Price for automatic calculations")

class ProductSizesModel(BaseModel):
    sizeId: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")
    productWeight: StrictInt = Field(..., gt=0, description="Weight")
    productWeightNet: StrictInt = Field(..., gt=0, description="Net weight")
    productRetailPrice: float = Field(..., gt=0, description="Gross price")
    productWholesalePrice: float = Field(..., gt=0, description="Wholesale price")
    productMinimalPrice: float = Field(..., gt=0, description="Minimal price")
    productAutomaticCalculationPrice: float = Field(..., gt=0, description="")
    productPosPrice: float = Field(..., gt=0, description="price for POS")
    productAuctionPrices: List[ProductAuctionPricesModel] = Field(..., description="Prices for marketplaces")
    productCode: str = Field(..., description="External product system code")
    productInPersistent: BooleanStrShortEnum = Field(..., description="Product visible even though out of stock")
    productStocksData: ProductStocksDataModel = Field(..., description="Product stock quantity data")
    shopsSizeAttributes: List[ShopsSizeAttributesModel] = Field(..., description="Object contains information dependent on shop and size")

# --- Product Descriptions / Names related
class ProductNamesLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productName: str = Field(..., description="Product name")

class ProductNamesModel(BaseModel):
    productNamesLangData: List[ProductNamesLangDataModel] = Field(..., description="...")

# --- Dispatch related
class FreeShippingSettingsModel(BaseModel):
    mode: ModeEnum = Field(..., description="Edition mode")
    availablePaymentForms: AvailablePaymentFormsModel = Field(..., description="Set free shipping for the payment method only")
    availableCouriers: List[int] = Field(..., description="List of courier services for which shipping is free")
    availableRegions: List[int] = Field(..., description="List of regions with free shipment")

class ShippingSettingsModel(BaseModel):
    codDisabled: bool = Field(..., description="Disable cash on delivery orders")
    dvpOnly: bool = Field(..., description="Only personal collection")
    atypicalSize: bool = Field(..., description="Oversized product")
    insuranceOnly: bool = Field(..., description="Insurance required")
    excludeSmileService: bool = Field(..., description="Exclusion from the Smile service")
    disallowedCouriers: List[int] = Field(..., description="List of courier services which cannot be used to ship this product")

class ReturnOptionsModel(BaseModel):
    enabled: bool = Field(..., description="...")
    firm: bool = Field(..., description="true - for companies")
    hurt: bool = Field(..., description="true - for wholesalers")
    detalist: bool = Field(..., description="true - for retailers")

class ReturnProductSettingsModel(BaseModel):
    returnOptions: ReturnOptionsModel = Field(..., description="Product can be returned")
    byOwnService: bool = Field(..., description="...")
    byInPostSzybkieZwrotyByIAI: bool = Field(..., description="...")

class DispatchSettingsModel(BaseModel):
    enabled: bool = Field(False, description="...")
    shippingSettings: ShippingSettingsModel = Field(..., description="Shipping settings")
    freeShippingSettings: FreeShippingSettingsModel = Field(..., description="Free shipping settings")
    returnProductSettings: ReturnProductSettingsModel = Field(..., description="Return and complaint settings")


# --- Delete DTOs
class ProductsDeleteModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Products list")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")

# --- Post DTOs
class PictureSettingsPostModel(BaseModel):
    picturesSettingInitialUrlPart: str = Field(..., description="Object determines photo URL")
    picturesSettingInputType: PicturesSettingInputTypeEnum = Field(..., description="Object determines the method of adding photos in 'pictures' object")
    picturesSettingOverwrite: BooleanStrShortEnum = Field(..., description="Object determines the method of adding product photos. Allowed values 'n' - photos are uploaded from the first free place, 'y' - photos are uploaded from the first place")
    picturesSettingScaling: BooleanStrShortEnum = Field(..., description="Object determines if the photo should be scaled. Allowed values 'n' - no scaling allowance, 'y' - scaling allowance")

class PriceComparisonSitesPostModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    priceComparisonSiteId: StrictInt = Field(..., ge=1, description="Price comparison website ID")

class ProductDescriptionsLangDataPostModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productDescription: str = Field(..., description="Short product description")

class ProductDescriptionsModel(BaseModel):
    productDescriptionsLangData: List[ProductDescriptionsLangDataPostModel] = Field(..., description="Array of language-dependent elements")

class ProductVersionPostModel(BaseModel):
    versionParentId: StrictInt = Field(..., description="ID of the main item (variant) in the group")
    versionPriority: StrictInt = Field(..., description="The order of products in the group. Value needs to be more than 0")
    versionSettings: VersionSettingsCommonModel = Field(..., description="Settings for groups of items (variants)")
    versionNames: VersionNamesModel = Field(..., description="Parameter value names")
    versionGroupNames: VersionGroupNamesModel = Field(..., description="Parameter names")

class ProductsPostModel(ProductsBaseModel):
    priceComparisonSites: List[PriceComparisonSitesPostModel] = Field(..., description="Selection of comparison sites for which the product visibility will be changed")
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")
    priceChangeMode: PriceChangeModeEnum = Field(..., description="Optional element, that determines prices edition mode. Default value is 'amount_set', when indicated element is omitted in API gate call")
    priceFormula: PriceFormulaModel | None = Field(None, description="The JavaScript formula calculating prices")
    productRetailPrice: float = Field(..., gt=0, description="Gross price")
    productWholesalePrice: float = Field(..., gt=0, description="Wholesale price")
    productMinimalPrice: float = Field(..., gt=0, description="Minimal price")
    productAutomaticCalculationPrice: float = Field(..., gt=0, description="Price for automatic calculations")
    productPosPrice: float = Field(..., gt=0, description="Price for POS")
    productProfitPoints: float = Field(..., ge=0, description="Product value in points")
    productWeight: StrictInt = Field(..., gt=0, description="Weight")
    productInVisible: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Product visibility")
    productInPersistent: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Product visible even though out of stock")
    availableProfile: StrictInt = Field(..., ge=1, description="Availability profile ID")
    productRebate: StrictInt = Field(..., ge=1, description="Discount profile ID")
    warrantyId: StrictInt = Field(..., ge=1, description="Product warranty ID")
    productPriority: StrictInt = Field(..., ge=1, lt=11, description="Priority")
    productIcon: str = Field(..., description="Product icon details")
    productWatermarkId: StrictInt = Field(..., ge=1, description="Watermark ID")
    productWatermarkUrl: str = Field(..., description="Link to watermark")
    productPictures: List[str] = Field(..., description="List of product photos")
    productDescriptionPictures: List[str] = Field(..., description="List of photos descriptions")
    associatedProducts: List[AssociatedProductsModel] = Field(..., description="List of products recommended with this product")
    productSizes: List[ProductSizesModel] = Field(..., description="Sizes available for products data")
    productShopsAttributes: List[ProductShopsAttributesModel] = Field(..., description="Data concerning attributes dependent on indicated stores with particular product assigned")
    subscription: List[SubscriptionModel] = Field(..., description="Products subscription settings")
    productNames: ProductNamesModel = Field(..., description="Product name")
    productDescriptions: ProductDescriptionsModel = Field(..., description="...")
    productVersion: ProductVersionPostModel = Field(..., description="Data on product groups (variants)")
    currencyId: str = Field(..., description="Currency ID")
    delivererId: StrictInt = Field(..., ge=1, description="Supplier ID")
    productParametersDistinctionChangeMode: ProductParametersDistinctionChangeModeEnum = Field(..., description="This parameter is optional and it determines properties edition mode. Default value is 'replace'")
    productDeliveryTime: ProductDeliveryTimeModel = Field(..., description="Product delivery time from the producer to the shop")
    productSumInBasket: BooleanStrShortEnum = Field(..., description="Do You wish to sum up the products in the basket as a one order?")
    dispatchSettings: DispatchSettingsModel = Field(..., description="Shipping, returns and complaints settings")
    standardUnit: StandardUnitModel = Field(..., description="Standard unit settings")
    minQuantityPerOrder: MinQuantityPerOrderModel = Field(..., description="Minimal number of products in an order")
    productDimensions: ProductDimensionsModel = Field(..., description="Dimensions and overall weight")
    responsibleProducerCode: str = Field(..., description="Responsible producer code")
    responsiblePersonCode: str = Field(..., description="Responsible person code")

class SettingsPostModel(BaseModel):
    settingPriceFormat: str | None = Field(None, description="Price format. Parameter is currently unused")
    settingAddingCategoryAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new categories can be added when category linked with product couldn't be found in system") # just in case set to NO
    settingAddingSizeAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new product sizes can be added when size linked with product couldn't be found in system") # just in case set to NO
    settingAddingProducerAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new producers can be added when producer linked with product couldn't be found in system") # just in case set to NO
    settingAddingSeriesAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new product series can be added when series linked with product couldn't be found in system") # just in case set to NO
    settingDefaultCategory: SettingDefaultCategoryModel = Field(..., description="Object determines default category which will be linked with product when it will not be linked with any category")
    settingDefaultSizesGroup: SettingDefaultSizesGroupModel = Field(..., description="Element specifying the default size group that will be assigned to the new product in case no size group has been explicitly assigned")
    settingsAddingDefaultShopMaskAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The item shall determine whether the default visibility in stores can be set if a new commodity is to be created and no parameters have been uploaded to set visibility in at least one store") # just in case set to NO
    settingsAddingManuallySelectedShopMaskAllowed: int | None = Field(None, description="Element specifying whether the default visibility in stores can be set according to the list of stores indicated in the web import source configuration, if a new product will be created and no parameters have been sent to set visibility in at least one store")


# --- Put DTOs
class AttachmentsModel(BaseModel):
    attachmentUrl: str = Field(..., description="Attachment file link")
    attachmentName: AttachmentNameModel = Field(..., description="Attachment name")
    attachmentFileType: AttachmentFileTypeEnum = Field(..., description="File type: audio, video, doc, other")
    attachmentEnable: AttachmentEnableEnum = Field(..., description="Type of customer, attachment should be available for")
    attachmentId: StrictInt = Field(..., ge=1, description="Attachment ID")
    attachmentDownloadLog: BooleanStrShortEnum = Field(..., description="Attachment downloads record")
    attachmentFileExtension: str = Field(..., description="Attachment file extension")
    attachmentPriority: StrictInt = Field(..., ge=1, description="Attachment number")
    documentTypes: List[DocumentTypesModel] = Field(..., description="Attachment document types list")

class PriceModifierValuesModel(BaseModel):
    parameterId: StrictInt = Field(..., ge=1, description="Parameter ID")
    modifierValue: StrictInt = Field(..., ge=1, description="...")
    modifierType: ModifierTypeEnum = Field(..., description="Available values")

class ParametersConfigurableModel(BaseModel):
    parameterId: StrictInt = Field(..., ge=1, description="Parameter ID")
    priceConfigurableType: PriceConfigurableTypeEnum = Field(..., description="Parameter type")
    priceModifierValues: List[PriceModifierValuesModel] = Field(..., description="Price modifier value")

class PicturesSettingApplyMacroForIconModel(BaseModel):
    iconType: str = Field(..., description="Icon type")
    macroId: StrictInt = Field(..., ge=1, description="Macro identifier")

class PictureSettingsPutModel(BaseModel):
    picturesSettingInitialUrlPart: str = Field(..., description="Object determines photo URL")
    picturesSettingInputType: PicturesSettingInputTypeEnum = Field(..., description="Object determines the method of adding photos in 'pictures' object")
    picturesSettingOverwrite: BooleanStrShortEnum = Field(..., description="Object determines the method of adding product photos. Allowed values 'n' - photos are uploaded from the first free place, 'y' - photos are uploaded from the first place")
    picturesSettingDeleteProductPictures: BooleanStrShortEnum = Field(..., description="Element determining whether or not to delete existing merchandise images")
    picturesSettingDeleteProductIcons: BooleanStrShortEnum = Field(..., description="Element determining whether to delete existing commodity icons")
    picturesSettingDeleteIcon: PicturesSettingDeleteIconEnum = Field(..., description="Element determining whether to remove the selected icon")
    picturesSettingCreateIconFromPicture: PicturesSettingCreateIconFromPictureEnum = Field(..., description="Element determining whether or not to create icon from the selected photo")
    picturesSettingRestoreOriginalPictures: BooleanStrShortEnum = Field(..., description="Element determining whether to restore existing original images")
    picturesSettingRestoreOriginalIcons: PicturesSettingRestoreOriginalIconsEnum = Field(..., description="Element determining the type of icon whose original is to be restored, if any")
    picturesSettingApplyMacroForPictures: int | None = Field(None, ge=1, description="Macro ID to be applied to images on the product")
    picturesSettingApplyMacroForIcon: PicturesSettingApplyMacroForIconModel = Field(..., description="Macro for the selected icon")
    picturesSettingShopId: str = Field(..., description="Identifier of the shop for which the action is to be performed")
    picturesSettingServiceId: StrictInt = Field(..., ge=1, description="Identifier of an external service for which the action is to be performed on photos in the goods")
    picturesSettingScaling: BooleanStrShortEnum = Field(..., description="Object determines if the photo should be scaled. Allowed values 'n' - no scaling allowance, 'y' - scaling allowance")
    picturesSettingDeleteOriginalPictures: BooleanStrShortEnum = Field(..., description="Element determining whether to delete existing original images")
    picturesSettingDeleteOriginalIcons: PicturesSettingDeleteOriginalIconsEnum = Field(..., description="Element specifying the type of icon whose original is to be deleted")
    picturesSettingRestoreBackupPicturesAndIconsByDateTime: str | None = Field(None, description="...")

class VersionGroupNamesPutModel(BaseModel):
    versionGroupNamesLangData: List[VersionGroupNamesLangDataModel] = Field(..., description="Parameter name")

class VersionNamesPutModel(BaseModel):
    versionNamesLangData: List[VersionNamesLangDataModel] = Field(..., description="Array of languages, values are displayed in")

class VersionParentModel(BaseModel):
    versionParentId: str = Field(..., description="Value")
    versionParentType: VersionParentTypeEnum = Field(..., description="Identifier type")

class VersionParentPutModel(BaseModel):
    versionParentId: str = Field(..., description="Value")
    versionParentType: VersionParentTypeEnum = Field(..., description="Identifier type")

class VersionSettingsPutModel(VersionSettingsBaseModel):
    versionDisplayAllInPanel: BooleanStrShortEnum = Field(..., description="Show in panel")
    versionDisplayRelCanonicalInShop: BooleanStrShortEnum = Field(..., description="Adding the canonical links to the site")
    versionCommonAuctionName: BooleanStrShortEnum = Field(..., description="The same product's name for Internet auctions")
    versionCommonMetaTags: BooleanStrShortEnum = Field(..., description="The same meta settings")
    versionCommonCurrency: BooleanStrShortEnum = Field(..., description="The same currency")
    versionCommonPriceFormula: BooleanStrShortEnum = Field(..., description="The same formula for calculating prices")
    versionCommonPromotions: BooleanStrShortEnum = Field(..., description="Same promotions")
    versionCommonJavaScriptOnCard: BooleanStrShortEnum = Field(..., description="The same JavaScript displayed on the product card")
    versionCommonMenuItems: BooleanStrShortEnum = Field(..., description="The same objects in menu")
    versionCommonDeliverer: BooleanStrShortEnum = Field(..., description="The same supplier")
    versionCommonAttachments: BooleanStrShortEnum = Field(..., description="The same attachments")
    versionCommonAuctionIcon: BooleanStrShortEnum = Field(..., description="The same icons for auctions")
    versionCommonSerialNumbers: BooleanStrShortEnum = Field(..., description="The same serial numbers")

class ProductVersionPutModel(BaseModel):
    versionParent: VersionParentPutModel = Field(..., description="ID of the main item (variant) in the group")
    versionPriority: StrictInt = Field(..., ge=1, description="The order of products in the group. Value needs to be more than 0")
    versionSettings: VersionSettingsCommonModel = Field(..., description="Settings for groups of items (variants)")
    versionNames: VersionNamesModel = Field(..., description="Parameter value names")
    versionGroupNames: VersionGroupNamesModel = Field(..., description="Parameter names")

class VirtualAttachmentsModel(VirtualAttachmentsBaseModel):
    pass

class ChangeParametersDistinctionModel(BaseModel):
    productParameterId: StrictInt = Field(..., ge=1, description="Parameter ID")
    productParameterTextIdent: str = Field(..., description="Parameter name (if ID was not used")
    langId: str = Field(..., description="Language ID")
    productParameterDescriptionType: ProductParameterDescriptionTypeEnum = Field(..., description="...")
    parameterDistinctionValue: BooleanStrShortEnum = Field(..., description="Value")

class ClearStockQuantitiesModel(BaseModel):
    clearAllStockQuantities: bool = Field(..., description="The setting allows you to reset the inventories of warehouse M0 and all your own warehouses")
    stocksListToClear: List[int] = Field(..., description="List of warehouses for which inventories are to be reset")

class JavaScriptInTheItemCardModel(BaseModel):
    shopId: StrictInt = Field(..., description="Shop Id")
    scriptCode: str = Field(..., description="JavaScript code displayed in the product page of the IdoSell Shop")

class LoyaltyPointsModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    loyaltyPointsClientsType: LoyaltyPointsClientsTypeEnum = Field(..., description="Customer type")
    loyaltyPointsOperation: LoyaltyPointsOperationEnum = Field(..., description="Operation")
    loyaltyPointsType: LoyaltyPointsTypeEnum = Field(..., description="Loyalty points type")
    numberOfLoyaltyPoints: float = Field(..., ge=0, description="Number of points")

class PriceInPointsModel(BaseModel):
    priceInPointsOperation: PriceInPointsOperationEnum = Field(..., description="Element determines what kind of operation should be performed")
    shopId: StrictInt = Field(..., ge=1, description="ShopId")
    priceInPointsPrice: float = Field(..., ge=0, description="Price in points for manual points quantity configuration. Price in points will be calculated on basis of default exchange rates set for indicated store, when this value is 0")
    priceInPointsClients: PriceInPointsClientsEnum = Field(..., description="Element determines for which customers prices will be changed")

class ProductCurrenciesShopsModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    currencyId: str = Field(..., description="Currency ID")

class ProductHotspotsZonesModel(BaseModel):
    productHotspotIsEnabled: bool = Field(..., description="Is attribute set")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    productIsPromotion: bool = Field(..., description="Promotion for shop")
    productIsDiscount: bool = Field(..., description="Discount for shop")
    productIsDistinguished: bool = Field(..., description="Distinguished product in store")
    productIsSpecial: bool = Field(..., description="Special product in store")

class ProductPicturesReplaceModel(BaseModel):
    productPictureNumber: StrictInt = Field(..., ge=1, description="A product photo's number")
    productPictureSource: str = Field(..., description="A picture in url or base64 (depends on pictures_input_type")

class ProductLongDescriptionsInAuctionModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productLongDescriptionsInAuction: str = Field(..., description="...")

class ProductPriorityInMenuNodesModel(BaseModel):
    productMenuNodeId: StrictInt = Field(..., ge=1, description="Menu element ID")
    productPriority: StrictInt = Field(..., ge=1, description="Priority")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    productMenuTreeId: StrictInt = Field(..., ge=1, description="Tree menu ID")

class ProductNamesInAuctionLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productNameInAuction: str = Field(..., description="...")

class ProductNamesInAuctionModel(BaseModel):
    productNamesInAuctionLangData: List[ProductNamesInAuctionLangDataModel] = Field(..., description="...")

class ProductNamesInPriceComparerLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productNameInPriceComparer: str = Field(..., description="Product name for price comparison websites")

class ProductNamesInPriceComparerModel(BaseModel):
    productNamesInPriceComparerLangData: List[ProductNamesInPriceComparerLangDataModel] = Field(..., description="...")

class ProductParamDescriptionsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productParamDescriptions: str = Field(..., description="Product short description")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    serviceId: StrictInt = Field(..., ge=1, description="External service identifier")

class ProductParamDescriptionsModel(BaseModel):
    productParamDescriptionsLangData: List[ProductParamDescriptionsLangDataModel] = Field(..., description="...")

class ProductMenuItemsModel(BaseModel):
    productMenuOperation: ProductMenuOperationEnum = Field(..., description="Menu element operation type")
    menuItemId: StrictInt = Field(..., ge=1, description="ID of the menu node to which the product is to be assigned")
    menuItemTextId: str = Field(..., description="Menu element text identifier. Example: item1\item2\item3") # type: ignore
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    menuId: StrictInt = Field(..., ge=1, description="ID of the menu zone displayed in the mask")

class RemoveAllProductsAssignedToMenuModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    menuId: StrictInt = Field(..., ge=1, description="ID of the menu zone displayed in the mask")

class RemoveAttachmentsModel(BaseModel):
    langId: str = Field(..., description="Language ID")

class SettingDeleteIndividualDescriptionsByShopsMaskModel(BaseModel):
    shopsMask: StrictInt = Field(..., description="Bit mask of shop IDs. Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up")

class SettingDeleteIndividualMetaByShopsMaskModel(BaseModel):
    shopsMask: StrictInt = Field(..., description="Bit mask of shop IDs. Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up")

class PriceComparisonSitesModel(BaseModel):
    priceComparisonSiteId: StrictInt = Field(..., ge=1, description="price comparison website ID")
    productPriceComparisonSitePrice: float = Field(..., gt=0, description="Price for a price comparison website in a shop")
    productPriceComparisonSitePriceNet: float = Field(..., gt=0, description="Net price for price comparison service in shop")

class ProductParameterTextIdsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productParameterTextId: str = Field(..., description="Parameter ID")

class ProductParametersDescriptionsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productParametersDescription: str = Field(..., description="Parameter description")

class ProductParametersModel(BaseModel):
    productParameterOperation: ProductParameterOperationEnum = Field(..., description="...")
    productParameterId: StrictInt = Field(..., ge=1, description="Parameter ID")
    productParameterPriority: int | None = Field(None, description="Determines where the parameter will be added. If no value is specified, the parameter will be placed at the end of the list. If a value of e.g. 5 is set, the value of all priorities >= 5 will be increased by 1 to provide a unique priority value")
    productParameterTextIdsLangData: List[ProductParameterTextIdsLangDataModel] = Field(..., description="Allows to enter parameter name i multiple languages at the same time. If it is used, item_textid and lang_id are ingored")
    langId: str = Field(..., description="Language ID")
    productParametersDescriptionsLangData: List[ProductParametersDescriptionsLangDataModel] = Field(..., description="Parameters descriptions in indicated language versions")

class ProductsPutModel(ProductsBaseModel):
    priceComparisonSites: List[PriceComparisonSitesModel] = Field(..., description="Selection of comparison sites for which the product visibility will be changed")
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    productIndex: str = Field(..., description="One of the unique, indexed product codes (IAI code / External system code / Producer code)")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")
    productSizeCodeProducer: str = Field(..., description="Producer code for size")
    sizesGroupName: str = Field(..., description="Size group name")
    priceChangeMode: PriceChangeModeEnum = Field(..., description="Optional element, that determines prices edition mode. Default value is 'amount_set', when indicated element is omitted in API gate call")
    productRetailPrice: float = Field(..., gt=0, description="Gross price")
    productRetailPriceNet: float = Field(..., gt=0, description="Net retail price for every shop")
    productWholesalePrice: float = Field(..., gt=0, description="Wholesale price")
    productWholesalePriceNet: float = Field(..., gt=0, description="Net wholesale price for every shop")
    productMinimalPrice: float = Field(..., gt=0, description="Minimal price")
    productMinimalPriceNet: float = Field(..., gt=0, description="Net minimum price for every shop")
    productAutomaticCalculationPrice: float = Field(..., gt=0, description="Price for automatic calculations")
    productAutomaticCalculationPriceNet: float = Field(..., gt=0, description="Net wholesale price for every shop")
    productPosPrice: float = Field(..., gt=0, description="Price for POS")
    productPosPriceNet: float = Field(..., description="Price for POS")
    productSuggestedPrice: float = Field(..., description="Recommended retail price")
    productSuggestedPriceNet: float = Field(..., description="Suggested net commodity price")
    productStrikethroughRetailPrice: float = Field(..., description="Strikethrough gross retail price")
    productStrikethroughRetailPriceNet: float = Field(..., description="Strikethrough net retail price")
    productStrikethroughWholesalePrice: float = Field(..., description="Strikethrough gross wholesale price")
    productStrikethroughWholesalePriceNet: float = Field(..., description="Strikethrough net wholesale price")
    productHotspotsZones: List[ProductHotspotsZonesModel] = Field(..., description="Settings of hotspots display")
    priceInPoints: List[PriceInPointsModel] = Field(..., description="...")
    loyaltyPoints: List[LoyaltyPointsModel] = Field(..., description="Loyalty points")
    productWeight: StrictInt = Field(..., gt=0, description="Weight")
    productInVisible: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Product visibility")
    exportToAmazonExportAllSizes: BooleanStrShortEnum = Field(..., description="Export sizes to Amazon. 'y' - all, 'n' - leave without change")
    exportAmazonUpdateStocks: BooleanStrShortEnum = Field(..., description="Update merchandise inventory, on the Amazon side")
    productInExportToStrefaMarekAllegro: ProductInExportToStrefaMarekAllegroEnum = Field(..., description="Visibility of product during the import to Strefa Marek Allegro")
    productInExportToSmaPreset: StrictInt = Field(..., description="Profile ID which should be used when sending products to Strefa Marek Allegro")
    availableProfile: StrictInt = Field(..., ge=1, description="Availability profile ID")
    productRebate: StrictInt = Field(..., ge=1, description="Discount profile ID")
    warrantyId: StrictInt = Field(..., ge=1, description="Product warranty ID")
    warrantyName: str = Field(..., description="Name of warranty for indicated product")
    priceFormula: PriceFormulaModel = Field(..., description="The JavaScript formula calculating prices")
    sizeChartId: StrictInt = Field(..., ge=1, description="Size chart ID")
    sizeChartName: str = Field(..., description="Size chart name")
    productPriority: StrictInt = Field(..., ge=1, lt=11, description="Priority")
    productPriorityInMenuNodes: List[ProductPriorityInMenuNodesModel] = Field(..., description="Product priority in menu node")
    productIconLink: str = Field(..., description="Product icon link")
    productAuctionIconLink: str = Field(..., description="Photo without background")
    productGroupIconLink: str = Field(..., description="Icon for a product group")
    productPictures: List[str] = Field(..., description="List of product photos")
    productPicturesReplace: List[ProductPicturesReplaceModel] = Field(..., description="List of a product's photos with indication of a particular number of the photo")
    parametersConfigurable: List[ParametersConfigurableModel] = Field(..., description="Configuration parameters")
    associatedProducts: List[AssociatedProductsModel] = Field(..., description="List of products recommended with this product")
    productSizes: List[ProductSizesModel] = Field(..., description="Sizes available for products data")
    attachments: List[AttachmentsModel] = Field(..., description="Product attachments list")
    removeAttachments: List[RemoveAttachmentsModel] = Field(..., description="The list of attachments to be deleted")
    virtualAttachmentsToRemove: bool = Field(..., description="Do you want to delete attachments for digital files")
    virtualAttachments: List[VirtualAttachmentsModel] = Field(..., description="List of product's virtual attachments")
    attachmentOperationValues: AttachmentOperationValuesEnum = Field(..., description="Operation, that will be performed on attachments to product")
    productShopsAttributes: List[ProductShopsAttributesModel] = Field(..., description="Data concerning attributes dependent on indicated stores with particular product assigned")
    subscription: List[SubscriptionModel] = Field(..., description="Products subscription settings")
    productNames: ProductNamesModel = Field(..., description="Product name")
    productNamesInAuction: ProductNamesInAuctionModel = Field(..., description="DEPRECATED. This parameter is deprecated. Product name for online auctions")
    productNamesInPriceComparer: ProductNamesInPriceComparerModel = Field(..., description="Product name for price comparison websites")
    productParamDescriptions: ProductParamDescriptionsModel = Field(..., description="Product short description")
    productLongDescriptions: ProductLongDescriptionsModel = Field(..., description="Long product description")
    productLongDescriptionsInAuction: ProductLongDescriptionsInAuctionModel = Field(..., description="DEPRECATED. This parameter is deprecated. Product description for marketplaces")
    productVersion: ProductVersionPutModel = Field(..., description="Data on product groups (variants)")
    currencyId: str = Field(..., description="Currency ID")
    productCurrenciesShops: List[ProductCurrenciesShopsModel] = Field(..., description="Currency, in which product prices are stored")
    delivererId: StrictInt = Field(..., ge=1, description="Supplier ID")
    delivererName: str = Field(..., description="Supplier name")
    productParametersDistinctionChangeMode: ProductParametersDistinctionChangeModeEnum = Field(..., description="This parameter is optional and it determines properties edition mode. Default value is 'replace'")
    productDeliveryTime: ProductDeliveryTimeModel = Field(..., description="Product delivery time from the producer to the shop")
    productParameters: List[ProductParametersModel] = Field(..., description="Parameters")
    clearProductParameters: bool = Field(..., description="...")
    changeParametersDistinction: List[ChangeParametersDistinctionModel] = Field(..., description="Change parameter distinction")
    productPriceVatChangeMode: ProductPriceVatChangeModeEnum = Field(..., description="VAT rate change mode")
    productMenuItems: List[ProductMenuItemsModel] = Field(..., description="An array of menu elements")
    removeAllProductsAssignedToMenu: RemoveAllProductsAssignedToMenuModel = Field(..., description="Deletes all items assigned to the product of the selected menu")
    productSumInBasket: BooleanStrShortEnum = Field(..., description="Do You wish to sum up the products in the basket as a one order?")
    productShopsPricesConfig: ProductShopsPricesConfigEnum = Field(..., description="Settings of prices for shop")
    productPosPricesConfig: ProductPosPricesConfigEnum = Field(..., description="Price settings for POS")
    productType: ProductTypeEnum = Field(..., description="Product type")
    priceRoundMode: PriceRoundModeEnum = Field(..., description="Forced rounding up method")
    productAvailabilityManagementType: ProductAvailabilityManagementTypeEnum = Field(..., description="Product availability management method")
    removeChooseSizesValues: List[str] = Field(..., description="List of unused sizes in product to be deleted")
    removeAllUnusedProductSizes: bool = Field(..., description="Remove all unused sizes")
    producerCodesStandard: ProducerCodesStandardEnum = Field(..., description="Standard producer code")
    javaScriptInTheItemCard: List[JavaScriptInTheItemCardModel] = Field(..., description="JavaScript code displayed in the product page of the IdoSell Shop")
    serialNumbersOption: SerialNumbersOptionEnum = Field(..., description="Saving serial numbers")
    dispatchSettings: DispatchSettingsModel = Field(..., description="Shipping, returns and complaints settings")
    standardUnit: StandardUnitModel = Field(..., description="Standard unit settings")
    minQuantityPerOrder: MinQuantityPerOrderModel = Field(..., description="Minimal number of products in an order")
    dynamicPricingEnabled: str = Field(..., description="...")
    clearStockQuantities: ClearStockQuantitiesModel = Field(..., description="The setting allows you to reset the inventory to zero")
    productDimensions: ProductDimensionsModel = Field(..., description="Dimensions and overall weight")
    responsibleProducerCode: str = Field(..., description="Responsible producer code")
    responsiblePersonCode: str = Field(..., description="Responsible person code")

class SettingsPutModel(BaseModel):
    settingModificationType: SettingModificationTypeEnum = Field(..., description="Object determines the products modification mode")
    settingPriceFormat: str | None = Field(None, description="Price format. Parameter is currently unused")
    settingCalculateBasePriceSizes: SettingCalculateBasePriceSizesEnum = Field(..., description="Element defining the way of calculating product base price basing on prices of sizes. If value is not provided, the base price will be calculated basing on prices of sizes with stock levels. In case of lack of the stock levels, the base price will be calculated basing on prices of all sizes")
    settingAddingCategoryAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new categories can be added when category linked with product couldn't be found in system") # just in case set to NO
    settingAddingSizeAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new product sizes can be added when size linked with product couldn't be found in system") # just in case set to NO
    settingAddingProducerAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new producers can be added when producer linked with product couldn't be found in system") # just in case set to NO
    settingAddingSeriesAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="Object determines if new product series can be added when series linked with product couldn't be found in system") # just in case set to NO
    settingAddingSizeschartAllowed: BooleanStrShortEnum = Field(..., description="Element determines, whether new size charts can be added, when no size chart assigned to sizes is not found in the system. Default = n")
    settingDefaultCategory: SettingDefaultCategoryModel = Field(..., description="Object determines default category which will be linked with product when it will not be linked with any category")
    settingDefaultSizesGroup: SettingDefaultSizesGroupModel = Field(..., description="Element specifying the default size group that will be assigned to the new product in case no size group has been explicitly assigned")
    settingTextIdSeparator: str | None = Field(None, description="Delimiter separating elements of text ID")
    settingIgnoreRetailPricesInCaseOfPromotion: BooleanStrShortEnum = Field(..., description="Element indicating if retail price in special offer should be ignored")
    returnPromotionStatus: BooleanStrShortEnum = Field(..., description="Element indicating if information about special offer should be retrieved")
    settingsRestoreDeletedProducts: BooleanStrShortEnum = Field(..., description="Element specifying whether the item is to be restored after deletion")
    settingsAddingDefaultShopMaskAllowed: BooleanStrShortEnum = Field(BooleanStrShortEnum.NO, description="The item shall determine whether the default visibility in stores can be set if a new commodity is to be created and no parameters have been uploaded to set visibility in at least one store") # just in case set to NO
    settingsAddingManuallySelectedShopMaskAllowed: int | None = Field(None, description="Element specifying whether the default visibility in stores can be set according to the list of stores indicated in the web import source configuration, if a new product will be created and no parameters have been sent to set visibility in at least one store")
    settingAddingSupplierAllowed: BooleanStrShortEnum = Field(..., description="Element specifying whether the system should create a new provider in case of not finding one in the panel")
    settingActualizeDelivererMode: SettingActualizeDelivererModeEnum = Field(..., description="The element specifies how to update the product supplier")
    settingDeleteIndividualDescriptionsByShopsMask: SettingDeleteIndividualDescriptionsByShopsMaskModel = Field(..., description="Element specifying the mask of stores for which individual names and descriptions are to be removed")
    settingDeleteIndividualMetaByShopsMask: SettingDeleteIndividualMetaByShopsMaskModel = Field(..., description="Element that specifies the mask of stores for which individual meta updated products are to be removed")
    settingsSkipDuplicatedProducers: bool = Field(..., description="Automatically skip adding manufacturer code and external system code in the product when adding goods if a duplicate code is encountered in other products")


# --- Search DTOs
class AvailablePaymentFormsSearchModel(BaseModel):
    prepaid: bool = Field(..., description="...")
    cashOnDelivery: bool = Field(..., description="Cash on delivery")
    tradeCredit: bool = Field(..., description="...")

class FreeShippingSettingsSearchModel(BaseModel):
    mode: ModeSearchEnum = Field(..., description="Edition mode")
    availablePaymentForms: List[AvailablePaymentFormsSearchModel] = Field(..., description="Set free shipping for the payment method only")
    availableCouriers: List[int] = Field(..., description="List of courier services for which shipping is free. IDs couriers")
    availableCouriersForSingleProduct: List[int] = Field(...,  description="List of courier services by which the products can be sent free of charge. IDs couriers")
    availableRegions: List[int] = Field(..., description="List of regions with free shipment. IDs Delivery regions")

class ReturnOptionsSearchModel(BaseModel):
    enabled: bool = Field(..., description="...")
    firm: bool = Field(..., description="...")
    hurt: bool = Field(..., description="...")
    detalist: bool = Field(..., description="...")

class ReturnProductSettingsSearchModel(BaseModel):
    returnOptions: ReturnOptionsSearchModel = Field(..., description="Product can be returned")
    byOwnService: BooleanStrLongEnum = Field(..., description="...")
    byInPostSzybkieZwrotyByIAI: BooleanStrLongEnum = Field(..., description="...")

class ShippingSettingsSearchModel(BaseModel):
    codDisabled: BooleanStrLongEnum = Field(..., description="...")
    dvpOnly: BooleanStrLongEnum = Field(..., description="...")
    insuranceOnly: BooleanStrLongEnum = Field(..., description="...")
    atypicalSize: bool = Field(..., description="...")
    excludeSmileService: bool = Field(..., description="Exclusion from the Smile service")
    disallowedCouriers: List[int] = Field(..., description="List of courier services which cannot be used to ship this product. IDs couriers")

class DispatchSettingsSearchModel(BaseModel):
    enabled: bool = Field(..., description="...")
    shippingSettings: ShippingSettingsSearchModel = Field(..., description="...")
    freeShippingSettings: FreeShippingSettingsSearchModel = Field(..., description="...")
    returnProductSettings: ReturnProductSettingsSearchModel = Field(..., description="...")

class MenuItemsTextIdsSearchModel(BaseModel):
    menuItemTextId: str = Field(..., description="Menu element text identifier. Example: 'item1\item2\item3'") # type: ignore
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    menuId: StrictInt = Field(..., ge=1, description="ID of the menu zone displayed in the mask")
    menuItemTextIdSeparator: str = Field(..., description="The separator separates the individual elements of a text id. Default: ''")

class PicturesDataSearchModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    serviceId: StrictInt = Field(..., ge=1, description="External service identifier")

class PoductMenuItemsSearchModel(BaseModel):
    menuItemsIds: List[int] = Field(..., description="An array of IDs")
    menuItemsTextIds: List[MenuItemsTextIdsSearchModel] = Field(..., description="An array of text IDs")

class CategoriesSearchModel(BaseModel):
    categoryId: StrictInt = Field(..., ge=1, description="Category id")
    categoryName: str = Field(..., description="Category name")

class ProducersSearchModel(BaseModel):
    categoryId: StrictInt = Field(..., ge=1, description="Category id")
    categoryName: str = Field(..., description="Category name")

class ProductParamsSearchModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    productCode: str = Field(..., description="External product system code")
    productName: str = Field(..., description="Product name")
    productSizeCodeExternal: str = Field(..., description="External product system code for size")
    productProducerCode: str = Field(..., description="Producer code")
    productIsGratis: BooleanStrShortEnum = Field(..., description="The product is free of charge. Possible values: 'y' - is free of charge, 'n' - is not free of charge")

class ProductIndexesSearchModel(BaseModel):
    productIndex: str = Field(..., description="One of the unique, indexed product codes (IAI code / External system code / Producer code)")

class ProductShopsSearchModel(BaseModel):
    shopsMask: StrictInt = Field(..., ge=1, description="it mask of shop IDs. Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")

    @model_validator(mode='after')
    def validate_shops_mask(self):
        """Validate that shopsMask is a positive bitmask value."""
        if self.shopsMask <= 0:
            raise ValueError("shopsMask must be positive")
        # Validate that shopsMask is a valid combination of powers of 2 (valid bitmask)
        if self.shopsMask & (self.shopsMask + 1) != 0 and (self.shopsMask & (self.shopsMask - 1)) != 0:
            # This is a more complex check - for now just ensure it's positive
            pass
        return self

class ProductDateSearchModel(BaseModel):
    productDateMode: ProductDateModeSearchEnum = Field(..., description="Date type")
    productDateBegin: str = Field(..., description="Starting date in the YYYY-MM-DD format")
    productDateEnd: str = Field(..., description="End date in the YYYY-MM-DD format")

class ProductParameterIdsSearchModel(BaseModel):
    productParameterIdsEnabled: List[int] = Field(..., description="Set properties groups ID")
    productParameterIdsDisabled: List[int] = Field(..., description="Unset properties groups ID")

class ProductParametersParamsSearchModel(BaseModel):
    parameterNames: List[str] = Field(..., description="Parameters group name")
    parameterValuesIds: List[int]  = Field(..., description="Properties IDs")
    parameterValuesNames: List[str] = Field(..., description="Parameters name")
    productParameterIds: ProductParameterIdsSearchModel = Field(..., description="Parameters group ID")

class SeriesDescriptionsLangDataSearchModel(BaseModel):
    seriesName: str = Field(..., description="Name of series in indicated language")
    langId: str = Field(..., description="Language ID")

class ProductSeriesParams(BaseModel):
    seriesId: StrictInt = Field(..., ge=1, description="ID of series, to which product belongs")
    seriesPanelName: str = Field(..., description="Name of series, to which the product belongs, visible in panel")
    seriesDescriptionsLangData: List[SeriesDescriptionsLangDataSearchModel] = Field(..., description="Names of series in indicated language visible in shop")

class ProductUnitsSearchModel(BaseModel):
    unitId: StrictInt = Field(..., ge=1, description="Product unit of measure ID")
    unitName: str = Field(..., description="Product unit of measure name")
    unitPrecision: StrictInt = Field(..., ge=1, description="Unit of measure precision")

class ProductWarrantiesSearchModel(BaseModel):
    warrantyId: StrictInt = Field(..., ge=1, description="Product warranty ID")
    warrantyName: str = Field(..., description="Name of warranty for indicated product")

class ProductAvailableInStocksSearchModel(BaseModel):
    productIsAvailableInStocks: BooleanStrShortEnum = Field(..., description="Determines whether availability in stocks has been set")
    productAvailableInStocksIds: List[int] = Field(..., description="Narrowing list to stocks sought trough Empty list concerns all stocks")

class ProductAvailableInAuctionsSearchModel(BaseModel):
    productIsAvailableInAuctions: BooleanStrShortEnum = Field(..., description="Determines whether availability on auctions has been set")
    productAvailableInAuctionsAccountsIds: List[int] = Field(..., description="Narrow list of auction accounts sought through")

class SearchByShopsModel(BaseModel):
    searchModeInShops: SearchModeInShopsEnum = Field(..., description="Determine data search method on basis of options set for stores. Available values: 'in_one_of_selected' - in one of indicated stores, 'in_all_of_selected' - in all indicated stores, This parameter is optional. When it's lacking, search is performed by option: in one of indicated stores (in_one_of_selected)")
    shopsMask: StrictInt = Field(..., ge=1, description="it mask of shop IDs. Mask for indicated store is calculated on basis of following formula: 2^(store_ID - 1). If the product should be available in more than one shop, the masks should be summed up")
    shopsIds: List[int] = Field(..., description="List of stores IDs When mask is determined, this parameter is omitted")

    @model_validator(mode='after')
    def validate_shops_mask(self):
        """Validate that shopsMask is a positive value."""
        if self.shopsMask <= 0:
            raise ValueError("shopsMask must be positive")
        return self

class ProductSearchPriceRangeSearchModel(BaseModel):
    productSearchPriceMode: ProductSearchPriceModeEnum = Field(..., description="Determines price type for indicated values")
    productSearchPriceMin: float = Field(..., ge=0, description="Minimal price for product")
    productSearchPriceMax: float = Field(..., ge=0, description="Maximum price for product")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")

class ProductTypeSearchModel(BaseModel):
    productTypeInItem: bool = Field(..., description="Should collections be returned. By default this parameter is set on true")
    productTypeInBundle: bool = Field(..., description="Should collections be returned. By default this parameter is set on true")
    productTypeInCollection: bool = Field(..., description="Should collections be returned. By default this parameter is set on true")
    productTypeInPackaging: bool = Field(..., description="Should packagings be returned on list. By default this parameter is set on true")
    productTypeInService: bool = Field(..., description="Should services be returned. By default this parameter is set on true")
    productTypeInVirtual: bool = Field(..., description="Should virtuals be returned. By default this parameter is set on true")
    productTypeInConfigurable: bool = Field(..., description="Should configurable be returned. By default this parameter is set on true")
