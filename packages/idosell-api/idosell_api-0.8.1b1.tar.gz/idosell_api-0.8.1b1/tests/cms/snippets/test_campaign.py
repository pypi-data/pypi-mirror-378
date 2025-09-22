import pytest
from pydantic import ValidationError

from src.idosell.cms.snippets.campaign import (
    SnippetsCampaignConfigVariablesModel, SnippetsCampaignModel,
    PostSnippetsCampaignModel, PutSnippetsCampaignModel,
    PostCmsSnippetsCampaignParamsModel, PutCmsSnippetsCampaignParamsModel,
    Get, Post, Put, Delete
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for DTOs
class TestSnippetsCampaignConfigVariablesModel:
    def test_valid(self):
        dto = SnippetsCampaignConfigVariablesModel(
            key="test_key",
            value="test_value"
        )
        assert dto.key == "test_key"
        assert dto.value == "test_value"

    def test_invalid_key_empty(self):
        with pytest.raises(ValidationError):
            SnippetsCampaignConfigVariablesModel(
                key="",
                value="value"
            )

    def test_invalid_key_too_long(self):
        with pytest.raises(ValidationError):
            SnippetsCampaignConfigVariablesModel(
                key="a" * 256,
                value="value"
            )

    def test_invalid_value_too_long(self):
        with pytest.raises(ValidationError):
            SnippetsCampaignConfigVariablesModel(
                key="key",
                value="a" * 256
            )

class TestSnippetsCampaignModel:
    def test_valid_minimal(self):
        dto = SnippetsCampaignModel()
        assert dto.description is None
        assert dto.shop is None

    def test_valid_with_all_fields(self):
        dto = SnippetsCampaignModel(
            description="Test description",
            shop=[1, 2],
            active=BooleanStrShortEnum.YES,
            order=10,
            configVariables=[
                SnippetsCampaignConfigVariablesModel(
                    key="key1",
                    value="value1"
                )
            ]
        )
        assert dto.description == "Test description"
        assert dto.shop == [1, 2]
        assert dto.active == BooleanStrShortEnum.YES
        assert dto.order == 10
        assert len(dto.configVariables) == 1

class TestPostSnippetsCampaignModel:
    def test_valid(self):
        dto = PostSnippetsCampaignModel(
            name="Campaign Name",
            description="Description",
            shop=[1]
        )
        assert dto.name == "Campaign Name"
        assert dto.id is None

    def test_valid_with_id(self):
        dto = PostSnippetsCampaignModel(
            name="Campaign Name",
            id=1,
            active=BooleanStrShortEnum.NO
        )
        assert dto.id == 1

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PostSnippetsCampaignModel(
                name="Name",
                id=0
            )

class TestPutSnippetsCampaignModel:
    def test_valid(self):
        dto = PutSnippetsCampaignModel(
            id=1,
            name="Updated Name",
            description="Updated Description"
        )
        assert dto.id == 1
        assert dto.name == "Updated Name"

    def test_valid_without_name(self):
        dto = PutSnippetsCampaignModel(
            id=2,
            shop=[3, 4]
        )
        assert dto.id == 2
        assert dto.name is None

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PutSnippetsCampaignModel(
                id=0
            )

class TestPostCmsSnippetsCampaignParamsModel:
    def test_valid(self):
        dto = PostCmsSnippetsCampaignParamsModel(
            campaigns=[
                PostSnippetsCampaignModel(name="Camp1"),
                PostSnippetsCampaignModel(name="Camp2", id=1)
            ]
        )
        assert len(dto.campaigns) == 2
        assert dto.campaigns[0].name == "Camp1"
        assert dto.campaigns[1].id == 1

class TestPutCmsSnippetsCampaignParamsModel:
    def test_valid(self):
        dto = PutCmsSnippetsCampaignParamsModel(
            campaigns=[
                PutSnippetsCampaignModel(id=1, name="Updated"),
                PutSnippetsCampaignModel(id=2, active=BooleanStrShortEnum.YES)
            ]
        )
        assert len(dto.campaigns) == 2
        assert dto.campaigns[0].id == 1
        assert dto.campaigns[1].active == BooleanStrShortEnum.YES


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.shopId is None
        assert dto.id is None
        assert dto.omitDeleted is None

    def test_instantiate_with_params(self):
        dto = Get(
            shopId=[1, 2],
            id=[10, 20],
            omitDeleted=BooleanStrShortEnum.YES
        )
        assert dto.shopId == [1, 2]
        assert dto.id == [10, 20]
        assert dto.omitDeleted == BooleanStrShortEnum.YES

    def test_invalid_shopId_empty_list(self):
        with pytest.raises(ValidationError):
            Get(shopId=[])

    def test_invalid_id_empty_list(self):
        with pytest.raises(ValidationError):
            Get(id=[])

    def test_invalid_shopId_with_zero(self):
        with pytest.raises(ValidationError):
            Get(shopId=[0, 1])

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCmsSnippetsCampaignParamsModel(
                campaigns=[
                    PostSnippetsCampaignModel(name="Test Campaign")
                ]
            )
        )
        assert len(dto.params.campaigns) == 1
        assert dto.params.campaigns[0].name == "Test Campaign"

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsSnippetsCampaignParamsModel(
                campaigns=[
                    PutSnippetsCampaignModel(
                        id=1,
                        name="Updated Campaign",
                        active=BooleanStrShortEnum.NO
                    )
                ]
            )
        )
        assert len(dto.params.campaigns) == 1
        assert dto.params.campaigns[0].id == 1
        assert dto.params.campaigns[0].active == BooleanStrShortEnum.NO

class TestDelete:
    def test_instantiate(self):
        dto = Delete(id=[1, 2, 3])
        assert dto.id == [1, 2, 3]
