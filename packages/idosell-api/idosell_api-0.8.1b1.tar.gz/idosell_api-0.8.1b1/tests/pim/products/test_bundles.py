import pytest
from pydantic import ValidationError

from src.idosell.pim.products.bundles import (
    # DTOs
    DeleteProductsPimProductsBundlesParamsModel,
    PostBundlesPimProductsBundlesParamsModel,
    PostProductsPimProductsBundlesParamsModel,
    PutProductsQuantityPimProductsBundlesParamsModel,
    PutRenewPimProductsBundlesParamsModel,
    # Endpoints
    PostBundles,
    DeleteProducts,
    PostProducts,
    PutProductsQuantity,
    PutRenew,
)
from src.idosell.pim.products._common import (
    ProductIdentBundlesModel,
    ProductPutRenewModel,
    ProductsBundleDeleteProductsModel,
    ProductsBundlesPostModel,
    ProductsBundlesPostProductsModel,
    ProductsPutProductsQuantityModel,
    ProductSizesBundlesModel,
    ProductSizesBundlesCollectionsModel,
    AddTypeEnum,
    IdentTypeEnum,
)


# --- Tests for DTOs
class TestDeleteProductsPimProductsBundlesParamsModel:
    def test_valid(self):
        dto = DeleteProductsPimProductsBundlesParamsModel(
            products=[ProductsBundleDeleteProductsModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="123"
                )
            )],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 1
        assert dto.bundleIdent.identValue == "999"

    def test_multiple_products(self):
        dto = DeleteProductsPimProductsBundlesParamsModel(
            products=[
                ProductsBundleDeleteProductsModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    )
                ),
                ProductsBundleDeleteProductsModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.INDEX,
                        identValue="ABC"
                    )
                )
            ],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            DeleteProductsPimProductsBundlesParamsModel(
                products=[],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )


class TestPostBundlesPimProductsBundlesParamsModel:
    def test_valid(self):
        dto = PostBundlesPimProductsBundlesParamsModel(
            products=[ProductsBundlesPostModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                productSizes=ProductSizesBundlesModel(
                    size="M",
                    sizePanelName="Medium"
                ),
                addType=AddTypeEnum.ALLSIZES,
                quantity=2.0
            )]
        )
        assert len(dto.products) == 1
        assert dto.products[0].addType == AddTypeEnum.ALLSIZES

    def test_multiple_products(self):
        dto = PostBundlesPimProductsBundlesParamsModel(
            products=[
                ProductsBundlesPostModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    productSizes=ProductSizesBundlesModel(
                        size="M",
                        sizePanelName="Medium"
                    ),
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=2.0
                ),
                ProductsBundlesPostModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.INDEX,
                        identValue="XYZ"
                    ),
                    productSizes=ProductSizesBundlesModel(
                        size="L",
                        sizePanelName="Large"
                    ),
                    addType=AddTypeEnum.SELECTEDSIZES,
                    quantity=1.5
                )
            ]
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PostBundlesPimProductsBundlesParamsModel(
                products=[]
            )


class TestPostProductsPimProductsBundlesParamsModel:
    def test_valid(self):
        dto = PostProductsPimProductsBundlesParamsModel(
            products=[ProductsBundlesPostProductsModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                productSizes=ProductSizesBundlesCollectionsModel(
                    size="M",
                    sizePanelName="Medium"
                ),
                addType=AddTypeEnum.ALLSIZES,
                quantity=3.0
            )],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 1
        assert dto.bundleIdent.identValue == "999"

    def test_multiple_products(self):
        dto = PostProductsPimProductsBundlesParamsModel(
            products=[
                ProductsBundlesPostProductsModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    productSizes=ProductSizesBundlesCollectionsModel(
                        size="M",
                        sizePanelName="Medium"
                    ),
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=2.0
                ),
                ProductsBundlesPostProductsModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.INDEX,
                        identValue="ABC"
                    ),
                    productSizes=ProductSizesBundlesCollectionsModel(
                        size="L",
                        sizePanelName="Large"
                    ),
                    addType=AddTypeEnum.SELECTEDSIZES,
                    quantity=1.0
                )
            ],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PostProductsPimProductsBundlesParamsModel(
                products=[],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )


class TestPutProductsQuantityPimProductsBundlesParamsModel:
    def test_valid(self):
        dto = PutProductsQuantityPimProductsBundlesParamsModel(
            products=[ProductsPutProductsQuantityModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                quantity=5.0
            )],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 1
        assert dto.products[0].quantity == 5.0

    def test_multiple_products(self):
        dto = PutProductsQuantityPimProductsBundlesParamsModel(
            products=[
                ProductsPutProductsQuantityModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    quantity=3.0
                ),
                ProductsPutProductsQuantityModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.INDEX,
                        identValue="DEF"
                    ),
                    quantity=2.5
                )
            ],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PutProductsQuantityPimProductsBundlesParamsModel(
                products=[],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )


