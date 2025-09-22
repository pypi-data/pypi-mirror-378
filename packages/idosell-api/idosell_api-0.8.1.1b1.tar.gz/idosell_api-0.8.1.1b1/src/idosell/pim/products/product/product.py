from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt, model_validator

from src.idosell._common import BooleanStrShortEnum, AppendableGateway, Gateway, OrdersBySearchModel, PageableCamelGateway
from src.idosell.pim.products.product._common import (
    CategoriesSearchModel, DispatchSettingsSearchModel, PicturesDataSearchModel, PoductMenuItemsSearchModel, ProducersSearchModel,
    ProductAvailableInAuctionsSearchModel, ProductAvailableInStocksSearchModel, ProductDateSearchModel, ProductInExportToPriceComparisonSitesSearchEnum,
    ProductIndexesSearchModel, ProductParametersParamsSearchModel, ProductParamsSearchModel, ProductSearchPriceRangeSearchModel, ProductSeriesParams,
    ProductShopsSearchModel, ProductTypeSearchModel, ProductUnitsSearchModel, ProductWarrantiesSearchModel, ReturnElementsSearchEnum,
    ReturnProductsSearchEnum, ReturnProductsVersionsSearchEnum, SearchByShopsModel,
    PictureSettingsPostModel, PictureSettingsPutModel, ProductsDeleteModel, ProductsPostModel, ProductsPutModel, SettingsPostModel, SettingsPutModel, YNSelectedEnum
)


# --- DTOs
class DeletePimProductsProductProductParamsModel(BaseModel):
    products: List[ProductsDeleteModel] = Field(..., min_length=1 , description="Products list") # type: ignore

class PostPimProductsProductProductParamsModel(BaseModel):
    settings: SettingsPostModel = Field(..., description="Settings")
    picturesSettings: PictureSettingsPostModel = Field(..., description="Icon and photos settings")
    products: List[ProductsPostModel] = Field(..., min_length=1, description="Products list") # type: ignore

class PutPimProductsProductProductParamsModel(BaseModel):
    settings: SettingsPutModel = Field(..., description="Settings")
    picturesSettings: PictureSettingsPutModel | None = Field(None, description="Icon and photos settings")
    products: List[ProductsPutModel] = Field(..., min_length=1, description="Products list") # type: ignore

