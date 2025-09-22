import re
from enum import Enum, StrEnum
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field, StrictInt, BeforeValidator
from typing_extensions import Annotated


# --- Constraints
NAME_MAX_LEN = 255
DESC_MAX_LEN = 2000
BATCH_MIN = 1
BATCH_MAX = 100


# --- Enums
class AllYNEnum(StrEnum):
    ALL = 'all'
    YES = 'y'
    NO = 'n'

class BooleanStrLongEnum(StrEnum):
    """yes/no"""
    YES = 'yes'
    NO = 'no'

class BooleanStrShortEnum(StrEnum):
    """y/n"""
    YES = 'y'
    NO = 'n'

class ElementNameSearchEnum(StrEnum):
    ID = 'id' # product ID,
    NAME = 'name' # Product name,
    CODE = 'code' # Product code,
    PRODUCT_SIZECODE = 'product_sizecode' # External system code,
    CODE_PRODUCER = 'code_producer' # Producer code,
    RETAIL_PRICE = 'retail_price' # Retail price of the product,
    POS_PRICE = 'pos_price' # price for POS,
    VAT = 'vat' # Value of VAT,
    WHOLESALE_PRICE = 'wholesale_price' # wholesale price,
    MINIMAL_PRICE = 'minimal_price' # Minimal price,
    PICTURES_COUNT = 'pictures_count' # number of product photos,
    AUCTION_NAME = 'auction_name' # product name for auction sites,
    PRICECOMPARER_NAME = 'pricecomparer_name' # Product name for price comparison websites,
    VERSION_NAME = 'version_name' # Name of the good in the group,
    SERIES_NAME = 'series_name' # Name of the batch,
    CATEGORY_NAME = 'category_name' # Category name,
    DELIVERER_NAME = 'deliverer_name' # Supplier name,
    ADDING_TIME = 'adding_time' # Date of entry,
    MODIFICATION_TIME = 'modification_time' # date modified,
    PRICE_CHANGED_TIME = 'price_changed_time' # Date of last price change,
    QUANTITY_CHANGED_TIME = 'quantity_changed_time' # Date of modification of stock levels,
    CURRENCY = 'currency' # Currency DEPRECATED. This parameter is deprecated,
    CURRENCY_SHOP = 'currency_shop' # Currency,
    TAXCODE = 'taxcode' # PKWiU [PCPandS],
    META_TITLE = 'meta_title' # Products meta titles,
    META_DESCRIPTION = 'meta_description' # Products meta description,
    META_KEYWORDS = 'meta_keywords' # Products meta keywords,
    SUGGESTED_PRICE = 'suggested_price' # Recommended price.
    OBSERVED_CLIENTS = 'observed_clients' # Number of visitors, who signed up to re-availability notifications
    OBSERVED_TIME = 'observed_time' # Average time of waiting for availability notification
    WISHES_CLIENTS = 'wishes_clients' # Customers, who added product to favorites
    WISHES_TIME = 'wishes_time' # Average number of days, product is in favorites

class LanguageEnum(StrEnum):
    POLISH = "pol"
    ENGLISH = "eng"

class SortDirectionSearchEnum(StrEnum):
    ASC = 'ASC' # ascending,
    DESC = 'DESC' # descending


# --- Models
class PayerAddressBaseModel(BaseModel):
    payerAddressFirstName: str = Field(..., description="Buyer's first name")
    payerAddressLastName: str = Field(..., description="Buyer's last name")
    payerAddressFirm: str = Field(..., description="Company name")
    payerAddressNip: str = Field(..., description="Customer VAT ID")
    payerAddressStreet: str = Field(..., description="Buyer's street name and house number")
    payerAddressZipCode: str = Field(..., description="Buyer's postal code")
    payerAddressCity: str = Field(..., description="Buyer's city")
    payerAddressCountryId: str = Field(..., description="Country code in the ISO-3166-1 alpha-2 standard (2 letters)")
    payerAddressPhone: str = Field(..., description="Buyer's telephone number")

