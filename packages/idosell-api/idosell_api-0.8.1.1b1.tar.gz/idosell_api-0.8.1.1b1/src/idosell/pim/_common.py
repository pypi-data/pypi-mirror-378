from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, StrictInt

from src.idosell._common import BooleanStrShortEnum
from src.idosell.pim.products._common import GraphicTypeEnum


# ---  Menu Enums
class FormatEnum(StrEnum):
    JPG = 'jpg'
    JPEG = 'jpeg'
    PNG = 'png'
    GIF = 'gif'
    SVG = 'svg'
    WEBP = 'webp'

class ItemTypeEnum(StrEnum):
    PRODUCTS = 'products'
    NAVIGATION = 'navigation'
    PRODUCTS_WITH_RICH_TEXT = 'products_with_rich_text'
    NAVIGATION_WITH_RICH_TEXT = 'navigation_with_rich_text'
    RICH_TEXT = 'rich_text'
    STATIC = 'static'
    LINK = 'link'

class HrefTargetEnum(StrEnum):
    SELF = '_self' # open on the same page
    BLANK = '_blank' # open in a new page

class DefaultViewEnum(StrEnum):
    NORMAL = 'normal'
    LIST = 'list'
    GALLERY = 'gallery'

class ActionEnum(StrEnum):
    EXPAND = 'expand' # Display subelements of the menu if any available, if not - create
    RELOAD = 'reload' # reload the page and open

class DisplayAllTypeEnum(StrEnum):
    PRODUCTS_LIST = 'products_list' # link to the list of products
    NAVIGATION_SITE = 'navigation_site' # link to the "Navigation" page

class MetaRobotsIndexEnum(StrEnum):
    DEFAULT = 'default' # automatically generate
    INDEX = 'index' # index
    NOINDEX = 'noindex' # noindex

class MetaRobotsFollowEnum(StrEnum):
    DEFAULT = 'default' # automatically generate
    FOLLOW = 'follow' # follow
    NOFOLLOW = 'nofollow' # nofollow

class MenuFilterValueSortEnum(StrEnum):
    Y = 'y'
    N = 'n'
    PRIORITY = 'priority'

class MenuFilterDisplayEnum(StrEnum):
    NAME = 'name'
    GFX = 'gfx'
    NAMEGFX = 'namegfx'

class ViewEnum(StrEnum):
    NORMAL = 'normal'
    LIST = 'list'
    GALLERY = 'gallery'

class SortByEnum(StrEnum):
    DATE = 'date'
    PRIORITY = 'priority'
    PRIORITYNAME = 'priorityName'
    NAME = 'name'
    PRICE = 'price'

class SortOrderEnum(StrEnum):
    ASC = 'asc'
    DESC = 'desc'

# --- Responsibility Enums
class EntityTypeEnum(StrEnum):
    PRODUCER = 'producer'
    PERSON = 'person'

# --- Sizecharts Enums
class DisplayModeEnum(StrEnum):
    ALL = 'all'
    SINGLE = 'single'

# --- Enums
class OperationSizesEnum(StrEnum):
    ADD = 'add'
    EDIT = 'edit'
    DEL = 'del'

# --- Warranties Enums
class FormatWarrantiesEnum(StrEnum):
    JPG = 'jpg'
    GIF = 'gif'
    PNG = 'png'

class DataTypeEnum(StrEnum):
    URL = 'url'
    BASE64 = 'base64'

class FieldEnum(StrEnum):
    WARRANTY_ID = 'warranty_id'
    WARRANTY_NAME = 'warranty_name'

class OrderEnum(StrEnum):
    ASCENDING = 'ascending'
    DESCENDING = 'descending'

class TypeEnum(StrEnum):
    SELLER = 'seller'
    PRODUCER = 'producer'

class WarrantyTypeEnum(StrEnum):
    SELLER = 'seller'
    PRODUCER = 'producer'


