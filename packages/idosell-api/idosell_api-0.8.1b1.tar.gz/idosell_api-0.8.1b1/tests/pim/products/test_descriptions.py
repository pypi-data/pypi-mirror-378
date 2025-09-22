import pytest
from pydantic import ValidationError

from src.idosell.pim.products.descriptions import (
    # DTOs
    PutPimProductsDescriptionsParamsModel,
    # Endpoints
    Get,
    Put,
)
from src.idosell.pim.products._common import (
    ProductIdentModel,
    SectionModel,
    DescriptionSectionsModel,
    ProductDescriptionSectionsModel,
    ProductDescriptionsLangDataModel,
    ProductsDescriptionsModel,
    ProductAuctionDescriptionsDataModel,
    IdentTypeEnum,
    TypeEnum,
)


# --- Tests for DTOs
class TestPutPimProductsDescriptionsParamsModel:
    def test_valid(self):
        dto = PutPimProductsDescriptionsParamsModel(
            products=[
                ProductsDescriptionsModel(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    productDescriptionsLangData=[
                        ProductDescriptionsLangDataModel(
                            langId="en",
                            shopId=1,
                            productName="Product Name",
                            productAuctionName="Auction Name",
                            productPriceComparerName="Price Comparer",
                            productDescription="Description",
                            productLongDescription="Long desc",
                            productDescriptionSections=ProductDescriptionSectionsModel(descriptionSections=[]),
                            productAuctionLongDescription="Deprecated desc",
                            productMetaTitle="Meta Title",
                            productMetaDescription="Meta Desc",
                            productMetaKeywords="keywords"
                        )
                    ],
                    productAuctionDescriptionsData=[]
                )
            ]
        )
        assert len(dto.products) == 1
        assert dto.products[0].productIdent.identValue == "123"

    def test_multiple_products(self):
        dto = PutPimProductsDescriptionsParamsModel(
            products=[
                ProductsDescriptionsModel(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    productDescriptionsLangData=[],
                    productAuctionDescriptionsData=[]
                ),
                ProductsDescriptionsModel(
                    productIdent=ProductIdentModel(
                        identValue="456",
                        productIdentType=IdentTypeEnum.INDEX
                    ),
                    productDescriptionsLangData=[],
                    productAuctionDescriptionsData=[]
                )
            ]
        )
        assert len(dto.products) == 2

    def test_empty_products(self):
        # Should raise ValidationError due to min_length=1
        with pytest.raises(ValidationError):
            PutPimProductsDescriptionsParamsModel(products=[])


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get(
            type=IdentTypeEnum.ID,
            ids=[1],
            shopId=None
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/descriptions'
        assert dto.type == IdentTypeEnum.ID
        assert dto.ids == [1]
        assert dto.shopId is None

    def test_instantiate_with_shop_id(self):
        dto = Get(
            type=IdentTypeEnum.INDEX,
            ids=[2, 3],
            shopId=1
        )
        assert dto.shopId == 1
        assert dto.ids == [2, 3]

    def test_invalid_ids_empty(self):
        with pytest.raises(ValidationError):
            Get(
                type=IdentTypeEnum.ID,
                ids=[],
                shopId=None
            )

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            Get(
                type=IdentTypeEnum.ID,
                ids=[1],
                shopId=0
            )


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsDescriptionsParamsModel(
                products=[
                    ProductsDescriptionsModel(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        productDescriptionsLangData=[],
                        productAuctionDescriptionsData=[]
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/descriptions'
        assert len(dto.params.products) == 1

    def test_instantiate_with_full_data(self):
        dto = Put(
            params=PutPimProductsDescriptionsParamsModel(
                products=[
                    ProductsDescriptionsModel(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        productDescriptionsLangData=[
                            ProductDescriptionsLangDataModel(
                                langId="en",
                                shopId=1,
                                productName="Test Product",
                                productAuctionName="Auction",
                                productPriceComparerName="Comparer",
                                productDescription="Short desc",
                                productLongDescription="Long description",
                                productDescriptionSections=ProductDescriptionSectionsModel(
                                    descriptionSections=[
                                        DescriptionSectionsModel(
                                            section_1=SectionModel(
                                                type=TypeEnum.HTML,
                                                content="<p>Section 1</p>"
                                            ),
                                            section_2=SectionModel(
                                                type=TypeEnum.TEXT,
                                                content="Section 2"
                                            )
                                        )
                                    ]
                                ),
                                productAuctionLongDescription="Deprecated",
                                productMetaTitle="Title",
                                productMetaDescription="Meta desc",
                                productMetaKeywords="keywords"
                            )
                        ],
                        productAuctionDescriptionsData=[
                            ProductAuctionDescriptionsDataModel(
                                productAuctionId="auction123",
                                productAuctionSiteId="site456",
                                productAuctionName="Auction Product",
                                productAuctionAdditionalName="Additional",
                                productAuctionDescription="Description for auction"
                            )
                        ]
                    )
                ]
            )
        )
        assert dto.params.products[0].productDescriptionsLangData[0].langId == "en"
        assert dto.params.products[0].productAuctionDescriptionsData[0].productAuctionId == "auction123"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()

    def test_invalid_params_empty_products(self):
        with pytest.raises(ValidationError):
            Put(
                params=PutPimProductsDescriptionsParamsModel(products=[])
            )
