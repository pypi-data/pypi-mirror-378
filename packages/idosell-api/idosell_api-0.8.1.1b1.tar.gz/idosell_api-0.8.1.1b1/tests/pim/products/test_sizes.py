import pytest
from pydantic import ValidationError

from src.idosell.pim.products.sizes import (
    # DTOs
    ProductPricesSizesModel,
    SitesDataModel,
    SizeDataModel,
    IndexesDataSizesPutModel,
    SizesParamsDeleteModel,
    DeletePimProductsSizesParamsModel,
    SizesModel,
    SizesProductsDataPutModel,
    # Endpoints
    Delete,
    Get,
    Put,
    # Enums
    DeleteModeSizesEnum,
    PutModeSizesEnum,
)


# --- Tests for DTOs
class TestProductPricesSizesModel:
    def test_valid(self):
        dto = ProductPricesSizesModel(
            productPriceRetail=100.0,
            productPriceWholesale=80.0,
            productSearchPriceMin=50.0,
            productPriceSuggested=90.0
        )
        assert dto.productPriceRetail == 100.0
        assert dto.productPriceWholesale == 80.0
        assert dto.productSearchPriceMin == 50.0
        assert dto.productPriceSuggested == 90.0

    def test_invalid_price_retail_zero(self):
        with pytest.raises(ValidationError):
            ProductPricesSizesModel(
                productPriceRetail=0,
                productPriceWholesale=80.0,
                productSearchPriceMin=50.0,
                productPriceSuggested=90.0
            )

    def test_invalid_price_retail_negative(self):
        with pytest.raises(ValidationError):
            ProductPricesSizesModel(
                productPriceRetail=-10.0,
                productPriceWholesale=80.0,
                productSearchPriceMin=50.0,
                productPriceSuggested=90.0
            )


class TestSitesDataModel:
    def test_valid(self):
        dto = SitesDataModel(
            siteId=1,
            productPrices=ProductPricesSizesModel(
                productPriceRetail=100.0,
                productPriceWholesale=80.0,
                productSearchPriceMin=50.0,
                productPriceSuggested=90.0
            )
        )
        assert dto.siteId == 1
        assert dto.productPrices.productPriceRetail == 100.0

    def test_invalid_site_id_zero(self):
        with pytest.raises(ValidationError):
            SitesDataModel(
                siteId=0,
                productPrices=ProductPricesSizesModel(
                    productPriceRetail=100.0,
                    productPriceWholesale=80.0,
                    productSearchPriceMin=50.0,
                    productPriceSuggested=90.0
                )
            )


class TestSizeDataModel:
    def test_valid(self):
        dto = SizeDataModel(
            productWeight=1000,
            codeProducer="ABC123",
            productSizeCodeExternal="EXT456",
            sitesData=[SitesDataModel(
                siteId=1,
                productPrices=ProductPricesSizesModel(
                    productPriceRetail=100.0,
                    productPriceWholesale=80.0,
                    productSearchPriceMin=50.0,
                    productPriceSuggested=90.0
                )
            )]
        )
        assert dto.productWeight == 1000
        assert dto.codeProducer == "ABC123"
        assert dto.productSizeCodeExternal == "EXT456"
        assert len(dto.sitesData) == 1

    def test_multiple_sites(self):
        dto = SizeDataModel(
            productWeight=500,
            codeProducer="XYZ789",
            productSizeCodeExternal="EXT789",
            sitesData=[
                SitesDataModel(
                    siteId=1,
                    productPrices=ProductPricesSizesModel(
                        productPriceRetail=100.0,
                        productPriceWholesale=80.0,
                        productSearchPriceMin=50.0,
                        productPriceSuggested=90.0
                    )
                ),
                SitesDataModel(
                    siteId=2,
                    productPrices=ProductPricesSizesModel(
                        productPriceRetail=120.0,
                        productPriceWholesale=95.0,
                        productSearchPriceMin=60.0,
                        productPriceSuggested=110.0
                    )
                )
            ]
        )
        assert len(dto.sitesData) == 2

    def test_invalid_weight_zero(self):
        with pytest.raises(ValidationError):
            SizeDataModel(
                productWeight=0,
                codeProducer="ABC123",
                productSizeCodeExternal="EXT456",
                sitesData=[]
            )


