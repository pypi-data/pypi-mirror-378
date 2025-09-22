from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, StrictInt, model_validator

from src.idosell._common import BooleanStrLongEnum, BooleanStrShortEnum, ErrorsModel


# --- Enums
class AddTypeEnum(StrEnum):
    SELECTEDSIZES = 'selectedSizes' # Add products in sizes selected by me
    SELECTEDSIZESASSEPARATEITEMS = 'selectedSizesAsSeparateItems' # Add products with chosen sizes as a new item on the list
    ALLSIZES = 'allSizes' # Add entire products and leave size selection to customers
    ALLSIZESWITHVARIANTS = 'allSizesWithVariants' # Add an entire product with all variants and leave size and variant selection to customers

class AttachmentFileTypeEnum(StrEnum):
    AUDIO = 'audio'
    VIDEO = 'video'
    DOC = 'doc'
    OTHER = 'other'
    IMAGE = 'image'

class AttachmentTypeEnum(StrEnum):
    DEMO = 'demo'
    FULL = 'Full'

class DocumentTypeEnum(StrEnum):
    ENERGY_LABEL = 'energy_label'
    INSTRUCTION_WITH_SAFETY_INFORMATION = 'instruction_with_safety_information'
    USER_MANUAL = 'user_manual'
    INSTALLATION_INSTRUCTIONS = 'installation_instructions'
    PRODUCT_CARD = 'product_card'
    GUIDE = 'guide'
    OTHERS = 'others'

class IdentTypeEnum(StrEnum):
    ID = 'id'
    INDEX = 'index'
    CODEEXTERN = 'codeExtern'
    CODEPRODUCER = 'codeProducer'

class MetaRobotsSettingsFollowEnum(StrEnum):
    AUTO = 'auto'
    FOLLOW = 'follow'
    NOFOLLOW = 'nofollow'

class MetaRobotsSettingsIndexEnum(StrEnum):
    AUTO = 'auto'
    INDEX = 'index'
    NOINDEX = 'noindex'

class MetaSettingsEnum(StrEnum):
    AUTO = 'auto'
    CUSTOM = 'custom'

class SortModeGridEnum(StrEnum):
    D_RELEVANCE = 'd_relevance'
    D_DATE = 'd_date'
    A_DATE = 'a_date'
    D_PRIORITY = 'd_priority'
    A_PRIORITY = 'a_priority'
    A_PRIORITYNAME = 'a_priorityname'
    D_PRIORITYNAME = 'd_priorityname'
    D_PRIORITYONLY = 'd_priorityonly'
    A_PRIORITYONLY = 'a_priorityonly'
    A_NAME = 'a_name'
    D_NAME = 'd_name'
    A_PRICE = 'a_price'
    D_PRICE = 'd_price'

class ViewEnum(StrEnum):
    DEFAULT = 'default'
    OWN = 'own'

class DisplayInPanelEnum(StrEnum):
    ALL = 'all'
    FIRSTAVAILABLE = 'firstAvailable'

class DisplayOnPageEnum(StrEnum):
    ALL = 'all'
    FIRSTAVAILABLE = 'firstAvailable'
    SPECIFIED = 'specified'

class FilterValueSortEnum(StrEnum):
    NO = 'n' # by frequency and order of occurrence of indicated parameter value in found products
    PRIORITY = 'priority' # according to value sequence in parameter
    YES = 'y' # alfabetically

class FilterDisplayEnum(StrEnum):
    NAME = 'name' # text
    GFX = 'gfx' # graphics
    NAMEGFX = 'namegfx' # text and graphics

class GraphicTypeEnum(StrEnum):
    IMG = 'img' # Image (one size for computers, tablets and smartphones, not recommended)
    IMG_RWD = 'img_rwd' # Image (three sizes for RWD)

class OperationEnum(StrEnum):
    ADD = 'add' # adds new category,
    DEL = 'del' # deletes existing category
    EDIT = 'edit' # edits existing category

class ProductsImagesSourceTypeEnum(StrEnum):
    BASE64 = 'base64'
    URL = 'url'

class ProductIconTypeEnum(StrEnum):
    AUCTION = 'auction'
    GROUP = 'group'
    SHOP = 'shop'

class SourceTypeEnum(StrEnum):
    BASE64 = 'base64'
    URL = 'url'

class TypeEnum(StrEnum):
    HTML = 'html'
    PHOTO = 'photo'
    TEXT = 'text'
    VIDEO = 'video'

# --- Marketing Enums
class AssignmentModeEnum(StrEnum):
    AUTO = 'auto'
    MANUAL = 'manual'

class BasePricingEnum(StrEnum):
    GROSS = 'gross'
    NET = 'net'

class CalculationMethodEnum(StrEnum):
    CHOOSEADVANTAGEOUS = 'chooseAdvantageous'
    SUM = 'sum'

class ElementTypeEnum(StrEnum):
    PRODUCT = 'product'
    SERIES = 'series'
    PRODUCER = 'producer'
    CATEGORY = 'category'
    MENU = 'menu'

class ModeEnum(StrEnum):
    PERCENT_DIFF = 'percent_diff'
    AMOUNT_DIFF = 'amount_diff'
    AMOUNT_SET = 'amount_set'

# --- Miscs Enums
class AttachmentEnableEnum(StrEnum):
    ALL = 'all'
    ORDERED = 'ordered'
    WHOLESALER = 'wholesaler'
    WHOLESALER_OR_ORDERED = 'wholesaler_or_ordered'
    WHOLESALER_AND_ORDERED = 'wholesaler_and_ordered'

