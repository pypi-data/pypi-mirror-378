import pytest
from pydantic import ValidationError

from src.idosell.pim.products.stocks import (
    # DTOs
    IdentStocksModel,
    PutPimProductsStocksSettingsModel,
    AdditionalLocationsStocksModel,
    QuantityOperationModel,
    StocksModel,
    QuantityStocksModel,
    SizesStocksModel,
    ProductsStocksModel,
    PutPimProductsStocksParamsModel,
    ProductsStocksPutQuantityModel,
    # Endpoints
    Get,
    Put,
    # Enums
    AdditionalLocationSettingsEnum,
    OperationStocksEnum,
)
from src.idosell.pim.products._common import IdentTypeEnum
from src.idosell.pim.products.stocks import ErrorModel


# --- Tests for DTOs
class TestIdentStocksModel:
    def test_valid(self):
        dto = IdentStocksModel(
            identType=IdentTypeEnum.ID,
            identValue="123"
        )
        assert dto.identType == IdentTypeEnum.ID
        assert dto.identValue == "123"

    def test_index_type(self):
        dto = IdentStocksModel(
            identType=IdentTypeEnum.INDEX,
            identValue="PROD001"
        )
        assert dto.identType == IdentTypeEnum.INDEX
        assert dto.identValue == "PROD001"


class TestPutPimProductsStocksSettingsModel:
    def test_valid(self):
        dto = PutPimProductsStocksSettingsModel(
            productIndent=IdentStocksModel(
                identType=IdentTypeEnum.ID,
                identValue="123"
            ),
            sizesIndent=IdentStocksModel(
                identType=IdentTypeEnum.INDEX,
                identValue="PROD001"
            )
        )
        assert dto.productIndent.identType == IdentTypeEnum.ID
        assert dto.sizesIndent.identValue == "PROD001"


class TestAdditionalLocationsStocksModel:
    def test_valid(self):
        dto = AdditionalLocationsStocksModel(
            additionalLocationSettings=AdditionalLocationSettingsEnum.ADD,
            additionalLocationId=1,
            additionalLocationTextId="warehouse/section/location",
            additionalLocationCode="WL001"
        )
        assert dto.additionalLocationSettings == AdditionalLocationSettingsEnum.ADD
        assert dto.additionalLocationId == 1
        assert dto.additionalLocationTextId == "warehouse/section/location"
        assert dto.additionalLocationCode == "WL001"

    def test_remove_operation(self):
        dto = AdditionalLocationsStocksModel(
            additionalLocationSettings=AdditionalLocationSettingsEnum.REMOVE,
            additionalLocationId=2,
            additionalLocationTextId="warehouse/section/location2",
            additionalLocationCode="WL002"
        )
        assert dto.additionalLocationSettings == AdditionalLocationSettingsEnum.REMOVE

    def test_invalid_location_id_zero(self):
        with pytest.raises(ValidationError):
            AdditionalLocationsStocksModel(
                additionalLocationSettings=AdditionalLocationSettingsEnum.ADD,
                additionalLocationId=0,
                additionalLocationTextId="warehouse/section/location",
                additionalLocationCode="WL001"
            )


class TestQuantityOperationModel:
    def test_add_operation(self):
        dto = QuantityOperationModel(
            operation=OperationStocksEnum.ADD,
            quantity=10.5
        )
        assert dto.operation == OperationStocksEnum.ADD
        assert dto.quantity == 10.5

    def test_set_operation(self):
        dto = QuantityOperationModel(
            operation=OperationStocksEnum.SET,
            quantity=25.0
        )
        assert dto.operation == OperationStocksEnum.SET

    def test_subtract_operation(self):
        dto = QuantityOperationModel(
            operation=OperationStocksEnum.SUBSTRACT,
            quantity=5.0
        )
        assert dto.operation == OperationStocksEnum.SUBSTRACT

    def test_invalid_quantity_zero(self):
        with pytest.raises(ValidationError):
            QuantityOperationModel(
                operation=OperationStocksEnum.ADD,
                quantity=0
            )