class OrdersBySearchModel(BaseModel):
    elementName: ElementNameSearchEnum = Field(..., description="Name of field, list will be sorted by")
    sortDirection: SortDirectionSearchEnum = Field(..., description="Determines sorting direction")

class PageableCamelModel(BaseModel):
    resultsPage: StrictInt | None = Field(None, ge=0, description="Page with results number. Numeration starts from 0")
    resultsLimit: StrictInt | None = Field(None, ge=BATCH_MIN, le=BATCH_MAX, description="Number of results on page. Value from 1 to 100")


# --- Paged Responses
class PagedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    results_number_all: StrictInt = Field(..., alias="resultsNumberAll", description="Number of all results found")
    results_number_page: StrictInt = Field(..., alias="resultsNumberPage", description="Number of pages of results found")
    results_page: StrictInt | None = Field(None, alias="resultsPage", description="Page with results number. Numeration starts from 0")
    results_limit: StrictInt | None = Field(None, alias="resultsLimit", ge=BATCH_MIN, le=BATCH_MAX, description="Number of results on page. Value from 1 to 100")

class PagedSnakecaseResponse(BaseModel):
    results_number_all: StrictInt = Field(..., description="Total number of found elements")
    results_number_page: StrictInt = Field(..., description="Number of pages of results found")
    results_page: StrictInt | None = Field(None, description="Page with results number. Numeration starts from 0")
    results_limit: StrictInt | None = Field(None, alias="resultsLimit", ge=BATCH_MIN, le=BATCH_MAX, description="Number of results on page. Value from 1 to 100")

# --- Base Gateway Models
class Gateway(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    def build_body(self) -> Dict: # type: ignore
        """Build the request body for the API.
        The API expects all payload fields nested under a top-level "params" key.
        This method serializes the model into a dictionary (using the model's
        serialization routine) and wraps the resulting mapping under "params".
        Serialization details:
        - Uses the model's dump/serialization method with aliases enabled so that
            field names follow the API's expected keys.
        - Omits fields with value None so they are not included in the payload.
        Returns:
                dict: A dictionary of the form {"params": { ... }} suitable for use
                as a JSON request body.
        Example:
                >>> body = instance.build_body()
                >>> assert "params" in body and isinstance(body["params"], dict)
        """

        return {"params": self.model_dump(by_alias=True, exclude_none=True)} # type: ignore

class AppendableGateway(Gateway):
    model_config = ConfigDict(extra = "forbid")

class PageableSnakeGateway(Gateway):
    model_config = ConfigDict(extra = "forbid")

    results_page: StrictInt | None = Field(None, ge=0, description="Page with results number. Numeration starts from 0")
    results_limit: StrictInt | None = Field(None, ge=BATCH_MIN, le=BATCH_MAX, description="Number of results on page. Value from 1 to 100")

class PageableCamelGateway(Gateway):
    model_config = ConfigDict(extra = "forbid")

    resultsPage: StrictInt | None = Field(None, ge=0, description="Page with results number. Numeration starts from 0")
    resultsLimit: StrictInt | None = Field(None, ge=BATCH_MIN, le=BATCH_MAX, description="Number of results on page. Value from 1 to 100")

# --- Fault
class FaultCodeString(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    fault_code: StrictInt = Field(..., alias="faultCode", description="Error code")
    fault_string: str = Field(..., alias="faultString", description="Error description")


# --- Methods
def _serialize_param_value(value: Any) -> Any:
    """
    Convert model field value to a query-safe representation:
    - Enum -> enum.value
    - list/tuple/set -> comma-separated string of items (uses enum.value for enum items)
    - other types are returned as-is
    """
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple, set)):
        parts = []
        for item in value: # type: ignore
            if isinstance(item, Enum):
                parts.append(str(item.value)) # type: ignore
            else:
                parts.append(str(item)) # type: ignore
        return ",".join(parts) # type: ignore
    return value

