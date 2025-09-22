from typing import List, Any
from src.idosell._common import BooleanStrLongEnum, BooleanStrShortEnum
from src.idosell.crm._common import BalanceModel, BalanceOperationTypeEnum, ClientTypeEnum
from src.idosell.crm.clients import (
    GetBalance as CrmClientsGetBalance, Get as CrmClientsGet, OperationClientsEnum,
    PostBalance as CrmClientsPostBalance, Post as CrmClientsPost, PostBalanceCrmClientsParamsModel, PostCrmClientsClientsModel, PostCrmClientsParamsModel, Put as CrmClientsPut, PutCrmClientsClientsModel, PutCrmClientsParamsModel, SettingsPostModel, SettingsPostPutModel
)
from src.idosell.crm.crm import Search as CrmCrmSearch, PostParamsSearchModel
from src.idosell.crm.deliveryaddress import (
    ClientDeliveryAddressModel,
    ClientSettingsDeliveryAddressModel,
    ClientsDeliveryAddressPostModel,
    ClientsDeliveryAddressPutModel,
    Delete as CrmDeliveryaddressDelete,
    DeleteCrmDeliveryaddressParamsModel,
    Get as CrmDeliveryaddressGet,
    Post as CrmDeliveryaddressPost,
    PostCrmDeliveryaddressParamsModel, Put as CrmDeliveryaddressPut,
    PutCrmDeliveryaddressParamsModel
)
from src.idosell.crm.discounts import (
    DeleteGroups as CrmDiscountsDeleteGroups, DeleteGroupsCrmDiscountsParamsModel, DeleteGroupsProducts as CrmDiscountsDeleteGroupsProducts, DeleteGroupsProductsCrmDiscountsParamsModel, DeleteRebatesCard as CrmDiscountsDeleteRebatesCard, DeleteRebatesCode as CrmDiscountsDeleteRebatesCode, CategoriesModel,
    GetGroupsClients as CrmDiscountsGetGroupsClients, GetGroups as CrmDiscountsGetGroups, MenuItemsModel,
    PostGroups as CrmDiscountsPostGroups, PostGroupsCrmDiscountsParamsModel, PostRebatesCard as CrmDiscountsPostRebatesCard, PostRebatesCode as CrmDiscountsPostRebatesCode, ProducersModel, ProductsDiscountsModel,
    PutGroups as CrmDiscountsPutGroups, PutGroupsCrmDiscountsParamsModel, PutGroupsProducts as CrmDiscountsPutGroupsProducts, PutGroupsProductsCrmDiscountsParamsModel, PutRebatesBlockCard as CrmDiscountsPutRebatesBlockCard, PutRebatesUnblockCard as CrmDiscountsPutRebatesUnblockCard, SeriesModel,
)
from src.idosell.crm.externalcode import Put as CrmExternalCodePut, PutCrmExternalcodeParamsModel
from src.idosell.crm.giftcards import (
    Delete as CrmGiftcardsDelete, DeleteCrmGiftcardsParamsModel,
    GetTypes as CrmGiftcardsGetTypes,
    GiftCardDeleteModel,
    GiftCardPostModel,
    GiftCardPutModel,
    PostCrmGiftcardsParamsModel,
    PutBlockCrmGiftcardsParamsModel,
    PutCrmGiftcardsParamsModel,
    PutUnblockCrmGiftcardsParamsModel, Search as CrmGiftcardsSearch,
    Post as CrmGiftcardsPost, PutBlock as CrmGiftcardsPutBlock, Put as CrmGiftcardsPut, PutUnblock as CrmGiftcardsPutUnblock,
    SearchCrmGiftcardsParamsModel,
)
from src.idosell.crm.membership import GetCards as CrmMembershipGetCards, MembershipCardsModel, PutCards as CrmMembershipPutCards, PutCardsCrmMembershipParamsModel, SettingsModel, ErrorModel, FaultCodeEnum
from src.idosell.crm.newsletter import SearchEmail as CrmNewsletterSearchEmail, SearchEmailCrmNewsletterParamsModel, SearchSmsCrmNewsletterParamsModel, SearchSms as CrmNewsletterSearchSms
from src.idosell.crm.payeraddress import (
    Delete as CrmPayeraddressDelete,
    DeleteParamsPayersAddressModel,
    Get as CrmPayeraddressGet,
    PayerModel,
    Post as CrmPayeraddressPost,
    PostParamsPayersAddressModel,
    PostPayersModel, Put as CrmPayeraddressPut,
    PutParamsPayersAddressModel,
    PutPayersModel
)
from src.idosell.crm.pricelists import (
    CategoriesPriceListsModel,
    Delete as CrmPricelistsDelete,
    DeleteCrmPricelistsParamsModel,
    GetClients as CrmPricelistsGetClients, Get as CrmPricelistsGet, GetProducts as CrmPricelistsGetProducts,
    MenuItemsPriceListsModel,
    Post as CrmPricelistsPost,
    PostCrmPricelistsParamsModel,
    ProducersPriceListsModel,
    ProductsModel,
    PutClients as CrmPricelistsPutClients, Put as CrmPricelistsPut,
    PutClientsCrmPricelistsParamsModel,
    PutCrmPricelistsParamsModel, PutProducts as CrmPricelistsPutProducts,
    PutProductsCrmPricelistsParamsModel, PutRename as CrmPricelistsPutRename,
    PutRenameCrmPricelistsParamsModel,
    SeriesPriceListsModel
)
from src.idosell.crm.profitpoints import Get as CrmProfitpointsGet
from src.idosell.crm.provincelist import Get as CrmProvincelistGet
from src.idosell.crm.tags import (
    ClientTagsModel, DeleteClear as CrmTagsDeleteClear, Delete as CrmTagsDelete, DeleteClearCrmTagsParamsModel, DeleteCrmTagsParamsModel,
    Get as CrmTagsGet,
    Post as CrmTagsPost, PostCrmTagsParamsModel, Put as CrmTagsPut, PutCrmTagsParamsModel, OperationTagsEnum
)
from src.idosell.crm.vouchers import (
    Delete as CrmVouchersDelete,
    DeleteCrmVouchersParamsModel,
    GetTypes as CrmVouchersGetTypes, Get as CrmVouchersGet,
    Post as CrmVouchersPost,
    PostCrmVouchersParamsModel, PutBlock as CrmVouchersPutBlock,
    PutBlockCrmVouchersParamsModel,
    PutCrmVouchersParamsModel, PutUnblock as CrmVouchersPutUnblock, Put as CrmVouchersPut,
    PutUnblockCrmVouchersParamsModel,
    StatusEnum,
    VoucherModel,
    VoucherPostModel,
    VoucherPutModel
)

