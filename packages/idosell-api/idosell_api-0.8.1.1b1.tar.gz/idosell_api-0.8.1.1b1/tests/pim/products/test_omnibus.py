import pytest
from pydantic import ValidationError

from src.idosell.pim.products.omnibus import (
    # DTOs
    PutPricesPimProductsOmnibusParamsModel,
    # Endpoints
    GetPrices,
    PutPrices,
)
from src.idosell.pim.products._common import (
    ProductsOmnibusModel,
    SizesOmnibusModel,
    ShopsModel,
    OmnibusPricesModel,
    IdentModel,
    IdentTypeEnum,
    OmnibusPriceManagementEnum,
)


# --- Tests for DTOs
class TestPutPricesPimProductsOmnibusParamsModel:
    def test_valid(self):
        dto = PutPricesPimProductsOmnibusParamsModel(
            products=[
                ProductsOmnibusModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.ID,
                        value="123"
                    ),
                    sizes=[
                        SizesOmnibusModel(
                            ident=IdentModel(
                                type=IdentTypeEnum.ID,
                                value="1"
                            ),
                            omnibusPrices=OmnibusPricesModel(
                                omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                                omnibusPriceRetail=100.0,
                                omnibusPriceWholesale=90.0
                            ),
                            shops=[
                                ShopsModel(
                                    shopId=1,
                                    omnibusPrices=OmnibusPricesModel(
                                        omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                                        omnibusPriceRetail=100.0,
                                        omnibusPriceWholesale=90.0
                                    )
                                )
                            ]
                        )
                    ],
                    omnibusPrices=OmnibusPricesModel(
                        omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                        omnibusPriceRetail=100.0,
                        omnibusPriceWholesale=90.0
                    ),
                    shops=[
                        ShopsModel(
                            shopId=1,
                            omnibusPrices=OmnibusPricesModel(
                                omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                                omnibusPriceRetail=100.0,
                                omnibusPriceWholesale=90.0
                            )
                        )
                    ]
                )
            ]
        )
        assert len(dto.products) == 1
        assert dto.products[0].ident.value == "123"

    def test_multiple_products(self):
        dto = PutPricesPimProductsOmnibusParamsModel(
            products=[
                ProductsOmnibusModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.ID,
                        value="123"
                    ),
                    sizes=[],
                    omnibusPrices=OmnibusPricesModel(
                        omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                        omnibusPriceRetail=100.0,
                        omnibusPriceWholesale=90.0
                    ),
                    shops=[]
                ),
                ProductsOmnibusModel(
                    ident=IdentModel(
                        type=IdentTypeEnum.INDEX,
                        value="456"
                    ),
                    sizes=[],
                    omnibusPrices=OmnibusPricesModel(
                        omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                        omnibusPriceRetail=200.0,
                        omnibusPriceWholesale=180.0
                    ),
                    shops=[]
                )
            ]
        )
        assert len(dto.products) == 2

    # --- Tests for Endpoints
class TestGetPrices:
    def test_instantiate_minimal(self):
        dto = GetPrices()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/omnibusPrices'
        assert dto.identType is None
        assert dto.products is None

    def test_instantiate_with_ident_type(self):
        dto = GetPrices(
            identType=IdentTypeEnum.ID,
            products=["123", "456"]
        )
        assert dto.identType == IdentTypeEnum.ID
        assert dto.products == ["123", "456"]

    def test_invalid_products_empty_list(self):
        with pytest.raises(ValidationError):
            GetPrices(
                identType=IdentTypeEnum.ID,
                products=[]
            )


class TestPutPrices:
    def test_instantiate_minimal(self):
        dto = PutPrices(
            params=PutPricesPimProductsOmnibusParamsModel(
                products=[
                    ProductsOmnibusModel(
                        ident=IdentModel(
                            type=IdentTypeEnum.ID,
                            value="123"
                        ),
                        sizes=[],
                        omnibusPrices=OmnibusPricesModel(
                            omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                            omnibusPriceRetail=100.0,
                            omnibusPriceWholesale=90.0
                        ),
                        shops=[]
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/omnibusPrices'
        assert len(dto.params.products) == 1

    def test_instantiate_with_multiple_products(self):
        dto = PutPrices(
            params=PutPricesPimProductsOmnibusParamsModel(
                products=[
                    ProductsOmnibusModel(
                        ident=IdentModel(
                            type=IdentTypeEnum.ID,
                            value="123"
                        ),
                        sizes=[],
                        omnibusPrices=OmnibusPricesModel(
                            omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                            omnibusPriceRetail=100.0,
                            omnibusPriceWholesale=90.0
                        ),
                        shops=[]
                    ),
                    ProductsOmnibusModel(
                        ident=IdentModel(
                            type=IdentTypeEnum.INDEX,
                            value="456"
                        ),
                        sizes=[],
                        omnibusPrices=OmnibusPricesModel(
                            omnibusPriceManagement=OmnibusPriceManagementEnum.MANUAL,
                            omnibusPriceRetail=200.0,
                            omnibusPriceWholesale=180.0
                        ),
                        shops=[]
                    )
                ]
            )
        )
        assert len(dto.params.products) == 2

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutPrices()
