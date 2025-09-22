import pytest
from pydantic import ValidationError

from src.idosell.pim.sizes import (
    # DTOs
    PutPimSizesParamsModel,
    # Endpoints
    Get, Put
)
from src.idosell.pim._common import (
    SizesPutModel, LangDataSizesModel, OperationSizesEnum
)


# --- Tests for DTOs
class TestPutPimSizesParamsModel:
    def test_valid(self):
        dto = PutPimSizesParamsModel(
            sizes=[
                SizesPutModel(
                    faultCode=0,
                    faultString="OK",
                    group_id=1,
                    id="S",
                    name="Small",
                    description="Small size",
                    operation=OperationSizesEnum.ADD,
                    lang_data=[
                        LangDataSizesModel(lang_id="eng", name="Small"),
                        LangDataSizesModel(lang_id="pol", name="Mały")
                    ]
                )
            ]
        )
        assert len(dto.sizes) == 1
        assert dto.sizes[0].group_id == 1
        assert dto.sizes[0].operation == OperationSizesEnum.ADD

    def test_multiple_sizes(self):
        dto = PutPimSizesParamsModel(
            sizes=[
                SizesPutModel(
                    faultCode=0,
                    faultString="OK",
                    group_id=1,
                    id="S",
                    name="Small",
                    description="Small size",
                    operation=OperationSizesEnum.ADD,
                    lang_data=[]
                ),
                SizesPutModel(
                    faultCode=0,
                    faultString="OK",
                    group_id=1,
                    id="M",
                    name="Medium",
                    description="Medium size",
                    operation=OperationSizesEnum.EDIT,
                    lang_data=[LangDataSizesModel(lang_id="eng", name="Medium")]
                ),
                SizesPutModel(
                    faultCode=0,
                    faultString="OK",
                    group_id=2,
                    id="L",
                    name="Large",
                    description="Large size",
                    operation=OperationSizesEnum.DEL,
                    lang_data=[]
                )
            ]
        )
        assert len(dto.sizes) == 3
        assert dto.sizes[1].operation == OperationSizesEnum.EDIT


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/sizes/sizes'
        assert dto.return_last_changed_time is None

    def test_instantiate_with_return_last_changed_time(self):
        dto = Get(return_last_changed_time="y")
        assert dto.return_last_changed_time == "y"

    def test_instantiate_with_return_last_changed_time_no(self):
        dto = Get(return_last_changed_time="n")
        assert dto.return_last_changed_time == "n"

class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimSizesParamsModel(
                sizes=[
                    SizesPutModel(
                        faultCode=0,
                        faultString="OK",
                        group_id=1,
                        id="XS",
                        name="Extra Small",
                        description="Very small size",
                        operation=OperationSizesEnum.ADD,
                        lang_data=[]
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/sizes/sizes'
        assert len(dto.params.sizes) == 1
        assert dto.params.sizes[0].name == "Extra Small"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()

    def test_complex_sizes_update(self):
        dto = Put(
            params=PutPimSizesParamsModel(
                sizes=[
                    SizesPutModel(
                        faultCode=100,
                        faultString="Size group not found",
                        group_id=99,
                        id="XXL",
                        name="Extra Extra Large",
                        description="Very large size",
                        operation=OperationSizesEnum.ADD,
                        lang_data=[
                            LangDataSizesModel(lang_id="eng", name="XXL"),
                            LangDataSizesModel(lang_id="deu", name="XXL"),
                            LangDataSizesModel(lang_id="fra", name="XXL")
                        ]
                    ),
                    SizesPutModel(
                        faultCode=0,
                        faultString="OK",
                        group_id=2,
                        id="M",
                        name="Medium Modified",
                        description="Modified medium size",
                        operation=OperationSizesEnum.EDIT,
                        lang_data=[
                            LangDataSizesModel(lang_id="eng", name="Medium"),
                            LangDataSizesModel(lang_id="pol", name="Średni")
                        ]
                    )
                ]
            )
        )
        assert len(dto.params.sizes) == 2
        assert dto.params.sizes[0].faultCode == 100
        assert dto.params.sizes[1].lang_data[1].lang_id == "pol"
