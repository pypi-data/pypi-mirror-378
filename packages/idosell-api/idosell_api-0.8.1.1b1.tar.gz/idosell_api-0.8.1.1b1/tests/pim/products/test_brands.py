import pytest
from pydantic import ValidationError

from src.idosell.pim.products.brands import (
    # DTOs
    DeletePimProductsBrandsParamsModel,
    PostPimProductsBrandsParamsModel,
    PutPimProductsBrandsParamsModel,
    PutFilterPimProductsBrandsParamsModel,
    # Endpoints
    Delete,
    GetFilter,
    PutFilter,
    Get,
    Post,
    Put,
)
from src.idosell.pim.products._common import (
    FilterActiveModel,
    ProducerPostModel,
    ProducerPutModel,
    FilterDisplayEnum,
    FilterValueSortEnum,
    ImagesSettingsModel,
    SourceTypeEnum,
    LanguagesConfigurationsModel,
    ProductsListImagesConfigurationModel,
    ProductCardImagesConfigurationModel,
    GraphicTypeEnum,
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for DTOs
class TestDeletePimProductsBrandsParamsModel:
    def test_valid(self):
        dto = DeletePimProductsBrandsParamsModel(
            ids=[1, 2, 3]
        )
        assert dto.ids == [1, 2, 3]

    def test_empty_list(self):
        dto = DeletePimProductsBrandsParamsModel(
            ids=[]
        )
        assert dto.ids == []


class TestPostPimProductsBrandsParamsModel:
    def test_valid(self):
        dto = PostPimProductsBrandsParamsModel(
            producers=[ProducerPostModel(
                nameInPanel="Brand Name",
                imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                languagesConfigurations=[]
            )]
        )
        assert len(dto.producers) == 1
        assert dto.producers[0].nameInPanel == "Brand Name"

    def test_multiple_producers(self):
        dto = PostPimProductsBrandsParamsModel(
            producers=[
                ProducerPostModel(
                    nameInPanel="Brand 1",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                    languagesConfigurations=[]
                ),
                ProducerPostModel(
                    nameInPanel="Brand 2",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.BASE64),
                    languagesConfigurations=[]
                )
            ]
        )
        assert len(dto.producers) == 2

    def test_empty_producers(self):
        dto = PostPimProductsBrandsParamsModel(
            producers=[]
        )
        assert dto.producers == []


class TestPutPimProductsBrandsParamsModel:
    def test_valid(self):
        dto = PutPimProductsBrandsParamsModel(
            producers=[ProducerPutModel(
                id=1,
                nameInPanel="Brand Name",
                imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                languagesConfigurations=[]
            )]
        )
        assert len(dto.producers) == 1
        assert dto.producers[0].id == 1

    def test_multiple_producers(self):
        dto = PutPimProductsBrandsParamsModel(
            producers=[
                ProducerPutModel(
                    id=1,
                    nameInPanel="Brand 1",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                    languagesConfigurations=[]
                ),
                ProducerPutModel(
                    id=2,
                    nameInPanel="Brand 2",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.BASE64),
                    languagesConfigurations=[]
                )
            ]
        )
        assert len(dto.producers) == 2

    def test_empty_producers(self):
        dto = PutPimProductsBrandsParamsModel(
            producers=[]
        )
        assert dto.producers == []

    def test_invalid_producer_id_zero(self):
        with pytest.raises(ValidationError):
            PutPimProductsBrandsParamsModel(
                producers=[ProducerPutModel(
                    id=0,
                    nameInPanel="Brand Name",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                    languagesConfigurations=[]
                )]
            )


