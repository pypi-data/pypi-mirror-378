import pytest
from pydantic import ValidationError

from src.idosell.pim.products.strikethrough import (
    # DTOs
    StpSettingsModel,
    ShopsStrikethroughModel,
    SizesStrikethroughModel,
    ProductsStrikethroughModel,
    PutPricesPimProductsStrikethroughParamsModel,
    PutPricesPimProductsStrikethroughSettingsModel,
    # Endpoints
    GetPrices,
    PutPrices,
    # Enums
    CalculateBasePriceSizesStrikethroughEnum,
    PriceChangeModeStrikethroughEnum,
    PriceChangeBasevalueStrikethroughEnum,
    PriceModeStrikethroughEnum,
)
from src.idosell.pim.products._common import IdentModel, IdentTypeEnum, PriceRoundModeEnum


# --- Tests for DTOs
class TestStpSettingsModel:
    def test_valid(self):
        dto = StpSettingsModel(
            price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
            price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
            retail_price_change_value=10.5,
            wholesale_price_change_value=8.0
        )
        assert dto.price_change_mode == PriceChangeModeStrikethroughEnum.AMOUNT_SET
        assert dto.price_change_basevalue == PriceChangeBasevalueStrikethroughEnum.PRICE
        assert dto.retail_price_change_value == 10.5
        assert dto.wholesale_price_change_value == 8.0


class TestShopsStrikethroughModel:
    def test_valid(self):
        dto = ShopsStrikethroughModel(
            shop_id=1,
            stp_settings=StpSettingsModel(
                price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                retail_price_change_value=10.0,
                wholesale_price_change_value=8.0
            )
        )
        assert dto.shop_id == 1
        assert dto.stp_settings.price_change_mode == PriceChangeModeStrikethroughEnum.AMOUNT_SET

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            ShopsStrikethroughModel(
                shop_id=0,
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=8.0
                )
            )


class TestSizesStrikethroughModel:
    def test_valid(self):
        dto = SizesStrikethroughModel(
            ident=IdentModel(
                type=IdentTypeEnum.ID,
                value="M"
            ),
            stp_settings=StpSettingsModel(
                price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                retail_price_change_value=10.0,
                wholesale_price_change_value=8.0
            ),
            shops=[ShopsStrikethroughModel(
                shop_id=1,
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=8.0
                )
            )]
        )
        assert dto.ident.type == IdentTypeEnum.ID
        assert dto.ident.value == "M"
        assert len(dto.shops) == 1


class TestProductsStrikethroughModel:
    def test_valid(self):
        dto = ProductsStrikethroughModel(
            ident=IdentModel(
                type=IdentTypeEnum.INDEX,
                value="PROD001"
            ),
            sizes=[SizesStrikethroughModel(
                ident=IdentModel(
                    type=IdentTypeEnum.ID,
                    value="L"
                ),
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=8.0
                ),
                shops=[]
            )],
            stp_settings=StpSettingsModel(
                price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                retail_price_change_value=15.0,
                wholesale_price_change_value=12.0
            ),
            shops=[ShopsStrikethroughModel(
                shop_id=1,
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=8.0
                )
            )]
        )
        assert dto.ident.value == "PROD001"
        assert len(dto.sizes) == 1
        assert len(dto.shops) == 1


class TestPutPricesPimProductsStrikethroughParamsModel:
    def test_valid(self):
        dto = PutPricesPimProductsStrikethroughParamsModel(
            products=[ProductsStrikethroughModel(
                ident=IdentModel(
                    type=IdentTypeEnum.ID,
                    value="123"
                ),
                sizes=[],
                stp_settings=StpSettingsModel(
                    price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                    price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                    retail_price_change_value=10.0,
                    wholesale_price_change_value=8.0
                ),
                shops=[]
            )]
        )
        assert len(dto.products) == 1

    def test_multiple_products(self):
        dto = PutPricesPimProductsStrikethroughParamsModel(
            products=[
                ProductsStrikethroughModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.ID,
                        value="123"
                    ),
                    sizes=[],
                    stp_settings=StpSettingsModel(
                        price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                        price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                        retail_price_change_value=10.0,
                        wholesale_price_change_value=8.0
                    ),
                    shops=[]
                ),
                ProductsStrikethroughModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.INDEX,
                        value="PROD002"
                    ),
                    sizes=[],
                    stp_settings=StpSettingsModel(
                        price_change_mode=PriceChangeModeStrikethroughEnum.PERCENT_DIFF,
                        price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                        retail_price_change_value=20.0,
                        wholesale_price_change_value=15.0
                    ),
                    shops=[]
                )
            ]
        )
        assert len(dto.products) == 2


