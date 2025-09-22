from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.pim.products._common import IdentTypeEnum


# --- Enums
class AdditionalLocationSettingsEnum(StrEnum):
    ADD = 'add'
    REMOVE = 'remove'

class ErrorModel(BaseModel):
    faultCode: StrictInt = Field(..., description="Error code")
    faultString: str = Field(..., description="Error description")

class OperationStocksEnum(StrEnum):
    ADD = 'add'
    SET = 'set'
    SUBSTRACT = 'substract'


# --- DTOs
class IdentStocksModel(BaseModel):
    identType: IdentTypeEnum = Field(..., description="...")
    identValue: str = Field(..., description="ID value")

class PutPimProductsStocksSettingsModel(BaseModel):
    productIndent: IdentStocksModel = Field(..., description="...")
    sizesIndent: IdentStocksModel = Field(..., description="...")

class AdditionalLocationsStocksModel(BaseModel):
    additionalLocationSettings: AdditionalLocationSettingsEnum = Field(..., description="Element specifying the modification mode for additional locations")
    additionalLocationId: StrictInt = Field(..., ge=1, description="Warehouse location ID")
    additionalLocationTextId: str = Field(..., description="Warehouse location full path")
    additionalLocationCode: str = Field(..., description="Storage location code")

class QuantityOperationModel(BaseModel):
    operation: OperationStocksEnum = Field(..., description="Operation type")
    quantity: float = Field(..., gt=0, description="Product quantity")

class StocksModel(BaseModel):
    stock_id: StrictInt = Field(..., ge=1, description="Stock ID")
    quantity_operation: QuantityOperationModel = Field(..., description="...")
    location_id: StrictInt = Field(..., ge=1, description="Warehouse location ID")
    location_text_id: str = Field(..., description="Warehouse location full path. Use a backslash () as a separator, for example: M1\Section name\Location name. If location_id parameter is provided, the full warehouse location path will not be taken into account") # type: ignore
    location_code: str = Field(..., description="Storage location code")
    additionalLocations: List[AdditionalLocationsStocksModel] = Field(..., description="Additional locations")

class QuantityStocksModel(BaseModel):
    stocks: List[StocksModel] = Field(..., description="Stock operations")

class SizesStocksModel(BaseModel):
    ident: IdentStocksModel = Field(..., description="")
    quantity: QuantityStocksModel = Field(..., description="Product quantity")

class ProductsStocksModel(BaseModel):
    ident: IdentStocksModel = Field(..., description="...")
    sizes: List[SizesStocksModel] = Field(..., description="List of sizes")
    settings: PutPimProductsStocksSettingsModel = Field(..., description="...")
    error: ErrorModel = Field(..., description="Error information")

class PutPimProductsStocksParamsModel(BaseModel):
    products: List[ProductsStocksModel] = Field(..., description="Products list")

class ProductsStocksPutQuantityModel(BaseModel):
    productIndex: Optional[str] = Field(None, description="Product index")
    productSizeCodeProducer: Optional[str] = Field(None, description="Product size code producer")
    productSizeCodeExternal: Optional[str] = Field(None, description="External product system code for size")
    stockId: Optional[StrictInt] = Field(None, ge=1, description="Stock ID") # type: ignore
    productSizeQuantity: Optional[float] = Field(None, gt=0, description="Product stock quantity")
    productPurchasePrice: Optional[float] = Field(None, ge=0, description="Cost price")
    productPurchasePriceNet: Optional[float] = Field(None, ge=0, description="Net purchase price")

class PutQuantityPimProductsStocksParamsModel(BaseModel):
    products: List[ProductsStocksPutQuantityModel] = Field(..., min_length=1, description="Products list") # type: ignore

# --- ENDPOINTS
class PutQuantity(AppendableGateway):
    """
    Metoda pozwala na edycje danych dotyczacych ilosci
    DOCS_URL: https://idosell.readme.io/reference/productsstockquantityput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/stockQuantity')

    params: PutQuantityPimProductsStocksParamsModel | None = Field(None, description="Parameters transmitted to method")

class Get(Gateway):
    """
    Method that enables getting information about product stock levels and warehouse locations.
    DOCS_URL: https://idosell.readme.io/reference/productsstocksget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/stocks')

    identType: IdentTypeEnum | None = Field(None, description="Identifier type")
    products: List[str] | None = Field(None, min_length=1, max_length=100, description="Products list") # type: ignore


class Put(AppendableGateway):
    """
    Method that enables setting product stock levels and warehouse locations.
    DOCS_URL: https://idosell.readme.io/reference/productsstocksput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/stocks')

    params: PutPimProductsStocksParamsModel = Field(..., description="Parameters transmitted to method")
    settings: PutPimProductsStocksSettingsModel = Field(..., description="...")
