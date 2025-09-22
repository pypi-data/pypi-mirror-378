import pytest
from pydantic import ValidationError

from src.idosell.pim.products._common import (
    # --- Enums
    AddTypeEnum,
    AttachmentFileTypeEnum,
    AttachmentTypeEnum,
    DocumentTypeEnum,
    IdentTypeEnum,
    MetaRobotsSettingsFollowEnum,
    MetaRobotsSettingsIndexEnum,
    MetaSettingsEnum,
    SortModeGridEnum,
    ViewEnum,
    DisplayInPanelEnum,
    DisplayOnPageEnum,
    FilterValueSortEnum,
    FilterDisplayEnum,
    GraphicTypeEnum,
    OperationEnum,
    ProductsImagesSourceTypeEnum,
    ProductIconTypeEnum,
    SourceTypeEnum,
    TypeEnum,
    # --- Marketing Enums
    AssignmentModeEnum,
    BasePricingEnum,
    CalculationMethodEnum,
    ElementTypeEnum,
    ModeEnum,
    # --- Miscs Enums
    AttachmentEnableEnum,
    ProductIdBySizeCodeEnum,
    ProductIdentTypeCodeExistanceEnum,
    # --- Omnibus Enums
    OmnibusPriceManagementEnum,
    # --- Opinions Enums
    ElementNameEnum,
    SortDirectionEnum,
    RateEnum,
    OpinionsTypeEnum,
    TypeProductsGetEnum,
    TypeProductsEnum,
    # --- Parameters Enums
    ContextIdParametersEnum,
    IconsInputTypeParametersEnum,
    # --- Questions Enums
    ProductIdentTypeQuestionsEnum,
    # --- Series Enums
    FilterDisplaySeriesEnum,
    PriceRoundModeEnum,
    # --- Models
    AttachmentLanguagesModel,
    AttachmentNameModel,
    DocumentTypesModel,
    ProductLongDescriptionsLangDataModel,
    ProductLongDescriptionsModel,
    ProductAuctionDescriptionsDataModel,
    ShopsConfigurationsBaseModel,
    ProductSizesBundlesCollectionsModel,
    IdentModel,
    # --- Brands DTOs
    FilterActiveModel,
    ShopsConfigurationsModel,
    ProductsListImagesConfigurationModel,
    ProductCardImagesConfigurationModel,
    LanguagesConfigurationsModel,
    ImagesSettingsModel,
    ProducerPostModel,
    ProducerPutModel,
    # --- Bundles DTOs
    ProductIdentBundlesModel,
    ProductSizesBundlesModel,
    ProductsBundlesPostModel,
    ProductPutRenewModel,
    ProductsPutProductsQuantityModel,
    ProductsBundlesPostProductsModel,
    ProductsBundleDeleteProductsModel,
    # --- Categories DTOs
    CategoriesModel,
    # --- Collections DTOs
    CollectionIdentModel,
    ProductSizesPostModel,
    ProductIdentCollectionsModel,
    ProductsCollectionsPostModel,
    ProductsCollectionsPostProductsModel,
    ProductsCollectionsPutRenewModel,
    ProductsCollectionsPutProductsModel,
    ProductsCollectionsDeleteProductsModel,
    # --- Descriptions DTOs
    ProductIdentModel,
    SectionModel,
    DescriptionSectionsModel,
    ProductDescriptionSectionsModel,
    ProductDescriptionsLangDataModel,
    ProductsDescriptionsModel,
    # --- Groups DTOs
    GroupsPutSettingsModel,
    ProductsInOrderModel,
    # --- Images DTOs
    ProductsImagesSettingsModel,
    ProductIconsModel,
    ProductImagesModel,
    ProductsImages,
    # --- Marketing DTOs
    PromotionElementsModel,
    MarketingZonesPromotionModel,
    MarketingZonesModel,
    NewPriceSettingsModel,
    ProductsMarketingModel,
    ShopsPutZonesModel,
    # --- Miscs DTOs
    AttachmentsModel,
    AttachmentLimitsModel,
    ErrorsModel,
    VirtualAttachmentsBaseModel,
    VirtualAttachmentsModel,
    ProductsDeliveryTimeProductsSearchModel,
    ProductAttachmentPutModel,
    # --- Omnibus DTOs
    OmnibusPricesModel,
    ShopsModel,
    SizesOmnibusModel,
    ProductsOmnibusModel,
    # --- Opinions DTOs
    ClientsOpinionsModel,
    ProductsModel,
    OpinionsPostModel,
    OpinionGetModel,
    ProductsOpinionsGetModel,
    ClientsGetModel,
    ScorePositiveGetModel,
    ScoreNegativeGetModel,
    DateRangeGetModel,
)
from src.idosell._common import BooleanStrShortEnum, BooleanStrLongEnum


# --- Tests for General Enums
class TestAddTypeEnum:
    def test_valid_values(self):
        assert AddTypeEnum.SELECTEDSIZES == 'selectedSizes'
        assert AddTypeEnum.SELECTEDSIZESASSEPARATEITEMS == 'selectedSizesAsSeparateItems'
        assert AddTypeEnum.ALLSIZES == 'allSizes'
        assert AddTypeEnum.ALLSIZESWITHVARIANTS == 'allSizesWithVariants'


class TestAttachmentFileTypeEnum:
    def test_valid_values(self):
        assert AttachmentFileTypeEnum.AUDIO == 'audio'
        assert AttachmentFileTypeEnum.VIDEO == 'video'
        assert AttachmentFileTypeEnum.DOC == 'doc'
        assert AttachmentFileTypeEnum.OTHER == 'other'
        assert AttachmentFileTypeEnum.IMAGE == 'image'


class TestAttachmentTypeEnum:
    def test_valid_values(self):
        assert AttachmentTypeEnum.DEMO == 'demo'
        assert AttachmentTypeEnum.FULL == 'Full'


