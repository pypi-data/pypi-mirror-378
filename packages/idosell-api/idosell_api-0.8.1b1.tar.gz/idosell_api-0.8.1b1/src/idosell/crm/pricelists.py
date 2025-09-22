from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import BooleanStrLongEnum, Gateway, PageableCamelGateway


# --- Enums
class ReturnElementsPriceListsEnum(StrEnum):
    PRICELISTID = 'priceListId'
    PRICELISTNAME = 'priceListName'
    ONLYORDERPRODUCTSWITHMANUALLYSETPRICES = 'onlyOrderProductsWithManuallySetPrices'
    ONLYSEEPRODUCTSWITHMANUALLYSETPRICES = 'onlySeeProductsWithManuallySetPrices'


# --- DTOs
class ProductsModel(BaseModel):
    productId: StrictInt = Field(..., ge=1, description="Product IAI code")
    price: float = Field(..., description="Price")
    currencyId: str = Field(..., description="Currency ID")

class ProducersPriceListsModel(BaseModel):
    producerId: StrictInt = Field(..., ge=1, description="Brand ID")
    price: float = Field(..., description="Price")
    currencyId: str = Field(..., description="Currency ID")

class SeriesPriceListsModel(BaseModel):
    seriesId: StrictInt = Field(..., ge=1, description="ID of series, to which product belongs")
    price: float = Field(..., description="Price")
    currencyId: str = Field(..., description="Currency ID")

class CategoriesPriceListsModel(BaseModel):
    categoryId: StrictInt = Field(..., ge=1, description="Category id")
    price: float = Field(..., description="Price")
    currencyId: str = Field(..., description="Currency ID")

class MenuItemsPriceListsModel(BaseModel):
    menuItemId: StrictInt = Field(..., ge=1, description="ID of the menu node to which the product is to be assigned")
    price: float = Field(..., description="Price")
    currencyId: str = Field(..., description="Currency ID")

class PutClientsCrmPricelistsParamsModel(BaseModel):
    priceListId: StrictInt = Field(..., ge=1, description="Individual price list ID")
    clientsIds: List[int] = Field(..., description="Customer numbers")

class DeleteCrmPricelistsParamsModel(BaseModel):
    priceListId: StrictInt = Field(..., ge=1, description="Individual price list ID")

class PostCrmPricelistsParamsModel(BaseModel):
    priceListName: str = Field(..., description="Name of individual price list")
    onlyOrderProductsWithManuallySetPrices: BooleanStrLongEnum = Field(..., description="Restrict visibility to products listed in price list (other products will remain hidden)")
    onlySeeProductsWithManuallySetPrices: BooleanStrLongEnum = Field(..., description="Restrict products visibility to products listed in price list, remaining products will be seen as 'Call for price'")

class PutCrmPricelistsParamsModel(BaseModel):
    priceListId: StrictInt = Field(..., ge=1, description="Individual price list ID")
    priceListName: str = Field(..., description="Name of individual price list")
    onlyOrderProductsWithManuallySetPrices: BooleanStrLongEnum = Field(..., description="Restrict visibility to products listed in price list (other products will remain hidden)")
    onlySeeProductsWithManuallySetPrices: BooleanStrLongEnum = Field(..., description="Restrict products visibility to products listed in price list, remaining products will be seen as 'Call for price'")

class PutProductsCrmPricelistsParamsModel(BaseModel):
    priceListId: StrictInt = Field(..., ge=1, description="Individual price list ID")
    products: List[ProductsModel] = Field(..., description="Products list")
    producers: List[ProducersPriceListsModel] = Field(..., description="List of manufacturers assigned to sought products")
    series: List[SeriesPriceListsModel] = Field(..., description="Series list")
    categories: List[CategoriesPriceListsModel] = Field(..., description="List of categories in which sought products are present")
    menuItems: List[MenuItemsPriceListsModel] = Field(..., description="...")

class PutRenameCrmPricelistsParamsModel(BaseModel):
    priceListName: str = Field(..., description="Name of individual price list")
    priceListId: StrictInt = Field(..., ge=1, description="Individual price list ID")


# --- ENDPOINTS
class GetClients(Gateway):
    """
    The getClients method returns a list of customer IDs assigned to an individual price list
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsclientsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists/clients')

    priceListId: StrictInt | None = Field(None, ge=1, description="Individual price list ID")

class PutClients(Gateway):
    """
    The setClients method allows you to assign customers to an individual price list
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsclientsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists/clients')

    params: PutClientsCrmPricelistsParamsModel = Field(..., description="Parameters transmitted to method")

class Delete(Gateway):
    """
    The delete method enables to delete an individual pricelist. The pricelist must not be associated with any customer. In order to check the clients related to the given group, the getClients method shall be used
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsdeletepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists/delete')

    params: DeleteCrmPricelistsParamsModel = Field(..., description="Parameters transmitted to method")

class Get(PageableCamelGateway):
    """
    The get method allows you to download individual price lists available in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists')

    priceListIds: Optional[List[int]] = Field(default=None, min_length=1, description="List of individual price lists (each >=1)")  # type: ignore
    returnElements: Optional[List[ReturnElementsPriceListsEnum]] = Field(default=None, min_length=1, description="Elements to be returned by the endpoint. By default all elements are returned. Available elements: priceListId, priceListName, onlyOrderProductsWithManuallySetPrices, onlySeeProductsWithManuallySetPrices")  # type: ignore

class Post(Gateway):
    """
    The insert method enables you to add a new individual price list to the administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistspost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists')

    params: PostCrmPricelistsParamsModel = Field(..., description="Parameters transmitted to method")

class Put(Gateway):
    """
    The update method allows you to change the individual price list
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists')

    params: PutCrmPricelistsParamsModel = Field(..., description="Parameters transmitted to method")

class GetProducts(PageableCamelGateway):
    """
    The getProducts method enables the retrieval of products from an individual price list together with the price
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsproductsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists/products')

    priceListId: StrictInt | None = Field(None, ge=1,  description="Individual price list ID")

class PutProducts(Gateway):
    """
    The setProducts method allows you to add goods to an individual price list and specify their price
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsproductsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists/products')

    params: PutProductsCrmPricelistsParamsModel = Field(..., description="Parameters transmitted to method")

class PutRename(Gateway):
    """
    The rename method enables changing the name of an individual price list
    DOCS_URL: https://idosell.readme.io/reference/clientspricelistsrenameput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/pricelists/rename')

    params: PutRenameCrmPricelistsParamsModel = Field(..., description="Parameters transmitted to method")
