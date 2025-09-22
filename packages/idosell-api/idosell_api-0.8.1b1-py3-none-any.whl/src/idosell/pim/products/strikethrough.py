from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.pim.products._common import IdentModel, IdentTypeEnum, PriceRoundModeEnum


# --- Enums
class CalculateBasePriceSizesStrikethroughEnum(StrEnum):
    ALL = 'all'
    AVAILABLE = 'available'

class PriceChangeModeStrikethroughEnum(StrEnum):
    AMOUNT_SET = 'amount_set'
    AMOUNT_DIFF = 'amount_diff'
    PERCENT_DIFF = 'percent_diff'

class PriceChangeBasevalueStrikethroughEnum(StrEnum):
    PRICE = 'price'
    PRICE_MINIAL = 'price_minimal'
    PRICE_POS = 'price_pos'
    PRICE_SRP = 'price_srp'
    PRICE_CROSSED = 'price_crossed'

class PriceModeStrikethroughEnum(StrEnum):
    GROSS = 'gross'
    NET = 'net'


# --- DTOs
class StpSettingsModel(BaseModel):
    price_change_mode: PriceChangeModeStrikethroughEnum = Field(..., description="...")
    price_change_basevalue: PriceChangeBasevalueStrikethroughEnum = Field(..., description="...")
    retail_price_change_value: float = Field(..., description="Strikethrough retail price value change in relation to the starting price")
    wholesale_price_change_value: float = Field(..., description="Strikethrough wholesale price value change in relation to the starting price")

class ShopsStrikethroughModel(BaseModel):
    shop_id: StrictInt = Field(..., ge=1, description="Shop Id")
    stp_settings: StpSettingsModel = Field(..., description="...")

class SizesStrikethroughModel(BaseModel):
    ident: IdentModel = Field(..., description="Identifier type")
    stp_settings: StpSettingsModel = Field(..., description="...")
    shops: List[ShopsStrikethroughModel] = Field(..., description="Strikethrough price settings for the page")

class ProductsStrikethroughModel(BaseModel):
    ident: IdentModel = Field(..., description="Identifier type")
    sizes: List[SizesStrikethroughModel] = Field(..., description="List of sizes")
    stp_settings: StpSettingsModel = Field(..., description="...")
    shops: List[ShopsStrikethroughModel] = Field(..., description="Strikethrough price settings for the page")

class PutPricesPimProductsStrikethroughParamsModel(BaseModel):
    products: List[ProductsStrikethroughModel] = Field(..., description="Products list")

class PutPricesPimProductsStrikethroughSettingsModel(BaseModel):
    calculate_base_price_sizes: CalculateBasePriceSizesStrikethroughEnum = Field(..., description="...")
    price_mode: PriceModeStrikethroughEnum = Field(..., description="...")
    price_round_mode: PriceRoundModeEnum = Field(..., description="...")


# --- ENDPOINTS``
class GetPrices(Gateway):
    """
    Allows for getting information about product strikethrough price settings
    DOCS_URL: https://idosell.readme.io/reference/productsstrikethroughpricesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/strikethroughPrices')

    identType: IdentTypeEnum | None = Field(None, description="Identifier type")
    products: List[str] | None = Field(None, min_length=1, max_length=100, description="Products list") # type: ignore

class PutPrices(AppendableGateway):
    """
    Allows for editing product strikethrough price settings
    DOCS_URL: https://idosell.readme.io/reference/productsstrikethroughpricesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/strikethroughPrices')

    params: PutPricesPimProductsStrikethroughParamsModel = Field(..., description="Parameters transmitted to method")
    settings: PutPricesPimProductsStrikethroughSettingsModel = Field(..., description="Settings")