class ProductIdBySizeCodeEnum(StrEnum):
    EXTERNAL = 'external'
    PRODUCER = 'producer'
    ALL = 'all'

class ProductIdentTypeCodeExistanceEnum(StrEnum):
    ID = 'id'
    INDEX = 'index'
    CODEEXTERN = 'codeExtern'
    CODEPRODUCER = 'codeProducer'
    CODEDELIVERER = 'codeDeliverer'

# --- Omnibus Enums
class OmnibusPriceManagementEnum(StrEnum):
    AUTOMATIC = 'automatic'
    MANUAL = 'manual'

# --- Opinions Enums
class ElementNameEnum(StrEnum):
    DATE = 'date' # Date of adding an opinion
    RATING = 'rating' # Rating attached to opinion
    SCOREPOSITIVE = 'scorePositive' # Usefulness of the opinion - number of positive ratings
    SCORENEGATIVE = 'scoreNegative' #  Usefulness of the opinion - number of negative ratings
    MODIFICATIONDATETIME = 'modificationDatetime' # Last modification date

class SortDirectionEnum(StrEnum):
    ASC = 'ASC' # ascending
    DESC = 'DESC' # descending

class RateEnum(StrEnum):
    POSITIVE = 'positive'
    NEGATUVE = 'negative'

class OpinionsTypeEnum(StrEnum):
    ID = 'id'
    LOGIN = 'login'
    CODEEXTERN = 'codeExtern'

class TypeProductsGetEnum(StrEnum):
    ID = 'id'
    INDEX = 'index'
    CODEEXTERN = 'codeExtern'
    CODEPRODUCER = 'codeProducer'

class TypeProductsEnum(StrEnum):
    ID = 'id'
    INDEX = 'index'
    CODEEXTERN = 'codeExtern'
    CODEPRODUCER = 'codeProducer'

