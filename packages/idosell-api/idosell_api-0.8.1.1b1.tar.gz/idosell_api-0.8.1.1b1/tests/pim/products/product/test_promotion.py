import pytest
from pydantic import ValidationError

from src.idosell.pim.products.product.promotion import (
    # DTOs
    DeleteProductsToPromotionPimProductsProductPromotionParamsModel,
    PostProductsToPromotionPimProductsProductPromotionParamsModel,
    # Endpoints
    DeleteProductsToPromotion,
    PostProductsToPromotion,
)


# --- Tests for DTOs
class TestDeleteProductsToPromotionPimProductsProductPromotionParamsModel:
    def test_valid(self):
        dto = DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId=123,
            products=[1, 2, 3]
        )
        assert dto.promotionId == 123
        assert dto.products == [1, 2, 3]

    def test_single_product(self):
        dto = DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId=456,
            products=[42]
        )
        assert dto.promotionId == 456
        assert dto.products == [42]

    def test_empty_products(self):
        with pytest.raises(ValidationError):
            DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=123,
                products=[]
            )

    def test_invalid_promotion_id_zero(self):
        with pytest.raises(ValidationError):
            DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=0,
                products=[1, 2]
            )

    def test_invalid_promotion_id_negative(self):
        with pytest.raises(ValidationError):
            DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=-1,
                products=[1, 2]
            )


class TestPostProductsToPromotionPimProductsProductPromotionParamsModel:
    def test_valid(self):
        dto = PostProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId=789,
            products=[4, 5, 6]
        )
        assert dto.promotionId == 789
        assert dto.products == [4, 5, 6]

    def test_single_product(self):
        dto = PostProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId=321,
            products=[99]
        )
        assert dto.promotionId == 321
        assert dto.products == [99]

    def test_empty_products(self):
        with pytest.raises(ValidationError):
            PostProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=789,
                products=[]
            )

    def test_invalid_products_none(self):
        with pytest.raises(ValidationError):
            PostProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=789,
                products=None
            )

    def test_promotion_id_zero(self):
        dto = PostProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId=0,
            products=[1, 2]
        )
        assert dto.promotionId == 0

    def test_promotion_id_negative(self):
        dto = PostProductsToPromotionPimProductsProductPromotionParamsModel(
            promotionId=-5,
            products=[1, 2]
        )
        assert dto.promotionId == -5


# --- Tests for Endpoints
class TestDeleteProductsToPromotion:
    def test_instantiate_with_params(self):
        endpoint = DeleteProductsToPromotion(
            params=DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=123,
                products=[1, 2, 3]
            )
        )
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/products/productsToPromotion/delete'
        assert endpoint.params.promotionId == 123
        assert endpoint.params.products == [1, 2, 3]

    def test_instantiate_missing_params(self):
        with pytest.raises(ValidationError):
            DeleteProductsToPromotion()

    def test_empty_params_products_validation(self):
        with pytest.raises(ValidationError):
            DeleteProductsToPromotion(
                params=DeleteProductsToPromotionPimProductsProductPromotionParamsModel(
                    promotionId=123,
                    products=[]
                )
            )


class TestPostProductsToPromotion:
    def test_instantiate_with_params(self):
        endpoint = PostProductsToPromotion(
            params=PostProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=789,
                products=[4, 5, 6]
            )
        )
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/products/productsToPromotion'
        assert endpoint.params.promotionId == 789
        assert endpoint.params.products == [4, 5, 6]

    def test_instantiate_missing_params(self):
        with pytest.raises(ValidationError):
            PostProductsToPromotion()

    def test_empty_params_products_validation(self):
        with pytest.raises(ValidationError):
            PostProductsToPromotion(
                params=PostProductsToPromotionPimProductsProductPromotionParamsModel(
                    promotionId=789,
                    products=[]
                )
            )

    def test_endpoint_with_zero_promotion_id(self):
        endpoint = PostProductsToPromotion(
            params=PostProductsToPromotionPimProductsProductPromotionParamsModel(
                promotionId=0,
                products=[1, 2]
            )
        )
        assert endpoint.params.promotionId == 0
