import pytest
from pydantic import ValidationError

from src.idosell.pim.warranties import (
    # DTOs
    DeletePimWarrantiesParamsModel,
    PostPimWarrantiesParamsModel,
    PutLanguageDataPimWarrantiesParamsModel,
    PutPimWarrantiesParamsModel,
    # Endpoints
    GetCountTotal, PutLanguageData, Delete, Get, Post, Put
)
from src.idosell.pim._common import (
    WarrantiesPostModel, WarrantiesPutModel, LangDataWarrantiesModel,
    ResultsOrderWarrantiesGetModel, TypeEnum, ShopnameWarrantiesModel,
    DescriptionWarrantiesModel, LanguagesWarrantiesModel, FieldEnum,
    OrderEnum, LangWarrantiesModel, IconSettingsModel, FormatWarrantiesEnum,
    DataTypeEnum
)


# --- Tests for DTOs
class TestDeletePimWarrantiesParamsModel:
    def test_valid(self):
        dto = DeletePimWarrantiesParamsModel(
            warranty_ids=["warranty1", "warranty2"]
        )
        assert dto.warranty_ids == ["warranty1", "warranty2"]

    def test_single_id(self):
        dto = DeletePimWarrantiesParamsModel(
            warranty_ids=["w1"]
        )
        assert dto.warranty_ids == ["w1"]

class TestPostPimWarrantiesParamsModel:
    def test_valid(self):
        dto = PostPimWarrantiesParamsModel(
            warranties=[
                WarrantiesPostModel(
                    name="2 Year Warranty",
                    type=TypeEnum.SELLER,
                    period=24,
                    shopname=ShopnameWarrantiesModel(
                        languages=[
                            LanguagesWarrantiesModel(language_id="eng", language_name="English", value="2 Years"),
                            LanguagesWarrantiesModel(language_id="pol", language_name="Polski", value="2 Lata")
                        ]
                    ),
                    description=DescriptionWarrantiesModel(
                        languages=[
                            LanguagesWarrantiesModel(language_id="eng", language_name="English", value="Full coverage")
                        ]
                    )
                )
            ]
        )
        assert len(dto.warranties) == 1
        assert dto.warranties[0].period == 24

    def test_multiple_warranties(self):
        dto = PostPimWarrantiesParamsModel(
            warranties=[
                WarrantiesPostModel(
                    name="Standard Warranty",
                    type=TypeEnum.SELLER,
                    period=12,
                    shopname=ShopnameWarrantiesModel(languages=[]),
                    description=DescriptionWarrantiesModel(languages=[])
                ),
                WarrantiesPostModel(
                    name="Extended Warranty",
                    type=TypeEnum.PRODUCER,
                    period=36,
                    shopname=ShopnameWarrantiesModel(languages=[]),
                    description=DescriptionWarrantiesModel(languages=[])
                )
            ]
        )
        assert len(dto.warranties) == 2

class TestPutLanguageDataPimWarrantiesParamsModel:
    def test_valid(self):
        dto = PutLanguageDataPimWarrantiesParamsModel(
            lang_data=LangDataWarrantiesModel(
                warranty_id="warranty1",
                lang=[
                    LangWarrantiesModel(
                        lang_id="eng",
                        name="Updated Warranty",
                        icon="icon_data",
                        icon_settings=IconSettingsModel(
                            format=FormatWarrantiesEnum.JPG,
                            data_type=DataTypeEnum.BASE64
                        ),
                        description="Updated description"
                    )
                ]
            )
        )
        assert dto.lang_data.warranty_id == "warranty1"

class TestPutPimWarrantiesParamsModel:
    def test_valid(self):
        dto = PutPimWarrantiesParamsModel(
            warranties=[
                WarrantiesPutModel(
                    id="warranty1",
                    name="Updated Warranty",
                    type=TypeEnum.SELLER,
                    period=18
                )
            ]
        )
        assert len(dto.warranties) == 1
        assert dto.warranties[0].id == "warranty1"


# --- Tests for Endpoints
class TestGetCountTotal:
    def test_instantiate_minimal(self):
        dto = GetCountTotal()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/warranties/countTotal'
        assert dto.warranty_ids is None

    def test_instantiate_with_warranty_ids(self):
        dto = GetCountTotal(warranty_ids=["w1", "w2", "w3"])
        assert dto.warranty_ids == ["w1", "w2", "w3"]

class TestPutLanguageData:
    def test_instantiate_minimal(self):
        dto = PutLanguageData(
            params=PutLanguageDataPimWarrantiesParamsModel(
                lang_data=LangDataWarrantiesModel(
                    warranty_id="warranty1",
                    lang=[]
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/warranties/languageData'
        assert dto.params.lang_data.warranty_id == "warranty1"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutLanguageData()

class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=DeletePimWarrantiesParamsModel(warranty_ids=["w1"])
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/warranties/warranties/delete'
        assert dto.params.warranty_ids == ["w1"]

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()

    def test_multiple_ids(self):
        dto = Delete(
            params=DeletePimWarrantiesParamsModel(warranty_ids=["w1", "w2", "w3", "w4"])
        )
        assert len(dto.params.warranty_ids) == 4

class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/warranties/warranties'
        assert dto.warranty_ids is None
        assert dto.resultsOrder is None

    def test_instantiate_with_warranty_ids(self):
        dto = Get(warranty_ids=["w1", "w2"])
        assert dto.warranty_ids == ["w1", "w2"]

    def test_instantiate_with_results_order(self):
        dto = Get(
            resultsOrder=ResultsOrderWarrantiesGetModel(
                field=FieldEnum.WARRANTY_NAME,
                order=OrderEnum.ASCENDING
            )
        )
        assert dto.resultsOrder.field == FieldEnum.WARRANTY_NAME
        assert dto.resultsOrder.order == OrderEnum.ASCENDING

    def test_instantiate_with_all_params(self):
        dto = Get(
            warranty_ids=["w1"],
            resultsOrder=ResultsOrderWarrantiesGetModel(
                field=FieldEnum.WARRANTY_ID,
                order=OrderEnum.DESCENDING
            )
        )
        assert dto.warranty_ids == ["w1"]
        assert dto.resultsOrder.field == FieldEnum.WARRANTY_ID

class TestPost:
    def test_instantiate_minimal(self):
        dto = Post(
            params=PostPimWarrantiesParamsModel(
                warranties=[
                    WarrantiesPostModel(
                        name="Basic Warranty",
                        type=TypeEnum.SELLER,
                        period=12,
                        shopname=ShopnameWarrantiesModel(languages=[]),
                        description=DescriptionWarrantiesModel(languages=[])
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/warranties/warranties'
        assert len(dto.params.warranties) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Post()

class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimWarrantiesParamsModel(
                warranties=[
                    WarrantiesPutModel(
                        id="warranty1",
                        name="Updated Warranty",
                        type=TypeEnum.SELLER,
                        period=24
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/warranties/warranties'
        assert len(dto.params.warranties) == 1
        assert dto.params.warranties[0].name == "Updated Warranty"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()