class TestPutPricesPimProductsStrikethroughSettingsModel:
    def test_valid(self):
        dto = PutPricesPimProductsStrikethroughSettingsModel(
            calculate_base_price_sizes=CalculateBasePriceSizesStrikethroughEnum.ALL,
            price_mode=PriceModeStrikethroughEnum.GROSS,
            price_round_mode=PriceRoundModeEnum.NONE
        )
        assert dto.calculate_base_price_sizes == CalculateBasePriceSizesStrikethroughEnum.ALL
        assert dto.price_mode == PriceModeStrikethroughEnum.GROSS
        assert dto.price_round_mode == PriceRoundModeEnum.NONE


# --- Tests for Endpoints
class TestGetPrices:
    def test_instantiate_minimal(self):
        dto = GetPrices()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/strikethroughPrices'
        assert dto.identType is None
        assert dto.products is None

    def test_instantiate_with_params(self):
        dto = GetPrices(
            identType=IdentTypeEnum.ID,
            products=["123", "456"]
        )
        assert dto.identType == IdentTypeEnum.ID
        assert dto.products == ["123", "456"]

    def test_invalid_products_empty_list(self):
        with pytest.raises(ValidationError):
            GetPrices(products=[])

    def test_invalid_products_too_many(self):
        with pytest.raises(ValidationError):
            GetPrices(products=["item"] * 101)


class TestPutPrices:
    def test_instantiate_minimal(self):
        dto = PutPrices(
            params=PutPricesPimProductsStrikethroughParamsModel(products=[]),
            settings=PutPricesPimProductsStrikethroughSettingsModel(
                calculate_base_price_sizes=CalculateBasePriceSizesStrikethroughEnum.ALL,
                price_mode=PriceModeStrikethroughEnum.GROSS,
                price_round_mode=PriceRoundModeEnum.NONE
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/strikethroughPrices'
        assert len(dto.params.products) == 0

    def test_instantiate_with_products(self):
        dto = PutPrices(
            params=PutPricesPimProductsStrikethroughParamsModel(
                products=[ProductsStrikethroughModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.ID,
                        value="123"
                    ),
                    sizes=[],
                    stp_settings=StpSettingsModel(
                        price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                        price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                        retail_price_change_value=10.0,
                        wholesale_price_change_value=8.0
                    ),
                    shops=[ShopsStrikethroughModel(
                        shop_id=1,
                        stp_settings=StpSettingsModel(
                            price_change_mode=PriceChangeModeStrikethroughEnum.AMOUNT_SET,
                            price_change_basevalue=PriceChangeBasevalueStrikethroughEnum.PRICE,
                            retail_price_change_value=10.0,
                            wholesale_price_change_value=8.0
                        )
                    )]
                )]
            ),
            settings=PutPricesPimProductsStrikethroughSettingsModel(
                calculate_base_price_sizes=CalculateBasePriceSizesStrikethroughEnum.AVAILABLE,
                price_mode=PriceModeStrikethroughEnum.NET,
                price_round_mode=PriceRoundModeEnum.VALX0
            )
        )
        assert len(dto.params.products) == 1
        assert len(dto.params.products[0].shops) == 1
        assert dto.settings.price_mode == PriceModeStrikethroughEnum.NET

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutPrices(
                params=PutPricesPimProductsStrikethroughParamsModel(products=[])
                # missing required settings
            )