class TestDocumentTypeEnum:
    def test_valid_values(self):
        assert DocumentTypeEnum.ENERGY_LABEL == 'energy_label'
        assert DocumentTypeEnum.INSTRUCTION_WITH_SAFETY_INFORMATION == 'instruction_with_safety_information'
        assert DocumentTypeEnum.USER_MANUAL == 'user_manual'
        assert DocumentTypeEnum.INSTALLATION_INSTRUCTIONS == 'installation_instructions'
        assert DocumentTypeEnum.PRODUCT_CARD == 'product_card'
        assert DocumentTypeEnum.GUIDE == 'guide'
        assert DocumentTypeEnum.OTHERS == 'others'


class TestIdentTypeEnum:
    def test_valid_values(self):
        assert IdentTypeEnum.ID == 'id'
        assert IdentTypeEnum.INDEX == 'index'
        assert IdentTypeEnum.CODEEXTERN == 'codeExtern'
        assert IdentTypeEnum.CODEPRODUCER == 'codeProducer'


class TestMetaRobotsSettingsFollowEnum:
    def test_valid_values(self):
        assert MetaRobotsSettingsFollowEnum.AUTO == 'auto'
        assert MetaRobotsSettingsFollowEnum.FOLLOW == 'follow'
        assert MetaRobotsSettingsFollowEnum.NOFOLLOW == 'nofollow'


class TestMetaRobotsSettingsIndexEnum:
    def test_valid_values(self):
        assert MetaRobotsSettingsIndexEnum.AUTO == 'auto'
        assert MetaRobotsSettingsIndexEnum.INDEX == 'index'
        assert MetaRobotsSettingsIndexEnum.NOINDEX == 'noindex'


class TestMetaSettingsEnum:
    def test_valid_values(self):
        assert MetaSettingsEnum.AUTO == 'auto'
        assert MetaSettingsEnum.CUSTOM == 'custom'


class TestSortModeGridEnum:
    def test_valid_values(self):
        assert SortModeGridEnum.D_RELEVANCE == 'd_relevance'
        assert SortModeGridEnum.D_DATE == 'd_date'
        assert SortModeGridEnum.A_DATE == 'a_date'
        assert SortModeGridEnum.D_PRIORITY == 'd_priority'
        assert SortModeGridEnum.A_PRIORITY == 'a_priority'
        assert SortModeGridEnum.A_PRIORITYNAME == 'a_priorityname'
        assert SortModeGridEnum.D_PRIORITYNAME == 'd_priorityname'
        assert SortModeGridEnum.D_PRIORITYONLY == 'd_priorityonly'
        assert SortModeGridEnum.A_PRIORITYONLY == 'a_priorityonly'
        assert SortModeGridEnum.A_NAME == 'a_name'
        assert SortModeGridEnum.D_NAME == 'd_name'
        assert SortModeGridEnum.A_PRICE == 'a_price'
        assert SortModeGridEnum.D_PRICE == 'd_price'


class TestViewEnum:
    def test_valid_values(self):
        assert ViewEnum.DEFAULT == 'default'
        assert ViewEnum.OWN == 'own'


class TestDisplayInPanelEnum:
    def test_valid_values(self):
        assert DisplayInPanelEnum.ALL == 'all'
        assert DisplayInPanelEnum.FIRSTAVAILABLE == 'firstAvailable'


class TestDisplayOnPageEnum:
    def test_valid_values(self):
        assert DisplayOnPageEnum.ALL == 'all'
        assert DisplayOnPageEnum.FIRSTAVAILABLE == 'firstAvailable'
        assert DisplayOnPageEnum.SPECIFIED == 'specified'


class TestFilterValueSortEnum:
    def test_valid_values(self):
        assert FilterValueSortEnum.NO == 'n'
        assert FilterValueSortEnum.PRIORITY == 'priority'
        assert FilterValueSortEnum.YES == 'y'


class TestFilterDisplayEnum:
    def test_valid_values(self):
        assert FilterDisplayEnum.NAME == 'name'
        assert FilterDisplayEnum.GFX == 'gfx'
        assert FilterDisplayEnum.NAMEGFX == 'namegfx'


class TestGraphicTypeEnum:
    def test_valid_values(self):
        assert GraphicTypeEnum.IMG == 'img'
        assert GraphicTypeEnum.IMG_RWD == 'img_rwd'


class TestOperationEnum:
    def test_valid_values(self):
        assert OperationEnum.ADD == 'add'
        assert OperationEnum.DEL == 'del'
        assert OperationEnum.EDIT == 'edit'


class TestProductsImagesSourceTypeEnum:
    def test_valid_values(self):
        assert ProductsImagesSourceTypeEnum.BASE64 == 'base64'
        assert ProductsImagesSourceTypeEnum.URL == 'url'


class TestProductIconTypeEnum:
    def test_valid_values(self):
        assert ProductIconTypeEnum.AUCTION == 'auction'
        assert ProductIconTypeEnum.GROUP == 'group'
        assert ProductIconTypeEnum.SHOP == 'shop'


class TestSourceTypeEnum:
    def test_valid_values(self):
        assert SourceTypeEnum.BASE64 == 'base64'
        assert SourceTypeEnum.URL == 'url'


class TestTypeEnum:
    def test_valid_values(self):
        assert TypeEnum.HTML == 'html'
        assert TypeEnum.PHOTO == 'photo'
        assert TypeEnum.TEXT == 'text'
        assert TypeEnum.VIDEO == 'video'


# --- Tests for Marketing Enums
class TestAssignmentModeEnum:
    def test_valid_values(self):
        assert AssignmentModeEnum.AUTO == 'auto'
        assert AssignmentModeEnum.MANUAL == 'manual'


class TestBasePricingEnum:
    def test_valid_values(self):
        assert BasePricingEnum.GROSS == 'gross'
        assert BasePricingEnum.NET == 'net'


class TestCalculationMethodEnum:
    def test_valid_values(self):
        assert CalculationMethodEnum.CHOOSEADVANTAGEOUS == 'chooseAdvantageous'
        assert CalculationMethodEnum.SUM == 'sum'