from src.idosell.crm.giftcards import GiftCardModel

crm_delete: List[Any] = [ # type: ignore
    CrmDeliveryaddressDelete(
        params = DeleteCrmDeliveryaddressParamsModel(
            clients = ClientDeliveryAddressModel(
                clientLogin = "Customer's login",
                clientCodeExternal = "External system code",
                clientDeliveryAddressId = 1
            )
        )
    ),
    CrmDiscountsDeleteGroups(
        params = DeleteGroupsCrmDiscountsParamsModel(discountGroupId = 1)
    ),
    CrmDiscountsDeleteGroupsProducts(
        params = DeleteGroupsProductsCrmDiscountsParamsModel(discountGroupId = 1) # type: ignore
    ),
    CrmDiscountsDeleteRebatesCard(campaign_id = 1), # type: ignore
    CrmDiscountsDeleteRebatesCode(campaign_id = 1), # type: ignore
    CrmGiftcardsDelete(
        params = DeleteCrmGiftcardsParamsModel(
            giftCards = [GiftCardDeleteModel(id = 1, number = '1234')]
        ),
    ),
    CrmPayeraddressDelete(
        params = DeleteParamsPayersAddressModel(
            payers = [PayerModel(
                clientId = 1,
                payerAddressId = 1
            )]
        )
    ),
    CrmPricelistsDelete(
        params = DeleteCrmPricelistsParamsModel(priceListId = 1)
    ),
    CrmTagsDeleteClear(
        params = DeleteClearCrmTagsParamsModel(clientId = 1)
    ),
    CrmTagsDelete(
        params = [DeleteCrmTagsParamsModel(clientId = 1, tagId = 1)]
    ),
    CrmVouchersDelete(
        params = DeleteCrmVouchersParamsModel(vouchers=[VoucherModel(id=1, number='1234')]) # type: ignore
    ),
]
crm_get: List[Any] = [ # type: ignore
    CrmClientsGetBalance(), # type: ignore
    CrmClientsGet(), # type: ignore
    CrmDeliveryaddressGet(), # type: ignore
    CrmDiscountsGetGroupsClients(
        discountGroupId = 1
    ),
    CrmDiscountsGetGroups(), # type: ignore
    CrmGiftcardsGetTypes(), # type: ignore
    CrmMembershipGetCards(), # type: ignore
    CrmPayeraddressGet(), # type: ignore
    CrmPricelistsGetClients(), # type: ignore
    CrmPricelistsGet(), # type: ignore
    CrmPricelistsGetProducts(), # type: ignore
    CrmProfitpointsGet(), # type: ignore
    CrmProvincelistGet(), # type: ignore
    CrmTagsGet(), # type: ignore
    CrmVouchersGetTypes(), # type: ignore
    CrmVouchersGet(), # type: ignore
]

