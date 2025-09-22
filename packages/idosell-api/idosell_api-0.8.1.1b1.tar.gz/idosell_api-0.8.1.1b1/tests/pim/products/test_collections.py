import pytest
from pydantic import ValidationError

from src.idosell.pim.products.collections import (
    # DTOs
    DeleteProductsPimProductsCollectionsParamsModel,
    PostPimProductsCollectionsParamsModel,
    PostProductsPimProductsCollectionsParamsModel,
    PutProductsPimProductsCollectionsParamsModel,
    PutRenewPimProductsCollectionsParamsModel,
    # Endpoints
    Post,
    DeleteProducts,
    PostProducts,
    PutProducts,
    PutRenew,
)
from src.idosell.pim.products._common import (
    ProductIdentCollectionsModel,
    ProductsCollectionsDeleteProductsModel,
    ProductsCollectionsPostModel,
    ProductsCollectionsPostProductsModel,
    ProductsCollectionsPutProductsModel,
    ProductsCollectionsPutRenewModel,
    ProductSizesPostModel,
    ProductSizesBundlesCollectionsModel,
    CollectionIdentModel,
    AddTypeEnum,
    IdentTypeEnum,
)


# --- Tests for DTOs
class TestDeleteProductsPimProductsCollectionsParamsModel:
    def test_valid(self):
        dto = DeleteProductsPimProductsCollectionsParamsModel(
            products=[ProductsCollectionsDeleteProductsModel(
                productId=123
            )],
            collectionId=1
        )
        assert len(dto.products) == 1
        assert dto.collectionId == 1

    def test_multiple_products(self):
        dto = DeleteProductsPimProductsCollectionsParamsModel(
            products=[
                ProductsCollectionsDeleteProductsModel(
                    productId=123
                ),
                ProductsCollectionsDeleteProductsModel(
                    productId=456
                )
            ],
            collectionId=5
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            DeleteProductsPimProductsCollectionsParamsModel(
                products=[],
                collectionId=1
            )

    def test_invalid_collection_id_zero(self):
        with pytest.raises(ValidationError):
            DeleteProductsPimProductsCollectionsParamsModel(
                products=[ProductsCollectionsDeleteProductsModel(
                    productId=123
                )],
                collectionId=0
            )


class TestPostPimProductsCollectionsParamsModel:
    def test_valid(self):
        dto = PostPimProductsCollectionsParamsModel(
            products=[ProductsCollectionsPostModel(
                productId=123,
                productSizes=[ProductSizesPostModel(
                    size="M"
                )],
                quantity=2
            )]
        )
        assert len(dto.products) == 1
        assert dto.products[0].quantity == 2

    def test_multiple_products(self):
        dto = PostPimProductsCollectionsParamsModel(
            products=[
                ProductsCollectionsPostModel(
                    productId=123,
                    productSizes=[ProductSizesPostModel(
                        size="M"
                    )],
                    quantity=2
                ),
                ProductsCollectionsPostModel(
                    productId=456,
                    productSizes=[ProductSizesPostModel(
                        size="L"
                    )],
                    quantity=1
                )
            ]
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PostPimProductsCollectionsParamsModel(
                products=[]
            )


class TestPostProductsPimProductsCollectionsParamsModel:
    def test_valid(self):
        dto = PostProductsPimProductsCollectionsParamsModel(
            products=[ProductsCollectionsPostProductsModel(
                productId=123,
                productSizes=[ProductSizesPostModel(
                    size="M"
                )],
                addType=AddTypeEnum.ALLSIZES,
                quantity=3
            )],
            collectionId=2
        )
        assert len(dto.products) == 1
        assert dto.collectionId == 2

    def test_multiple_products(self):
        dto = PostProductsPimProductsCollectionsParamsModel(
            products=[
                ProductsCollectionsPostProductsModel(
                    productId=123,
                    productSizes=[ProductSizesPostModel(
                        size="M"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=2
                ),
                ProductsCollectionsPostProductsModel(
                    productId=456,
                    productSizes=[ProductSizesPostModel(
                        size="L"
                    )],
                    addType=AddTypeEnum.SELECTEDSIZES,
                    quantity=1
                )
            ],
            collectionId=5
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PostProductsPimProductsCollectionsParamsModel(
                products=[],
                collectionId=1
            )

    def test_invalid_collection_id_zero(self):
        with pytest.raises(ValidationError):
            PostProductsPimProductsCollectionsParamsModel(
                products=[ProductsCollectionsPostProductsModel(
                    productId=123,
                    productSizes=[ProductSizesPostModel(
                        size="M"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=3
                )],
                collectionId=0
            )


class TestPutProductsPimProductsCollectionsParamsModel:
    def test_valid(self):
        dto = PutProductsPimProductsCollectionsParamsModel(
            products=[ProductsCollectionsPutProductsModel(
                productId=123,
                quantity=5
            )],
            collectionId=2
        )
        assert len(dto.products) == 1
        assert dto.products[0].quantity == 5

    def test_multiple_products(self):
        dto = PutProductsPimProductsCollectionsParamsModel(
            products=[
                ProductsCollectionsPutProductsModel(
                    productId=123,
                    quantity=3
                ),
                ProductsCollectionsPutProductsModel(
                    productId=456,
                    quantity=3
                )
            ],
            collectionId=5
        )
        assert len(dto.products) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PutProductsPimProductsCollectionsParamsModel(
                products=[],
                collectionId=1
            )


class TestPutRenewPimProductsCollectionsParamsModel:
    def test_valid(self):
        dto = PutRenewPimProductsCollectionsParamsModel(
            products=[ProductsCollectionsPutRenewModel(
                productIdent=ProductIdentCollectionsModel(
                    productId="123",
                    productIdentType=IdentTypeEnum.ID
                ),
                productSizes=[ProductSizesBundlesCollectionsModel(
                    size="M",
                    sizePanelName="Medium"
                )],
                addType=AddTypeEnum.ALLSIZES,
                quantity=1
            )],
            collectionIdent=CollectionIdentModel(
                collectionId="5",
                collectionIdentType=IdentTypeEnum.ID
            )
        )
        assert len(dto.products) == 1
        assert dto.products[0].quantity == 1

    def test_multiple_products(self):
        dto = PutRenewPimProductsCollectionsParamsModel(
            products=[
                ProductsCollectionsPutRenewModel(
                    productIdent=ProductIdentCollectionsModel(
                        productId="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    productSizes=[ProductSizesBundlesCollectionsModel(
                        size="M",
                        sizePanelName="Medium"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=2
                ),
                ProductsCollectionsPutRenewModel(
                    productIdent=ProductIdentCollectionsModel(
                        productId="456",
                        productIdentType=IdentTypeEnum.ID
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
            collectionIdent=CollectionIdentModel(
                collectionId="10",
                collectionIdentType=IdentTypeEnum.ID
            )
        )
        assert len(dto.products) == 2
        assert len(dto.products[1].productSizes) == 2

    def test_empty_products_invalid(self):
        with pytest.raises(ValidationError):
            PutRenewPimProductsCollectionsParamsModel(
                products=[],
                collectionIdent=CollectionIdentModel(
                    collectionId="5",
                    collectionIdentType=IdentTypeEnum.ID
                )
            )


# --- Tests for Endpoints
class TestPost:
    def test_instantiate_with_products(self):
        dto = Post(
            params=PostPimProductsCollectionsParamsModel(
                products=[ProductsCollectionsPostModel(
                    productId=123,
                    productSizes=[ProductSizesPostModel(
                        size="M"
                    )],
                    quantity=2
                )]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/collections'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Post()


class TestDeleteProducts:
    def test_instantiate_with_single_collection(self):
        dto = DeleteProducts(
            params=[
                DeleteProductsPimProductsCollectionsParamsModel(
                    products=[ProductsCollectionsDeleteProductsModel(
                        productId=123
                    )],
                    collectionId=1
                )
            ]
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/collections/products/delete'
        assert len(dto.params) == 1

    def test_instantiate_with_multiple_collections(self):
        dto = DeleteProducts(
            params=[
                DeleteProductsPimProductsCollectionsParamsModel(
                    products=[ProductsCollectionsDeleteProductsModel(
                        productId=123
                    )],
                    collectionId=1
                ),
                DeleteProductsPimProductsCollectionsParamsModel(
                    products=[
                        ProductsCollectionsDeleteProductsModel(
                            productId=456
                        )
                    ],
                    collectionId=2
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
            params=PostProductsPimProductsCollectionsParamsModel(
                products=[ProductsCollectionsPostProductsModel(
                    productId=123,
                    productSizes=[ProductSizesPostModel(
                        size="M"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=3
                )],
                collectionId=2
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/collections/products'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PostProducts()


class TestPutProducts:
    def test_instantiate_with_products(self):
        dto = PutProducts(
            params=PutProductsPimProductsCollectionsParamsModel(
                products=[ProductsCollectionsPutProductsModel(
                    productId=123,
                    quantity=5
                )],
                collectionId=2
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/collections/products'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutProducts()


class TestPutRenew:
    def test_instantiate_with_products(self):
        dto = PutRenew(
            params=PutRenewPimProductsCollectionsParamsModel(
                products=[ProductsCollectionsPutRenewModel(
                    productIdent=ProductIdentCollectionsModel(
                        productId="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    productSizes=[ProductSizesBundlesCollectionsModel(
                        size="M",
                        sizePanelName="Medium"
                    )],
                    addType=AddTypeEnum.ALLSIZES,
                    quantity=1
                )],
                collectionIdent=CollectionIdentModel(
                    collectionId="5",
                    collectionIdentType=IdentTypeEnum.ID
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/collections/renew'
        assert len(dto.params.products) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutRenew()
