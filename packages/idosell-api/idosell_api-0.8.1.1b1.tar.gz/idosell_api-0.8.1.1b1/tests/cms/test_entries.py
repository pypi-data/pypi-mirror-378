import pytest
from pydantic import ValidationError

from src.idosell.cms.entries import (
    PictureFormatEntriesEnum,
    LangsEntriesModel, VisibleOnSitesListEntriesModel, ProductsEntriesModel,
    PictureEntriesDataModel, EntitiesModel, DeleteCmsEntriesParamsModel,
    PostCmsEntriesParamsModel, PutCmsEntriesParamsModel,
    Delete, Get, Post, Put, GetPagesToDisplay, GetSources
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for Enums
class TestPictureFormatEntriesEnum:
    def test_valid_values(self):
        assert PictureFormatEntriesEnum.JPG == 'jpg'
        assert PictureFormatEntriesEnum.JPEG == 'jpeg'
        assert PictureFormatEntriesEnum.PNG == 'png'
        assert PictureFormatEntriesEnum.GIF == 'gif'


# --- Tests for DTOs
class TestLangsEntriesModel:
    def test_valid(self):
        dto = LangsEntriesModel(
            langId="en",
            title="Test Title",
            shortDescription="Short desc",
            longDescription="Long description",
            blogUrl="http://blog.com",
            newsUrl="http://news.com"
        )
        assert dto.langId == "en"
        assert dto.title == "Test Title"

class TestVisibleOnSitesListEntriesModel:
    def test_valid(self):
        dto = VisibleOnSitesListEntriesModel(siteId="site1")
        assert dto.siteId == "site1"

class TestProductsEntriesModel:
    def test_valid(self):
        dto = ProductsEntriesModel(productId=1)
        assert dto.productId == 1

    def test_invalid_productId_zero(self):
        with pytest.raises(ValidationError):
            ProductsEntriesModel(productId=0)

class TestPictureEntriesDataModel:
    def test_valid(self):
        dto = PictureEntriesDataModel(
            pictureBase64="base64data",
            pictureFormat=PictureFormatEntriesEnum.JPG
        )
        assert dto.pictureBase64 == "base64data"
        assert dto.pictureFormat == PictureFormatEntriesEnum.JPG

class TestEntitiesModel:
    def test_valid_minimal(self):
        dto = EntitiesModel()
        assert dto.shopId is None

    def test_valid_with_all_fields(self):
        dto = EntitiesModel(
            shopId=1,
            date="2023-01-01",
            visible=BooleanStrShortEnum.YES,
            visibleOnSitesList=[VisibleOnSitesListEntriesModel(siteId="site1")],
            products=[ProductsEntriesModel(productId=1)],
            pictureData=PictureEntriesDataModel(
                pictureBase64="data",
                pictureFormat=PictureFormatEntriesEnum.PNG
            ),
            langs=[LangsEntriesModel(
                langId="en",
                title="Title",
                shortDescription="Short",
                longDescription="Long",
                blogUrl="http://blog.com",
                newsUrl="http://news.com"
            )],
            titleLinkType="fullContentLink",
            link="http://link.com"
        )
        assert dto.shopId == 1
        assert dto.visible == BooleanStrShortEnum.YES
        assert len(dto.visibleOnSitesList) == 1

class TestDeleteCmsEntriesParamsModel:
    def test_valid(self):
        dto = DeleteCmsEntriesParamsModel(entryId=1)
        assert dto.entryId == 1

    def test_invalid_entryId_zero(self):
        with pytest.raises(ValidationError):
            DeleteCmsEntriesParamsModel(entryId=0)

class TestPostCmsEntriesParamsModel:
    def test_valid(self):
        dto = PostCmsEntriesParamsModel(
            shopId=1,
            date="2023-01-01"
        )
        assert dto.shopId == 1

class TestPutCmsEntriesParamsModel:
    def test_valid(self):
        dto = PutCmsEntriesParamsModel(
            entryId=1,
            deletePicture=BooleanStrShortEnum.NO,
            shopId=2
        )
        assert dto.entryId == 1
        assert dto.deletePicture == BooleanStrShortEnum.NO

    def test_invalid_entryId_zero(self):
        with pytest.raises(ValidationError):
            PutCmsEntriesParamsModel(
                entryId=0,
                deletePicture=BooleanStrShortEnum.YES
            )


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate(self):
        dto = Delete(
            params=DeleteCmsEntriesParamsModel(entryId=1)
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.params.entryId == 1

class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.entryId is None
        assert dto.langId is None

    def test_instantiate_with_params(self):
        dto = Get(entryId=1, langId="en")
        assert dto.entryId == 1
        assert dto.langId == "en"

    def test_invalid_entryId_zero(self):
        with pytest.raises(ValidationError):
            Get(entryId=0)

    def test_invalid_langId_empty(self):
        with pytest.raises(ValidationError):
            Get(langId="")

class TestPost:
    def test_instantiate_minimal(self):
        dto = Post(params=PostCmsEntriesParamsModel())
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

    def test_instantiate_with_params(self):
        dto = Post(
            params=PostCmsEntriesParamsModel(shopId=1)
        )
        assert dto.params.shopId == 1

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCmsEntriesParamsModel(
                entryId=1,
                deletePicture=BooleanStrShortEnum.YES,
                langs=[LangsEntriesModel(
                    langId="en",
                    title="Title",
                    shortDescription="Short",
                    longDescription="Long",
                    blogUrl="http://blog.com",
                    newsUrl="http://news.com"
                )]
            )
        )
        assert dto.params.entryId == 1
        assert dto.params.deletePicture == BooleanStrShortEnum.YES

class TestGetPagesToDisplay:
    def test_instantiate_minimal(self):
        dto = GetPagesToDisplay()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.langId is None

    def test_instantiate_with_params(self):
        dto = GetPagesToDisplay(langId="en")
        assert dto.langId == "en"

class TestGetSources:
    def test_instantiate_minimal(self):
        dto = GetSources()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto.type is None

    def test_instantiate_with_params(self):
        dto = GetSources(type=["blog", "news"])
        assert dto.type == ["blog", "news"]

    def test_invalid_type_empty_list(self):
        with pytest.raises(ValidationError):
            GetSources(type=[])