# --- Menu DTOs
class MenuFiltersActivePutFilterModel(BaseModel):
    menuFilterId: str = Field(..., description="Menu filter ID")
    menuFilterName: str = Field(..., description="Filter name on page")
    menuFilterDisplay: MenuFilterDisplayEnum = Field(..., description="Display as")
    menuFilterValueSort: MenuFilterValueSortEnum = Field(..., description="Sort by")
    menuFilterDefaultEnabled: BooleanStrShortEnum = Field(..., description="Enabled by default")

class MenuListPutSortModel(BaseModel):
    shop_id: StrictInt = Field(..., description="Shop Id")
    menu_id: StrictInt = Field(..., ge=1, description="Menu ID")
    lang_id: str = Field(..., description="Language ID")
    parent_id: StrictInt = Field(..., ge=1, description="Menu element text identifier")
    parent_textid: str = Field(..., description=r"Menu element text identifier. Example: 'item1\item2\item3'")
    recursive: BooleanStrShortEnum = Field(..., description="Recurring")

class SettingsPutSortModel(BaseModel):
    textid_separator: str = Field(..., description="Default: ''")

class SortLangDataModelModel(BaseModel):
    view: ViewEnum = Field(..., description="Default product list view")
    sort_by: SortByEnum = Field(..., description="Sort by")
    sort_order: SortOrderEnum = Field(..., description="Sort order")

class DisplayLimitLangDataModel(BaseModel):
    view: ViewEnum = Field(..., description="Default product list view")
    limit: StrictInt = Field(..., ge=1, description="Limit")

class GfxModel(BaseModel):
    base64: str = Field(..., description="Graphic encoded with Base64")
    format: FormatEnum = Field(..., description="Graphic format")

class LangDataModel(BaseModel):
    lang_id: str = Field(..., description="Language ID")
    name: str = Field(..., description="Menu element name")
    priority: StrictInt = Field(..., ge=1, description="Menu element order")
    description: str = Field(..., description="Description displayed at the top of products list")
    description_bottom: str = Field(..., description="Description displayed at the bottom of products list")
    link: str = Field(..., description="Own link")
    item_type: ItemTypeEnum = Field(..., description="...")
    meta_title: str = Field(..., description="Meta title")
    meta_description: str = Field(..., description="Meta description")
    meta_keywords: str = Field(..., description="Meta - keywords")
    url: str = Field(..., description="URL address")
    href_target: HrefTargetEnum = Field(..., description="Link target attribute")
    sort: List[SortLangDataModelModel] = Field(..., description="...")
    display_limit: List[DisplayLimitLangDataModel] = Field(..., description="...")
    default_view: DefaultViewEnum = Field(..., description="...")
    headline_name: str = Field(..., description="Headline name. Leaving this value empty will automatically generate name basing on a name in menu")
    expand: BooleanStrShortEnum = Field(..., description="Display by default nested elements")
    hidden: BooleanStrShortEnum = Field(..., description="Element of the menu hidden from the clients")
    action: ActionEnum = Field(..., description="After clicking on the element in the menu")
    display_all_type: DisplayAllTypeEnum = Field(..., description="...")
    display_all: BooleanStrShortEnum = Field(..., description="Display element 'show all'")
    allow_sort_change: BooleanStrShortEnum = Field(..., description="Disable changing 'sort by' for customers")
    allow_limit_change: BooleanStrShortEnum = Field(..., description="Disable possibility of changing the number of displayed products on the page by customers")
    node_gfx: BooleanStrShortEnum = Field(..., description="Disable possibility of changing the number of displayed products on the page by customers")
    gfx_active_type: GraphicTypeEnum = Field(..., description="Type of graphics - When the cursor is on the link")
    gfx_inactive_type: GraphicTypeEnum = Field(..., description="Type of graphics - When the cursor is outside link")
    gfx_omo_type: GraphicTypeEnum = Field(..., description="Type of graphics - When the link is opened")
    gfx_nav: GfxModel = Field(..., description="Graphic on the 'navigation' page")
    gfx_active: GfxModel = Field(..., description="Graphic - When the cursor is on the link")
    gfx_active_desktop: GfxModel = Field(..., description="Graphic - When the cursor is on the link - Desktop")
    gfx_active_tablet: GfxModel = Field(..., description="Graphic - When the cursor is on the link - Tablet")
    gfx_active_mobile: GfxModel = Field(..., description="Graphic - When the cursor is on the link - Mobile")
    gfx: GfxModel = Field(..., description="Graphic - When the cursor is outside link")
    gfx_inactive_desktop: GfxModel = Field(..., description="Graphic - When the cursor is outside link - Desktop")
    gfx_inactive_tablet: GfxModel = Field(..., description="Graphic - When the cursor is outside link - Tablet")
    gfx_inactive_mobile: GfxModel = Field(..., description="Graphic - When the cursor is outside link - Mobile")
    gfx_onmouseover: GfxModel = Field(..., description="Graphic - When the link is opened")
    gfx_omo_desktop: GfxModel = Field(..., description="Graphic - When the link is opened - Desktop")
    gfx_omo_tablet: GfxModel = Field(..., description="Graphic - When the link is opened - Tablet")
    gfx_omo_mobile: GfxModel = Field(..., description="Graphic - When the link is opened - Mobile")
    canonical_to_parent: BooleanStrShortEnum = Field(..., description="Add a canonical link that points to the parent menu item")
    meta_robots_index: MetaRobotsIndexEnum = Field(..., description="Meta robots index settings")
    meta_robots_follow: MetaRobotsFollowEnum = Field(..., description="Meta robots follow settings")