class SearchPimProductsProductProductParamsModel(BaseModel):
    dispatchSettings: DispatchSettingsSearchModel | None = Field(None, description="...")
    returnProducts: ReturnProductsSearchEnum | None = Field(None, description="Element determines which products should be returned by the gate. Undeleted products are returned by default")
    returnElements: ReturnElementsSearchEnum | None = Field(None, description="Elements to be returned by the endpoint. By default all elements are returned")
    productIsAvailable: BooleanStrShortEnum | None = Field(None, description="Product availability")
    productIsVisible: BooleanStrShortEnum | None = Field(None, description="Product visibility in store")
    productVersionId: StrictInt | None = Field(None, ge=1, description="Product group ID")
    productInPromotion: BooleanStrShortEnum | None = Field(None, description="Promoted product")
    productInDiscount: BooleanStrShortEnum | None = Field(None, description="Product on sale")
    productInDistinguished: BooleanStrShortEnum | None = Field(None, description="Distinguished product")
    productInSpecial: BooleanStrShortEnum | None = Field(None, description="Special product")
    productInForPointsSelling: BooleanStrShortEnum | None = Field(None, description="Product available for points")
    productIsObservedByClients: BooleanStrShortEnum | None = Field(None, description="Observed product")
    skipDefaultProduct: BooleanStrShortEnum | None = Field(None, description="Element determines if default product (with 0 ID, contains settings of newly added products) should be omitted")
    showPromotionsPrices: BooleanStrShortEnum | None = Field(None, description="The item specifies whether promotional prices are to be shown in price nodes")
    categories: List[CategoriesSearchModel] | None = Field(None, description="List of categories in which sought products are present")
    producers: List[ProducersSearchModel] | None = Field(None, description="List of manufacturers assigned to sought products")
    productParams: List[ProductParamsSearchModel] | None = Field(None, description="List of sought products. This parameter can be used, when there have been no other parameter entered productIndexes")
    productIndexes: List[ProductIndexesSearchModel] | None = Field(None, description="List of sought products by indexes")
    productShops: List[ProductShopsSearchModel] | None = Field(None, description="Data of stores product is assigned to")
    productPromotionsIds: List[int] | None = Field(None, description="List of special offers, sought products are assigned to")
    productDate: List[ProductDateSearchModel] | None = Field(None, description="Settings concerning narrowing list of products found by date")
    productParametersParams: List[ProductParametersParamsSearchModel] | None = Field(None, description="Series, sought products are assigned to")
    productSeriesParams: List[ProductSeriesParams] | None = Field(None, description="Series, sought products are assigned to")
    productUnits: List[ProductUnitsSearchModel] | None = Field(None, description="List of units of measure assigned to sought products")
    productWarranties: List[ProductWarrantiesSearchModel] | None = Field(None, description="Narrowing list of products by set warranties")
    deliverersIds: List[int] | None = Field(None, description="Suppliers, sought products are assigned to")
    containsText: str | None = Field(None, description="Product contains text (searches in short and long description)")
    containsCodePart: str | None = Field(None, description="Product code or it's part (based on producer's code, external product system code and code that is visible on a product card). Search is accesible only with available products")
    productAvailableInStocks: ProductAvailableInStocksSearchModel | None = Field(None, description="Product availability in stocks")
    productAvailableInAuctions: ProductAvailableInAuctionsSearchModel | None = Field(None, description="Product availability on auctions")
    ordersBy: List[OrdersBySearchModel] | None = Field(None, description="Possibility of sorting returned list")
    productSearchingLangId: str | None = Field(None, description="Language ID that allows to search and return data in chosen language. This parameter is optional. If it's lacking, she search process unfolds in all available languages")
    productSearchingCurrencyId: str | None = Field(None, description="Currency ID allowing to search and browse products in given currency. This parameter is optional, when it's lacking, the search process unfolds in all available currencies")
    returnPricesCurrency: str | None = Field(None, description="Currency ID allowing for returning all product prices in an indicated currency")
    productHasNote: str | None = Field(None, description="Annotation contains text")
    productInExportToPriceComparisonSites: ProductInExportToPriceComparisonSitesSearchEnum | None = Field(None, description="Product visibility in export to price comparison and marketplaces")
    productInExportToAmazonMarketplace: YNSelectedEnum | None = Field(None, description="Visibility of an item in an export to Amazon Marketplace")
    selectedAmazonMarketplacesList: List[str] | None = Field(None, description="List of Amazon regional sites to which the product is exported (only in case of 'selected' option)")
    productInBestseller: BooleanStrShortEnum | None = Field(None, description="Product is bestseller")
    productInNew: BooleanStrShortEnum | None = Field(None, description="Product is new")
    searchByShops: SearchByShopsModel | None = Field(None, description="Shops")
    productSearchPriceRange: ProductSearchPriceRangeSearchModel | None = Field(None, description="Price range for sought products")
    productVatRates: List[int] | None = Field(None,description="VAT value for sought products")
    productIsVatFree: BooleanStrShortEnum | None = Field(None, description="Is product VAT-free")
    productHasWholesalePrice: BooleanStrShortEnum | None = Field(None, description="Product has defined wholesale price")
    productInPersistent: BooleanStrShortEnum | None = Field(None, description="Product visible even though out of stock")
    returnProductsVersions: ReturnProductsVersionsSearchEnum | None = Field(None, description="Settings of products returned with variants. All products with variants are returned by default")
    productInSumInBasket: BooleanStrShortEnum | None = Field(None, description="Do You wish to sum up the products in the basket as a one order?")
    productType: ProductTypeSearchModel | None = Field(None, description="Product type")
    productMenuItems: List[PoductMenuItemsSearchModel] | None = Field(None, description="An array of menu elements")
    productLocationId: StrictInt | None = Field(None, ge=1, description="Warehouse location ID")
    productLocationTextId: str | None = Field(None, description="Warehouse location full path. Use a backslash () as a separator, for example: M1\Section name\Location name. If location_id parameter is provided, the full warehouse location path will not be taken into account") # type: ignore
    alwaysReturnProductShopSizesAttributes: bool | None = Field(None, description="Return all size attributes regardless of whether product prices are the same as the base price or if they differ from it")
    returnEmptyStocksWithReservation: bool | None = Field(None, description="Returns reservation information regardless of inventory levels")
    picturesData: PicturesDataSearchModel | None = Field(None, description="Data for operations on individual photos")
    responsibleProducerCode: str | None = Field(None, description="Responsible producer code")
    responsiblePersonCode: str | None = Field(None, description="Responsible person code")


# --- ENDPOINTS
class Delete(AppendableGateway):
    """
    Method used for deleting products from the IdoSell Shop administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsproductsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/products/delete')

    params: DeletePimProductsProductProductParamsModel = Field(..., description="Parameters transmitted to method")

class Get(Gateway):
    """
    Method that enables extracting information about non-deleted products available in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsproductsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/products')

    productIds: List[str] = Field(..., min_length=1, max_length=100, description="List of the unique, indexed product codes (IAI code / External system code / Producer code). You can transfer a maximum of 100 products IDs in one request") # type: ignore

    @model_validator(mode='after')
    def validate_product_ids(self):
        """Validate that product IDs are unique with no duplicates."""
        if len(self.productIds) != len(set(self.productIds)):
            raise ValueError("Product IDs must be unique - duplicates are not allowed")
        return self

class Post(AppendableGateway):
    """
    The method is used to add products
    DOCS_URL: https://idosell.readme.io/reference/productsproductspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/products')

    params: PostPimProductsProductProductParamsModel = Field(..., description="Parameters transmitted to method")

class Put(AppendableGateway):
    """
    Method that enables editing and adding new products to the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsproductsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/products')

    params: PutPimProductsProductProductParamsModel = Field(..., description="Parameters transmitted to method")

class Search(PageableCamelGateway):
    """
    Method that enables extracting information about non-deleted products available in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/productsproductssearchpost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/products/search')

    params: SearchPimProductsProductProductParamsModel = Field(..., description="Parameters transmitted to method")