class TestIndexesDataSizesPutModel:
    def test_valid(self):
        dto = IndexesDataSizesPutModel(
            sizeIndex="SIZE001",
            sizeData=SizeDataModel(
                productWeight=1000,
                codeProducer="ABC123",
                productSizeCodeExternal="EXT456",
                sitesData=[SitesDataModel(
                    siteId=1,
                    productPrices=ProductPricesSizesModel(
                        productPriceRetail=100.0,
                        productPriceWholesale=80.0,
                        productSearchPriceMin=50.0,
                        productPriceSuggested=90.0
                    )
                )]
            )
        )
        assert dto.sizeIndex == "SIZE001"
        assert dto.sizeData.productWeight == 1000


class TestSizesParamsDeleteModel:
    def test_valid(self):
        dto = SizesParamsDeleteModel(
            sizeId="S",
            sizePanelName="Small"
        )
        assert dto.sizeId == "S"
        assert dto.sizePanelName == "Small"


class TestDeletePimProductsSizesParamsModel:
    def test_valid(self):
        dto = DeletePimProductsSizesParamsModel(
            productId=1,
            sizes=[SizesParamsDeleteModel(
                sizeId="S",
                sizePanelName="Small"
            )]
        )
        assert dto.productId == 1
        assert len(dto.sizes) == 1

    def test_multiple_sizes(self):
        dto = DeletePimProductsSizesParamsModel(
            productId=2,
            sizes=[
                SizesParamsDeleteModel(sizeId="S", sizePanelName="Small"),
                SizesParamsDeleteModel(sizeId="M", sizePanelName="Medium"),
                SizesParamsDeleteModel(sizeId="L", sizePanelName="Large")
            ]
        )
        assert len(dto.sizes) == 3

    def test_invalid_product_id_zero(self):
        with pytest.raises(ValidationError):
            DeletePimProductsSizesParamsModel(
                productId=0,
                sizes=[SizesParamsDeleteModel(sizeId="S", sizePanelName="Small")]
            )


class TestSizesModel:
    def test_valid(self):
        dto = SizesModel(
            sizeId="M",
            sizePanelName="Medium",
            sizeData=SizeDataModel(
                productWeight=1000,
                codeProducer="ABC123",
                productSizeCodeExternal="EXT456",
                sitesData=[SitesDataModel(
                    siteId=1,
                    productPrices=ProductPricesSizesModel(
                        productPriceRetail=100.0,
                        productPriceWholesale=80.0,
                        productSearchPriceMin=50.0,
                        productPriceSuggested=90.0
                    )
                )]
            )
        )
        assert dto.sizeId == "M"
        assert dto.sizePanelName == "Medium"
        assert dto.sizeData.productWeight == 1000