class TestStocksModel:
    def test_valid(self):
        dto = StocksModel(
            stock_id=1,
            quantity_operation=QuantityOperationModel(
                operation=OperationStocksEnum.ADD,
                quantity=10.0
            ),
            location_id=1,
            location_text_id="warehouse/section/location",
            location_code="WL001",
            additionalLocations=[AdditionalLocationsStocksModel(
                additionalLocationSettings=AdditionalLocationSettingsEnum.ADD,
                additionalLocationId=2,
                additionalLocationTextId="warehouse/section/location2",
                additionalLocationCode="WL002"
            )]
        )
        assert dto.stock_id == 1
        assert dto.quantity_operation.operation == OperationStocksEnum.ADD
        assert dto.location_id == 1
        assert len(dto.additionalLocations) == 1

    def test_multiple_additional_locations(self):
        dto = StocksModel(
            stock_id=2,
            quantity_operation=QuantityOperationModel(
                operation=OperationStocksEnum.SET,
                quantity=50.0
            ),
            location_id=2,
            location_text_id="warehouse/main/location",
            location_code="WM001",
            additionalLocations=[
                AdditionalLocationsStocksModel(
                    additionalLocationSettings=AdditionalLocationSettingsEnum.ADD,
                    additionalLocationId=3,
                    additionalLocationTextId="warehouse/extra/location",
                    additionalLocationCode="WE001"
                ),
                AdditionalLocationsStocksModel(
                    additionalLocationSettings=AdditionalLocationSettingsEnum.REMOVE,
                    additionalLocationId=4,
                    additionalLocationTextId="warehouse/old/location",
                    additionalLocationCode="WO001"
                )
            ]
        )
        assert len(dto.additionalLocations) == 2

    def test_empty_additional_locations(self):
        dto = StocksModel(
            stock_id=3,
            quantity_operation=QuantityOperationModel(
                operation=OperationStocksEnum.SUBSTRACT,
                quantity=5.0
            ),
            location_id=3,
            location_text_id="warehouse/secondary/location",
            location_code="WS001",
            additionalLocations=[]
        )
        assert dto.additionalLocations == []

    def test_invalid_stock_id_zero(self):
        with pytest.raises(ValidationError):
            StocksModel(
                stock_id=0,
                quantity_operation=QuantityOperationModel(
                    operation=OperationStocksEnum.ADD,
                    quantity=10.0
                ),
                location_id=1,
                location_text_id="warehouse/section/location",
                location_code="WL001",
                additionalLocations=[]
            )

    def test_invalid_location_id_zero(self):
        with pytest.raises(ValidationError):
            StocksModel(
                stock_id=1,
                quantity_operation=QuantityOperationModel(
                    operation=OperationStocksEnum.ADD,
                    quantity=10.0
                ),
                location_id=0,
                location_text_id="warehouse/section/location",
                location_code="WL001",
                additionalLocations=[]
            )


class TestQuantityStocksModel:
    def test_valid(self):
        dto = QuantityStocksModel(
            stocks=[StocksModel(
                stock_id=1,
                quantity_operation=QuantityOperationModel(
                    operation=OperationStocksEnum.ADD,
                    quantity=10.0
                ),
                location_id=1,
                location_text_id="warehouse/section/location",
                location_code="WL001",
                additionalLocations=[]
            )]
        )
        assert len(dto.stocks) == 1

    def test_multiple_stocks(self):
        dto = QuantityStocksModel(
            stocks=[
                StocksModel(
                    stock_id=1,
                    quantity_operation=QuantityOperationModel(
                        operation=OperationStocksEnum.ADD,
                        quantity=10.0
                    ),
                    location_id=1,
                    location_text_id="warehouse/section/location1",
                    location_code="WL001",
                    additionalLocations=[]
                ),
                StocksModel(
                    stock_id=2,
                    quantity_operation=QuantityOperationModel(
                        operation=OperationStocksEnum.SET,
                        quantity=25.0
                    ),
                    location_id=2,
                    location_text_id="warehouse/section/location2",
                    location_code="WL002",
                    additionalLocations=[]
                )
            ]
        )
        assert len(dto.stocks) == 2


class TestSizesStocksModel:
    def test_valid(self):
        dto = SizesStocksModel(
            ident=IdentStocksModel(
                identType=IdentTypeEnum.ID,
                identValue="S"
            ),
            quantity=QuantityStocksModel(
                stocks=[StocksModel(
                    stock_id=1,
                    quantity_operation=QuantityOperationModel(
                        operation=OperationStocksEnum.ADD,
                        quantity=10.0
                    ),
                    location_id=1,
                    location_text_id="warehouse/section/location",
                    location_code="WL001",
                    additionalLocations=[]
                )]
            )
        )
        assert dto.ident.identType == IdentTypeEnum.ID
        assert dto.ident.identValue == "S"


