import pytest
from datetime import date
from pydantic import ValidationError

from src.idosell.cms.snippets.snippets import (
    SnippetsTypeEnum,
    DateBeginSnippetsModel, DateEndSnippetsModel,
    DisplaySnippetsModel, PagesSnippetsModel, SnippetsModel,
    PostSnippetsModel, PutSnippetsModel,
    PostCmsSnippetsSnippetsParamsModel, PutCmsSnippetsSnippetsParamsModel,
    Get, Post, Put, Delete
)
from src.idosell.cms._common import PageEnum, ClientTypeEnum, ZoneEnum
from src.idosell._common import BooleanStrShortEnum, AllYNEnum


# --- Tests for Enums
class TestSnippetsTypeEnum:
    def test_valid_values(self):
        assert SnippetsTypeEnum.HTML == 'html'
        assert SnippetsTypeEnum.JAVASCRIPT == 'javascript'
        assert SnippetsTypeEnum.CGI == 'cgi'


# --- Tests for DTOs
class TestDateBeginSnippetsModel:
    def test_valid(self):
        # Use the alias name 'date' instead of field name 'date_value'
        dto = DateBeginSnippetsModel(**{
            'defined': BooleanStrShortEnum.YES,
            'date': date(2023, 1, 1),
            'autoBlock': BooleanStrShortEnum.NO
        })
        assert dto.defined == BooleanStrShortEnum.YES
        assert dto.date_value == date(2023, 1, 1)

class TestDateEndSnippetsModel:
    def test_valid(self):
        # Use the alias name 'date' instead of field name 'date_value'
        dto = DateEndSnippetsModel(**{
            'defined': BooleanStrShortEnum.YES,
            'date': date(2023, 12, 31)
        })
        assert dto.defined == BooleanStrShortEnum.YES
        assert dto.date_value == date(2023, 12, 31)

class TestDisplaySnippetsModel:
    def test_valid(self):
        dto = DisplaySnippetsModel(
            clientType=ClientTypeEnum.ALL,
            newsletter=AllYNEnum.NO,
            hasOrders=AllYNEnum.ALL,
            useRebateCode=AllYNEnum.NO,
            screen=BooleanStrShortEnum.YES,
            tablet=BooleanStrShortEnum.YES,
            phone=BooleanStrShortEnum.NO
        )
        assert dto.screen == BooleanStrShortEnum.YES

class TestPagesSnippetsModel:
    def test_valid_all_true(self):
        dto = PagesSnippetsModel(
            all=BooleanStrShortEnum.YES,
            pages=[],
            url=[]
        )
        assert dto.all == BooleanStrShortEnum.YES

    def test_valid_with_pages(self):
        dto = PagesSnippetsModel(
            all=BooleanStrShortEnum.NO,
            pages=[PageEnum.HOME, PageEnum.BASKET],
            url=[]
        )
        assert dto.pages == [PageEnum.HOME, PageEnum.BASKET]

    def test_valid_with_url(self):
        dto = PagesSnippetsModel(
            all=BooleanStrShortEnum.NO,
            pages=[],
            url=["/home", "/products"]
        )
        assert dto.url == ["/home", "/products"]

class TestSnippetsModel:
    def test_valid_minimal(self):
        dto = SnippetsModel()
        assert dto.active is None

    def test_valid_with_fields(self):
        dto = SnippetsModel(
            active=BooleanStrShortEnum.YES,
            type=SnippetsTypeEnum.HTML,
            zone=ZoneEnum.HEAD,
            order=5,
            timeout=5
        )
        assert dto.active == BooleanStrShortEnum.YES
        assert dto.type == SnippetsTypeEnum.HTML

    def test_invalid_timeout_below_min(self):
        with pytest.raises(ValidationError):
            SnippetsModel(timeout=0)

    def test_invalid_timeout_above_max(self):
        with pytest.raises(ValidationError):
            SnippetsModel(timeout=11)

class TestPostSnippetsModel:
    def test_valid(self):
        dto = PostSnippetsModel(
            name="Test Snippet",
            campaign=1,
            active=BooleanStrShortEnum.YES
        )
        assert dto.name == "Test Snippet"
        assert dto.campaign == 1

    def test_valid_with_id(self):
        dto = PostSnippetsModel(
            id=10,
            name="Test Snippet",
            campaign=2,
            type=SnippetsTypeEnum.JAVASCRIPT
        )
        assert dto.id == 10

    def test_invalid_campaign_zero(self):
        with pytest.raises(ValidationError):
            PostSnippetsModel(name="Test", campaign=0)

class TestPutSnippetsModel:
    def test_valid(self):
        dto = PutSnippetsModel(
            id=1,
            name="Updated Snippet",
            campaign=2
        )
        assert dto.id == 1
        assert dto.name == "Updated Snippet"

    def test_valid_without_name_and_campaign(self):
        dto = PutSnippetsModel(
            id=2,
            active=BooleanStrShortEnum.NO
        )
        assert dto.id == 2
        assert dto.name is None
        assert dto.campaign is None

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PutSnippetsModel(id=0)

    def test_invalid_campaign_zero(self):
        with pytest.raises(ValidationError):
            PutSnippetsModel(id=1, campaign=0)

class TestPostCmsSnippetsSnippetsParamsModel:
    def test_valid(self):
        dto = PostCmsSnippetsSnippetsParamsModel(
            snippets=[
                PostSnippetsModel(name="Snippet1", campaign=1),
                PostSnippetsModel(name="Snippet2", campaign=2)
            ]
        )
        assert len(dto.snippets) == 2

class TestPutCmsSnippetsSnippetsParamsModel:
    def test_valid(self):
        dto = PutCmsSnippetsSnippetsParamsModel(
            snippets=[
                PutSnippetsModel(id=1, name="Updated1"),
                PutSnippetsModel(id=2, name="Updated2")
            ]
        )
        assert len(dto.snippets) == 2


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.campaign is None

    def test_instantiate_with_params(self):
        dto = Get(
            campaign=[1, 2],
            id=[10, 20],
            omitDeleted=BooleanStrShortEnum.YES
        )
        assert dto.campaign == [1, 2]
        assert dto.id == [10, 20]
        assert dto.omitDeleted == BooleanStrShortEnum.YES

    def test_invalid_campaign_empty_list(self):
        with pytest.raises(ValidationError):
            Get(campaign=[])

    def test_invalid_id_empty_list(self):
        with pytest.raises(ValidationError):
            Get(id=[])

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCmsSnippetsSnippetsParamsModel(
                snippets=[
                    PostSnippetsModel(name="Test Snippet", campaign=1)
                ]
            )
        )
        assert len(dto.params.snippets) == 1

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsSnippetsSnippetsParamsModel(
                snippets=[
                    PutSnippetsModel(id=1, name="Updated Snippet")
                ]
            )
        )
        assert len(dto.params.snippets) == 1

class TestDelete:
    def test_instantiate(self):
        dto = Delete(id=[1, 2, 3])
        assert dto.id == [1, 2, 3]