class TestElementTypeEnum:
    def test_valid_values(self):
        assert ElementTypeEnum.PRODUCT == 'product'
        assert ElementTypeEnum.SERIES == 'series'
        assert ElementTypeEnum.PRODUCER == 'producer'
        assert ElementTypeEnum.CATEGORY == 'category'
        assert ElementTypeEnum.MENU == 'menu'


class TestModeEnum:
    def test_valid_values(self):
        assert ModeEnum.PERCENT_DIFF == 'percent_diff'
        assert ModeEnum.AMOUNT_DIFF == 'amount_diff'
        assert ModeEnum.AMOUNT_SET == 'amount_set'


# --- Tests for Miscs Enums
class TestAttachmentEnableEnum:
    def test_valid_values(self):
        assert AttachmentEnableEnum.ALL == 'all'
        assert AttachmentEnableEnum.ORDERED == 'ordered'
        assert AttachmentEnableEnum.WHOLESALER == 'wholesaler'
        assert AttachmentEnableEnum.WHOLESALER_OR_ORDERED == 'wholesaler_or_ordered'
        assert AttachmentEnableEnum.WHOLESALER_AND_ORDERED == 'wholesaler_and_ordered'


class TestProductIdBySizeCodeEnum:
    def test_valid_values(self):
        assert ProductIdBySizeCodeEnum.EXTERNAL == 'external'
        assert ProductIdBySizeCodeEnum.PRODUCER == 'producer'
        assert ProductIdBySizeCodeEnum.ALL == 'all'


class TestProductIdentTypeCodeExistanceEnum:
    def test_valid_values(self):
        assert ProductIdentTypeCodeExistanceEnum.ID == 'id'
        assert ProductIdentTypeCodeExistanceEnum.INDEX == 'index'
        assert ProductIdentTypeCodeExistanceEnum.CODEEXTERN == 'codeExtern'
        assert ProductIdentTypeCodeExistanceEnum.CODEPRODUCER == 'codeProducer'
        assert ProductIdentTypeCodeExistanceEnum.CODEDELIVERER == 'codeDeliverer'


# --- Tests for Omnibus Enums
class TestOmnibusPriceManagementEnum:
    def test_valid_values(self):
        assert OmnibusPriceManagementEnum.AUTOMATIC == 'automatic'
        assert OmnibusPriceManagementEnum.MANUAL == 'manual'


# --- Tests for Opinions Enums
class TestElementNameEnum:
    def test_valid_values(self):
        assert ElementNameEnum.DATE == 'date'
        assert ElementNameEnum.RATING == 'rating'
        assert ElementNameEnum.SCOREPOSITIVE == 'scorePositive'
        assert ElementNameEnum.SCORENEGATIVE == 'scoreNegative'
        assert ElementNameEnum.MODIFICATIONDATETIME == 'modificationDatetime'


class TestSortDirectionEnum:
    def test_valid_values(self):
        assert SortDirectionEnum.ASC == 'ASC'
        assert SortDirectionEnum.DESC == 'DESC'


class TestRateEnum:
    def test_valid_values(self):
        assert RateEnum.POSITIVE == 'positive'
        assert RateEnum.NEGATUVE == 'negative'


class TestOpinionsTypeEnum:
    def test_valid_values(self):
        assert OpinionsTypeEnum.ID == 'id'
        assert OpinionsTypeEnum.LOGIN == 'login'
        assert OpinionsTypeEnum.CODEEXTERN == 'codeExtern'


class TestTypeProductsGetEnum:
    def test_valid_values(self):
        assert TypeProductsGetEnum.ID == 'id'
        assert TypeProductsGetEnum.INDEX == 'index'
        assert TypeProductsGetEnum.CODEEXTERN == 'codeExtern'
        assert TypeProductsGetEnum.CODEPRODUCER == 'codeProducer'


class TestTypeProductsEnum:
    def test_valid_values(self):
        assert TypeProductsEnum.ID == 'id'
        assert TypeProductsEnum.INDEX == 'index'
        assert TypeProductsEnum.CODEEXTERN == 'codeExtern'
        assert TypeProductsEnum.CODEPRODUCER == 'codeProducer'


# --- Tests for Parameters Enums
class TestContextIdParametersEnum:
    def test_valid_values(self):
        assert ContextIdParametersEnum.CONTEXT_STATE == '1'
        assert ContextIdParametersEnum.CONTEXT_STD_UNIT_WEIGHT == '2'
        assert ContextIdParametersEnum.CONTEXT_STD_UNIT_VOLUME == '3'
        assert ContextIdParametersEnum.CONTEXT_SEX == '4'
        assert ContextIdParametersEnum.CONTEXT_AGE_GROUP == '5'
        assert ContextIdParametersEnum.CONTEXT_MAX_QUANTITY_PER_RETAIL_ORDER == '6'
        assert ContextIdParametersEnum.CONTEXT_MAX_QUANTITY_PER_WHOLESALE_ORDER == '7'
        assert ContextIdParametersEnum.CONTEXT_MIN_QUANTITY_PER_RETAIL_ORDER == '8'
        assert ContextIdParametersEnum.CONTEXT_MIN_QUANTITY_PER_WHOLESALE_ORDER == '9'
        assert ContextIdParametersEnum.CONTEXT_MAX_SIZE_QUANTITY_PER_RETAIL_ORDER == '10'
        assert ContextIdParametersEnum.CONTEXT_MAX_SIZE_QUANTITY_PER_WHOLESALE_ORDER == '11'
        assert ContextIdParametersEnum.CONTEXT_MIN_SIZE_QUANTITY_PER_RETAIL_ORDER == '12'
        assert ContextIdParametersEnum.CONTEXT_MIN_SIZE_QUANTITY_PER_WHOLESALE_ORDER == '13'
        assert ContextIdParametersEnum.CONTEXT_WEIGHT_NET == '14'
        assert ContextIdParametersEnum.CONTEXT_COLOR == '15'
        assert ContextIdParametersEnum.CONTEXT_ONLY_ADULTS == '16'
        assert ContextIdParametersEnum.CONTEXT_PRESCRIPTION_MEDICINE == '17'
        assert ContextIdParametersEnum.CONTEXT_SEASON == '18'
        assert ContextIdParametersEnum.CONTEXT_HAZMAT_SIGNAL == '19'
        assert ContextIdParametersEnum.CONTEXT_HAZMAT_PICTOGRAM == '20'
        assert ContextIdParametersEnum.CONTEXT_HAZMAT_STATEMENT == '21'
        assert ContextIdParametersEnum.CONTEXT_REPAIR_SCORE == '22'
        assert ContextIdParametersEnum.CONTEXT_SAFETY_PICTOGRAM == '23'
        assert ContextIdParametersEnum.CONTEXT_SAFETY_STATEMENT == '24'