crm_post: List[Any] = [ # type: ignore
    CrmClientsPostBalance(
        params = PostBalanceCrmClientsParamsModel(
            clientId = 1,
            operation = OperationClientsEnum.ADD,
            balance = 0,
            currency = 'PLN',
            note = 'Note',
            prepaidId = 1
        ),
        settings = SettingsPostPutModel(
            clientSettingSendMail = False,
            clientSettingSendSms = False
        )
    ),
    CrmClientsPost(
        params = PostCrmClientsParamsModel(
            clients = [PostCrmClientsClientsModel(
                login="test_login",
                code_extern="test_code",
                email="test@example.com",
                firstname="Test",
                lastname="User",
                street="Test Street 1",
                zipcode="00-000",
                city="Test City",
                country_code="PL",
                province_code="MAZ",
                password="password123",
                birth_date="1990-01-01",
                phone="123456789",
                company="",
                vat_number="",
                wholesaler=False,
                client_type=ClientTypeEnum.PERSON,
                language="pol",
                shops=[1],
                block_autosigning_to_shops=False,
                currency="PLN",
                delivery_dates=[],
                external_balance_value=0.0,
                external_trade_credit_limit_value=0.0,
                email_newsletter=BooleanStrShortEnum.YES,
                sms_newsletter=BooleanStrShortEnum.YES,
                client_group=1,
                request_reference="test_ref",
                newsletter_email_approvals=[],
                newsletter_sms_approvals=[],
                block_group_auto_assignment=False
            )]
        ),
        settings = SettingsPostModel(
            send_mail = False,
            send_sms = False
        )
    ),
    CrmDeliveryaddressPost(
        params = PostCrmDeliveryaddressParamsModel(
            clients = [ClientsDeliveryAddressPostModel(
                clientLogin="test_login",
                clientCodeExternal="test_code",
                shopsIds=[1],
                currencyId="PLN",
                clientDeliveryAddressFirstName="Test",
                clientDeliveryAddressLastName="User",
                clientDeliveryAddressAdditional="Additional info",
                clientDeliveryAddressPhone1="123456789",
                clientDeliveryAddressCity="Test City",
                clientDeliveryAddressStreet="Test Street 1",
                clientDeliveryAddressRegionId="Region",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="00-000",
                clientDeliveryAddressCountry="PL"
            )],
            clientsSettings = ClientSettingsDeliveryAddressModel(
                clientSettingSendMail=False,
                clientSettingSendSms=False
            )
        )
    ),
    CrmDiscountsPostGroups(
        params = PostGroupsCrmDiscountsParamsModel(
            discountGroupName = 'Discount group name'
        )
    ),
    CrmDiscountsPostRebatesCard(
        campaign_id = 1,
        card_number = 'Card number'
    ),
    CrmDiscountsPostRebatesCode(
        campaign_id = 1,
        code_number = 'Code'
    ),
    CrmGiftcardsPost(
        params = PostCrmGiftcardsParamsModel(
            giftCards = [GiftCardPostModel(
                number = '123456789',
                pin = '1234',
                name = 'Test Gift Card',
                expirationDate = '2025-12-31',
                balanceOperationType = BalanceOperationTypeEnum.ADD,
                balance = BalanceModel(amount = 100.0, currency = 'PLN'),
                shops = [1],
                note = 'Test note',
                typeId = 1
            )]
        )
    ),
    CrmPayeraddressPost(
        params = PostParamsPayersAddressModel(
            payers = [PostPayersModel(
                clientId = 1,
                payerAddressFirstName = "Test",
                payerAddressLastName = "User",
                payerAddressFirm = "Test Company",
                payerAddressNip = "1234567890",
                payerAddressStreet = "Test Street 1",
                payerAddressZipCode = "00-000",
                payerAddressCity = "Test City",
                payerAddressCountryId = "PL",
                payerAddressPhone = "123456789"
            )]
        )
    ),
    CrmPricelistsPost(
        params = PostCrmPricelistsParamsModel(
            priceListName = 'Name of individual price list',
            onlyOrderProductsWithManuallySetPrices = BooleanStrLongEnum.NO,
            onlySeeProductsWithManuallySetPrices = BooleanStrLongEnum.NO
        )
    ),
    CrmTagsPost(
        params = PostCrmTagsParamsModel(
            clientId = 1,
            tagName = 'Tag name',
            tagValue = 1
        )
    ),
    CrmVouchersPost(
        params = PostCrmVouchersParamsModel(
            vouchers = [VoucherPostModel(
                number = 'TEST_VOUCHER_123',
                name = 'Test Voucher',
                expirationDate = '2025-12-31',
                balance = BalanceModel(amount = 100.0, currency = 'PLN'),
                shops = [1],
                note = 'Test voucher note',
                typeId = 1
            )]
        )
    ),
]