# --- Parameters Enums
class ContextIdParametersEnum(StrEnum):
    # Takes values context_value_id
    # - Value of additional feature is set automatically basing on the parameter's value. (if not defined)

    # 1. Status
    # - CONTEXT_STATE_NEW - New,
    # - CONTEXT_STATE_USED - Used,
    # - CONTEXT_STATE_USED_EXCELLENT - Used - excellent condition
    # - CONTEXT_STATE_USED_VERYGOOD - Used - very good condition
    # - CONTEXT_STATE_USED_CORRECT - Used - good condition
    # - CONTEXT_STATE_USED_ACCEPTABLE - Used - acceptable condition
    # - CONTEXT_STATE_REFURBISHED_EXCELLENT - Refurbished - excellent condition
    # - CONTEXT_STATE_REFURBISHED_VERYGOOD - Refurbished - very good condition
    # - CONTEXT_STATE_REFURBISHED_CORRECT - Refurbished - good condition
    # - CONTEXT_STATE_NEW_OTHERS - New other (see details)
    # - CONTEXT_STATE_NEW_WITH_DEFECTS - New with defects
    # - CONTEXT_STATE_NEW_OEM - New - OEM
    # - CONTEXT_STATE_NEW_OPEN_BOX - New - open box
    # - CONTEXT_STATE_REFURBISHED_BY_PRODUCER - Renewed by a manufacturer,
    # - CONTEXT_STATE_REFURBISHED_BY_SELLER - Renewed by a seller,
    # - CONTEXT_STATE_FOR_PARTS_OR_BROKEN - In parts or damaged.
    CONTEXT_STATE = '1'

    # 2. Product weight in grams:
    CONTEXT_STD_UNIT_WEIGHT = '2'

    # 3. A product's value in milliliters:
    CONTEXT_STD_UNIT_VOLUME = '3'

    # 4. Sex:
    # - CONTEXT_SEX_MAN - Man,
    # - CONTEXT_SEX_WOMAN - Woman,
    # - CONTEXT_SEX_UNISEX - Unisex.
    CONTEXT_SEX = '4'

    # 5. Age group:
    # - CONTEXT_AGE_GROUP_ADULT - Adults,
    # - CONTEXT_AGE_GROUP_MINOR - Children.
    CONTEXT_AGE_GROUP = '5'

    # 6. Maximum number of products in an order:
    CONTEXT_MAX_QUANTITY_PER_RETAIL_ORDER = '6'

    # 7. Maximum number of products in a wholesale order:
    CONTEXT_MAX_QUANTITY_PER_WHOLESALE_ORDER = '7'

    # 8. Minimal number of products in an order:
    CONTEXT_MIN_QUANTITY_PER_RETAIL_ORDER = '8'

    # 9. Minimum number of products in a wholesale order:
    CONTEXT_MIN_QUANTITY_PER_WHOLESALE_ORDER = '9'

    # 10. Maximal number of a single size in an order:
    CONTEXT_MAX_SIZE_QUANTITY_PER_RETAIL_ORDER = '10'

    # 11. Maximal number of a single size in a wholesale order:
    CONTEXT_MAX_SIZE_QUANTITY_PER_WHOLESALE_ORDER = '11'

    # 12. Minimal number of a single size in an order:
    CONTEXT_MIN_SIZE_QUANTITY_PER_RETAIL_ORDER = '12'

    # 13. Minimal number of a single size in a wholesale order:
    CONTEXT_MIN_SIZE_QUANTITY_PER_WHOLESALE_ORDER = '13'

    # 14. Net weight:
    CONTEXT_WEIGHT_NET = '14'

    # 15. Color:
    CONTEXT_COLOR = '15'

    # 16. #!TylkoDlaDoroslych!#:
    # - CONTEXT_ONLY_ADULTS_YES - yes,
    # - CONTEXT_ONLY_ADULTS_NO - no.
    CONTEXT_ONLY_ADULTS = '16'

    # 17. Prescription drug:
    # - CONTEXT_PRESCRIPTION_MEDICINE_YES - yes,
    # - CONTEXT_PRESCRIPTION_MEDICINE_NO - no.
    CONTEXT_PRESCRIPTION_MEDICINE = '17'

    # 18. Season Rate:
    # - CONTEXT_SEASON_SPRING - Spring,
    # - CONTEXT_SEASON_SUMMER - Summer,
    # - CONTEXT_SEASON_FALL - Autumn,
    # - CONTEXT_SEASON_WINTER - Winter,
    # - CONTEXT_SEASON_SPRING_SUMMER - Spring/Summer,
    # - CONTEXT_SEASON_FALL_WINTER - Autumn/Winter
    CONTEXT_SEASON = '18'

    # 19. Risk - signal word:
    # - CONTEXT_HAZMAT_SIGNAL_DANGER - danger,
    # - CONTEXT_HAZMAT_SIGNAL_WARNING - warnging,
    # - CONTEXT_HAZMAT_SIGNAL_CAUTION - caution,
    # - CONTEXT_HAZMAT_SIGNAL_NOTICE - notice,
    CONTEXT_HAZMAT_SIGNAL = '19'

    # 20. Risk - warning pictogram
    # - GHS01, GHS02, GHS03, GHS04, GHS05, GHS06, GHS07, GHS08, GHS09
    CONTEXT_HAZMAT_PICTOGRAM = '20'

    # 21. Risk - type of hazard:
    # - H200, H201, H202, H203, H204, H205, H220, H221, H222, H223, H224, H225, H226, H228, H240, H241, H242, H250, H251, H252, H260, H261, H270, H271, H272,
    # H280, H281, H290, H300, H301, H302, H304, H310, H311, H312, H314, H315, H317, H318, H319, H330, H331, H332, H334, H335, H336, H340, H341, H350, H351, H360,
    # H361, H362, H370, H371, H372, H373, H400, H410, H411, H412, H413, EUH 001, EUH 014, EUH 018, EUH 019, EUH 044, EUH 029, EUH 031, EUH 032, EUH 066,
    # EUH 070, EUH 071, EUH 201, EUH 201A, EUH 202, EUH 203, EUH 204, EUH 205, EUH 206, EUH 207, EUH 208, EUH 209, EUH 209A, EUH 210, EUH 401
    CONTEXT_HAZMAT_STATEMENT = '21'

    # 22. Repair score:
    # - The value of the additional feature is set automatically based on the parameter's value
    CONTEXT_REPAIR_SCORE = '22'

    # 23. Safety - information pictogram:
    # - 1 (Not suitable for small children)
    # - 2 (CE mark)
    CONTEXT_SAFETY_PICTOGRAM = '23'

    # 24. Safety - type of warning:
    # - 1 (Not suitable for children under 3 years)
    # - 2 (Keep out of the reach of children)
    # - 3 (Product contains a button cell or coin battery)
    # - 4 (Use under the direct supervision of adults)
    # - 5 (Required protective gear. Do not use in public traffic)
    # - 6 (Contains toy. Adult supervision recommended)
    # - 7 (To prevent possible injury from entanglement, remove this toy as soon as the child begins to crawl)
    # - 8 (Use only in shallow water under adult supervision)
    # - 9 (Only use under adult supervision)
    # - 10 (This toy does not provide protection)
    # - 11 (Contains fragrances that may cause allergies)
    # - 12 (For household use only).
    CONTEXT_SAFETY_STATEMENT = '24'

class IconsInputTypeParametersEnum(StrEnum):
    BASE64 = 'base64'
    URL = 'url'

# --- Questions Enums
class ProductIdentTypeQuestionsEnum(StrEnum):
    ID = 'id'
    CODEEXTERN = 'codeExtern'
    CODEPRODUCER = 'codeProducer'

# --- Series Enums
class FilterDisplaySeriesEnum(StrEnum):
    NAME = 'name' # text
    GFX = 'gfx' # graphics
    NAMEGFX = 'namegfx' # text and graphics

class PriceRoundModeEnum(StrEnum):
    NONE = 'none'
    VAL00 = '00'
    VAL99 = '99'
    VALX0 = 'x0'
    VALX9 = 'x9'


###
#
class AttachmentLanguagesModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    langName: str = Field(..., description="Language name")
    langValue: str = Field(..., description="Literal in selected language")

class AttachmentNameModel(BaseModel):
    attachmentLanguages: List[AttachmentLanguagesModel] = Field(..., description="List of languages")

class DocumentTypesModel(BaseModel):
    documentType: DocumentTypeEnum = Field(..., description="Document type")
    description: str = Field(..., description="Additional description")

class ProductLongDescriptionsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    productLongDescription: str = Field(..., description="Long product description")

class ProductLongDescriptionsModel(BaseModel):
    productLongDescriptionsLangData: List[ProductLongDescriptionsLangDataModel] = Field(..., description="...")

class ProductAuctionDescriptionsDataModel(BaseModel):
    productAuctionId: str = Field(..., description="Auction system ID")
    productAuctionSiteId: str = Field(..., description="Auction site ID")
    productAuctionName: str = Field(..., description="Product name for auction service")
    productAuctionAdditionalName: str = Field(..., description="Subtitle for auction service")
    productAuctionDescription: str = Field(..., description="Product description for marketplaces")