class TestIconsInputTypeParametersEnum:
    def test_valid_values(self):
        assert IconsInputTypeParametersEnum.BASE64 == 'base64'
        assert IconsInputTypeParametersEnum.URL == 'url'


# --- Tests for Questions Enums
class TestProductIdentTypeQuestionsEnum:
    def test_valid_values(self):
        assert ProductIdentTypeQuestionsEnum.ID == 'id'
        assert ProductIdentTypeQuestionsEnum.CODEEXTERN == 'codeExtern'
        assert ProductIdentTypeQuestionsEnum.CODEPRODUCER == 'codeProducer'


# --- Tests for Series Enums
class TestFilterDisplaySeriesEnum:
    def test_valid_values(self):
        assert FilterDisplaySeriesEnum.NAME == 'name'
        assert FilterDisplaySeriesEnum.GFX == 'gfx'
        assert FilterDisplaySeriesEnum.NAMEGFX == 'namegfx'


class TestPriceRoundModeEnum:
    def test_valid_values(self):
        assert PriceRoundModeEnum.NONE == 'none'
        assert PriceRoundModeEnum.VAL00 == '00'
        assert PriceRoundModeEnum.VAL99 == '99'
        assert PriceRoundModeEnum.VALX0 == 'x0'
        assert PriceRoundModeEnum.VALX9 == 'x9'


# --- Tests for Models
class TestAttachmentLanguagesModel:
    def test_valid(self):
        model = AttachmentLanguagesModel(
            langId="en",
            langName="English",
            langValue="Value"
        )
        assert model.langId == "en"


class TestAttachmentNameModel:
    def test_valid(self):
        model = AttachmentNameModel(
            attachmentLanguages=[]
        )
        assert model.attachmentLanguages == []


class TestDocumentTypesModel:
    def test_valid(self):
        model = DocumentTypesModel(
            documentType=DocumentTypeEnum.USER_MANUAL,
            description="Manual description"
        )
        assert model.documentType == DocumentTypeEnum.USER_MANUAL


class TestProductLongDescriptionsLangDataModel:
    def test_valid(self):
        model = ProductLongDescriptionsLangDataModel(
            langId="en",
            productLongDescription="Long desc"
        )
        assert model.langId == "en"


class TestProductLongDescriptionsModel:
    def test_valid(self):
        model = ProductLongDescriptionsModel(
            productLongDescriptionsLangData=[]
        )
        assert model.productLongDescriptionsLangData == []


class TestProductAuctionDescriptionsDataModel:
    def test_valid(self):
        model = ProductAuctionDescriptionsDataModel(
            productAuctionId="123",
            productAuctionSiteId="456",
            productAuctionName="Auction Name",
            productAuctionAdditionalName="Additional",
            productAuctionDescription="Description"
        )
        assert model.productAuctionId == "123"


class TestShopsConfigurationsBaseModel:
    def test_valid(self):
        model = ShopsConfigurationsBaseModel(
            headerName="Header",
            shopId=1,
            view=ViewEnum.DEFAULT,
            enableSort=True,
            enableChangeDisplayCount=True,
            numberOfProductsGrid=10,
            sortModeGrid=SortModeGridEnum.D_NAME,
            metaSettings=None,
            metaTitle=None,
            metaDescription=None,
            metaKeywords=None,
            metaRobotsSettingsIndex=MetaRobotsSettingsIndexEnum.AUTO,
            metaRobotsSettingsFollow=MetaRobotsSettingsFollowEnum.AUTO
        )
        assert model.shopId == 1
        assert model.numberOfProductsGrid == 10


class TestProductSizesBundlesCollectionsModel:
    def test_valid(self):
        model = ProductSizesBundlesCollectionsModel(
            size="M",
            sizePanelName="Medium"
        )
        assert model.size == "M"


class TestIdentModel:
    def test_valid(self):
        model = IdentModel(
            type=IdentTypeEnum.ID,
            value="123"
        )
        assert model.type == IdentTypeEnum.ID


# --- Tests for Brands DTOs
class TestFilterActiveModel:
    def test_valid(self):
        model = FilterActiveModel(
            filterId="color",
            filterName="Color Filter",
            filterDisplay=FilterDisplayEnum.NAME,
            filterValueSort=FilterValueSortEnum.YES,
            filterDefaultEnabled=BooleanStrShortEnum.YES
        )
        assert model.filterId == "color"


class TestShopsConfigurationsModel:
    def test_valid(self):
        model = ShopsConfigurationsModel(
            headerName="Header",
            shopId=1,
            view=ViewEnum.DEFAULT,
            enableSort=True,
            enableChangeDisplayCount=True,
            numberOfProductsGrid=10,
            sortModeGrid=SortModeGridEnum.D_NAME,
            name="Shop Name",
            descriptionTop="Top desc",
            descriptionBottom="Bottom desc",
            metaSettings=None,
            metaTitle=None,
            metaDescription=None,
            metaKeywords=None,
            metaRobotsSettingsIndex=MetaRobotsSettingsIndexEnum.AUTO,
            metaRobotsSettingsFollow=MetaRobotsSettingsFollowEnum.AUTO
        )
        assert model.name == "Shop Name"