crm_put: List[Any] = [ # type: ignore
    CrmClientsPut(
        params = PutCrmClientsParamsModel(
            clients = [PutCrmClientsClientsModel(
                clientLogin="test_login",
                clientEmail="test@example.com",
                clientFirstName="Test",
                clientLastName="User",
                clientStreet="Test Street 1",
                clientZipCode="00-000",
                clientCity="Test City",
                clientCountryId="PL",
                clientProvinceId="MAZ",
                clientPassword="password123",
                clientBirthDate="1990-01-01",
                clientPhone1="123456789",
                clientFirm="",
                clientNip="",
                clientIsWholesaler=False,
                clientType=ClientTypeEnum.PERSON,
                langId="pl",
                blockLoginToOtherShops=False,
                shopsIds=[1],
                currencyId="PLN",
                clientCodeExternal="test_code",
                deliveryDates=[],
                clientBalanceAmountExternal=0.0,
                clientTradeCreditLimitExternal=0.0,
                newsletterEmailApproval=True,
                newsletterSmsApproval=True,
                clientGroupDiscountNumber=1,
                requestReference="test_ref",
                newsletterEmailApprovalsData=[],
                newsletterSmsApprovalsData=[],
                clientActive=True,
                numberOfDaysToPay=30,
                affiliateLogin="",
                clientNote="Test note"
            )]
        ),
        clientsSettings = SettingsPostPutModel(
            clientSettingSendMail = False,
            clientSettingSendSms = False
        )
    ),
    CrmDeliveryaddressPut(
        params = PutCrmDeliveryaddressParamsModel(
            clients = [ClientsDeliveryAddressPutModel(
                clientLogin="test_login",
                clientCodeExternal="test_code",
                shopsIds=[1],
                currencyId="PLN",
                clientDeliveryAddressFirstName="Test",
                clientDeliveryAddressLastName="User",
                clientDeliveryAddressAdditional="Additional info",
                clientDeliveryAddressPhone1="123456789",
                clientDeliveryAddressCity="Test City",
                clientDeliveryAddressStreet="Test Street 1",
                clientDeliveryAddressRegionId="Region",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="00-000",
                clientDeliveryAddressCountry="PL",
                clientDeliveryAddressId="123"
            )],
            clientsSettings = ClientSettingsDeliveryAddressModel(
                clientSettingSendMail=False,
                clientSettingSendSms=False
            )
        )
    ),
    CrmDiscountsPutGroups(
        params = PutGroupsCrmDiscountsParamsModel(
            discountGroupId = 1,
            discountGroupName = 'Discount group name'
        )
    ),
    CrmDiscountsPutGroupsProducts(
        params = PutGroupsProductsCrmDiscountsParamsModel(
            discountGroupId = 1,
            products = [ProductsDiscountsModel(id=1, price=10.0, currency="PLN")],
            producers = [ProducersModel(id=1, price=10.0, currency="PLN")],
            series = [SeriesModel(id=1, price=10.0, currency="PLN")],
            categories = [CategoriesModel(id=1, price=10.0, currency="PLN")],
            menuItems = [MenuItemsModel(id=1, price=10.0, currency="PLN")]
        )
    ),
    CrmDiscountsPutRebatesBlockCard(
        card_number = 'Card number'
    ),
    CrmDiscountsPutRebatesUnblockCard(
        card_number = 'Card number'
    ),
    CrmExternalCodePut(
        params = PutCrmExternalcodeParamsModel(
            client_id = 1,
            client_login = 'Customer login (non-empty)',
            code_extern = 'External system code (non-empty)'
        )
    ),
    CrmGiftcardsPutBlock(
        params = PutBlockCrmGiftcardsParamsModel(
            giftCards = [GiftCardModel(id=1, number='1234', pin='1234')]
        )
    ),
    CrmGiftcardsPut(
        params = PutCrmGiftcardsParamsModel(
            giftCards = [GiftCardPutModel(
                id = 1,
                number = '123456789',
                pin = '1234',
                name = 'Test Gift Card',
                expirationDate = '2025-12-31',
                balanceOperationType = BalanceOperationTypeEnum.ADD,
                balance = BalanceModel(amount = 100.0, currency = 'PLN'),
                shops = [1],
                note = 'Test note'
            )]
        )
    ),
    CrmGiftcardsPutUnblock(
        params = PutUnblockCrmGiftcardsParamsModel(
            giftCards = [GiftCardModel(id=1, number='1234', pin='1234')]
        )
    ),
    CrmMembershipPutCards(
        params = PutCardsCrmMembershipParamsModel(
            id = 1,
            login = 'Customer login (non-empty)',
            membership_cards = [MembershipCardsModel(
                ordinal_number = 1,
                card_type = 1,
                number = '123456',
                pin = 1234,
                creation_date = '2023-01-01',
                deactivate = False,
                set_rebate_group = True,
                errors = ErrorModel(
                    faultCode = FaultCodeEnum.OPERATION_WAS_SUCCESSFUL,
                    faultString = 'Success'
                )
            )],
            settings = SettingsModel(
                sendMail = True,
                sendSms = False
            )
        )
    ),
    CrmPayeraddressPut(
        params = PutParamsPayersAddressModel(
            payers = [PutPayersModel(
                clientId = "1",
                payerAddressId = "1",
                payerAddressFirstName = "Test",
                payerAddressLastName = "User",
                payerAddressFirm = "Test Company",
                payerAddressNip = "1234567890",
                payerAddressStreet = "Test Street 1",
                payerAddressZipCode = "00-000",
                payerAddressCity = "Test City",
                payerAddressCountryId = "PL",
                payerAddressPhone = "123456789"
            )]
        )
    ),
    CrmPricelistsPutClients(
        params = PutClientsCrmPricelistsParamsModel(
            priceListId = 1,
            clientsIds = [1]
        )
    ),
    CrmPricelistsPut(
        params = PutCrmPricelistsParamsModel(
            priceListId = 1,
            priceListName = 'Name of individual price list',
            onlyOrderProductsWithManuallySetPrices = BooleanStrLongEnum.NO,
            onlySeeProductsWithManuallySetPrices = BooleanStrLongEnum.NO
        )
    ),
    CrmPricelistsPutProducts(
        params = PutProductsCrmPricelistsParamsModel(
            priceListId = 1,
            products = [ProductsModel(productId=1, price=10.0, currencyId='PLN')],
            producers = [ProducersPriceListsModel(producerId=1, price=10.0, currencyId='PLN')],
            series = [SeriesPriceListsModel(seriesId=1, price=10.0, currencyId='PLN')],
            categories = [CategoriesPriceListsModel(categoryId=1, price=10.0, currencyId='PLN')],
            menuItems = [MenuItemsPriceListsModel(menuItemId=1, price=10.0, currencyId='PLN')]
        )
    ),
    CrmPricelistsPutRename(
        params = PutRenameCrmPricelistsParamsModel(
            priceListName = 'Name of individual price list',
            priceListId = 1
        )
    ),
    CrmTagsPut(
        params = PutCrmTagsParamsModel(
            clientId = 1,
            clientTags = [ClientTagsModel(tagId=1, operation=OperationTagsEnum.ADD, tagValue=1)]
        )
    ),
    CrmVouchersPutBlock(
        params = PutBlockCrmVouchersParamsModel(
            id = 1,
            number = 'Number'
        )
    ),
    CrmVouchersPutUnblock(
        params = PutUnblockCrmVouchersParamsModel(
            vouchers = [VoucherModel(id=1, number='1234')]
        )
    ),
    CrmVouchersPut(
        params = PutCrmVouchersParamsModel(
            vouchers = [VoucherPutModel(
                id=1,
                number='TEST_VOUCHER_123',
                name='Test Voucher',
                expirationDate='2025-12-31',
                balance=BalanceModel(amount=100.0, currency='PLN'),
                shops=[1],
                note='Test voucher note',
                balanceOperationType=BalanceOperationTypeEnum.ADD,
                status=StatusEnum.UNUSED
            )]
        )
    ),
]

crm_search: List[Any] = [ # type: ignore
    CrmCrmSearch(params = PostParamsSearchModel(clientCodeExternal = 'blah')), # type: ignore
    CrmGiftcardsSearch(
        params = SearchCrmGiftcardsParamsModel(
            giftCards=[
                GiftCardModel(id=1,) # type: ignore
            ]
        )
    ),
    CrmNewsletterSearchEmail(
        params = SearchEmailCrmNewsletterParamsModel() # type: ignore
    ),
    CrmNewsletterSearchSms(
        params = SearchSmsCrmNewsletterParamsModel() # type: ignore
    ),
]