class MenuListDeleteModel(BaseModel):
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")
    menu_id: StrictInt = Field(..., ge=1, description="Menu ID")
    item_id: StrictInt = Field(..., ge=1, description="Menu element ID")
    item_textid: str = Field(..., description=r"Menu element text identifier. Example: 'item1\item2\item3'")

class MenuListPutModel(BaseModel):
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")
    menu_id: StrictInt = Field(..., ge=1, description="Menu Id")
    item_id: str = Field(..., description="Menu element ID")
    item_textid: str = Field(..., description=r"Menu element text identifier. Example: 'item1\item2\item3'")
    lang_data: List[LangDataModel] = Field(..., description="...")

class MenuListPostModel(BaseModel):
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")
    menu_id: StrictInt = Field(..., ge=1, description="Menu Id")
    parent_id: str = Field(..., description="Parent menu element ID")
    parent_textid: str = Field(..., description=r"Menu element text identifier. Example: 'item1\item2'")
    lang_data: List[LangDataModel] = Field(..., description="...")

class SettingsModel(BaseModel):
    textid_separator: str = Field(..., description="Default: ''")


# --- Responsibility DTOs
class EntitiesResponsibilityModel(BaseModel):
    code: str = Field(..., description="Short name/code")
    name: str = Field(..., description="Full name")
    mail: str = Field(..., description="E-mail address")
    street: str = Field(..., description="Street")
    number: str | None = Field(None, description="Building number")
    subnumber: str | None = Field(None, description="Apartment number")
    zipcode: str = Field(..., description="Zipcode")
    city: str = Field(..., description="City")
    country: str = Field(..., description="2-letter ISO country code")
    phone: str | None = Field(None, description="Phone number")
    description: str | None = Field(None, description="Additional description")
    url: str | None = Field(None, description="URL to contact page")

class EntitiesResponsibilityPostModel(EntitiesResponsibilityModel):
    id: int | None = Field(None, ge=1, description="Identificator of the entity")

class EntitiesResponsibilityPutModel(EntitiesResponsibilityModel):
    id: StrictInt = Field(..., ge=1, description="Identificator of the entity")


