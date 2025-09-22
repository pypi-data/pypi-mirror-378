import pytest
from pydantic import ValidationError

from src.idosell.pim.sizecharts import (
    # DTOs
    DeletePimSizechartsParamsModel,
    PutPimSizechartsParamsModel,
    # Endpoints
    Delete, Get, Put
)
from src.idosell.pim._common import (
    SizeChartsPutModel, LanguagesDataModel, ColumnsModel,
    SizesModel, DescriptionsModel, DisplayModeEnum
)


# --- Tests for DTOs
class TestDeletePimSizechartsParamsModel:
    def test_valid(self):
        dto = DeletePimSizechartsParamsModel(
            ids=[1, 2, 3]
        )
        assert dto.ids == [1, 2, 3]

    def test_single_id(self):
        dto = DeletePimSizechartsParamsModel(
            ids=[42]
        )
        assert dto.ids == [42]

class TestPutPimSizechartsParamsModel:
    def test_valid(self):
        dto = PutPimSizechartsParamsModel(
            sizeCharts=[
                SizeChartsPutModel(
                    id=1,
                    nameInPanel="Size Chart 1",
                    displayMode=DisplayModeEnum.ALL,
                    languagesData=[
                        LanguagesDataModel(
                            language="eng",
                            columns=[ColumnsModel(columnNumber=1, columnTitle="Size")],
                            sizes=[SizesModel(sizeId="S", priority=1, descriptions=[DescriptionsModel(columnNumber=1, value="Small")])]
                        )
                    ]
                )
            ]
        )
        assert len(dto.sizeCharts) == 1
        assert dto.sizeCharts[0].id == 1

    def test_multiple_sizecharts(self):
        dto = PutPimSizechartsParamsModel(
            sizeCharts=[
                SizeChartsPutModel(
                    id=1,
                    nameInPanel="Chart 1",
                    displayMode=DisplayModeEnum.ALL,
                    languagesData=[]
                ),
                SizeChartsPutModel(
                    id=2,
                    nameInPanel="Chart 2",
                    displayMode=DisplayModeEnum.SINGLE,
                    languagesData=[
                        LanguagesDataModel(
                            language="pol",
                            columns=[ColumnsModel(columnNumber=1, columnTitle="Rozmiar")],
                            sizes=[SizesModel(sizeId="M", priority=2, descriptions=[DescriptionsModel(columnNumber=1, value="Średni")])]
                        )
                    ]
                )
            ]
        )
        assert len(dto.sizeCharts) == 2


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=DeletePimSizechartsParamsModel(ids=[1])
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/sizecharts/sizecharts/delete'
        assert dto.params.ids == [1]

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Delete()

    def test_multiple_ids(self):
        dto = Delete(
            params=DeletePimSizechartsParamsModel(ids=[1, 2, 3, 4, 5])
        )
        assert dto.params.ids == [1, 2, 3, 4, 5]

class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/sizecharts/sizecharts'
        assert dto.ids is None
        assert dto.names is None
        assert dto.languages is None

    def test_instantiate_with_ids(self):
        dto = Get(ids=[1, 2, 3])
        assert dto.ids == [1, 2, 3]

    def test_instantiate_with_names(self):
        dto = Get(names=["Chart1", "Chart2"])
        assert dto.names == ["Chart1", "Chart2"]

    def test_instantiate_with_languages(self):
        dto = Get(languages=["eng", "pol"])
        assert dto.languages == ["eng", "pol"]

    def test_instantiate_with_all_params(self):
        dto = Get(
            ids=[1, 2],
            names=["Test Chart"],
            languages=["eng"]
        )
        assert dto.ids == [1, 2]
        assert dto.names == ["Test Chart"]
        assert dto.languages == ["eng"]

class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimSizechartsParamsModel(
                sizeCharts=[
                    SizeChartsPutModel(
                        id=1,
                        nameInPanel="Minimal Chart",
                        displayMode=DisplayModeEnum.ALL,
                        languagesData=[]
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/sizecharts/sizecharts'
        assert len(dto.params.sizeCharts) == 1
        assert dto.params.sizeCharts[0].nameInPanel == "Minimal Chart"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()

    def test_complex_sizechart(self):
        dto = Put(
            params=PutPimSizechartsParamsModel(
                sizeCharts=[
                    SizeChartsPutModel(
                        id=42,
                        nameInPanel="Complex Size Chart",
                        displayMode=DisplayModeEnum.ALL,
                        languagesData=[
                            LanguagesDataModel(
                                language="eng",
                                columns=[
                                    ColumnsModel(columnNumber=1, columnTitle="Size"),
                                    ColumnsModel(columnNumber=2, columnTitle="CM")
                                ],
                                sizes=[
                                    SizesModel(
                                        sizeId="S",
                                        priority=1,
                                        descriptions=[
                                            DescriptionsModel(columnNumber=1, value="Small"),
                                            DescriptionsModel(columnNumber=2, value="90-95")
                                        ]
                                    ),
                                    SizesModel(
                                        sizeId="M",
                                        priority=2,
                                        descriptions=[
                                            DescriptionsModel(columnNumber=1, value="Medium"),
                                            DescriptionsModel(columnNumber=2, value="96-100")
                                        ]
                                    )
                                ]
                            ),
                            LanguagesDataModel(
                                language="pol",
                                columns=[
                                    ColumnsModel(columnNumber=1, columnTitle="Rozmiar"),
                                    ColumnsModel(columnNumber=2, columnTitle="CM")
                                ],
                                sizes=[
                                    SizesModel(
                                        sizeId="S",
                                        priority=1,
                                        descriptions=[
                                            DescriptionsModel(columnNumber=1, value="Mały"),
                                            DescriptionsModel(columnNumber=2, value="90-95")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        assert len(dto.params.sizeCharts) == 1
        assert len(dto.params.sizeCharts[0].languagesData) == 2
        assert dto.params.sizeCharts[0].languagesData[0].columns[0].columnTitle == "Size"
        assert dto.params.sizeCharts[0].languagesData[1].columns[1].columnTitle == "CM"
