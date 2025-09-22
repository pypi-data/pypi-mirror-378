import pytest
from pydantic import ValidationError

from src.idosell.pim.products.supplier import (
    # DTOs
    PutCodePimProductsSupplierParamsModel,
    PutProductDataPimProductsSupplierParamsModel,
    # Endpoints
    PutCode,
    PutProductData,
)


# --- Tests for DTOs
class TestPutCodePimProductsSupplierParamsModel:
    def test_valid(self):
        from src.idosell.pim.products._common import ProductsSupplierPutCodeModel, ProductDeliverersSupplierModel, ProductSizesSupplierModel

        dto = PutCodePimProductsSupplierParamsModel(
            products=[ProductsSupplierPutCodeModel(
                productId=1,
                productDeliverers=[ProductDeliverersSupplierModel(
                    delivererId=1,
                    productSizes=[ProductSizesSupplierModel(
                        sizeId="M",
                        sizeDelivererCode="SUP_M"
                    )]
                )]
            )]
        )
        assert len(dto.products) == 1
        assert dto.products[0].productId == 1

    def test_multiple_products(self):
        from src.idosell.pim.products._common import ProductsSupplierPutCodeModel, ProductDeliverersSupplierModel, ProductSizesSupplierModel

        dto = PutCodePimProductsSupplierParamsModel(
            products=[
                ProductsSupplierPutCodeModel(
                    productId=1,
                    productDeliverers=[ProductDeliverersSupplierModel(
                        delivererId=1,
                        productSizes=[ProductSizesSupplierModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M"
                        )]
                    )]
                ),
                ProductsSupplierPutCodeModel(
                    productId=2,
                    productDeliverers=[ProductDeliverersSupplierModel(
                        delivererId=2,
                        productSizes=[ProductSizesSupplierModel(
                            sizeId="L",
                            sizeDelivererCode="SUP_L"
                        )]
                    )]
                )
            ]
        )
        assert len(dto.products) == 2

    def test_invalid_product_id_zero(self):
        from src.idosell.pim.products._common import ProductsSupplierPutCodeModel, ProductDeliverersSupplierModel, ProductSizesSupplierModel

        with pytest.raises(ValidationError):
            PutCodePimProductsSupplierParamsModel(
                products=[ProductsSupplierPutCodeModel(
                    productId=0,
                    productDeliverers=[ProductDeliverersSupplierModel(
                        delivererId=1,
                        productSizes=[ProductSizesSupplierModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M"
                        )]
                    )]
                )]
            )

    def test_invalid_deliverer_id_zero(self):
        from src.idosell.pim.products._common import ProductsSupplierPutCodeModel, ProductDeliverersSupplierModel, ProductSizesSupplierModel

        with pytest.raises(ValidationError):
            PutCodePimProductsSupplierParamsModel(
                products=[ProductsSupplierPutCodeModel(
                    productId=1,
                    productDeliverers=[ProductDeliverersSupplierModel(
                        delivererId=0,
                        productSizes=[ProductSizesSupplierModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M"
                        )]
                    )]
                )]
            )


