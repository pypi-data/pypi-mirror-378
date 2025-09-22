import pytest
from pydantic import ValidationError

from src.idosell.cms.snippets.cookies import (
    CategoryEnum, LifeTimeTypeEnum, TypeEnum,
    DescriptionCookiesModel, CookiesModel,
    PostCookiesModel, PutCookiesModel,
    PostCmsSnippetsCookiesParamsModel, PutCmsSnippetsCookiesParamsModel,
    Get, Post, Put, Delete
)


# --- Tests for Enums
class TestCategoryEnum:
    def test_valid_values(self):
        assert CategoryEnum.ANALYTICS == 'analytics'
        assert CategoryEnum.MARKETING == 'marketing'
        assert CategoryEnum.FUNCTIONAL == 'functional'

class TestLifeTimeTypeEnum:
    def test_valid_values(self):
        assert LifeTimeTypeEnum.TEMPORARY == 'temporary'
        assert LifeTimeTypeEnum.DAYS == 'days'
        assert LifeTimeTypeEnum.MINUTES == 'minutes'

class TestTypeEnum:
    def test_valid_values(self):
        assert TypeEnum.COOKIE == 'cookie'
        assert TypeEnum.PIXEL == 'pixel'
        assert TypeEnum.LOCALSTORAGE == 'localStorage'


# --- Tests for DTOs
class TestDescriptionCookiesModel:
    def test_valid(self):
        dto = DescriptionCookiesModel(
            lang="eng",
            body="Test description"
        )
        assert dto.lang == "eng"
        assert dto.body == "Test description"

    def test_invalid_lang_short(self):
        with pytest.raises(ValidationError):
            DescriptionCookiesModel(lang="en", body="test")

    def test_invalid_lang_long(self):
        with pytest.raises(ValidationError):
            DescriptionCookiesModel(lang="engg", body="test")

class TestCookiesModel:
    def test_valid_minimal(self):
        dto = CookiesModel()
        assert dto.category is None

    def test_valid_with_all_fields(self):
        dto = CookiesModel(
            category=CategoryEnum.ANALYTICS,
            description=[DescriptionCookiesModel(lang="eng", body="Desc")],
            name="test_cookie",
            type=TypeEnum.COOKIE,
            lifeTimeType=LifeTimeTypeEnum.DAYS,
            lifeTime=30
        )
        assert dto.category == CategoryEnum.ANALYTICS
        assert len(dto.description) == 1
        assert dto.name == "test_cookie"

class TestPostCookiesModel:
    def test_valid(self):
        dto = PostCookiesModel(
            snippetId=1,
            deliverer="Google",
            category=CategoryEnum.MARKETING,
            name="ga_cookie"
        )
        assert dto.snippetId == 1
        assert dto.deliverer == "Google"
        assert dto.id is None

    def test_valid_with_id(self):
        dto = PostCookiesModel(
            id=10,
            snippetId=2,
            deliverer="Test Vendor",
            type=TypeEnum.PIXEL
        )
        assert dto.id == 10
        assert dto.snippetId == 2

    def test_invalid_snippetId_zero(self):
        with pytest.raises(ValidationError):
            PostCookiesModel(snippetId=0, deliverer="Vendor")

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PostCookiesModel(id=0, snippetId=1, deliverer="Vendor")

    def test_invalid_deliverer_empty(self):
        with pytest.raises(ValidationError):
            PostCookiesModel(snippetId=1, deliverer="")

    def test_invalid_deliverer_too_long(self):
        with pytest.raises(ValidationError):
            PostCookiesModel(snippetId=1, deliverer="a" * 129)

class TestPutCookiesModel:
    def test_valid(self):
        dto = PutCookiesModel(
            id=1,
            snippetId=2,
            deliverer="Updated Vendor",
            category=CategoryEnum.FUNCTIONAL
        )
        assert dto.id == 1
        assert dto.snippetId == 2
        assert dto.deliverer == "Updated Vendor"

    def test_valid_without_snippetId(self):
        dto = PutCookiesModel(
            id=2,
            deliverer="Vendor",
            name="updated_name"
        )
        assert dto.id == 2
        assert dto.snippetId is None

    def test_valid_without_deliverer(self):
        dto = PutCookiesModel(
            id=3,
            snippetId=4,
            lifeTimeType=LifeTimeTypeEnum.MINUTES
        )
        assert dto.id == 3
        assert dto.deliverer is None

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            PutCookiesModel(id=0, snippetId=1, deliverer="Vendor")

    def test_invalid_snippetId_zero(self):
        with pytest.raises(ValidationError):
            PutCookiesModel(id=1, snippetId=0, deliverer="Vendor")

    def test_invalid_deliverer_empty(self):
        with pytest.raises(ValidationError):
            PutCookiesModel(id=1, snippetId=1, deliverer="")

class TestPostCmsSnippetsCookiesParamsModel:
    def test_valid(self):
        dto = PostCmsSnippetsCookiesParamsModel(
            cookies=[
                PostCookiesModel(snippetId=1, deliverer="Vendor1"),
                PostCookiesModel(snippetId=2, deliverer="Vendor2")
            ]
        )
        assert len(dto.cookies) == 2

    def test_invalid_empty_cookies(self):
        with pytest.raises(ValidationError):
            PostCmsSnippetsCookiesParamsModel(cookies=[])

    def test_invalid_too_many_cookies(self):
        cookies = [PostCookiesModel(snippetId=i + 1, deliverer=f"Vendor{i}") for i in range(101)]
        with pytest.raises(ValidationError):
            PostCmsSnippetsCookiesParamsModel(cookies=cookies)

class TestPutCmsSnippetsCookiesParamsModel:
    def test_valid(self):
        dto = PutCmsSnippetsCookiesParamsModel(
            cookies=[
                PutCookiesModel(id=1, snippetId=1, deliverer="Vendor1"),
                PutCookiesModel(id=2, snippetId=2, deliverer="Vendor2")
            ]
        )
        assert len(dto.cookies) == 2

    def test_invalid_empty_cookies(self):
        with pytest.raises(ValidationError):
            PutCmsSnippetsCookiesParamsModel(cookies=[])

    def test_invalid_too_many_cookies(self):
        cookies = [PutCookiesModel(id=i + 1, snippetId=i + 1, deliverer=f"Vendor{i}") for i in range(101)]
        with pytest.raises(ValidationError):
            PutCmsSnippetsCookiesParamsModel(cookies=cookies)


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.id is None

    def test_instantiate_with_params(self):
        dto = Get(id=[1, 2, 3])
        assert dto.id == [1, 2, 3]

    def test_invalid_id_empty_list(self):
        with pytest.raises(ValidationError):
            Get(id=[])

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCmsSnippetsCookiesParamsModel(
                cookies=[
                    PostCookiesModel(snippetId=1, deliverer="Vendor")
                ]
            )
        )
        assert len(dto.params.cookies) == 1

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsSnippetsCookiesParamsModel(
                cookies=[
                    PutCookiesModel(id=1, snippetId=1, deliverer="Vendor")
                ]
            )
        )
        assert len(dto.params.cookies) == 1

class TestDelete:
    def test_instantiate(self):
        dto = Delete(id=[1, 2, 3])
        assert dto.id == [1, 2, 3]