class ShopsConfigurationsBaseModel(BaseModel):
    headerName: str = Field(..., description="Name displayed in the website header")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    view: ViewEnum = Field(..., description="Products display settings")
    enableSort: bool = Field(..., description="Enable customers to change sorting")
    enableChangeDisplayCount: bool = Field(..., description="Enable customers to change the number of products displayed")
    numberOfProductsGrid: StrictInt = Field(..., ge=1, description="Number of displayed products")
    sortModeGrid: SortModeGridEnum = Field(..., description="Selected sorting mode")
    metaSettings: MetaSettingsEnum | None = Field(None, description="Meta settings")
    metaTitle: str | None = Field(None, description="Title")
    metaDescription: str | None = Field(None, description="Description")
    metaKeywords: str | None = Field(None, description="Keywords")
    metaRobotsSettingsIndex: MetaRobotsSettingsIndexEnum = Field(..., description="Meta robots settings for index attribute")
    metaRobotsSettingsFollow: MetaRobotsSettingsFollowEnum = Field(..., description="Meta robots settings for follow attribute")


# --- Bundles, Collections related
class ProductSizesBundlesCollectionsModel(BaseModel):
    size: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")


# --- Common DTOs
class IdentModel(BaseModel):
    type: IdentTypeEnum = Field(..., description="...")
    value: str = Field(..., description="Value")


# --- Brands DTOs
class FilterActiveModel(BaseModel):
    filterId: str = Field(..., description="Menu filter ID")
    filterName: str = Field(..., description="Filter name on page")
    filterDisplay: FilterDisplayEnum = Field(..., description="Display as: 'name' - text, 'gfx' - graphics, 'namegfx' - text and graphics")
    filterValueSort: FilterValueSortEnum = Field(..., description="Sort by: 'y' - alfabetically, 'n' - by frequency and order of occurrence of indicated parameter value in found products, 'priority' - according to value sequence in parameter")
    filterDefaultEnabled: BooleanStrShortEnum = Field(..., description="Enabled by default")

class ShopsConfigurationsModel(ShopsConfigurationsBaseModel):
    name: str = Field(..., description="Name")
    descriptionTop: str = Field(..., description="Description displayed at the top of products list")
    descriptionBottom: str = Field(..., description="Description displayed at the bottom of products list")

class ProductsListImagesConfigurationModel(BaseModel):
    graphicType: GraphicTypeEnum = Field(..., description="Type of graphics")
    singleGraphic: str = Field(..., description="Image (one size for computers, tablets and smartphones, not recommended)")
    pcGraphic: str = Field(..., description="!GrafikaDlaEkranowKomputera#!")
    tabletGraphic: str = Field(..., description="Graphics for tablets")
    phoneGraphic: str = Field(..., description="Graphics for smartphones")

class ProductCardImagesConfigurationModel(BaseModel):
    graphicType: GraphicTypeEnum = Field(..., description="Type of graphics")
    singleGraphic: str = Field(..., description="Image (one size for computers, tablets and smartphones, not recommended)")
    pcGraphic: str = Field(..., description="!GrafikaDlaEkranowKomputera#!")
    tabletGraphic: str = Field(..., description="Graphics for tablets")
    phoneGraphic: str = Field(..., description="Graphics for smartphones")

class LanguagesConfigurationsModel(BaseModel):
    productsListImagesConfiguration: ProductsListImagesConfigurationModel = Field(..., description="...")
    productCardImagesConfiguration: ProductCardImagesConfigurationModel = Field(..., description="Graphic displayed on product card")
    languageId: str = Field(..., description="Language ID (code in ISO-639-2)")
    shopsConfigurations: List[ShopsConfigurationsModel] = Field(..., description="...")

class ImagesSettingsModel(BaseModel):
    sourceType: SourceTypeEnum = Field(..., description="Images source type. Available values: base64 - image data encoded using the base64 algorithm (default), url - image file link")

class ProducerPostModel(BaseModel):
    nameInPanel: str = Field(..., description="Name in panel")
    imagesSettings: ImagesSettingsModel = Field(..., description="...")
    languagesConfigurations: List[LanguagesConfigurationsModel] = Field(..., description="...")

class ProducerPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Id")
    nameInPanel: str = Field(..., description="Name in panel")
    imagesSettings: ImagesSettingsModel = Field(..., description="...")
    languagesConfigurations: List[LanguagesConfigurationsModel] = Field(..., description="...")

# --- Bundles DTOs
class ProductIdentBundlesModel(BaseModel):
    productIdentType: IdentTypeEnum = Field(..., description="Identifier type")
    identValue: str = Field(..., description="Value")

class ProductSizesBundlesModel(BaseModel):
    size: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")

class ProductsBundlesPostModel(BaseModel):
    productIdent: ProductIdentBundlesModel = Field(..., description="Stock keeping unit")
    productSizes: ProductSizesBundlesModel = Field(..., description="Sizes available for products data")
    addType: AddTypeEnum = Field(..., description="Way of adding a product to a set")
    quantity: float = Field(..., description="Quantity of a component in a set")

class ProductPutRenewModel(BaseModel):
    productIdent: ProductIdentBundlesModel = Field(..., description="Stock keeping unit")
    productSizes: List[ProductSizesBundlesCollectionsModel] = Field(..., description="Sizes available for products data")
    addType: AddTypeEnum = Field(..., description="Way of adding a product to a set")
    quantity: StrictInt = Field(..., ge=1, description="Quantity of a component in a set")

