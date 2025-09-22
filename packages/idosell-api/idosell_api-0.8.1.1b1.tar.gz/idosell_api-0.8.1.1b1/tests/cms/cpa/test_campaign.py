import pytest
from pydantic import ValidationError

from src.idosell.cms.cpa.campaign import (
    CampaignModel, PostCampaignModel, PutCampaignModel,
    PostCmsCpaCampaignParamsModel, PutCmsCpaCampaignParamsModel,
    Get, Post, Put, Delete
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for DTOs
class TestCampaignModel:
    def test_valid_minimal(self):
        dto = CampaignModel()
        assert dto.description is None
        assert dto.shop is None
        assert dto.active is None

    def test_valid_with_fields(self):
        dto = CampaignModel(
            description="Test campaign description",
            shop=[1, 2],
            active=BooleanStrShortEnum.YES
        )
        assert dto.description == "Test campaign description"
        assert dto.shop == [1, 2]
        assert dto.active == BooleanStrShortEnum.YES

    def test_invalid_shop_empty_list(self):
        with pytest.raises(ValidationError):
            CampaignModel(shop=[])

class TestPostCampaignModel:
    def test_valid(self):
        dto = PostCampaignModel(
            name="Test Campaign",
            description="Description",
            shop=[1]
        )
        assert dto.name == "Test Campaign"
        assert dto.id is None

    def test_valid_with_id(self):
        dto = PostCampaignModel(
            name="Test Campaign",
            id=1,
            active=BooleanStrShortEnum.NO
        )
        assert dto.id == 1

class TestPutCampaignModel:
    def test_valid(self):
        dto = PutCampaignModel(
            id=1,
            name="Updated Campaign",
            description="Updated Description"
        )
        assert dto.id == 1
        assert dto.name == "Updated Campaign"

    def test_valid_without_name(self):
        dto = PutCampaignModel(
            id=2,
            shop=[3, 4]
        )
        assert dto.id == 2
        assert dto.name is None

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PutCampaignModel(id=0)

    def test_invalid_id_negative(self):
        with pytest.raises(ValidationError):
            PutCampaignModel(id=-1)

class TestPostCmsCpaCampaignParamsModel:
    def test_valid(self):
        dto = PostCmsCpaCampaignParamsModel(
            campaigns=[
                PostCampaignModel(name="Camp1"),
                PostCampaignModel(name="Camp2", id=1)
            ]
        )
        assert len(dto.campaigns) == 2
        assert dto.campaigns[0].name == "Camp1"
        assert dto.campaigns[1].id == 1

    def test_invalid_empty_campaigns(self):
        with pytest.raises(ValidationError):
            PostCmsCpaCampaignParamsModel(campaigns=[])

    def test_invalid_too_many_campaigns(self):
        with pytest.raises(ValidationError):
            PostCmsCpaCampaignParamsModel(campaigns=[PostCampaignModel(name="Camp")] * 101)

class TestPutCmsCpaCampaignParamsModel:
    def test_valid(self):
        dto = PutCmsCpaCampaignParamsModel(
            campaigns=[
                PutCampaignModel(id=1, name="Updated"),
                PutCampaignModel(id=2, active=BooleanStrShortEnum.YES)
            ]
        )
        assert len(dto.campaigns) == 2
        assert dto.campaigns[0].id == 1
        assert dto.campaigns[1].active == BooleanStrShortEnum.YES

    def test_invalid_empty_campaigns(self):
        with pytest.raises(ValidationError):
            PutCmsCpaCampaignParamsModel(campaigns=[])

    def test_invalid_too_many_campaigns(self):
        with pytest.raises(ValidationError):
            PutCmsCpaCampaignParamsModel(campaigns=[PutCampaignModel(id=1)] * 101)


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.shopId is None
        assert dto.id is None

    def test_instantiate_with_params(self):
        dto = Get(
            shopId=[1, 2],
            id=[10, 20]
        )
        assert dto.shopId == [1, 2]
        assert dto.id == [10, 20]

    def test_invalid_shopId_empty_list(self):
        with pytest.raises(ValidationError):
            Get(shopId=[])

    def test_invalid_id_empty_list(self):
        with pytest.raises(ValidationError):
            Get(id=[])

    def test_invalid_shopId_with_zero(self):
        with pytest.raises(ValidationError):
            Get(shopId=[0, 1])

    def test_invalid_id_with_zero(self):
        with pytest.raises(ValidationError):
            Get(id=[0, 1])

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCmsCpaCampaignParamsModel(
                campaigns=[
                    PostCampaignModel(name="Test Campaign")
                ]
            )
        )
        assert len(dto.params.campaigns) == 1
        assert dto.params.campaigns[0].name == "Test Campaign"

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsCpaCampaignParamsModel(
                campaigns=[
                    PutCampaignModel(
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

    def test_empty_id_allowed(self):
        # The Delete endpoint doesn't validate min_length for id, so empty lists are allowed
        dto = Delete(id=[])
        assert dto.id == []
