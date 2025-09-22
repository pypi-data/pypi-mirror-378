import pytest
from pydantic import ValidationError

from src.idosell.pim.products.parameters import (
    # DTOs
    DeletePimProductsParametersParamsModel,
    SearchPimProductsParametersParamsModel,
    # Endpoints
    Delete,
    Put,
    Search,
)
from src.idosell.pim.products._common import (
    IconsInputTypeParametersEnum,
    ItemsParametersModel,
    NamesParametersModel,
    ItemTextIdsParametersModel,
    SettingsParametersPutModel,
    TextIdsParametersSearchModel,
)


# --- Tests for DTOs
class TestDeletePimProductsParametersParamsModel:
    def test_valid(self):
        dto = DeletePimProductsParametersParamsModel(
            ids=[123, 456]
        )
        assert dto.ids == [123, 456]

    def test_single_id(self):
        dto = DeletePimProductsParametersParamsModel(
            ids=[789]
        )
        assert dto.ids == [789]

    def test_invalid_ids_empty(self):
        with pytest.raises(ValidationError):
            DeletePimProductsParametersParamsModel(ids=[])


class TestSearchPimProductsParametersParamsModel:
    def test_valid(self):
        dto = SearchPimProductsParametersParamsModel(
            ids=[1, 2, 3],
            textIds=[
                TextIdsParametersSearchModel(
                    languageId='en',
                    value='param1'
                )
            ],
            languagesIds=["en", "pl"],
            parameterValueIds=True
        )
        assert dto.ids == [1, 2, 3]
        assert dto.parameterValueIds is True

    def test_optional_fields_none(self):
        dto = SearchPimProductsParametersParamsModel()
        assert dto.ids is None
        assert dto.textIds is None
        assert dto.languagesIds is None
        assert dto.parameterValueIds is None

    def test_invalid_textIds_empty(self):
        with pytest.raises(ValidationError):
            SearchPimProductsParametersParamsModel(textIds=[])

    def test_invalid_languagesIds_empty(self):
        with pytest.raises(ValidationError):
            SearchPimProductsParametersParamsModel(languagesIds=[])


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=DeletePimProductsParametersParamsModel(
                ids=[123]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/parameters/delete'
        assert dto.params.ids == [123]

    def test_instantiate_multiple_ids(self):
        dto = Delete(
            params=DeletePimProductsParametersParamsModel(
                ids=[123, 456, 789]
            )
        )
        assert len(dto.params.ids) == 3

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()

    def test_invalid_ids_empty(self):
        with pytest.raises(ValidationError):
            Delete(params=DeletePimProductsParametersParamsModel(ids=[]))


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            items=[
                ItemsParametersModel(
                    id=1,
                    item_text_ids=[ItemTextIdsParametersModel(lang_id='en', value='parameter')],
                    names=[NamesParametersModel(lang_id='en', value='Test Parameter')],
                    descriptions=[],
                    search_description=[],
                    card_icons=[],
                    link_icons=[],
                    context_id=None,
                    context_value_id=None
                )
            ],
            settings=SettingsParametersPutModel(
                icons_input_type=IconsInputTypeParametersEnum.BASE64
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/parameters'
        assert len(dto.items) == 1
        assert dto.settings.icons_input_type == IconsInputTypeParametersEnum.BASE64

    def test_instantiate_with_multiple_items(self):
        dto = Put(
            items=[
                ItemsParametersModel(
                    id=1,
                    item_text_ids=[ItemTextIdsParametersModel(lang_id='en', value='section')],
                    names=[NamesParametersModel(lang_id='en', value='Section 1')],
                    descriptions=[],
                    search_description=[],
                    card_icons=[],
                    link_icons=[],
                    context_id=None,
                    context_value_id=None
                ),
                ItemsParametersModel(
                    id=2,
                    item_text_ids=[ItemTextIdsParametersModel(lang_id='en', value='parameter')],
                    names=[NamesParametersModel(lang_id='en', value='Parameter 1')],
                    descriptions=[],
                    search_description=[],
                    card_icons=[],
                    link_icons=[],
                    context_id=None,
                    context_value_id=None
                )
            ],
            settings=SettingsParametersPutModel(
                icons_input_type=IconsInputTypeParametersEnum.BASE64
            )
        )
        assert len(dto.items) == 2

    def test_invalid_items_empty(self):
        with pytest.raises(ValidationError):
            Put(
                items=[],
                settings=SettingsParametersPutModel(
                    icons_input_type=IconsInputTypeParametersEnum.BASE64
                )
            )

    def test_invalid_settings_missing(self):
        with pytest.raises(ValidationError):
            Put(items=[
                ItemsParametersModel(
                    id=1,
                    item_text_ids=[ItemTextIdsParametersModel(lang_id='en', value='parameter')],
                    names=[NamesParametersModel(lang_id='en', value='Test Parameter')],
                    descriptions=[],
                    search_description=[],
                    card_icons=[],
                    link_icons=[],
                    context_id=None,
                    context_value_id=None
                )
            ])


class TestSearch:
    def test_instantiate_minimal(self):
        dto = Search()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/parameters/search'
        assert dto.params is None

    def test_instantiate_with_params(self):
        dto = Search(
            params=SearchPimProductsParametersParamsModel(
                ids=[1, 2],
                parameterValueIds=True
            )
        )
        assert dto.params.ids == [1, 2]
        assert dto.params.parameterValueIds is True

    def test_invalid_params_missing(self):
        # Search params are optional, should instantiate without params
        dto = Search()
        assert dto.params is None