class ProductsPutProductsQuantityModel(BaseModel):
    productIdent: ProductIdentBundlesModel = Field(..., description="Stock keeping unit")
    quantity: float = Field(..., ge=1, description="Quantity of a component in a set")

class ProductsBundlesPostProductsModel(BaseModel):
    productIdent: ProductIdentBundlesModel = Field(..., description="Stock keeping unit")
    productSizes: ProductSizesBundlesCollectionsModel = Field(..., description="Sizes available for products data")
    addType: AddTypeEnum = Field(..., description="Way of adding a product to a set")
    quantity: float = Field(..., description="Quantity of a component in a set")

class ProductsBundleDeleteProductsModel(BaseModel):
    productIdent: ProductIdentBundlesModel = Field(..., description="Stock keeping unit")


# --- Categories DTOs
class CategoriesModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Category id")
    parent_id: StrictInt = Field(..., ge=1, description="Parent category ID")
    priority: StrictInt = Field(..., ge=1, lt=20, description="Category priority. Value from 1 to 19")
    operation: OperationEnum = Field(..., description="Operation code")


# --- Collections DTOs
class CollectionIdentModel(BaseModel):
    collectionId: str = Field(..., description="Value")
    collectionIdentType: IdentTypeEnum = Field(..., description="Identifier type")

class ProductSizesPostModel(BaseModel):
    size: str = Field(..., description="Size identifier")

class ProductIdentCollectionsModel(BaseModel):
    productId: str = Field(..., description="Product IAI code")
    productIdentType: IdentTypeEnum = Field(..., description="Identifier type")

class ProductsCollectionsPostModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Component ID")
    productSizes: List[ProductSizesPostModel] = Field(..., description="Size chart in which a product will be added as a collection component. Required in case of mode selectedSizes and selectedSizesAsSeparateItems in addType")
    quantity: StrictInt = Field(..., ge=1, description="Quantity of a component in a collection")

class ProductsCollectionsPostProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Component ID")
    productSizes: List[ProductSizesPostModel] = Field(..., description="Size chart in which a product will be added as a collection component. Required in case of mode selectedSizes and selectedSizesAsSeparateItems in addType")
    addType: AddTypeEnum = Field(..., description="Way of adding a product to a collection")
    quantity: StrictInt = Field(..., ge=1, description="Quantity of a component in a collection")

class ProductsCollectionsPutRenewModel(BaseModel):
    productIdent: ProductIdentCollectionsModel = Field(..., description="Stock keeping unit")
    productSizes: List[ProductSizesBundlesCollectionsModel] = Field(..., description="Size chart in which a product will be added as a collection component. Required in case of mode selectedSizes and selectedSizesAsSeparateItems in addType")
    addType: AddTypeEnum = Field(..., description="Way of adding a product to a collection")
    quantity: StrictInt = Field(..., ge=1, description="Quantity of a component in a collection")

class ProductsCollectionsPutProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    quantity: StrictInt = Field(..., ge=1, description="Quantity of a component in a collection")

class ProductsCollectionsDeleteProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Component ID")


# --- Descriptions DTOs
class ProductIdentModel(BaseModel):
    identValue: str = Field(..., description="ID value")
    productIdentType: IdentTypeEnum = Field(..., description="Identifier type")

class SectionModel(BaseModel):
    type: TypeEnum = Field(..., description="")
    content: str = Field(..., description="HTML content depending on the type")

class DescriptionSectionsModel(BaseModel):
    section_1: SectionModel = Field(..., description="...")
    section_2: SectionModel = Field(..., description="...")

class ProductDescriptionSectionsModel(BaseModel):
    descriptionSections: List[DescriptionSectionsModel] = Field(..., description="...")

class ProductDescriptionsLangDataModel(BaseModel):
    langId: str = Field(..., description="Language ID")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    productName: str = Field(..., description="Product name")
    productAuctionName: str = Field(..., description="Product name for auction service")
    productPriceComparerName: str = Field(..., description="Product name for price comparison websites")
    productDescription: str = Field(..., description="Short product description")
    productLongDescription: str = Field(..., description="Long product description")
    productDescriptionSections: ProductDescriptionSectionsModel = Field(..., description="...")
    productAuctionLongDescription: str = Field(..., description="DEPRECATED. This parameter is deprecated. Long product description for external listings")
    productMetaTitle: str = Field(..., description="Product meta title")
    productMetaDescription: str = Field(..., description="Product meta description")
    productMetaKeywords: str = Field(..., description="Product meta keywords")

class ProductsDescriptionsModel(BaseModel):
    productIdent: ProductIdentModel = Field(..., description="...")
    productDescriptionsLangData: List[ProductDescriptionsLangDataModel] = Field(..., description="Array of language-dependent elements")
    productAuctionDescriptionsData: List[ProductAuctionDescriptionsDataModel] = Field(..., description="Product data for auction services")


# --- Groups DTOs
class GroupsPutSettingsModel(BaseModel):
    productIdent: ProductIdentModel = Field(..., description="...")
    displayInPanel: DisplayInPanelEnum = Field(..., description="Display on the product list in the panel")
    displayOnPage: DisplayOnPageEnum = Field(..., description="Display on a product list on the page")
    specifiedProductIdent: ProductIdentModel = Field(..., description="Selected product in the group")

class ProductsInOrderModel(BaseModel):
    productIdent: ProductIdentModel = Field(..., description="...")
    priority: StrictInt = Field(..., ge=1, description="The order of products in the group. Value needs to be more than 0")