class TestPutFilterPimProductsBrandsParamsModel:
    def test_valid(self):
        dto = PutFilterPimProductsBrandsParamsModel(
            shopId=1,
            languageId="en",
            producerId=1,
            filterForNodeIsDefault=BooleanStrShortEnum.YES,
            filtersActive=[FilterActiveModel(
                filterId="size",
                filterName="Size Filter",
                filterDisplay=FilterDisplayEnum.NAME,
                filterValueSort=FilterValueSortEnum.YES,
                filterDefaultEnabled=BooleanStrShortEnum.YES
            )]
        )
        assert dto.shopId == 1
        assert dto.languageId == "en"
        assert dto.producerId == 1
        assert dto.filterForNodeIsDefault == BooleanStrShortEnum.YES
        assert len(dto.filtersActive) == 1

    def test_multiple_filters(self):
        dto = PutFilterPimProductsBrandsParamsModel(
            shopId=1,
            languageId="pl",
            producerId=2,
            filterForNodeIsDefault=BooleanStrShortEnum.NO,
            filtersActive=[
                FilterActiveModel(
                    filterId="color",
                    filterName="Color Filter",
                    filterDisplay=FilterDisplayEnum.GFX,
                    filterValueSort=FilterValueSortEnum.PRIORITY,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                ),
                FilterActiveModel(
                    filterId="size",
                    filterName="Size Filter",
                    filterDisplay=FilterDisplayEnum.NAMEGFX,
                    filterValueSort=FilterValueSortEnum.NO,
                    filterDefaultEnabled=BooleanStrShortEnum.NO
                )
            ]
        )
        assert len(dto.filtersActive) == 2

    def test_empty_filters_active(self):
        dto = PutFilterPimProductsBrandsParamsModel(
            shopId=1,
            languageId="en",
            producerId=1,
            filterForNodeIsDefault=BooleanStrShortEnum.YES,
            filtersActive=[]
        )
        assert dto.filtersActive == []

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsBrandsParamsModel(
                shopId=0,
                languageId="en",
                producerId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[]
            )

    def test_invalid_producer_id_zero(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsBrandsParamsModel(
                shopId=1,
                languageId="en",
                producerId=0,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[]
            )


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=DeletePimProductsBrandsParamsModel(ids=[])
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/brands/delete'
        assert dto.params.ids == []

    def test_instantiate_with_ids(self):
        dto = Delete(
            params=DeletePimProductsBrandsParamsModel(ids=[1, 2, 3])
        )
        assert dto.params.ids == [1, 2, 3]

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()


class TestGetFilter:
    def test_instantiate_with_all_params(self):
        dto = GetFilter(
            shopId=1,
            languageId="en",
            producerId=1
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/brands/filter'
        assert dto.shopId == 1
        assert dto.languageId == "en"
        assert dto.producerId == 1

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(
                shopId=0,
                languageId="en",
                producerId=1
            )

    def test_invalid_producer_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(
                shopId=1,
                languageId="en",
                producerId=0
            )


class TestPutFilter:
    def test_instantiate_minimal(self):
        dto = PutFilter(
            params=PutFilterPimProductsBrandsParamsModel(
                shopId=1,
                languageId="en",
                producerId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/brands/filter'
        assert dto.params.shopId == 1
        assert dto.params.languageId == "en"
        assert dto.params.producerId == 1

    def test_instantiate_with_filters(self):
        dto = PutFilter(
            params=PutFilterPimProductsBrandsParamsModel(
                shopId=1,
                languageId="pl",
                producerId=2,
                filterForNodeIsDefault=BooleanStrShortEnum.NO,
                filtersActive=[FilterActiveModel(
                    filterId="color",
                    filterName="Color Filter",
                    filterDisplay=FilterDisplayEnum.NAME,
                    filterValueSort=FilterValueSortEnum.YES,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )]
            )
        )
        assert dto.params.producerId == 2
        assert len(dto.params.filtersActive) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutFilter()


class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/brands'
        assert dto.languagesIds is None

    def test_instantiate_with_languages(self):
        dto = Get(
            languagesIds=["en", "pl", "de"]
        )
        assert dto.languagesIds == ["en", "pl", "de"]

    def test_empty_languages_ids(self):
        dto = Get(
            languagesIds=[]
        )
        assert dto.languagesIds == []


class TestPost:
    def test_instantiate_minimal(self):
        dto = Post(
            params=PostPimProductsBrandsParamsModel(producers=[])
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/brands'
        assert dto.params.producers == []

    def test_instantiate_with_producers(self):
        dto = Post(
            params=PostPimProductsBrandsParamsModel(
                producers=[ProducerPostModel(
                    nameInPanel="New Brand",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                    languagesConfigurations=[LanguagesConfigurationsModel(
                        productsListImagesConfiguration=ProductsListImagesConfigurationModel(
                            graphicType=GraphicTypeEnum.IMG,
                            singleGraphic="image.jpg",
                            pcGraphic="pc.jpg",
                            tabletGraphic="tablet.jpg",
                            phoneGraphic="phone.jpg"
                        ),
                        productCardImagesConfiguration=ProductCardImagesConfigurationModel(
                            graphicType=GraphicTypeEnum.IMG,
                            singleGraphic="card.jpg",
                            pcGraphic="card_pc.jpg",
                            tabletGraphic="card_tab.jpg",
                            phoneGraphic="card_mob.jpg"
                        ),
                        languageId="en",
                        shopsConfigurations=[]
                    )]
                )]
            )
        )
        assert len(dto.params.producers) == 1
        assert dto.params.producers[0].nameInPanel == "New Brand"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Post()


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsBrandsParamsModel(producers=[])
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/brands'
        assert dto.params.producers == []

    def test_instantiate_with_producers(self):
        dto = Put(
            params=PutPimProductsBrandsParamsModel(
                producers=[ProducerPutModel(
                    id=1,
                    nameInPanel="Updated Brand",
                    imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.BASE64),
                    languagesConfigurations=[]
                )]
            )
        )
        assert len(dto.params.producers) == 1
        assert dto.params.producers[0].id == 1
        assert dto.params.producers[0].nameInPanel == "Updated Brand"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()
