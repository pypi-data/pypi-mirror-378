import pytest
from pydantic import ValidationError

from src.idosell.cms.config_variables import (
    TypeConfigVariablesEnum,
    PutVariablesModel, PutCmsConfigVariablesModel,
    Get, Put, Delete
)


# --- Tests for Enums
class TestTypeConfigVariablesEnum:
    def test_valid_values(self):
        assert TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN == 'snippets_campaign'


# --- Tests for DTOs
class TestPutVariablesModel:
    def test_valid(self):
        dto = PutVariablesModel(
            key="test_key",
            value="test_value",
            type="snippet",
            itemId=1
        )
        assert dto.key == "test_key"
        assert dto.value == "test_value"
        assert dto.type == "snippet"
        assert dto.itemId == 1

    def test_valid_value_none(self):
        dto = PutVariablesModel(
            key="test_key",
            value=None,
            type="snippet",
            itemId=1
        )
        assert dto.value is None

    def test_invalid_key_empty(self):
        with pytest.raises(ValidationError):
            PutVariablesModel(
                key="",
                value="test",
                type="snippet",
                itemId=1
            )

    def test_invalid_key_too_long(self):
        with pytest.raises(ValidationError):
            PutVariablesModel(
                key="a" * 256,
                value="test",
                type="snippet",
                itemId=1
            )

    def test_invalid_value_too_long(self):
        with pytest.raises(ValidationError):
            PutVariablesModel(
                key="test",
                value="a" * 256,
                type="snippet",
                itemId=1
            )

    def test_invalid_itemId_zero(self):
        with pytest.raises(ValidationError):
            PutVariablesModel(
                key="test",
                value="test",
                type="snippet",
                itemId=0
            )

class TestPutCmsConfigVariablesModel:
    def test_valid(self):
        dto = PutCmsConfigVariablesModel(
            variables=[
                PutVariablesModel(
                    key="key1",
                    value="value1",
                    type="snippet",
                    itemId=1
                ),
                PutVariablesModel(
                    key="key2",
                    value=None,
                    type="snippet",
                    itemId=2
                )
            ]
        )
        assert len(dto.variables) == 2
        assert dto.variables[0].key == "key1"
        assert dto.variables[1].value is None


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.type == TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN
        assert dto.item is None
        assert dto.key is None

    def test_instantiate_with_params(self):
        dto = Get(
            item=[1, 2],
            key=["key1", "key2"]
        )
        assert dto.item == [1, 2]
        assert dto.key == ["key1", "key2"]

    def test_invalid_item_empty_list(self):
        with pytest.raises(ValidationError):
            Get(item=[])

    def test_invalid_key_empty_list(self):
        with pytest.raises(ValidationError):
            Get(key=[])

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsConfigVariablesModel(
                variables=[
                    PutVariablesModel(
                        key="key1",
                        value="value1",
                        type="snippet",
                        itemId=1
                    )
                ]
            )
        )
        assert len(dto.params.variables) == 1
        assert dto.params.variables[0].key == "key1"

class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            type=TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.type == TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN

    def test_instantiate_with_params(self):
        dto = Delete(
            type=TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN,
            item=[1, 2],
            key=["key1"]
        )
        assert dto.item == [1, 2]
        assert dto.key == ["key1"]