# --- Sizecharts DTOs
class ColumnsModel(BaseModel):
    columnNumber: StrictInt = Field(..., ge=1, description="Column number")
    columnTitle: str = Field(..., description="Column name")

class DescriptionsModel(BaseModel):
    columnNumber: StrictInt = Field(..., description="Column number")
    value: str = Field(..., description="Value")

class SizesModel(BaseModel):
    sizeId: str = Field(..., description="Size identifier")
    priority: StrictInt = Field(..., description="Priority")
    descriptions: List[DescriptionsModel] = Field(..., description="...")

class LanguagesDataModel(BaseModel):
    language: str = Field(..., description="Customer language ID")
    columns: List[ColumnsModel] = Field(..., description="...")
    sizes: List[SizesModel] = Field(..., description="List of sizes")

class SizeChartsPutModel(BaseModel):
    id: StrictInt = Field(..., ge=1, description="Id")
    nameInPanel: str = Field(..., description="Name in panel")
    displayMode: DisplayModeEnum = Field(..., description="Display mode")
    languagesData: List[LanguagesDataModel] = Field(..., description="...")


# --- Sizes DTOs
class LangDataSizesModel(BaseModel):
    lang_id: str = Field(..., description="Language code. Codes are compliant with ISO-639-3")
    name: str = Field(..., description="Category plural name")

class SizesPutModel(BaseModel):
    faultCode: StrictInt = Field(..., description="Error code")
    faultString: str = Field(..., description="Error description")
    group_id: StrictInt = Field(..., ge=1, description="Size group ID")
    id: str = Field(..., description="Size identifier")
    name: str = Field(..., description="Category plural name")
    description: str = Field(..., description="Size description")
    operation: OperationSizesEnum = Field(..., description="Operation type")
    lang_data: List[LangDataSizesModel] = Field(..., description="...")


# --- Warranties DTOs
class LanguagesWarrantiesModel(BaseModel):
    language_id: str = Field(..., description="Language ID")
    language_name: str = Field(..., description="Language name")
    value: str = Field(..., description="Literal in selected language")

class DescriptionWarrantiesModel(BaseModel):
    languages: List[LanguagesWarrantiesModel] = Field(..., description="...")

class IconSettingsModel(BaseModel):
    format: FormatWarrantiesEnum = Field(..., description="...")
    data_type: DataTypeEnum = Field(..., description="...")

class LangWarrantiesModel(BaseModel):
    lang_id: str = Field(..., description="Warranty language id (numeric) (three letter sequence)")
    name: str = Field(..., description="Warranty name")
    icon: str = Field(..., description="Warranty icon for language")
    icon_settings: IconSettingsModel = Field(..., description="...")
    description: str = Field(..., description="Warranty description")

class LangDataWarrantiesModel(BaseModel):
    warranty_id: str | int = Field(..., description="Warranty ID (numeric or text based)")
    lang: List[LangWarrantiesModel] = Field(..., description="...")

class ResultsOrderWarrantiesGetModel(BaseModel):
    field: FieldEnum = Field(..., description="...")
    order: OrderEnum = Field(..., description="Sorting order")

class ShopnameWarrantiesModel(BaseModel):
    languages: List[LanguagesWarrantiesModel] = Field(..., description="...")

class WarrantiesPostModel(BaseModel):
    name: str = Field(..., description="Name")
    type: TypeEnum = Field(..., description="...")
    period: StrictInt = Field(..., ge=0, description="Warranty time. Default value 12")
    shopname: ShopnameWarrantiesModel = Field(..., description="Name of warranty")
    description: DescriptionWarrantiesModel = Field(..., description="Warranty description")

class WarrantiesPutModel(BaseModel):
    id: str | int = Field(..., description="Warranty ID (numeric or text based)")
    name: str = Field(..., description="Name")
    type: TypeEnum = Field(..., description="...")
    period: StrictInt = Field(..., ge=0, description="Warranty time. Default value 12")
