import pytest
from pydantic import ValidationError

from src.idosell.pim.products.series import (
    # DTOs
    DeletePimProductsSeriesParamsModel,
    PutFilterPimProductsSeriesParamsModel,
    PutPimProductsSeriesParamsModel,
    # Endpoints
    Delete,
    GetFilter,
    PutFilter,
    Get,
    Put,
)
from src.idosell.pim.products._common import (
    FiltersActiveSeriesModel,
    SeriesPutModel,
    ShopsConfigurationsSeriesModel,
    ImagesConfigurationModel,
    GraphicTypeEnum,
    FilterValueSortEnum,
    FilterDisplaySeriesEnum,
    SortModeGridEnum,
    MetaRobotsSettingsIndexEnum,
    MetaRobotsSettingsFollowEnum,
    MetaSettingsEnum,
    ViewEnum,
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for DTOs
class TestDeletePimProductsSeriesParamsModel:
    def test_valid(self):
        dto = DeletePimProductsSeriesParamsModel(
            ids=[1, 2, 3]
        )
        assert dto.ids == [1, 2, 3]

    def test_invalid_empty_ids(self):
        with pytest.raises(ValidationError):
            DeletePimProductsSeriesParamsModel(ids=[])




class TestPutFilterPimProductsSeriesParamsModel:
    def test_valid(self):
        dto = PutFilterPimProductsSeriesParamsModel(
            shopId=1,
            languageId="eng",
            serieId=1,
            filterForNodeIsDefault=BooleanStrShortEnum.YES,
            filtersActive=[FiltersActiveSeriesModel(
                filterId="size",
                filterName="Size Filter",
                filterDisplay=FilterDisplaySeriesEnum.NAME,
                filterValueSort=FilterValueSortEnum.YES,
                filterDefaultEnabled=BooleanStrShortEnum.YES
            )]
        )
        assert dto.shopId == 1
        assert dto.languageId == "eng"
        assert dto.serieId == 1
        assert dto.filterForNodeIsDefault == BooleanStrShortEnum.YES
        assert len(dto.filtersActive) == 1

    def test_multiple_filters(self):
        dto = PutFilterPimProductsSeriesParamsModel(
            shopId=1,
            languageId="pol",
            serieId=2,
            filterForNodeIsDefault=BooleanStrShortEnum.NO,
            filtersActive=[
                FiltersActiveSeriesModel(
                    filterId="color",
                    filterName="Color Filter",
                    filterDisplay=FilterDisplaySeriesEnum.GFX,
                    filterValueSort=FilterValueSortEnum.PRIORITY,
                    filterDefaultEnabled=BooleanStrShortEnum.NO
                ),
                FiltersActiveSeriesModel(
                    filterId="material",
                    filterName="Material Filter",
                    filterDisplay=FilterDisplaySeriesEnum.NAMEGFX,
                    filterValueSort=FilterValueSortEnum.NO,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )
            ]
        )
        assert len(dto.filtersActive) == 2

    def test_invalid_language_id_length_short(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsSeriesParamsModel(
                shopId=1,
                languageId="en",
                serieId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[FiltersActiveSeriesModel(
                    filterId="size",
                    filterName="Size Filter",
                    filterDisplay=FilterDisplaySeriesEnum.NAME,
                    filterValueSort=FilterValueSortEnum.YES,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )]
            )

    def test_invalid_language_id_length_long(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsSeriesParamsModel(
                shopId=1,
                languageId="eng123",
                serieId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[FiltersActiveSeriesModel(
                    filterId="size",
                    filterName="Size Filter",
                    filterDisplay=FilterDisplaySeriesEnum.NAME,
                    filterValueSort=FilterValueSortEnum.YES,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )]
            )

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsSeriesParamsModel(
                shopId=0,
                languageId="eng",
                serieId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[FiltersActiveSeriesModel(
                    filterId="size",
                    filterName="Size Filter",
                    filterDisplay=FilterDisplaySeriesEnum.NAME,
                    filterValueSort=FilterValueSortEnum.YES,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )]
            )

    def test_invalid_serie_id_zero(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsSeriesParamsModel(
                shopId=1,
                languageId="eng",
                serieId=0,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[FiltersActiveSeriesModel(
                    filterId="size",
                    filterName="Size Filter",
                    filterDisplay=FilterDisplaySeriesEnum.NAME,
                    filterValueSort=FilterValueSortEnum.YES,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )]
            )

    def test_invalid_empty_filters_active(self):
        with pytest.raises(ValidationError):
            PutFilterPimProductsSeriesParamsModel(
                shopId=1,
                languageId="eng",
                serieId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[]
            )


class TestPutPimProductsSeriesParamsModel:
    def test_valid(self):
        dto = PutPimProductsSeriesParamsModel(
            series=[SeriesPutModel(
                id=1,
                nameInPanel="Test Series",
                shopsConfigurations=[]
            )]
        )
        assert len(dto.series) == 1
        assert dto.series[0].id == 1
        assert dto.series[0].nameInPanel == "Test Series"

    def test_multiple_series(self):
        dto = PutPimProductsSeriesParamsModel(
            series=[
                SeriesPutModel(
                    id=1,
                    nameInPanel="Series 1",
                    shopsConfigurations=[]
                ),
                SeriesPutModel(
                    id=2,
                    nameInPanel="Series 2",
                    shopsConfigurations=[]
                )
            ]
        )
        assert len(dto.series) == 2

    def test_invalid_empty_series(self):
        with pytest.raises(ValidationError):
            PutPimProductsSeriesParamsModel(series=[])

    def test_invalid_series_id_zero(self):
        with pytest.raises(ValidationError):
            PutPimProductsSeriesParamsModel(
                series=[SeriesPutModel(
                    id=0,
                    nameInPanel="Test Series",
                    shopsConfigurations=[]
                )]
            )


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=DeletePimProductsSeriesParamsModel(ids=[1, 2])
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/series/delete'
        assert dto.params.ids == [1, 2]

    def test_instantiate_with_ids(self):
        dto = Delete(
            params=DeletePimProductsSeriesParamsModel(ids=[10, 20, 30])
        )
        assert dto.params.ids == [10, 20, 30]

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()


class TestGetFilter:
    def test_instantiate_with_all_params(self):
        dto = GetFilter(
            shopId=1,
            languageId="eng",
            serieId=5
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/series/filter'
        assert dto.shopId == 1
        assert dto.languageId == "eng"
        assert dto.serieId == 5

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(
                shopId=0,
                languageId="eng",
                serieId=1
            )

    def test_invalid_serie_id_zero(self):
        with pytest.raises(ValidationError):
            GetFilter(
                shopId=1,
                languageId="eng",
                serieId=0
            )

    def test_invalid_language_id_length_short(self):
        with pytest.raises(ValidationError):
            GetFilter(
                shopId=1,
                languageId="en",
                serieId=1
            )

    def test_invalid_language_id_length_long(self):
        with pytest.raises(ValidationError):
            GetFilter(
                shopId=1,
                languageId="english",
                serieId=1
            )


class TestPutFilter:
    def test_instantiate_minimal(self):
        dto = PutFilter(
            params=PutFilterPimProductsSeriesParamsModel(
                shopId=1,
                languageId="eng",
                serieId=1,
                filterForNodeIsDefault=BooleanStrShortEnum.YES,
                filtersActive=[FiltersActiveSeriesModel(
                    filterId="size",
                    filterName="Size Filter",
                    filterDisplay=FilterDisplaySeriesEnum.NAME,
                    filterValueSort=FilterValueSortEnum.YES,
                    filterDefaultEnabled=BooleanStrShortEnum.YES
                )]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/series/filter'
        assert dto.params.shopId == 1
        assert dto.params.languageId == "eng"
        assert len(dto.params.filtersActive) == 1

    def test_instantiate_with_filters(self):
        dto = PutFilter(
            params=PutFilterPimProductsSeriesParamsModel(
                shopId=2,
                languageId="pol",
                serieId=3,
                filterForNodeIsDefault=BooleanStrShortEnum.NO,
                filtersActive=[FiltersActiveSeriesModel(
                    filterId="color",
                    filterName="Color Filter",
                    filterDisplay=FilterDisplaySeriesEnum.GFX,
                    filterValueSort=FilterValueSortEnum.PRIORITY,
                    filterDefaultEnabled=BooleanStrShortEnum.NO
                )]
            )
        )
        assert dto.params.shopId == 2
        assert dto.params.languageId == "pol"
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
        assert dto._endpoint == '/api/admin/v6/products/series'
        assert dto.return_last_changed_time is None
        assert dto.ids is None
        assert dto.names is None
        assert dto.languagesIds is None

    def test_instantiate_with_params(self):
        dto = Get(
            return_last_changed_time="y",
            ids=[1, 2, 3],
            names=["Series A", "Series B"],
            languagesIds=["en", "pl"]
        )
        assert dto.return_last_changed_time == "y"
        assert dto.ids == [1, 2, 3]
        assert dto.names == ["Series A", "Series B"]
        assert dto.languagesIds == ["en", "pl"]




class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsSeriesParamsModel(
                series=[SeriesPutModel(
                    id=1,
                    nameInPanel="Minimal Series",
                    shopsConfigurations=[]
                )]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/series'
        assert len(dto.params.series) == 1

    def test_instantiate_with_series(self):
        dto = Put(
            params=PutPimProductsSeriesParamsModel(
                series=[SeriesPutModel(
                    id=1,
                    nameInPanel="Sample Series",
                    shopsConfigurations=[ShopsConfigurationsSeriesModel(
                        headerName="Sample Series",
                        shopId=1,
                        language="eng",
                        nameOnPage="Sample Series EN",
                        description="Description",
                        enableSort=True,
                        enableChangeDisplayCount=True,
                        numberOfProductsGrid=20,
                        sortModeGrid=SortModeGridEnum.D_NAME,
                        view=ViewEnum.DEFAULT,
                        metaSettings=MetaSettingsEnum.AUTO,
                        metaTitle="Sample Series",
                        metaDescription="Sample Series Description",
                        metaKeywords="sample,series",
                        metaRobotsSettingsIndex=MetaRobotsSettingsIndexEnum.INDEX,
                        metaRobotsSettingsFollow=MetaRobotsSettingsFollowEnum.FOLLOW,
                        imagesConfiguration=ImagesConfigurationModel(
                            graphicType=GraphicTypeEnum.IMG,
                            singleGraphic="image.jpg",
                            pcGraphic="pc.jpg",
                            tabletGraphic="tablet.jpg",
                            phoneGraphic="phone.jpg"
                        )
                    )]
                )]
            )
        )
        assert len(dto.params.series) == 1
        assert dto.params.series[0].nameInPanel == "Sample Series"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()