class TestSizesProductsDataPutModel:
    def test_valid(self):
        dto = SizesProductsDataPutModel(
            productId=1,
            sizes=[SizesModel(
                sizeId="L",
                sizePanelName="Large",
                sizeData=SizeDataModel(
                    productWeight=1500,
                    codeProducer="XYZ789",
                    productSizeCodeExternal="EXT789",
                    sitesData=[SitesDataModel(
                        siteId=1,
                        productPrices=ProductPricesSizesModel(
                            productPriceRetail=120.0,
                            productPriceWholesale=95.0,
                            productSearchPriceMin=60.0,
                            productPriceSuggested=110.0
                        )
                    )]
                )
            )]
        )
        assert dto.productId == 1
        assert len(dto.sizes) == 1

    def test_multiple_sizes(self):
        dto = SizesProductsDataPutModel(
            productId=3,
            sizes=[
                SizesModel(
                    sizeId="XS",
                    sizePanelName="Extra Small",
                    sizeData=SizeDataModel(
                        productWeight=800,
                        codeProducer="ABC123",
                        productSizeCodeExternal="EXT123",
                        sitesData=[]
                    )
                ),
                SizesModel(
                    sizeId="XL",
                    sizePanelName="Extra Large",
                    sizeData=SizeDataModel(
                        productWeight=2000,
                        codeProducer="XYZ789",
                        productSizeCodeExternal="EXT789",
                        sitesData=[]
                    )
                )
            ]
        )
        assert len(dto.sizes) == 2

    def test_invalid_product_id_zero(self):
        with pytest.raises(ValidationError):
            SizesProductsDataPutModel(
                productId=0,
                sizes=[]
            )


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            mode=DeleteModeSizesEnum.DELETE_BY_SIZE,
            params=DeletePimProductsSizesParamsModel(
                productId=1,
                sizes=[SizesParamsDeleteModel(
                    sizeId="S",
                    sizePanelName="Small"
                )]
            ),
            deleteSizesIndexesData=["SIZE001"]
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/sizes/delete'
        assert dto.mode == DeleteModeSizesEnum.DELETE_BY_SIZE
        assert dto.params.productId == 1
        assert len(dto.deleteSizesIndexesData) == 1

    def test_instantiate_with_multiple_indexes(self):
        dto = Delete(
            mode=DeleteModeSizesEnum.DELETE_ALL,
            params=DeletePimProductsSizesParamsModel(
                productId=2,
                sizes=[]
            ),
            deleteSizesIndexesData=["SIZE001", "SIZE002", "SIZE003"]
        )
        assert dto.mode == DeleteModeSizesEnum.DELETE_ALL
        assert len(dto.deleteSizesIndexesData) == 3

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()

    def test_invalid_empty_indexes_required(self):
        with pytest.raises(ValidationError):
            Delete(
                mode=DeleteModeSizesEnum.DELETE_BY_SIZE,
                params=DeletePimProductsSizesParamsModel(
                    productId=1,
                    sizes=[SizesParamsDeleteModel(sizeId="S", sizePanelName="Small")]
                ),
                deleteSizesIndexesData=[]
            )


class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/sizes'
        assert dto.page is None
        assert dto.pageNumber is None

    def test_instantiate_minimal_get(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/sizes'

    def test_endpoint_properties(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            mode=PutModeSizesEnum.ADD,
            sizesProductsData=[SizesProductsDataPutModel(
                productId=1,
                sizes=[]
            )],
            indexesData=[IndexesDataSizesPutModel(
                sizeIndex="SIZE001",
                sizeData=SizeDataModel(
                    productWeight=1000,
                    codeProducer="ABC123",
                    productSizeCodeExternal="EXT456",
                    sitesData=[]
                )
            )]
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/sizes'
        assert dto.mode == PutModeSizesEnum.ADD

    def test_instantiate_with_sizes_data(self):
        dto = Put(
            mode=PutModeSizesEnum.REPLACE,
            sizesProductsData=[SizesProductsDataPutModel(
                productId=1,
                sizes=[SizesModel(
                    sizeId="M",
                    sizePanelName="Medium",
                    sizeData=SizeDataModel(
                        productWeight=1000,
                        codeProducer="ABC123",
                        productSizeCodeExternal="EXT456",
                        sitesData=[]
                    )
                )]
            )],
            indexesData=[IndexesDataSizesPutModel(
                sizeIndex="SIZE001",
                sizeData=SizeDataModel(
                    productWeight=1000,
                    codeProducer="ABC123",
                    productSizeCodeExternal="EXT456",
                    sitesData=[]
                )
            )]
        )
        assert dto.mode == PutModeSizesEnum.REPLACE
        assert len(dto.sizesProductsData[0].sizes) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()
