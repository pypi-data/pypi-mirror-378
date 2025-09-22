import pytest
from pydantic import ValidationError

from src.idosell.pim.products.categories import (
    # DTOs
    PutPimProductsCategoriesParamsModel,
    SearchIdosellPimProductsCategoriesParamsModel,
    # Endpoints
    Get,
    Put,
    SearchIdosell,
)
from src.idosell.pim.products._common import CategoriesModel, OperationEnum


# --- Tests for DTOs
class TestPutPimProductsCategoriesParamsModel:
    def test_valid(self):
        dto = PutPimProductsCategoriesParamsModel(
            categories=[CategoriesModel(
                id=1,
                parent_id=1,
                priority=1,
                operation=OperationEnum.ADD
            )]
        )
        assert len(dto.categories) == 1
        assert dto.categories[0].operation == OperationEnum.ADD

    def test_multiple_categories(self):
        dto = PutPimProductsCategoriesParamsModel(
            categories=[
                CategoriesModel(
                    id=1,
                    parent_id=1,
                    priority=1,
                    operation=OperationEnum.ADD
                ),
                CategoriesModel(
                    id=2,
                    parent_id=1,
                    priority=2,
                    operation=OperationEnum.EDIT
                ),
                CategoriesModel(
                    id=3,
                    parent_id=1,
                    priority=3,
                    operation=OperationEnum.ADD
                )
            ]
        )
        assert len(dto.categories) == 3

    def test_empty_categories(self):
        dto = PutPimProductsCategoriesParamsModel(
            categories=[]
        )
        assert dto.categories == []

    def test_invalid_category_id_zero(self):
        with pytest.raises(ValidationError):
            PutPimProductsCategoriesParamsModel(
                categories=[CategoriesModel(
                    id=0,
                    parent_id=0,
                    priority=1,
                    operation=OperationEnum.ADD
                )]
            )


class TestSearchIdosellPimProductsCategoriesParamsModel:
    def test_valid_minimal(self):
        dto = SearchIdosellPimProductsCategoriesParamsModel()
        assert dto.languagesIds is None
        assert dto.categoriesIdoSellIds is None
        assert dto.categoriesIdoSellNames is None
        assert dto.categoriesIdoSellPaths is None

    def test_with_all_params(self):
        dto = SearchIdosellPimProductsCategoriesParamsModel(
            languagesIds=["en", "pl"],
            categoriesIdoSellIds=["123", "456"],
            categoriesIdoSellNames=["Electronics", "Books"],
            categoriesIdoSellPaths=["/electronics", "/books"]
        )
        assert dto.languagesIds == ["en", "pl"]
        assert dto.categoriesIdoSellIds == ["123", "456"]
        assert dto.categoriesIdoSellNames == ["Electronics", "Books"]
        assert dto.categoriesIdoSellPaths == ["/electronics", "/books"]

    def test_partial_params(self):
        dto = SearchIdosellPimProductsCategoriesParamsModel(
            languagesIds=["en"],
            categoriesIdoSellNames=["Electronics"]
        )
        assert dto.languagesIds == ["en"]
        assert dto.categoriesIdoSellNames == ["Electronics"]
        assert dto.categoriesIdoSellIds is None
        assert dto.categoriesIdoSellPaths is None

    def test_empty_lists(self):
        dto = SearchIdosellPimProductsCategoriesParamsModel(
            languagesIds=[],
            categoriesIdoSellIds=[],
            categoriesIdoSellNames=[],
            categoriesIdoSellPaths=[]
        )
        assert dto.languagesIds == []
        assert dto.categoriesIdoSellIds == []
        assert dto.categoriesIdoSellNames == []
        assert dto.categoriesIdoSellPaths == []


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/categories'
        assert dto.ids is None
        assert dto.languages is None
        assert dto.return_last_changed_time is None

    def test_instantiate_with_all_params(self):
        dto = Get(
            ids=[1, 2, 3],
            languages=["eng", "pol"],
            return_last_changed_time="2023-01-01 00:00:00"
        )
        assert dto.ids == [1, 2, 3]
        assert dto.languages == ["eng", "pol"]
        assert dto.return_last_changed_time == "2023-01-01 00:00:00"

    def test_partial_params(self):
        dto = Get(
            ids=[1],
            languages=["eng"]
        )
        assert dto.ids == [1]
        assert dto.languages == ["eng"]
        assert dto.return_last_changed_time is None


class TestPut:
    def test_instantiate_with_categories(self):
        dto = Put(
            params=PutPimProductsCategoriesParamsModel(
                categories=[CategoriesModel(
                    id=1,
                    parent_id=1,
                    priority=1,
                    operation=OperationEnum.ADD
                )]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/categories'
        assert len(dto.params.categories) == 1

    def test_instantiate_with_multiple_categories(self):
        dto = Put(
            params=PutPimProductsCategoriesParamsModel(
                categories=[
                    CategoriesModel(
                        id=1,
                        parent_id=1,
                        priority=1,
                        operation=OperationEnum.ADD
                    ),
                    CategoriesModel(
                        id=2,
                        parent_id=1,
                        priority=2,
                        operation=OperationEnum.ADD
                    )
                ]
            )
        )
        assert len(dto.params.categories) == 2

    def test_instantiate_with_empty_categories(self):
        dto = Put(
            params=PutPimProductsCategoriesParamsModel(
                categories=[]
            )
        )
        assert dto.params.categories == []

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()


class TestSearchIdosell:
    def test_instantiate_minimal(self):
        dto = SearchIdosell(
            params=SearchIdosellPimProductsCategoriesParamsModel()
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/categoriesIdosell/search'

    def test_instantiate_with_all_params(self):
        dto = SearchIdosell(
            params=SearchIdosellPimProductsCategoriesParamsModel(
                languagesIds=["en"],
                categoriesIdoSellIds=["123"],
                categoriesIdoSellNames=["Electronics"],
                categoriesIdoSellPaths=["/electronics"]
            )
        )
        assert dto.params.languagesIds == ["en"]
        assert dto.params.categoriesIdoSellIds == ["123"]

    def test_instantiate_with_partial_search_params(self):
        dto = SearchIdosell(
            params=SearchIdosellPimProductsCategoriesParamsModel(
                categoriesIdoSellNames=["Computers"]
            )
        )
        assert dto.params.categoriesIdoSellNames == ["Computers"]
        assert dto.params.languagesIds is None

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            SearchIdosell()