class TestProductsListImagesConfigurationModel:
    def test_valid(self):
        model = ProductsListImagesConfigurationModel(
            graphicType=GraphicTypeEnum.IMG,
            singleGraphic="http://example.com/image.jpg",
            pcGraphic="http://example.com/pc.jpg",
            tabletGraphic="http://example.com/tablet.jpg",
            phoneGraphic="http://example.com/phone.jpg"
        )
        assert model.graphicType == GraphicTypeEnum.IMG


class TestProductCardImagesConfigurationModel:
    def test_valid(self):
        model = ProductCardImagesConfigurationModel(
            graphicType=GraphicTypeEnum.IMG,
            singleGraphic="http://example.com/image.jpg",
            pcGraphic="http://example.com/pc.jpg",
            tabletGraphic="http://example.com/tablet.jpg",
            phoneGraphic="http://example.com/phone.jpg"
        )
        assert model.graphicType == GraphicTypeEnum.IMG


class TestLanguagesConfigurationsModel:
    def test_valid(self):
        model = LanguagesConfigurationsModel(
            productsListImagesConfiguration=ProductsListImagesConfigurationModel(
                graphicType=GraphicTypeEnum.IMG,
                singleGraphic="img.jpg",
                pcGraphic="pc.jpg",
                tabletGraphic="tab.jpg",
                phoneGraphic="ph.jpg"
            ),
            productCardImagesConfiguration=ProductCardImagesConfigurationModel(
                graphicType=GraphicTypeEnum.IMG,
                singleGraphic="img.jpg",
                pcGraphic="pc.jpg",
                tabletGraphic="tab.jpg",
                phoneGraphic="ph.jpg"
            ),
            languageId="en",
            shopsConfigurations=[]
        )
        assert model.languageId == "en"


class TestImagesSettingsModel:
    def test_valid(self):
        model = ImagesSettingsModel(
            sourceType=SourceTypeEnum.URL
        )
        assert model.sourceType == SourceTypeEnum.URL


class TestProducerPostModel:
    def test_valid(self):
        model = ProducerPostModel(
            nameInPanel="Producer Name",
            imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
            languagesConfigurations=[]
        )
        assert model.nameInPanel == "Producer Name"


class TestProducerPutModel:
    def test_valid(self):
        model = ProducerPutModel(
            id=1,
            nameInPanel="Producer Name",
            imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
            languagesConfigurations=[]
        )
        assert model.id == 1

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            ProducerPutModel(
                id=0,
                nameInPanel="Producer Name",
                imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.URL),
                languagesConfigurations=[]
            )


# --- Tests for Bundles DTOs
class TestProductIdentBundlesModel:
    def test_valid(self):
        model = ProductIdentBundlesModel(
            productIdentType=IdentTypeEnum.ID,
            identValue="123"
        )
        assert model.productIdentType == IdentTypeEnum.ID


class TestProductSizesBundlesModel:
    def test_valid(self):
        model = ProductSizesBundlesModel(
            size="M",
            sizePanelName="Medium"
        )
        assert model.size == "M"


class TestProductsBundlesPostModel:
    def test_valid(self):
        model = ProductsBundlesPostModel(
            productIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="123"
            ),
            productSizes=ProductSizesBundlesModel(
                size="M",
                sizePanelName="Medium"
            ),
            addType=AddTypeEnum.ALLSIZES,
            quantity=2.0
        )
        assert model.quantity == 2.0


class TestProductPutRenewModel:
    def test_valid(self):
        model = ProductPutRenewModel(
            productIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="123"
            ),
            productSizes=[],
            addType=AddTypeEnum.ALLSIZES,
            quantity=1
        )
        assert model.quantity == 1


class TestProductsPutProductsQuantityModel:
    def test_valid(self):
        model = ProductsPutProductsQuantityModel(
            productIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="123"
            ),
            quantity=2.5
        )
        assert model.quantity == 2.5


class TestProductsBundlesPostProductsModel:
    def test_valid(self):
        model = ProductsBundlesPostProductsModel(
            productIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="123"
            ),
            productSizes=ProductSizesBundlesCollectionsModel(
                size="M",
                sizePanelName="Medium"
            ),
            addType=AddTypeEnum.ALLSIZES,
            quantity=3.0
        )
        assert model.quantity == 3.0


class TestProductsBundleDeleteProductsModel:
    def test_valid(self):
        model = ProductsBundleDeleteProductsModel(
            productIdent=ProductIdentBundlesModel(
                productIdentType=IdentTypeEnum.ID,
                identValue="123"
            )
        )
        assert model.productIdent.productIdentType == IdentTypeEnum.ID


# --- Tests for Categories DTOs
class TestCategoriesModel:
    def test_valid(self):
        model = CategoriesModel(
            id=1,
            parent_id=1,
            priority=1,
            operation=OperationEnum.ADD
        )
        assert model.id == 1
        assert model.priority == 1

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            CategoriesModel(
                id=0,
                parent_id=0,
                priority=1,
                operation=OperationEnum.ADD
            )


# --- Tests for Collections DTOs
class TestCollectionIdentModel:
    def test_valid(self):
        model = CollectionIdentModel(
            collectionId="col1",
            collectionIdentType=IdentTypeEnum.ID
        )
        assert model.collectionId == "col1"


class TestProductSizesPostModel:
    def test_valid(self):
        model = ProductSizesPostModel(
            size="L"
        )
        assert model.size == "L"


class TestProductIdentCollectionsModel:
    def test_valid(self):
        model = ProductIdentCollectionsModel(
            productId="123",
            productIdentType=IdentTypeEnum.ID
        )
        assert model.productId == "123"


class TestProductsCollectionsPostModel:
    def test_valid(self):
        model = ProductsCollectionsPostModel(
            productId=123,
            productSizes=[],
            quantity=2
        )
        assert model.productId == 123
        assert model.quantity == 2


class TestProductsCollectionsPostProductsModel:
    def test_valid(self):
        model = ProductsCollectionsPostProductsModel(
            productId=123,
            productSizes=[],
            addType=AddTypeEnum.ALLSIZES,
            quantity=3
        )
        assert model.quantity == 3