# --- Images DTOs
class ProductsImagesSettingsModel(BaseModel):
    productsImagesSourceType: ProductsImagesSourceTypeEnum = Field(..., description="How to provide information about images of products")
    productsImagesApplyMacro: bool = Field(..., description="Whether images for products should be scalable")

class ProductIconsModel(BaseModel):
    productIconSource: str = Field(..., description="Photo in the goods list")
    deleteProductIcon: bool = Field(..., description="Flag indicating whether to remove the product icon")
    productIconType: ProductIconTypeEnum = Field(..., description="Icon type")

class ProductImagesModel(BaseModel):
    productImageSource: str = Field(..., description="Product photo")
    productImageNumber: StrictInt = Field(..., description="A product photo's number")
    productImagePriority: StrictInt = Field(..., ge=1, description="Picture priority")
    deleteProductImage: bool = Field(..., description="lag marking if a picture should be deleted")

class ProductsImages(BaseModel):
    productIdent: ProductIdentModel = Field(..., description="...")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    otherShopsForPic: List[int] = Field(..., description="List of shops for which photos will be added (including shop provided in shopId). If parameter is empty or not provided, photos will be added to all shops")
    productImages: List[ProductImagesModel] = Field(..., description="Product photos details")
    productIcons: List[ProductIconsModel] = Field(..., description="Product icons list")
    productImagesSettings: ProductsImagesSettingsModel = Field(..., description="Product settings")


# --- Marketing DTOs
class PromotionElementsModel(BaseModel):
    elementType: ElementTypeEnum = Field(..., description="...")
    elementId: str = Field(..., description="Identifier of the element affected by the promotion (in the case of a menu in the format: storeId-menuId-itemId)")

class MarketingZonesPromotionModel(BaseModel):
    promotion: BooleanStrShortEnum = Field(..., description="Reduced price")
    discount: BooleanStrShortEnum = Field(..., description="Discount")
    distinguished: BooleanStrShortEnum = Field(..., description="Distinguished product")
    special: BooleanStrShortEnum = Field(..., description="Special")
    new: BooleanStrShortEnum = Field(..., description="New")

class MarketingZonesModel(BaseModel):
    promotion: BooleanStrLongEnum = Field(..., description="Promoted product")
    discount: BooleanStrLongEnum = Field(..., description="Product on sale")
    distinguished: BooleanStrLongEnum = Field(..., description="Distinguished product")
    special: BooleanStrLongEnum = Field(..., description="Special product")

class NewPriceSettingsModel(BaseModel):
    type: TypeEnum = Field(..., description="...")
    discountValue: float = Field(..., gt=0, description="Discount value")
    currencyId: str = Field(..., description="ISO-4217 (3 letters)")
    mode: ModeEnum = Field(..., description="Edition mode")
    endValue: str = Field(..., description="Fractional price value")

class ProductsMarketingModel(BaseModel):
    ident: IdentModel = Field(..., description="Identifier type")
    assignment_mode: AssignmentModeEnum = Field(..., description="...")
    marketing_zones: MarketingZonesModel = Field(..., description="...")

class ShopsPutZonesModel(BaseModel):
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")
    assignment_mode: AssignmentModeEnum = Field(..., description="...")
    marketing_zones: MarketingZonesModel = Field(..., description="...")


# --- Miscs DTOs
class AttachmentsModel(BaseModel):
    attachmentUrl: str = Field(..., description="Attachment file link")
    attachmentName: str = Field(..., description="Attachment name")
    langId: str = Field(..., description="Language ID")
    attachmentFileType: AttachmentFileTypeEnum = Field(..., description="File type: audio, video, doc, other")
    attachmentEnable: AttachmentEnableEnum = Field(..., description="Type of customer, attachment should be available for: 'all','ordered','wholesaler','wholesaler_or_ordered','wholesaler_and_ordered'")
    attachmentId: StrictInt = Field(..., ge=1, description="Attachment ID")
    attachmentDownloadLog: BooleanStrShortEnum = Field(..., description="Attachment downloads record")
    attachmentFileExtension: str = Field(..., description="Attachment file extension")
    attachmentPriority: StrictInt = Field(..., ge=1, description="Attachment number")
    attachmentToDelete: bool = Field(..., description="Flag indicating if an attachment should be removed")
    documentTypes: List[DocumentTypesModel] = Field(..., description="Attachment document types list")

class AttachmentLimitsModel(BaseModel):
    attachmentDownloadsLimit: StrictInt = Field(..., ge=1, description="Number of downloads limit")
    attachmentDaysLimit: StrictInt = Field(..., ge=1, description="Number of days file should be available")


class VirtualAttachmentsBaseModel(BaseModel):
    attachmentUrl: str = Field(..., description="Attachment file link")
    attachmentName: AttachmentNameModel = Field(..., description="Attachment name")
    attachmentType: AttachmentTypeEnum = Field(..., description="Full version or sample")
    attachmentLimits: AttachmentLimitsModel = Field(..., description="Number of attachment downloads limit")
    attachmentId: StrictInt = Field(..., ge=1, description="Attachment ID")
    attachmentPriority: StrictInt = Field(..., ge=1, description="Attachment number")

class VirtualAttachmentsModel(VirtualAttachmentsBaseModel):
    attachmentToDelete: bool = Field(..., description="Flag indicating if an attachment should be removed")
    errors: ErrorsModel | None = Field(None, description="Information on error that occurred during gate call")

class ProductsDeliveryTimeProductsSearchModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product Id")
    sizeId: str = Field(..., description="Size identifier")
    sizePanelName: str = Field(..., description="Size name")
    productIndex: str = Field(..., description="Product IAI code")
    productSizeQuantity: StrictInt = Field(..., ge=0, description="Product quantity")

class ProductAttachmentPutModel(BaseModel):
    productIdent: ProductIdentModel = Field(..., description="Stock keeping unit")
    attachments: List[AttachmentsModel] = Field(..., description="Product attachments list")
    virtualAttachments: List[VirtualAttachmentsModel] = Field(..., description="List of product's virtual attachments")
    errors: ErrorsModel | None = Field(None, description="Information on error that occurred during gate call")
    attachmentsErrorsOccurred: bool = Field(..., description="Flag indicating if there are errors in results of attachments settings")
    virtualAttachmentsErrorsOccurred: bool = Field(..., description="Flag indicating if there are errors in results of virtual attachments settings")


# --- Omnibus DTOs
class OmnibusPricesModel(BaseModel):
    omnibusPriceManagement: OmnibusPriceManagementEnum = Field(..., description="How to manage the lowest price before promotion")
    omnibusPriceRetail: float = Field(..., description="Lowest retail price before active promotion (gross)")
    omnibusPriceWholesale: float = Field(..., description="Lowest wholesale price before active promotion (gross)")

class ShopsModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    omnibusPrices: OmnibusPricesModel = Field(..., description="Strikethrough price settings")

class SizesOmnibusModel(BaseModel):
    ident: IdentModel = Field(..., description="Identifier type")
    omnibusPrices: OmnibusPricesModel = Field(..., description="Strikethrough price settings")
    shops: List[ShopsModel] = Field(..., description="Strikethrough price settings for the page")

class ProductsOmnibusModel(BaseModel):
    ident: IdentModel = Field(..., description="Identifier type")
    sizes: List[SizesOmnibusModel] = Field(..., description="List of sizes")
    omnibusPrices: OmnibusPricesModel = Field(..., description="Strikethrough price settings")
    shops: List[ShopsModel] = Field(..., description="Strikethrough price settings for the page")


# --- Opinions DTOs
class ClientsOpinionsModel(BaseModel):
    type: TypeEnum = Field(..., description="...")
    value: str = Field(..., description="...")
    name: str = Field(..., description="...")
    email: str = Field(..., description="E-mail address")

class ProductsModel(BaseModel):
    type: TypeProductsEnum = Field(..., description="...")
    value: str = Field(..., description="...")

class OpinionsPostModel(BaseModel):
    createDate: str = Field(..., description="...")
    confirmed: bool = Field(..., description="...")
    rating: str = Field(..., description="...")
    content: str = Field(..., description="...")
    language: str = Field(..., description="Customer language ID")
    picture: str = Field(..., description="...")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    host: str = Field(..., description="...")
    clients: ClientsOpinionsModel = Field(..., description="Customer data")
    scorePositive: StrictInt = Field(..., ge=0, description="Number of positive ratings indicating opinion usefulness")
    scoreNegative: StrictInt = Field(..., ge=0, description="Number of negative ratings indicating opinion usefulness")
    products: ProductsModel = Field(..., description="Product")
    orderSerialNumber: StrictInt = Field(..., ge=1, description="Order serial number")
    shopAnswer: str = Field(..., description="Reply to an opinion")
    opinionConfirmedByPurchase: bool = Field(..., description="Opinion confirmed with purchase")

class OpinionGetModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="...")
    language: str = Field(..., description="Customer language ID")
    confirmed: bool = Field(..., description="...")
    host: str | None = Field(None, description="...")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")

class ProductsOpinionsGetModel(BaseModel):
    type: TypeProductsGetEnum = Field(..., description="...")
    value: str = Field(..., description="...")

class ClientsGetModel(BaseModel):
    type: TypeEnum = Field(..., description="...")
    value: str = Field(..., description="...")

class ScorePositiveGetModel(BaseModel):
    from_: StrictInt = Field(..., ge=1, description="Amount of positive score from", alias="from")
    to: StrictInt = Field(..., ge=1, description="Amount of positive score to")

    @model_validator(mode='after')
    def validate_range(self):
        """Validate that 'to' value is greater than or equal to 'from' value."""
        if self.to < self.from_:
            raise ValueError("'to' value must be greater than or equal to 'from' value")
        return self

class ScoreNegativeGetModel(BaseModel):
    from_: StrictInt = Field(..., ge=1, description="Amount of negative score from", alias="from")
    to: StrictInt = Field(..., ge=1, description="Amount of negative score to")

    @model_validator(mode='after')
    def validate_range(self):
        """Validate that 'to' value is greater than or equal to 'from' value."""
        if self.to < self.from_:
            raise ValueError("'to' value must be greater than or equal to 'from' value")
        return self

class DateRangeGetModel(BaseModel):
    begin: str = Field(..., description="...")
    end: str = Field(..., description="...")

class OrdersByGetModel(BaseModel):
    elementName: ElementNameEnum = Field(..., description="Field name by which a list will be sorted")
    sortDirection: SortDirectionEnum = Field(..., description="Determines sorting direction")


# --- Parameters DTOs
class CardIconsParametersModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")

class ContextIdParametersModel(BaseModel):
    context_id: ContextIdParametersEnum = Field(..., description="Parameter's additional feature")
    context_value_id: str | None = Field(None, description="value of additional feature - Values described in context_id")

class DescriptionsParametersModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")

class ItemTextIdsParametersModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")

class LinkIconsParametersModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")

class NamesParametersModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")

class SearchDescriptionParametersModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")

class TextIdsParametersSearchModel(BaseModel):
    languageId: str = Field(..., description="Language ID")
    value: str = Field(..., description="Text value")

class ItemsParametersModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Parameter ID")
    item_text_ids: List[ItemTextIdsParametersModel] = Field(..., description="Element text ID - can be entered instead of 'id'. Recognized save format: 'section' (without backslash), 'parameter' (parameter without assigned value)")
    names: List[NamesParametersModel] = Field(..., description="Names of section, parameter or value")
    descriptions: List[DescriptionsParametersModel] = Field(..., description="Descriptions of section, parameter or value")
    search_description: List[SearchDescriptionParametersModel] = Field(..., description="Search descriptions of parameter value")
    card_icons: List[CardIconsParametersModel] = Field(..., description="Icons of section, parameter or value to display on the product card")
    link_icons: List[LinkIconsParametersModel] = Field(..., description="Icons of section, parameter or value to display on the list of products")
    context_id: ContextIdParametersModel | None = Field(None, description="...")
    context_value_id: str | None = Field(None, description="value of additional feature - Values described in context_id")

class SettingsParametersPutModel(BaseModel):
    icons_input_type: IconsInputTypeParametersEnum = Field(..., description="...")


# --- Questions DTOs
class ProductIdentQuestionsModel(BaseModel):
    productId: str = Field(..., description="Product IAI code")
    productIdentType: ProductIdentTypeQuestionsEnum = Field(..., description="Identifier type")

class QuestionsPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Question ID")
    lang: str = Field(..., description="Language of the question e.g. 'pol', 'eng'")
    question: str = Field(..., description="Your question(base64)")
    answer: str = Field(..., description="Content of the answer(base64)")
    dateAdd: str = Field(..., description="The date the question was created")
    host: str = Field(..., description="The name and address of the host from which the question was added")
    author: str = Field(..., description="Author")
    productIdent: ProductIdentQuestionsModel = Field(..., description="Stock keeping unit")
    visible: BooleanStrShortEnum = Field(..., description="Visibility")
    priority: StrictInt = Field(..., ge=1, description="Priority")
    confirmed: BooleanStrShortEnum = Field(..., description="Validate the question")
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    answerDate: str = Field(..., description="Date of response")
    answerAuthor: str = Field(..., description="Response author")


# --- Series DTOs
class FiltersActiveSeriesModel(BaseModel):
    filterId: str = Field(..., description="Menu filter ID")
    filterName: str = Field(..., description="Filter name on page")
    filterDisplay: FilterDisplaySeriesEnum = Field(..., description="Display as")
    filterValueSort: FilterValueSortEnum = Field(..., description="Sort by")
    filterDefaultEnabled: BooleanStrShortEnum = Field(..., description="Enabled by default")

class ImagesConfigurationModel(BaseModel):
    graphicType: GraphicTypeEnum = Field(..., description="Type of graphics")
    singleGraphic: str = Field(..., description="Image (one size for computers, tablets and smartphones, not recommended)")
    pcGraphic: str = Field(..., description="Graphics for computer screens")
    tabletGraphic: str = Field(..., description="Graphics for tablets")
    phoneGraphic: str = Field(..., description="Graphics for smartphones")

class ShopsConfigurationsSeriesModel(ShopsConfigurationsBaseModel):
    language: str = Field(..., description="Customer language ID")
    nameOnPage: str = Field(..., description="Name on the page")
    description: str = Field(..., description="Description")
    imagesConfiguration: ImagesConfigurationModel = Field(..., description="...")

class SeriesPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Id")
    nameInPanel: str = Field(..., description="Name in panel")
    shopsConfigurations: List[ShopsConfigurationsSeriesModel] = Field(..., description="...")


# --- Supplier DTOs
class ProductSizesSupplierModel(BaseModel):
    sizeId: str = Field(..., description="Size identifier")
    sizeDelivererCode: str = Field(..., description="Supplier code for size")

class ProductDeliverersSupplierModel(BaseModel):
    delivererId: StrictInt = Field(..., ge=1, description="Supplier ID")
    productSizes: List[ProductSizesSupplierModel] = Field(..., description="Sizes available for products data")

class ProductsSupplierPutCodeModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    productDeliverers: List[ProductDeliverersSupplierModel] = Field(..., description="Suppliers data")

# sTODO - simplify class names, make them more readable
class ProductSizesProductDeliverersProductsPutProductDataModelModel(ProductSizesSupplierModel):
    quantity: float = Field(..., gt=0, description="Supplier's stock level")
    lastPrice: float = Field(..., gt=0, description="Last purchase price")
    lastPriceNet: float = Field(..., gt=0, description="Last net purchase price")

class ProductDeliverersProductsPutProductDataModel(BaseModel):
    delivererId: StrictInt = Field(..., ge=1, description="Supplier ID")
    productSizes: List[ProductSizesProductDeliverersProductsPutProductDataModelModel] = Field(..., description="Sizes available for products data")
    clearAllQuantities: bool = Field(..., description="!UstawieniePozwalaWyzerowacStanyMagazynowegoDostawcyDlaWszystkichRozmiarowDanegoProduktu!#")

class ProductsSupplierPutProductDataModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    productDeliverers: List[ProductDeliverersProductsPutProductDataModel] = Field(..., description="Suppliers data")
