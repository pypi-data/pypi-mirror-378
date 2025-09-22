import pytest
from pydantic import ValidationError

from src.idosell.cms.cpa.cpa import (
    PageSettingsModeEnum, SourceEnum,
    DisplayModel, PageModel, PageSettingsModel, VariableModel,
    CpaModel, PostCpaModel, PutCpaModel,
    PostCmsCpaCpaParamsModel, PutCmsCpaCpaParamsModel,
    Get, Post, Put, Delete
)
from src.idosell._common import BooleanStrShortEnum, AllYNEnum
from src.idosell.cms._common import PageEnum, ZoneEnum, BodyModel


# --- Tests for Enums
class TestPageSettingsModeEnum:
    def test_valid_values(self):
        assert PageSettingsModeEnum.ADVANCED == 'advanced'
        assert PageSettingsModeEnum.SIMPLE == 'simple'

class TestSourceEnum:
    def test_valid_values(self):
        assert SourceEnum.COOKIE == 'cookie'
        assert SourceEnum.SESSION == 'session'


# --- Tests for DTOs
class TestDisplayModel:
    def test_inherits_from_display_base_model(self):
        dto = DisplayModel(
            clientType='all',
            newsletter=AllYNEnum.ALL,
            hasOrders=AllYNEnum.NO,
            useRebateCode=AllYNEnum.YES
        )
        assert dto.clientType == 'all'
        assert dto.newsletter == AllYNEnum.ALL

class TestPageModel:
    def test_valid(self):
        dto = PageModel(
            active=BooleanStrShortEnum.YES,
            page=PageEnum.HOME,
            zone=ZoneEnum.HEAD,
            body=[BodyModel(lang="eng", body="<html></html>")]
        )
        assert dto.active == BooleanStrShortEnum.YES
        assert dto.page == PageEnum.HOME
        assert dto.zone == ZoneEnum.HEAD
        assert len(dto.body) == 1

    def test_empty_body_allowed(self):
        # The PageModel doesn't validate min_length for body, so empty lists are allowed
        dto = PageModel(
            active=BooleanStrShortEnum.YES,
            page=PageEnum.HOME,
            zone=ZoneEnum.HEAD,
            body=[]
        )
        assert dto.body == []

class TestPageSettingsModel:
    def test_valid_simple_mode(self):
        dto = PageSettingsModel(
            mode=PageSettingsModeEnum.SIMPLE,
            zone=ZoneEnum.BODYBEGIN,
            body=[BodyModel(lang="eng", body="<html></html>")],
            pages=None
        )
        assert dto.mode == PageSettingsModeEnum.SIMPLE
        assert dto.zone == ZoneEnum.BODYBEGIN
        assert dto.pages is None

    def test_valid_advanced_mode(self):
        dto = PageSettingsModel(
            mode=PageSettingsModeEnum.ADVANCED,
            zone=None,
            body=None,
            pages=[PageModel(
                active=BooleanStrShortEnum.YES,
                page=PageEnum.BASKET,
                zone=ZoneEnum.HEAD,
                body=[BodyModel(lang="eng", body="<html></html>")]
            )]
        )
        assert dto.mode == PageSettingsModeEnum.ADVANCED
        assert dto.zone is None
        assert len(dto.pages) == 1

class TestVariableModel:
    def test_valid(self):
        dto = VariableModel(
            name="test_var",
            source=SourceEnum.COOKIE
        )
        assert dto.name == "test_var"
        assert dto.source == SourceEnum.COOKIE

    def test_invalid_name_too_long(self):
        with pytest.raises(ValidationError):
            VariableModel(
                name="a" * 151,  # exceeds max_length=150
                source=SourceEnum.COOKIE
            )

class TestCpaModel:
    def test_valid_minimal(self):
        dto = CpaModel()
        assert dto.active is None
        assert dto.pageSettings is None

    def test_valid_with_all_fields(self):
        dto = CpaModel(
            active=BooleanStrShortEnum.YES,
            pageSettings=PageSettingsModel(
                mode=PageSettingsModeEnum.SIMPLE,
                zone=ZoneEnum.HEAD,
                body=[BodyModel(lang="eng", body="<html></html>")],
                pages=None
            ),
            display=DisplayModel(
                clientType='all',
                newsletter=AllYNEnum.ALL,
                hasOrders=AllYNEnum.NO,
                useRebateCode=AllYNEnum.YES
            ),
            sources=None,
            variables=[VariableModel(name="var1", source=SourceEnum.COOKIE)]
        )
        assert dto.active == BooleanStrShortEnum.YES
        assert dto.pageSettings.mode == PageSettingsModeEnum.SIMPLE
        assert len(dto.variables) == 1