class TestProductsCollectionsPutRenewModel:
    def test_valid(self):
        model = ProductsCollectionsPutRenewModel(
            productIdent=ProductIdentCollectionsModel(
                productId="123",
                productIdentType=IdentTypeEnum.ID
            ),
            productSizes=[],
            addType=AddTypeEnum.ALLSIZES,
            quantity=4
        )
        assert model.quantity == 4


class TestProductsCollectionsPutProductsModel:
    def test_valid(self):
        model = ProductsCollectionsPutProductsModel(
            productId=123,
            quantity=5
        )
        assert model.quantity == 5


class TestProductsCollectionsDeleteProductsModel:
    def test_valid(self):
        model = ProductsCollectionsDeleteProductsModel(
            productId=123
        )
        assert model.productId == 123


# --- Tests for Descriptions DTOs
class TestProductIdentModel:
    def test_valid(self):
        model = ProductIdentModel(
            identValue="123",
            productIdentType=IdentTypeEnum.ID
        )
        assert model.productIdentType == IdentTypeEnum.ID


class TestSectionModel:
    def test_valid(self):
        model = SectionModel(
            type=TypeEnum.HTML,
            content="<p>Content</p>"
        )
        assert model.type == TypeEnum.HTML


class TestDescriptionSectionsModel:
    def test_valid(self):
        model = DescriptionSectionsModel(
            section_1=SectionModel(
                type=TypeEnum.TEXT,
                content="Text content"
            ),
            section_2=SectionModel(
                type=TypeEnum.HTML,
                content="<p>HTML content</p>"
            )
        )
        assert model.section_1.content == "Text content"


class TestProductDescriptionSectionsModel:
    def test_valid(self):
        model = ProductDescriptionSectionsModel(
            descriptionSections=[]
        )
        assert model.descriptionSections == []


class TestProductDescriptionsLangDataModel:
    def test_valid(self):
        model = ProductDescriptionsLangDataModel(
            langId="en",
            shopId=1,
            productName="Product Name",
            productAuctionName="Auction Name",
            productPriceComparerName="Price Comparer",
            productDescription="Description",
            productLongDescription="Long desc",
            productDescriptionSections=ProductDescriptionSectionsModel(descriptionSections=[]),
            productAuctionLongDescription="Deprecated desc",
            productMetaTitle="Meta Title",
            productMetaDescription="Meta Desc",
            productMetaKeywords="keywords"
        )
        assert model.langId == "en"


class TestProductsDescriptionsModel:
    def test_valid(self):
        model = ProductsDescriptionsModel(
            productIdent=ProductIdentModel(
                identValue="123",
                productIdentType=IdentTypeEnum.ID
            ),
            productDescriptionsLangData=[],
            productAuctionDescriptionsData=[]
        )
        assert model.productIdent.identValue == "123"


# --- Tests for Groups DTOs
class TestGroupsPutSettingsModel:
    def test_valid(self):
        model = GroupsPutSettingsModel(
            productIdent=ProductIdentModel(
                identValue="123",
                productIdentType=IdentTypeEnum.ID
            ),
            displayInPanel=DisplayInPanelEnum.ALL,
            displayOnPage=DisplayOnPageEnum.ALL,
            specifiedProductIdent=ProductIdentModel(
                identValue="456",
                productIdentType=IdentTypeEnum.ID
            )
        )
        assert model.displayInPanel == DisplayInPanelEnum.ALL


class TestProductsInOrderModel:
    def test_valid(self):
        model = ProductsInOrderModel(
            productIdent=ProductIdentModel(
                identValue="123",
                productIdentType=IdentTypeEnum.ID
            ),
            priority=1
        )
        assert model.priority == 1

    def test_invalid_priority_zero(self):
        with pytest.raises(ValidationError):
            ProductsInOrderModel(
                productIdent=ProductIdentModel(
                    identValue="123",
                    productIdentType=IdentTypeEnum.ID
                ),
                priority=0
            )


# --- Tests for Images DTOs
class TestProductsImagesSettingsModel:
    def test_valid(self):
        model = ProductsImagesSettingsModel(
            productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
            productsImagesApplyMacro=False
        )
        assert model.productsImagesSourceType == ProductsImagesSourceTypeEnum.URL


class TestProductIconsModel:
    def test_valid(self):
        model = ProductIconsModel(
            productIconSource="http://example.com/icon.jpg",
            deleteProductIcon=False,
            productIconType=ProductIconTypeEnum.SHOP
        )
        assert model.productIconType == ProductIconTypeEnum.SHOP


class TestProductImagesModel:
    def test_valid(self):
        model = ProductImagesModel(
            productImageSource="http://example.com/image.jpg",
            productImageNumber=1,
            productImagePriority=1,
            deleteProductImage=False
        )
        assert model.productImageNumber == 1
        assert model.productImagePriority == 1


class TestProductsImages:
    def test_valid(self):
        model = ProductsImages(
            productIdent=ProductIdentModel(
                identValue="123",
                productIdentType=IdentTypeEnum.ID
            ),
            shopId=1,
            otherShopsForPic=[],
            productImages=[],
            productIcons=[],
            productImagesSettings=ProductsImagesSettingsModel(
                productsImagesSourceType=ProductsImagesSourceTypeEnum.URL,
                productsImagesApplyMacro=False
            )
        )
        assert model.shopId == 1


# --- Tests for Marketing DTOs
class TestPromotionElementsModel:
    def test_valid(self):
        model = PromotionElementsModel(
            elementType=ElementTypeEnum.PRODUCT,
            elementId="123"
        )
        assert model.elementType == ElementTypeEnum.PRODUCT


class TestMarketingZonesPromotionModel:
    def test_valid(self):
        model = MarketingZonesPromotionModel(
            promotion=BooleanStrShortEnum.YES,
            discount=BooleanStrShortEnum.NO,
            distinguished=BooleanStrShortEnum.YES,
            special=BooleanStrShortEnum.NO,
            new=BooleanStrShortEnum.YES
        )
        assert model.promotion == BooleanStrShortEnum.YES


