import pytest
from pydantic import ValidationError

from src.idosell.pim.products.images import (
    # DTOs
    DeletePimProductsImagesParamsModel,
    PutPimProductsImagesParamsModel,
    # Endpoints
    Delete,
    Put,
)
from src.idosell.pim.products._common import (
    ProductIdentModel,
    ProductsImages,
    ProductsImagesSettingsModel,
    ProductImagesModel,
    ProductIconsModel,
    IdentTypeEnum,
    ProductsImagesSourceTypeEnum,
    ProductIconTypeEnum,
)


# --- Tests for DTOs
class TestDeletePimProductsImagesParamsModel:
    def test_valid(self):
        dto = DeletePimProductsImagesParamsModel(
            deleteAll=False,
            productId=1,
            shopId=1,
            productImagesId=["img1"]
        )
        assert dto.deleteAll is False
        assert dto.productId == 1
        assert len(dto.productImagesId) == 1

    def test_deleteAll_true(self):
        dto = DeletePimProductsImagesParamsModel(
            deleteAll=True,
            productId=1,
            shopId=1,
            productImagesId=["img1"]
        )
        assert dto.deleteAll is True

    def test_multiple_productImagesId(self):
        dto = DeletePimProductsImagesParamsModel(
            deleteAll=False,
            productId=1,
            shopId=1,
            productImagesId=["img1", "img2", "img3"]
        )
        assert len(dto.productImagesId) == 3

    def test_empty_productImagesId(self):
        # Should raise ValidationError due to min_length=1
        with pytest.raises(ValidationError):
            DeletePimProductsImagesParamsModel(
                deleteAll=False,
                productId=1,
                shopId=1,
                productImagesId=[]
            )

    def test_invalid_productId_zero(self):
        with pytest.raises(ValidationError):
            DeletePimProductsImagesParamsModel(
                deleteAll=False,
                productId=0,
                shopId=1,
                productImagesId=["img1"]
            )

    def test_invalid_shopId_zero(self):
        with pytest.raises(ValidationError):
            DeletePimProductsImagesParamsModel(
                deleteAll=False,
                productId=1,
                shopId=0,
                productImagesId=["img1"]
            )


class TestPutPimProductsImagesParamsModel:
    def test_valid(self):
        dto = PutPimProductsImagesParamsModel(
            productsImagesSettings=ProductsImagesSettingsModel(
                productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                productsImagesApplyMacro=False
            ),
            productsImages=[
                ProductsImages(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    shopId=1,
                    otherShopsForPic=[],
                    productImages=[
                        ProductImagesModel(
                            productImageSource="https://example.com/img1.jpg",
                            productImageNumber=1,
                            productImagePriority=1,
                            deleteProductImage=False
                        )
                    ],
                    productIcons=[],
                    productImagesSettings=ProductsImagesSettingsModel(
                        productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                        productsImagesApplyMacro=False
                    )
                )
            ]
        )
        assert len(dto.productsImages) == 1
        assert dto.productsImages[0].productIdent.identValue == "123"

    def test_multiple_productsImages(self):
        dto = PutPimProductsImagesParamsModel(
            productsImagesSettings=ProductsImagesSettingsModel(
                productsImagesSourceType=ProductsImagesSourceTypeEnum.BASE64,
                productsImagesApplyMacro=True
            ),
            productsImages=[
                ProductsImages(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    shopId=1,
                    otherShopsForPic=[2, 3],
                    productImages=[
                        ProductImagesModel(
                            productImageSource="data:image/jpeg;base64,encoded",
                            productImageNumber=1,
                            productImagePriority=1,
                            deleteProductImage=False
                        ),
                        ProductImagesModel(
                            productImageSource="data:image/jpeg;base64,encoded2",
                            productImageNumber=2,
                            productImagePriority=2,
                            deleteProductImage=False
                        )
                    ],
                    productIcons=[
                        ProductIconsModel(
                            productIconSource="data:image/jpeg;base64,icon",
                            deleteProductIcon=False,
                            productIconType=ProductIconTypeEnum.SHOP
                        )
                    ],
                    productImagesSettings=ProductsImagesSettingsModel(
                        productsImagesSourceType=ProductsImagesSourceTypeEnum.BASE64,
                        productsImagesApplyMacro=False
                    )
                ),
                ProductsImages(
                    productIdent=ProductIdentModel(
                        identValue="456",
                        productIdentType=IdentTypeEnum.INDEX
                    ),
                    shopId=2,
                    otherShopsForPic=[],
                    productImages=[],
                    productIcons=[],
                    productImagesSettings=ProductsImagesSettingsModel(
                        productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                        productsImagesApplyMacro=True
                    )
                )
            ]
        )
        assert len(dto.productsImages) == 2
        assert len(dto.productsImages[0].productImages) == 2
        assert len(dto.productsImages[0].productIcons) == 1

    def test_empty_productsImages(self):
        # Should raise ValidationError due to min_length=1
        with pytest.raises(ValidationError):
            PutPimProductsImagesParamsModel(
                productsImagesSettings=ProductsImagesSettingsModel(
                    productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                    productsImagesApplyMacro=False
                ),
                productsImages=[]
            )

    def test_invalid_productImagePriority_zero(self):
        with pytest.raises(ValidationError):
            PutPimProductsImagesParamsModel(
                productsImagesSettings=ProductsImagesSettingsModel(
                    productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                    productsImagesApplyMacro=False
                ),
                productsImages=[
                    ProductsImages(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        shopId=1,
                        otherShopsForPic=[],
                        productImages=[
                            ProductImagesModel(
                                productImageSource="https://example.com/img1.jpg",
                                productImageNumber=1,
                                productImagePriority=0,  # Invalid
                                deleteProductImage=False
                            )
                        ],
                        productIcons=[],
                        productImagesSettings=ProductsImagesSettingsModel(
                            productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                            productsImagesApplyMacro=False
                        )
                    )
                ]
            )


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=[
                DeletePimProductsImagesParamsModel(
                    deleteAll=False,
                    productId=1,
                    shopId=1,
                    productImagesId=["img1"]
                )
            ]
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/images/delete'
        assert len(dto.params[0].productImagesId) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()

    def test_invalid_params_empty_productImagesId(self):
        with pytest.raises(ValidationError):
            Delete(
                params=[
                    DeletePimProductsImagesParamsModel(
                        deleteAll=False,
                        productId=1,
                        shopId=1,
                        productImagesId=[]
                    )
                ]
            )


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsImagesParamsModel(
                productsImagesSettings=ProductsImagesSettingsModel(
                    productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                    productsImagesApplyMacro=False
                ),
                productsImages=[
                    ProductsImages(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        shopId=1,
                        otherShopsForPic=[],
                        productImages=[
                            ProductImagesModel(
                                productImageSource="https://example.com/img1.jpg",
                                productImageNumber=1,
                                productImagePriority=1,
                                deleteProductImage=False
                            )
                        ],
                        productIcons=[],
                        productImagesSettings=ProductsImagesSettingsModel(
                            productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                            productsImagesApplyMacro=False
                        )
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/images'
        assert len(dto.params.productsImages) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()

    def test_invalid_params_empty_productsImages(self):
        with pytest.raises(ValidationError):
            Put(
                params=PutPimProductsImagesParamsModel(
                    productsImagesSettings=ProductsImagesSettingsModel(
                        productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                        productsImagesApplyMacro=False
                    ),
                    productsImages=[]
                )
            )