class TestPutRenewPimProductsBundlesParamsModel:
    def test_valid(self):
        dto = PutRenewPimProductsBundlesParamsModel(
            products=[ProductPutRenewModel(
                productIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="123"
                ),
                productSizes=[ProductSizesBundlesCollectionsModel(
                    size="M",
                    sizePanelName="Medium"
                )],
                addType=AddTypeEnum.ALLSIZES,
                quantity=1
            )],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 1
        assert dto.products[0].quantity == 1

    def test_multiple_products(self):
        dto = PutRenewPimProductsBundlesParamsModel(
            products=[
                ProductPutRenewModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    productSizes=[ProductSizesBundlesCollectionsModel(
                        size="M",
                        sizePanelName="Medium"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=2
                ),
                ProductPutRenewModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.INDEX,
                        identValue="GHI"
                    ),
                    productSizes=[
                        ProductSizesBundlesCollectionsModel(
                            size="S",
                            sizePanelName="Small"
                        ),
                        ProductSizesBundlesCollectionsModel(
                            size="L",
                            sizePanelName="Large"
                        )
                    ],
                    addType=AddTypeEnum.SELECTEDSIZES,
                    quantity=1
                )
            ],
            bundleIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="999"
            )
        )
        assert len(dto.products) == 2
        assert len(dto.products[1].productSizes) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PutRenewPimProductsBundlesParamsModel(
                products=[],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )


# --- Tests for Endpoints
class TestPostBundles:
    def test_instantiate_with_products(self):
        dto = PostBundles(
            params=PostBundlesPimProductsBundlesParamsModel(
                products=[ProductsBundlesPostModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    productSizes=ProductSizesBundlesModel(
                        size="M",
                        sizePanelName="Medium"
                    ),
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=2.0
                )]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/bundles/bundles'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PostBundles()


class TestDeleteProducts:
    def test_instantiate_with_single_bundle(self):
        dto = DeleteProducts(
            params=[
                DeleteProductsPimProductsBundlesParamsModel(
                    products=[ProductsBundleDeleteProductsModel(
                        productIdent=ProductIdentBundlesModel(
                            productIdentType=IdentTypeEnum.ID,
                            identValue="123"
                        )
                    )],
                    bundleIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="999"
                    )
                )
            ]
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/bundles/products/delete'
        assert len(dto.params) == 1

    def test_instantiate_with_multiple_bundles(self):
        dto = DeleteProducts(
            params=[
                DeleteProductsPimProductsBundlesParamsModel(
                    products=[ProductsBundleDeleteProductsModel(
                        productIdent=ProductIdentBundlesModel(
                            productIdentType=IdentTypeEnum.ID,
                            identValue="123"
                        )
                    )],
                    bundleIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="999"
                    )
                ),
                DeleteProductsPimProductsBundlesParamsModel(
                    products=[
                        ProductsBundleDeleteProductsModel(
                            productIdent=ProductIdentBundlesModel(
                                productIdentType=IdentTypeEnum.INDEX,
                                identValue="ABC"
                            )
                        )
                    ],
                    bundleIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="888"
                    )
                )
            ]
        )
        assert len(dto.params) == 2

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            DeleteProducts()


class TestPostProducts:
    def test_instantiate_with_products(self):
        dto = PostProducts(
            params=PostProductsPimProductsBundlesParamsModel(
                products=[ProductsBundlesPostProductsModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    productSizes=ProductSizesBundlesCollectionsModel(
                        size="M",
                        sizePanelName="Medium"
                    ),
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=3.0
                )],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/bundles/products'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PostProducts()


class TestPutProductsQuantity:
    def test_instantiate_with_products(self):
        dto = PutProductsQuantity(
            params=PutProductsQuantityPimProductsBundlesParamsModel(
                products=[ProductsPutProductsQuantityModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    quantity=5.0
                )],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/bundles/productsQuantity'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutProductsQuantity()


class TestPutRenew:
    def test_instantiate_with_products(self):
        dto = PutRenew(
            params=PutRenewPimProductsBundlesParamsModel(
                products=[ProductPutRenewModel(
                    productIdent=ProductIdentBundlesModel(
                        productIdentType=IdentTypeEnum.ID,
                        identValue="123"
                    ),
                    productSizes=[ProductSizesBundlesCollectionsModel(
                        size="M",
                        sizePanelName="Medium"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=1
                )],
                bundleIdent=ProductIdentBundlesModel(
                    productIdentType=IdentTypeEnum.ID,
                    identValue="999"
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/bundles/renew'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutRenew()