class TestMarketingZonesModel:
    def test_valid(self):
        model = MarketingZonesModel(
            promotion=BooleanStrLongEnum.YES,
            discount=BooleanStrLongEnum.NO,
            distinguished=BooleanStrLongEnum.YES,
            special=BooleanStrLongEnum.NO
        )
        assert model.promotion == BooleanStrLongEnum.YES


class TestNewPriceSettingsModel:
    def test_valid(self):
        model = NewPriceSettingsModel(
            type=TypeEnum.TEXT,
            discountValue=10.5,
            currencyId="PLN",
            mode=ModeEnum.PERCENT_DIFF,
            endValue="100.00"
        )
        assert model.discountValue == 10.5


class TestProductsMarketingModel:
    def test_valid(self):
        model = ProductsMarketingModel(
            ident=IdentModel(
                type=IdentTypeEnum.ID,
                value="123"
            ),
            assignment_mode=AssignmentModeEnum.AUTO,
            marketing_zones=MarketingZonesModel(
                promotion=BooleanStrLongEnum.YES,
                discount=BooleanStrLongEnum.NO,
                distinguished=BooleanStrLongEnum.YES,
                special=BooleanStrLongEnum.NO
            )
        )
        assert model.assignment_mode == AssignmentModeEnum.AUTO


class TestShopsPutZonesModel:
    def test_valid(self):
        model = ShopsPutZonesModel(
            shop_id=1,
            assignment_mode=AssignmentModeEnum.MANUAL,
            marketing_zones=MarketingZonesModel(
                promotion=BooleanStrLongEnum.YES,
                discount=BooleanStrLongEnum.NO,
                distinguished=BooleanStrLongEnum.YES,
                special=BooleanStrLongEnum.NO
            )
        )
        assert model.shop_id == 1

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            ShopsPutZonesModel(
                shop_id=0,
                assignment_mode=AssignmentModeEnum.MANUAL,
                marketing_zones=MarketingZonesModel(
                    promotion=BooleanStrLongEnum.YES,
                    discount=BooleanStrLongEnum.NO,
                    distinguished=BooleanStrLongEnum.YES,
                    special=BooleanStrLongEnum.NO
                )
            )


# --- Tests for Miscs DTOs
class TestAttachmentsModel:
    def test_valid(self):
        model = AttachmentsModel(
            attachmentUrl="http://example.com/file.pdf",
            attachmentName="Manual.pdf",
            langId="en",
            attachmentFileType=AttachmentFileTypeEnum.DOC,
            attachmentEnable=AttachmentEnableEnum.ALL,
            attachmentId=1,
            attachmentDownloadLog=BooleanStrShortEnum.YES,
            attachmentFileExtension="pdf",
            attachmentPriority=1,
            attachmentToDelete=False,
            documentTypes=[]
        )
        assert model.attachmentId == 1
        assert model.attachmentPriority == 1

    def test_invalid_attachment_id_zero(self):
        with pytest.raises(ValidationError):
            AttachmentsModel(
                attachmentUrl="http://example.com/file.pdf",
                attachmentName="Manual.pdf",
                langId="en",
                attachmentFileType=AttachmentFileTypeEnum.DOC,
                attachmentEnable=AttachmentEnableEnum.ALL,
                attachmentId=0,
                attachmentDownloadLog=BooleanStrShortEnum.YES,
                attachmentFileExtension="pdf",
                attachmentPriority=1,
                attachmentToDelete=False,
                documentTypes=[]
            )


class TestAttachmentLimitsModel:
    def test_valid(self):
        model = AttachmentLimitsModel(
            attachmentDownloadsLimit=10,
            attachmentDaysLimit=30
        )
        assert model.attachmentDownloadsLimit == 10

    def test_invalid_attachment_downloads_limit_zero(self):
        with pytest.raises(ValidationError):
            AttachmentLimitsModel(
                attachmentDownloadsLimit=0,
                attachmentDaysLimit=30
            )


class TestErrorsModel:
    def test_valid(self):
        model = ErrorsModel(
            faultCode=0,
            faultString="OK"
        )
        assert model.faultCode == 0


class TestVirtualAttachmentsBaseModel:
    def test_valid(self):
        model = VirtualAttachmentsBaseModel(
            attachmentUrl="http://example.com/file.pdf",
            attachmentName=AttachmentNameModel(attachmentLanguages=[]),
            attachmentType=AttachmentTypeEnum.FULL,
            attachmentLimits=AttachmentLimitsModel(
                attachmentDownloadsLimit=10,
                attachmentDaysLimit=30
            ),
            attachmentId=1,
            attachmentPriority=1
        )
        assert model.attachmentId == 1

    def test_invalid_attachment_id_zero(self):
        with pytest.raises(ValidationError):
            VirtualAttachmentsBaseModel(
                attachmentUrl="http://example.com/file.pdf",
                attachmentName=AttachmentNameModel(attachmentLanguages=[]),
                attachmentType=AttachmentTypeEnum.FULL,
                attachmentLimits=AttachmentLimitsModel(
                    attachmentDownloadsLimit=10,
                    attachmentDaysLimit=30
                ),
                attachmentId=0,
                attachmentPriority=1
            )


class TestVirtualAttachmentsModel:
    def test_valid(self):
        model = VirtualAttachmentsModel(
            attachmentUrl="http://example.com/file.pdf",
            attachmentName=AttachmentNameModel(attachmentLanguages=[]),
            attachmentType=AttachmentTypeEnum.FULL,
            attachmentLimits=AttachmentLimitsModel(
                attachmentDownloadsLimit=10,
                attachmentDaysLimit=30
            ),
            attachmentId=1,
            attachmentPriority=1,
            attachmentToDelete=False,
            errors=ErrorsModel(faultCode=0, faultString="OK")
        )
        assert model.attachmentToDelete is False


class TestProductsDeliveryTimeProductsSearchModel:
    def test_valid(self):
        model = ProductsDeliveryTimeProductsSearchModel(
            productId=123,
            sizeId="M",
            sizePanelName="Medium",
            productIndex="IDX123",
            productSizeQuantity=5
        )
        assert model.productId == 123
        assert model.productSizeQuantity == 5