def build_query_params(model: "BaseModel", *, exclude_none: bool = True, by_alias: bool = True) -> Dict[str, Any]:
    """
    Dump a Pydantic model to a dict suitable for passing as HTTP query params:
    - excludes None values by default
    - uses field aliases by default (useful for camelCase)
    - serializes enums and lists according to OpenAPI style=form,explode=false (comma-separated)
    """
    raw = model.model_dump(exclude_none=exclude_none, by_alias=by_alias)
    return {k: _serialize_param_value(v) for k, v in raw.items()}


# --- Common Models
class ErrorsModel(BaseModel):
    """
    Common error model used across all API endpoints in 207 Multi-Status responses.
    Based on IdoSell API specification where errors have consistent structure.
    """
    faultCode: int | None = Field(None, description="Error code")
    faultString: str | None = Field(None, description="Error description")


# --- Date Types and Validators
class IdoSellDateValidator:
    """Common date validation patterns for IdoSell API"""

    # Standard ISO format: YYYY-MM-DD
    DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'

    # Standard datetime format: YYYY-MM-DD HH:MM:SS
    DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

    # PHP-style datetime format: Y-m-d H:i:s (same as standard but for clarity)
    PHP_DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

    @staticmethod
    def validate_date_format(v: str, pattern: str, format_name: str) -> str:
        """Validate string matches date pattern"""
        if not re.match(pattern, v):
            raise ValueError(f'{format_name} must be in correct format')
        return v

    @staticmethod
    def validate_datetime_format(v: str) -> str:
        """Validate YYYY-MM-DD HH:MM:SS format"""
        if not re.match(IdoSellDateValidator.DATETIME_PATTERN, v):
            raise ValueError('DateTime must be in YYYY-MM-DD HH:MM:SS format')
        return v

# Date field types with proper validation
def validate_date_format(v: str) -> str:
    """Validate YYYY-MM-DD format"""
    if not re.match(IdoSellDateValidator.DATE_PATTERN, v):
        raise ValueError('Date must be in YYYY-MM-DD format')
    return v

def validate_datetime_format(v: str) -> str:
    """Validate YYYY-MM-DD HH:MM:SS format"""
    if not re.match(IdoSellDateValidator.DATETIME_PATTERN, v):
        raise ValueError('DateTime must be in YYYY-MM-DD HH:MM:SS format')
    return v

def validate_php_datetime_format(v: str) -> str:
    """Validate Y-m-d H:i:s format"""
    if not re.match(IdoSellDateValidator.PHP_DATETIME_PATTERN, v):
        raise ValueError('DateTime must be in Y-m-d H:i:s format')
    return v

def validate_language_id(v: str) -> str:
    """Validate ISO-639-2 language code (3 letters)"""
    if len(v) != 3:
        raise ValueError('Language ID must be exactly 3 characters (ISO-639-2)')
    if not v.isalpha():
        raise ValueError('Language ID must contain only letters (ISO-639-2)')
    return v.lower()

# Date field type for YYYY-MM-DD format
IdoSellDate = Annotated[
    str,
    Field(description="Date in YYYY-MM-DD format"),
    BeforeValidator(validate_date_format)
]

# DateTime field type for YYYY-MM-DD HH:MM:SS format
IdoSellDateTime = Annotated[
    str,
    Field(description="DateTime in YYYY-MM-DD HH:MM:SS format"),
    BeforeValidator(validate_datetime_format)
]

# PHP DateTime field type for Y-m-d H:i:s format
IdoSellPhpDateTime = Annotated[
    str,
    Field(description="DateTime in Y-m-d H:i:s format"),
    BeforeValidator(validate_php_datetime_format)
]

# Language ID field type for ISO-639-2 codes (3-letter language codes)
IdoSellLanguageId = Annotated[
    str,
    Field(min_length=3, max_length=3, description="Language ID (code in ISO-639-2)"),
    BeforeValidator(validate_language_id)
]
