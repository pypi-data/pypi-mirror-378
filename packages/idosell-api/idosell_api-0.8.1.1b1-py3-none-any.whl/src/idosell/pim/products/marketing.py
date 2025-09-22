from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, BooleanStrShortEnum, Gateway, IdoSellPhpDateTime
from src.idosell.pim.products._common import (
    AssignmentModeEnum, BasePricingEnum, CalculationMethodEnum, IdentTypeEnum, MarketingZonesModel,
    MarketingZonesPromotionModel, NewPriceSettingsModel, ProductsMarketingModel, PromotionElementsModel, ShopsPutZonesModel
)


# DTOs
class PostPromotionPimProductsMarketingParamsModel(BaseModel):
    promotionName: str = Field(..., min_length=1, description="Promotion name")
    shopsIds: Optional[List[StrictInt]] = Field(None, min_length=1, description="List of stores IDs (min 1 item when provided)") # type: ignore
    marketingZones: MarketingZonesPromotionModel = Field(..., description="Special zones")
    newPriceSettings: NewPriceSettingsModel = Field(..., description="Promotional price settings")
    startDate: IdoSellPhpDateTime = Field(..., description="Promotion start date in Y-m-d H:i:s format")
    endDate: IdoSellPhpDateTime = Field(..., description="Promotion end date in Y-m-d H:i:s format")
    changeProductsToVisibleWhileStarting: BooleanStrShortEnum = Field(..., description="Change the status of hidden products to visible while starting the special offer")
    removeProductsAfterStockLevelRunsDown: BooleanStrShortEnum = Field(..., description="After running out of stock, automatically remove from the promotion products added separately (does not apply to series, producers, categories and menu)")
    removeProductsAfterOwnStockLevelRunsDown: BooleanStrShortEnum = Field(..., description="After running out of own stock, automatically remove from the promotion products added separately (does not apply to series, producers, categories and menu)")
    reduceBasingPrice: BasePricingEnum = Field(..., description="Reduce based on price (net/gross)")
    calculationMethod: CalculationMethodEnum = Field(..., description="Price reduction calculation method")
    promotionElements: List[PromotionElementsModel] = Field(..., description="Elements to be affected by the promotion")

class PutPromotionPimProductsMarketingParamsModel(BaseModel):
    promotionId: str = Field(..., description="Promotion ID")
    promotionName: str = Field(..., description="Promotion ID")
    shopsIds: Optional[List[StrictInt]] = Field(None, min_length=1, description="List of stores IDs (min 1 item when provided)") # type: ignore
    marketingZones: MarketingZonesPromotionModel = Field(..., description="Special zones")
    newPriceSettings: NewPriceSettingsModel = Field(..., description="Promotional price settings")
    startDate: IdoSellPhpDateTime = Field(..., description="Promotion start date in Y-m-d H:i:s format")
    endDate: IdoSellPhpDateTime = Field(..., description="Promotion end date in Y-m-d H:i:s format")
    changeProductsToVisibleWhileStarting: BooleanStrShortEnum = Field(..., description="Change the status of hidden products to visible while starting the special offer")
    removeProductsAfterStockLevelRunsDown: BooleanStrShortEnum = Field(..., description="After running out of stock, automatically remove from the promotion products added separately (does not apply to series, producers, categories and menu)")
    removeProductsAfterOwnStockLevelRunsDown: BooleanStrShortEnum = Field(..., description="After running out of own stock, automatically remove from the promotion products added separately (does not apply to series, producers, categories and menu)")
    reduceBasingPrice: BasePricingEnum = Field(..., description="Reduce based on price (net/gross)")
    calculationMethod: CalculationMethodEnum = Field(..., description="Price reduction calculation method")
    removeAllPromotionElements: BooleanStrShortEnum = Field(..., description="Specifies whether to remove all existing promotion elements")
    promotionElements: List[PromotionElementsModel] = Field(..., description="Elements to be affected by the promotion")

class PutZonesPimProductsMarketingParamsModel(BaseModel):
    products: List[ProductsMarketingModel] = Field(..., description="Products list")
    assignment_mode: AssignmentModeEnum = Field(..., description="...")
    marketing_zones: Optional[MarketingZonesModel] = Field(None, description="Marketing zones (optional)")
    shops: List[ShopsPutZonesModel] = Field(..., min_length=1, description="Marketing hotspots in shops") # type: ignore


# --- ENDPOINTS
class GetAllFacebookCatalogIds(Gateway):
    """
    The method allows you to download available Facebook catalogs in a given store
    DOCS_URL: https://idosell.readme.io/reference/productsmarketingallfacebookcatalogidsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/marketing/allFacebookCatalogIds')

    shopId: StrictInt = Field(..., ge=1, description="Shop Id")

class GetPromotion(Gateway):
    """
    The method allows to download a list of active promotions for the given store
    DOCS_URL: https://idosell.readme.io/reference/productsmarketingpromotionget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/marketing/promotion')

    shopId: StrictInt | None = Field(None, ge=1, description="Shop Id")
    products: List[int] | None = Field(None, min_length=1, description="Products list") # type: ignore

class PostPromotion(AppendableGateway):
    """
    The method allows you to add promotions from a new module with elements
    DOCS_URL: https://idosell.readme.io/reference/productsmarketingpromotionpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/marketing/promotion')

    params: PostPromotionPimProductsMarketingParamsModel = Field(..., description="Parameters transmitted to method")

class PutPromotion(AppendableGateway):
    """
    The method allows you to edit the promotion from the new module with the elements
    DOCS_URL: https://idosell.readme.io/reference/productsmarketingpromotionput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/marketing/promotion')

    params: PutPromotionPimProductsMarketingParamsModel = Field(..., description="Parameters transmitted to method")

class GetZones(Gateway):
    """
    Allows for getting information about products assigned to marketing hot spots
    DOCS_URL: https://idosell.readme.io/reference/productsmarketingzonesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/marketingZones')

    identType: IdentTypeEnum | None = Field(None, description="Identifier type")
    products: Optional[List[str]] = Field(None, min_length=1, description="Products list (array of strings), min 1 when provided") # type: ignore

class PutZones(AppendableGateway):
    """
    Allows for assigning products to marketing hot spots
    DOCS_URL: https://idosell.readme.io/reference/productsmarketingzonesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/marketingZones')

    params: PutZonesPimProductsMarketingParamsModel = Field(..., description="Parameters transmitted to method")