class TestProductAttachmentPutModel:
    def test_valid(self):
        model = ProductAttachmentPutModel(
            productIdent=ProductIdentModel(
                identValue="123",
                productIdentType=IdentTypeEnum.ID
            ),
            attachments=[],
            virtualAttachments=[],
            errors=ErrorsModel(faultCode=0, faultString="OK"),
            attachmentsErrorsOccurred=False,
            virtualAttachmentsErrorsOccurred=False
        )
        assert model.attachmentsErrorsOccurred is False


# --- Tests for Omnibus DTOs
class TestOmnibusPricesModel:
    def test_valid(self):
        model = OmnibusPricesModel(
            omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
            omnibusPriceRetail=100.50,
            omnibusPriceWholesale=90.25
        )
        assert model.omnibusPriceManagement == OmnibusPriceManagementEnum.AUTOMATIC


class TestShopsModel:
    def test_valid(self):
        model = ShopsModel(
            shopId=1,
            omnibusPrices=OmnibusPricesModel(
                omnibusPriceManagement=OmnibusPriceManagementEnum.MANUAL,
                omnibusPriceRetail=100.0,
                omnibusPriceWholesale=80.0
            )
        )
        assert model.shopId == 1

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            ShopsModel(
                shopId=0,
                omnibusPrices=OmnibusPricesModel(
                    omnibusPriceManagement=OmnibusPriceManagementEnum.MANUAL,
                    omnibusPriceRetail=100.0,
                    omnibusPriceWholesale=80.0
                )
            )


class TestSizesOmnibusModel:
    def test_valid(self):
        model = SizesOmnibusModel(
            ident=IdentModel(
                type=IdentTypeEnum.ID,
                value="123"
            ),
            omnibusPrices=OmnibusPricesModel(
                omnibusPriceManagement=OmnibusPriceManagementEnum.AUTOMATIC,
                omnibusPriceRetail=100.0,
                omnibusPriceWholesale=80.0
            ),
            shops=[]
        )
        assert model.ident.type == IdentTypeEnum.ID


class TestProductsOmnibusModel:
    def test_valid(self):
        model = ProductsOmnibusModel(
            ident=IdentModel(
                type=IdentTypeEnum.ID,
                value="123"
            ),
            sizes=[],
            omnibusPrices=OmnibusPricesModel(
                omnibusPriceManagement=OmnibusPriceManagementEnum.MANUAL,
                omnibusPriceRetail=100.0,
                omnibusPriceWholesale=80.0
            ),
            shops=[]
        )
        assert model.ident.value == "123"


# --- Tests for Opinions DTOs
class TestClientsOpinionsModel:
    def test_valid(self):
        model = ClientsOpinionsModel(
            type=TypeEnum.TEXT,
            value="John Doe",
            name="John",
            email="john@example.com"
        )
        assert model.type == TypeEnum.TEXT


class TestProductsModel:
    def test_valid(self):
        model = ProductsModel(
            type=TypeProductsEnum.ID,
            value="123"
        )
        assert model.type == TypeProductsEnum.ID


class TestOpinionsPostModel:
    def test_valid(self):
        model = OpinionsPostModel(
            createDate="2023-01-01",
            confirmed=True,
            rating="5",
            content="Great product!",
            language="en",
            picture="http://example.com/pic.jpg",
            shopId=1,
            host="example.com",
            clients=ClientsOpinionsModel(
                type=TypeEnum.TEXT,
                value="John",
                name="John",
                email="john@example.com"
            ),
            scorePositive=10,
            scoreNegative=0,
            products=ProductsModel(
                type=TypeProductsEnum.ID,
                value="123"
            ),
            orderSerialNumber=1,
            shopAnswer="Thank you!",
            opinionConfirmedByPurchase=True
        )
        assert model.rating == "5"
        assert model.scorePositive == 10

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            OpinionsPostModel(
                createDate="2023-01-01",
                confirmed=True,
                rating="5",
                content="Great product!",
                language="en",
                picture="http://example.com/pic.jpg",
                shopId=0,
                host="example.com",
                clients=ClientsOpinionsModel(
                    type=TypeEnum.TEXT,
                    value="John",
                    name="John",
                    email="john@example.com"
                ),
                scorePositive=10,
                scoreNegative=0,
                products=ProductsModel(
                    type=TypeProductsEnum.ID,
                    value="123"
                ),
                orderSerialNumber=1,
                shopAnswer="Thank you!",
                opinionConfirmedByPurchase=True
            )


class TestOpinionGetModel:
    def test_valid(self):
        model = OpinionGetModel(
            id=1,
            language="en",
            confirmed=True,
            host="example.com",
            shopId=1
        )
        assert model.id == 1

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            OpinionGetModel(
                id=0,
                language="en",
                confirmed=True,
                host="example.com",
                shopId=1
            )


class TestProductsOpinionsGetModel:
    def test_valid(self):
        model = ProductsOpinionsGetModel(
            type=TypeProductsGetEnum.ID,
            value="123"
        )
        assert model.type == TypeProductsGetEnum.ID


class TestClientsGetModel:
    def test_valid(self):
        model = ClientsGetModel(
            type=TypeEnum.TEXT,
            value="John"
        )
        assert model.value == "John"


class TestScorePositiveGetModel:
    def test_valid(self):
        model = ScorePositiveGetModel(**{"from":5, "to":10})
        assert model.from_ == 5
        assert model.to == 10

    def test_invalid_from_zero(self):
        with pytest.raises(ValidationError):
            ScorePositiveGetModel(**{"from":0, "to":10})


class TestScoreNegativeGetModel:
    def test_valid(self):
        model = ScoreNegativeGetModel(**{"from":1, "to":5})
        assert model.from_ == 1


class TestDateRangeGetModel:
    def test_valid(self):
        model = DateRangeGetModel(
            begin="2023-01-01",
            end="2023-12-31"
        )
        assert model.begin == "2023-01-01"
        assert model.end == "2023-12-31"