class TestProductsStocksModel:
    def test_valid(self):
        dto = ProductsStocksModel(
            ident=IdentStocksModel(
                identType=IdentTypeEnum.INDEX,
                identValue="PROD001"
            ),
            sizes=[SizesStocksModel(
                ident=IdentStocksModel(
                    identType=IdentTypeEnum.ID,
                    identValue="M"
                ),
                quantity=QuantityStocksModel(stocks=[])
            )],
            settings=PutPimProductsStocksSettingsModel(
                productIndent=IdentStocksModel(
                    identType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                sizesIndent=IdentStocksModel(
                    identType=IdentTypeEnum.INDEX,
                    identValue="PROD001"
                )
            ),
            error=ErrorModel(
                faultCode=0,
                faultString=""
            )
        )
        assert dto.ident.identValue == "PROD001"
        assert len(dto.sizes) == 1
        assert dto.error.faultCode == 0

    def test_with_error(self):
        dto = ProductsStocksModel(
            ident=IdentStocksModel(
                identType=IdentTypeEnum.ID,
                identValue="456"
            ),
            sizes=[],
            settings=PutPimProductsStocksSettingsModel(
                productIndent=IdentStocksModel(
                    identType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                sizesIndent=IdentStocksModel(
                    identType=IdentTypeEnum.INDEX,
                    identValue="PROD001"
                )
            ),
            error=ErrorModel(
                faultCode=123,
                faultString='Error occurred'
            )
        )
        assert dto.ident.identValue == "456"
        assert len(dto.sizes) == 0
        assert dto.error.faultCode == 123


class TestPutPimProductsStocksParamsModel:
    def test_valid(self):
        dto = PutPimProductsStocksParamsModel(
            products=[ProductsStocksModel(
                ident=IdentStocksModel(
                    identType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                sizes=[],
                settings=PutPimProductsStocksSettingsModel(
                    productIndent=IdentStocksModel(
                        identType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    sizesIndent=IdentStocksModel(
                        identType=IdentTypeEnum.INDEX,
                        identValue="PROD001"
                    )
                ),
                error=ErrorModel(faultCode=0, faultString="")
            )]
        )
        assert len(dto.products) == 1

    def test_multiple_products(self):
        dto = PutPimProductsStocksParamsModel(
            products=[
                ProductsStocksModel(
                    ident=IdentStocksModel(
                        identType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    sizes=[],
                    settings=PutPimProductsStocksSettingsModel(
                        productIndent=IdentStocksModel(
                            identType=IdentTypeEnum.ID,
                            identValue="123"
                        ),
                        sizesIndent=IdentStocksModel(
                            identType=IdentTypeEnum.INDEX,
                            identValue="PROD001"
                        )
                    ),
                    error=ErrorModel(faultCode=0, faultString="")
                ),
                ProductsStocksModel(
                    ident=IdentStocksModel(
                        identType=IdentTypeEnum.INDEX,
                        identValue="PROD002"
                    ),
                    sizes=[SizesStocksModel(
                        ident=IdentStocksModel(
                            identType=IdentTypeEnum.ID,
                            identValue="L"
                        ),
                        quantity=QuantityStocksModel(stocks=[])
                    )],
                    settings=PutPimProductsStocksSettingsModel(
                        productIndent=IdentStocksModel(
                            identType=IdentTypeEnum.ID,
                            identValue="456"
                        ),
                        sizesIndent=IdentStocksModel(
                            identType=IdentTypeEnum.INDEX,
                            identValue="PROD002"
                        )
                    ),
                    error=ErrorModel(faultCode=0, faultString="")
                )
            ]
        )
        assert len(dto.products) == 2
        assert len(dto.products[1].sizes) == 1


class TestProductsStocksPutQuantityModel:
    def test_valid(self):
        dto = ProductsStocksPutQuantityModel(
            productIndex="PROD001",
            productSizeCodeProducer="ABC123",
            productSizeCodeExternal="EXT456",
            stockId=1,
            productSizeQuantity=10.5,
            productPurchasePrice=100.0,
            productPurchasePriceNet=90.0
        )
        assert dto.productIndex == "PROD001"
        assert dto.productSizeCodeProducer == "ABC123"
        assert dto.stockId == 1
        assert dto.productSizeQuantity == 10.5

    def test_invalid_stock_id_zero(self):
        with pytest.raises(ValidationError):
            ProductsStocksPutQuantityModel(
                productIndex="PROD001",
                productSizeCodeProducer="ABC123",
                productSizeCodeExternal="EXT456",
                stockId=0,
                productSizeQuantity=10.5,
                productPurchasePrice=100.0,
                productPurchasePriceNet=90.0
            )

    def test_invalid_quantity_zero(self):
        with pytest.raises(ValidationError):
            ProductsStocksPutQuantityModel(
                productIndex="PROD001",
                productSizeCodeProducer="ABC123",
                productSizeCodeExternal="EXT456",
                stockId=1,
                productSizeQuantity=0,
                productPurchasePrice=100.0,
                productPurchasePriceNet=90.0
            )

    def test_zero_purchase_price_allowed(self):
        # Zero purchase price is actually allowed (no validation)
        dto = ProductsStocksPutQuantityModel(
            productIndex="PROD001",
            productSizeCodeProducer="ABC123",
            productSizeCodeExternal="EXT456",
            stockId=1,
            productSizeQuantity=10.5,
            productPurchasePrice=0.0,
            productPurchasePriceNet=90.0
        )
        assert dto.productPurchasePrice == 0.0


# --- Tests for Endpoints
# class TestPutQuantity:
#     def test_instantiate_minimal(self):
#         dto = PutQuantity(
#             products=[ProductsStocksPutQuantityModel(
#                 productIndex="PROD001",
#                 productSizeCodeProducer="ABC123",
#                 productSizeCodeExternal="EXT456",
#                 stockId=1,
#                 productSizeQuantity=10.5,
#                 productPurchasePrice=100.0,
#                 productPurchasePriceNet=90.0
#             )]
#         )
#         assert hasattr(dto, '_method')
#         assert hasattr(dto, '_endpoint')
#         assert dto._method == 'PUT'
#         assert dto._endpoint == '/api/admin/v6/products/stockQuantity'
#         assert len(dto.products) == 1

    # def test_instantiate_with_multiple_products(self):
    #     dto = PutQuantity(
    #         products=[
    #             ProductsStocksPutQuantityModel(
    #                 productIndex="PROD001",
    #                 productSizeCodeProducer="ABC123",
    #                 productSizeCodeExternal="EXT456",
    #                 stockId=1,
    #                 productSizeQuantity=10.5,
    #                 productPurchasePrice=100.0,
    #                 productPurchasePriceNet=90.0
    #             ),
    #             ProductsStocksPutQuantityModel(
    #                 productIndex="PROD002",
    #                 productSizeCodeProducer="XYZ789",
    #                 productSizeCodeExternal="EXT789",
    #                 stockId=2,
    #                 productSizeQuantity=25.0,
    #                 productPurchasePrice=150.0,
    #                 productPurchasePriceNet=135.0
    #             )
    #         ]
    #     )
    #     assert len(dto.products) == 2

class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/stocks'
        assert dto.identType is None
        assert dto.products is None

    def test_instantiate_with_params(self):
        dto = Get(
            identType=IdentTypeEnum.ID,
            products=["123", "456", "789"]
        )
        assert dto.identType == IdentTypeEnum.ID
        assert dto.products == ["123", "456", "789"]

    def test_invalid_products_empty_list(self):
        with pytest.raises(ValidationError):
            Get(products=[])

    def test_invalid_products_too_many(self):
        with pytest.raises(ValidationError):
            Get(products=["item"] * 101)


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsStocksParamsModel(products=[]),
            settings=PutPimProductsStocksSettingsModel(
                productIndent=IdentStocksModel(
                    identType=IdentTypeEnum.ID,
                    identValue="1"
                ),
                sizesIndent=IdentStocksModel(
                    identType=IdentTypeEnum.INDEX,
                    identValue="PROD001"
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/stocks'
        assert len(dto.params.products) == 0

    def test_instantiate_with_products(self):
        dto = Put(
            params=PutPimProductsStocksParamsModel(
                products=[ProductsStocksModel(
                    ident=IdentStocksModel(
                        identType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    sizes=[],
                    settings=PutPimProductsStocksSettingsModel(
                        productIndent=IdentStocksModel(
                            identType=IdentTypeEnum.ID,
                            identValue="123"
                        ),
                        sizesIndent=IdentStocksModel(
                            identType=IdentTypeEnum.INDEX,
                            identValue="PROD001"
                        )
                    ),
                    error=ErrorModel(faultCode=0, faultString="")
                )]
            ),
            settings=PutPimProductsStocksSettingsModel(
                productIndent=IdentStocksModel(
                    identType=IdentTypeEnum.ID,
                    identValue="1"
                ),
                sizesIndent=IdentStocksModel(
                    identType=IdentTypeEnum.INDEX,
                    identValue="GLOBAL"
                )
            )
        )
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put(
                params=PutPimProductsStocksParamsModel(products=[])
                # missing required settings
            )
