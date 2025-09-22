import pytest
from pydantic import ValidationError

from src.idosell.pim.products.product.facebook import (
    # DTOs
    DeleteToFacebookCatalogPimProductsProductFacebookParamsModel,
    PostToFacebookCatalogPimProductsProductFacebookParamsModel,
    # Endpoints
    DeleteToFacebookCatalog,
    GetToFacebookCatalog,
    PostToFacebookCatalog,
)


# --- Tests for DTOs
class TestDeleteToFacebookCatalogPimProductsProductFacebookParamsModel:
    def test_valid(self):
        dto = DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId=1,
            shopId=1,
            products=[1, 2, 3]
        )
        assert dto.facebookCatalogId == 1
        assert dto.shopId == 1
        assert dto.products == [1, 2, 3]

    def test_multiple_products(self):
        dto = DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId=2,
            shopId=2,
            products=[10, 20, 30, 40]
        )
        assert dto.facebookCatalogId == 2
        assert dto.shopId == 2
        assert dto.products == [10, 20, 30, 40]

    def test_single_product(self):
        dto = DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId=100,
            shopId=50,
            products=[999]
        )
        assert dto.facebookCatalogId == 100
        assert dto.shopId == 50
        assert dto.products == [999]

    def test_invalid_facebook_catalog_id_zero(self):
        with pytest.raises(ValidationError):
            DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
                facebookCatalogId=0,
                shopId=1,
                products=[1, 2, 3]
            )

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
                facebookCatalogId=1,
                shopId=0,
                products=[1, 2, 3]
            )

    def test_empty_products(self):
        with pytest.raises(ValidationError):
            DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
                facebookCatalogId=1,
                shopId=1,
                products=[]
            )


class TestPostToFacebookCatalogPimProductsProductFacebookParamsModel:
    def test_valid(self):
        dto = PostToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId=1,
            shopId=1,
            products=[1, 2, 3]
        )
        assert dto.facebookCatalogId == 1
        assert dto.shopId == 1
        assert dto.products == [1, 2, 3]

    def test_multiple_products(self):
        dto = PostToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId=2,
            shopId=2,
            products=[10, 20, 30, 40]
        )
        assert dto.facebookCatalogId == 2
        assert dto.shopId == 2
        assert dto.products == [10, 20, 30, 40]

    def test_single_product(self):
        dto = PostToFacebookCatalogPimProductsProductFacebookParamsModel(
            facebookCatalogId=100,
            shopId=50,
            products=[999]
        )
        assert dto.facebookCatalogId == 100
        assert dto.shopId == 50
        assert dto.products == [999]

    def test_empty_products(self):
        with pytest.raises(ValidationError):
            PostToFacebookCatalogPimProductsProductFacebookParamsModel(
                facebookCatalogId=1,
                shopId=1,
                products=[]
            )


# --- Tests for Endpoints
class TestDeleteToFacebookCatalog:
    def test_instantiate_with_params(self):
        endpoint = DeleteToFacebookCatalog(
            params=DeleteToFacebookCatalogPimProductsProductFacebookParamsModel(
                facebookCatalogId=1,
                shopId=1,
                products=[1, 2, 3]
            )
        )
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/products/productsToFacebookCatalog/delete'
        assert endpoint.params.facebookCatalogId == 1
        assert endpoint.params.shopId == 1
        assert endpoint.params.products == [1, 2, 3]

    def test_instantiate_missing_params(self):
        with pytest.raises(ValidationError):
            DeleteToFacebookCatalog()


class TestGetToFacebookCatalog:
    def test_instantiate_with_all_params(self):
        endpoint = GetToFacebookCatalog(
            facebookCatalogId=1,
            shopId=1
        )
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/products/productsToFacebookCatalog'
        assert endpoint.facebookCatalogId == 1
        assert endpoint.shopId == 1

    def test_invalid_facebook_catalog_id_zero(self):
        with pytest.raises(ValidationError):
            GetToFacebookCatalog(
                facebookCatalogId=0,
                shopId=1
            )

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            GetToFacebookCatalog(
                facebookCatalogId=1,
                shopId=0
            )


class TestPostToFacebookCatalog:
    def test_instantiate_with_params(self):
        endpoint = PostToFacebookCatalog(
            params=PostToFacebookCatalogPimProductsProductFacebookParamsModel(
                facebookCatalogId=1,
                shopId=1,
                products=[1, 2, 3]
            )
        )
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/products/productsToFacebookCatalog'
        assert endpoint.params.facebookCatalogId == 1
        assert endpoint.params.shopId == 1
        assert endpoint.params.products == [1, 2, 3]

    def test_instantiate_missing_params(self):
        with pytest.raises(ValidationError):
            PostToFacebookCatalog()