class TestPutProductDataPimProductsSupplierParamsModel:
    def test_valid(self):
        from src.idosell.pim.products._common import ProductsSupplierPutProductDataModel, ProductDeliverersProductsPutProductDataModel, ProductSizesProductDeliverersProductsPutProductDataModelModel

        dto = PutProductDataPimProductsSupplierParamsModel(
            products=[ProductsSupplierPutProductDataModel(
                productId=1,
                productDeliverers=[ProductDeliverersProductsPutProductDataModel(
                    delivererId=1,
                    productSizes=[ProductSizesProductDeliverersProductsPutProductDataModelModel(
                        sizeId="M",
                        sizeDelivererCode="SUP_M",
                        quantity=10.0,
                        lastPrice=100.0,
                        lastPriceNet=90.0
                    )],
                    clearAllQuantities=False
                )]
            )]
        )
        assert len(dto.products) == 1
        assert dto.products[0].productId == 1

    def test_clear_all_quantities_true(self):
        from src.idosell.pim.products._common import ProductsSupplierPutProductDataModel, ProductDeliverersProductsPutProductDataModel

        dto = PutProductDataPimProductsSupplierParamsModel(
            products=[ProductsSupplierPutProductDataModel(
                productId=1,
                productDeliverers=[ProductDeliverersProductsPutProductDataModel(
                    delivererId=1,
                    productSizes=[],
                    clearAllQuantities=True
                )]
            )]
        )
        assert dto.products[0].productDeliverers[0].clearAllQuantities == True

    def test_invalid_product_id_zero(self):
        from src.idosell.pim.products._common import ProductsSupplierPutProductDataModel, ProductDeliverersProductsPutProductDataModel, ProductSizesProductDeliverersProductsPutProductDataModelModel

        with pytest.raises(ValidationError):
            PutProductDataPimProductsSupplierParamsModel(
                products=[ProductsSupplierPutProductDataModel(
                    productId=0,
                    productDeliverers=[ProductDeliverersProductsPutProductDataModel(
                        delivererId=1,
                        productSizes=[ProductSizesProductDeliverersProductsPutProductDataModelModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M",
                            quantity=10.0,
                            lastPrice=100.0,
                            lastPriceNet=90.0
                        )],
                        clearAllQuantities=False
                    )]
                )]
            )

    def test_invalid_deliverer_id_zero(self):
        from src.idosell.pim.products._common import ProductsSupplierPutProductDataModel, ProductDeliverersProductsPutProductDataModel, ProductSizesProductDeliverersProductsPutProductDataModelModel

        with pytest.raises(ValidationError):
            PutProductDataPimProductsSupplierParamsModel(
                products=[ProductsSupplierPutProductDataModel(
                    productId=1,
                    productDeliverers=[ProductDeliverersProductsPutProductDataModel(
                        delivererId=0,
                        productSizes=[ProductSizesProductDeliverersProductsPutProductDataModelModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M",
                            quantity=10.0,
                            lastPrice=100.0,
                            lastPriceNet=90.0
                        )],
                        clearAllQuantities=False
                    )]
                )]
            )

    def test_invalid_quantity_zero(self):
        from src.idosell.pim.products._common import ProductsSupplierPutProductDataModel, ProductDeliverersProductsPutProductDataModel, ProductSizesProductDeliverersProductsPutProductDataModelModel

        with pytest.raises(ValidationError):
            PutProductDataPimProductsSupplierParamsModel(
                products=[ProductsSupplierPutProductDataModel(
                    productId=1,
                    productDeliverers=[ProductDeliverersProductsPutProductDataModel(
                        delivererId=1,
                        productSizes=[ProductSizesProductDeliverersProductsPutProductDataModelModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M",
                            quantity=0,
                            lastPrice=100.0,
                            lastPriceNet=90.0
                        )],
                        clearAllQuantities=False
                    )]
                )]
            )


# --- Tests for Endpoints
class TestPutCode:
    def test_invalid_empty_products(self):
        with pytest.raises(ValidationError):
            PutCodePimProductsSupplierParamsModel(products=[])

    def test_instantiate_with_products(self):
        from src.idosell.pim.products._common import ProductsSupplierPutCodeModel, ProductDeliverersSupplierModel, ProductSizesSupplierModel

        dto = PutCode(
            params=PutCodePimProductsSupplierParamsModel(
                products=[ProductsSupplierPutCodeModel(
                    productId=1,
                    productDeliverers=[ProductDeliverersSupplierModel(
                        delivererId=1,
                        productSizes=[ProductSizesSupplierModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M"
                        )]
                    )]
                )]
            )
        )
        assert len(dto.params.products) == 1
        assert dto.params.products[0].productId == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutCode()


class TestPutProductData:
    def test_invalid_empty_products(self):
        with pytest.raises(ValidationError):
            PutProductDataPimProductsSupplierParamsModel(products=[])

    def test_instantiate_with_products(self):
        from src.idosell.pim.products._common import ProductsSupplierPutProductDataModel, ProductDeliverersProductsPutProductDataModel, ProductSizesProductDeliverersProductsPutProductDataModelModel

        dto = PutProductData(
            params=PutProductDataPimProductsSupplierParamsModel(
                products=[ProductsSupplierPutProductDataModel(
                    productId=1,
                    productDeliverers=[ProductDeliverersProductsPutProductDataModel(
                        delivererId=1,
                        productSizes=[ProductSizesProductDeliverersProductsPutProductDataModelModel(
                            sizeId="M",
                            sizeDelivererCode="SUP_M",
                            quantity=10.0,
                            lastPrice=100.0,
                            lastPriceNet=90.0
                        )],
                        clearAllQuantities=False
                    )]
                )]
            )
        )
        assert len(dto.params.products) == 1
        assert dto.params.products[0].productId == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutProductData()