class TestPostCpaModel:
    def test_valid(self):
        dto = PostCpaModel(
            name="Test CPA Program",
            campaign=1
        )
        assert dto.name == "Test CPA Program"
        assert dto.id is None
        assert dto.campaign == 1

    def test_valid_with_id(self):
        dto = PostCpaModel(
            name="Test CPA Program",
            campaign=2,
            id=10,
            active=BooleanStrShortEnum.YES
        )
        assert dto.id == 10

    def test_invalid_campaign_zero(self):
        with pytest.raises(ValidationError):
            PostCpaModel(
                name="Test CPA Program",
                campaign=0
            )

class TestPutCpaModel:
    def test_valid(self):
        dto = PutCpaModel(
            id=1,
            name="Updated CPA Program",
            campaign=2
        )
        assert dto.id == 1
        assert dto.name == "Updated CPA Program"

    def test_valid_without_name_campaign(self):
        dto = PutCpaModel(
            id=3,
            pageSettings=PageSettingsModel(
                mode=PageSettingsModeEnum.ADVANCED,
                zone=None,
                body=None,
                pages=[]
            )
        )
        assert dto.id == 3
        assert dto.name is None
        assert dto.campaign is None

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PutCpaModel(id=0)

    def test_invalid_campaign_zero(self):
        with pytest.raises(ValidationError):
            PutCpaModel(
                id=1,
                campaign=0
            )

class TestPostCmsCpaCpaParamsModel:
    def test_valid(self):
        dto = PostCmsCpaCpaParamsModel(
            cpa=[
                PostCpaModel(name="CPA1", campaign=1),
                PostCpaModel(name="CPA2", campaign=2, id=5)
            ]
        )
        assert len(dto.cpa) == 2
        assert dto.cpa[0].name == "CPA1"
        assert dto.cpa[1].id == 5

    def test_invalid_empty_cpa(self):
        with pytest.raises(ValidationError):
            PostCmsCpaCpaParamsModel(cpa=[])

    def test_invalid_too_many_cpa(self):
        with pytest.raises(ValidationError):
            PostCmsCpaCpaParamsModel(cpa=[PostCpaModel(name="CPA", campaign=1)] * 101)

class TestPutCmsCpaCpaParamsModel:
    def test_valid(self):
        dto = PutCmsCpaCpaParamsModel(
            cpa=[
                PutCpaModel(id=1, name="Updated", campaign=2),
                PutCpaModel(id=2, active=BooleanStrShortEnum.YES)
            ]
        )
        assert len(dto.cpa) == 2
        assert dto.cpa[0].id == 1

    def test_invalid_empty_cpa(self):
        with pytest.raises(ValidationError):
            PutCmsCpaCpaParamsModel(cpa=[])

    def test_invalid_too_many_cpa(self):
        with pytest.raises(ValidationError):
            PutCmsCpaCpaParamsModel(cpa=[PutCpaModel(id=1)] * 101)


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.campaign is None
        assert dto.id is None

    def test_instantiate_with_params(self):
        dto = Get(
            campaign=[1, 2],
            id=[10, 20]
        )
        assert dto.campaign == [1, 2]
        assert dto.id == [10, 20]

    def test_invalid_campaign_empty_list(self):
        with pytest.raises(ValidationError):
            Get(campaign=[])

    def test_invalid_id_empty_list(self):
        with pytest.raises(ValidationError):
            Get(id=[])

    def test_invalid_campaign_with_zero(self):
        with pytest.raises(ValidationError):
            Get(campaign=[0, 1])

    def test_invalid_id_with_zero(self):
        with pytest.raises(ValidationError):
            Get(id=[0, 1])

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCmsCpaCpaParamsModel(
                cpa=[
                    PostCpaModel(name="Test CPA", campaign=1)
                ]
            )
        )
        assert len(dto.params.cpa) == 1
        assert dto.params.cpa[0].name == "Test CPA"

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsCpaCpaParamsModel(
                cpa=[
                    PutCpaModel(
                        id=1,
                        name="Updated CPA",
                        campaign=2
                    )
                ]
            )
        )
        assert len(dto.params.cpa) == 1
        assert dto.params.cpa[0].id == 1

class TestDelete:
    def test_instantiate(self):
        dto = Delete(id=[1, 2, 3])
        assert dto.id == [1, 2, 3]

    def test_empty_id_allowed(self):
        # The Delete endpoint doesn't validate min_length for id, so empty lists are allowed
        dto = Delete(id=[])
        assert dto.id == []
