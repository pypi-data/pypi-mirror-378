import pytest
from pydantic import ValidationError

from src.idosell.crm.clients import (
    BalanceOperationClientsEnum, OperationClientsEnum, ReturnElementsClientsEnum,
    ClientLastPurchaseDateModel, ClientLastModificationDateModel, DeliveryDateModel,
    LastPurchaseDateModel, NewsletterEmailApprovalModel, NewsletterSmsApprovalModel,
    PostCrmClientsClientsModel, PutCrmClientsClientsModel, PostBalanceCrmClientsParamsModel,
    PostCrmClientsParamsModel, PutCrmClientsParamsModel, SettingsPostModel, SettingsPostPutModel,
    GetBalance, PostBalance, Get, Post, Put
)
from src.idosell.crm._common import ClientTypeEnum
from src.idosell._common import BooleanStrShortEnum


# --- Tests for Enums
class TestBalanceOperationClientsEnum:
    def test_valid_values(self):
        assert BalanceOperationClientsEnum.ADD == 'add'
        assert BalanceOperationClientsEnum.REMOVE == 'remove'

class TestOperationClientsEnum:
    def test_valid_values(self):
        assert OperationClientsEnum.ADD == 'add'
        assert OperationClientsEnum.REMOVE == 'remove'

class TestReturnElementsClientsEnum:
    def test_valid_values(self):
        assert ReturnElementsClientsEnum.CLIENTID == 'clientId'
        assert ReturnElementsClientsEnum.CLIENTEMAIL == 'clientEmail'


# --- Tests for DTOs
class TestClientLastPurchaseDateModel:
    def test_valid(self):
        dto = ClientLastPurchaseDateModel(
            clientLastPurchaseDateBegin="2023-01-01",
            clientLastPurchaseDateEnd="2023-12-31"
        )
        assert dto.clientLastPurchaseDateBegin == "2023-01-01"

class TestClientLastModificationDateModel:
    def test_valid(self):
        dto = ClientLastModificationDateModel(
            clientsLastModificationDateBegin="2023-01-01",
            clientsLastModificationDateEnd="2023-12-31"
        )
        assert dto.clientsLastModificationDateBegin == "2023-01-01"

class TestDeliveryDateModel:
    def test_valid(self):
        dto = DeliveryDateModel(
            deliveryDate="2023-01-01",
            deliveryHours=["08:00"]
        )
        assert dto.deliveryDate == "2023-01-01"

class TestLastPurchaseDateModel:
    def test_valid(self):
        dto = LastPurchaseDateModel(
            **{"from": "2023-01-01"},
            to="2023-12-31"
        )
        assert dto.model_dump(by_alias=True)["from"] == "2023-01-01"

class TestNewsletterEmailApprovalModel:
    def test_valid(self):
        dto = NewsletterEmailApprovalModel(
            approval=BooleanStrShortEnum.YES,
            shop_id=1
        )
        assert dto.shop_id == 1

class TestNewsletterSmsApprovalModel:
    def test_valid(self):
        dto = NewsletterSmsApprovalModel(
            approval=BooleanStrShortEnum.NO,
            shop_id=2
        )
        assert dto.shop_id == 2

class TestPostCrmClientsClientsModel:
    def test_valid(self):
        dto = PostCrmClientsClientsModel(
            login="user1",
            code_extern="EXT123",
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            street="Street",
            zipcode="12345",
            city="City",
            country_code="US",
            province_code="CA",
            password="password123",
            birth_date="1990-01-01",
            phone="123456789",
            company="",
            vat_number="",
            wholesaler=False,
            client_type=ClientTypeEnum.PERSON,
            language="en",
            shops=[1],
            block_autosigning_to_shops=False,
            currency="USD",
            delivery_dates=["2023-01-01"],
            external_balance_value=0.0,
            external_trade_credit_limit_value=0.0,
            email_newsletter=BooleanStrShortEnum.YES,
            sms_newsletter=BooleanStrShortEnum.NO,
            client_group=1,
            request_reference="ref",
            newsletter_email_approvals=[],
            newsletter_sms_approvals=[],
            block_group_auto_assignment=False
        )
        assert dto.login == "user1"
        assert dto.email == "test@example.com"
        assert dto.external_balance_value == 0.0

    def test_invalid_client_group_zero(self):
        # Test a constraint, like ge=1 for client_group
        with pytest.raises(ValidationError):
            PostCrmClientsClientsModel(
                login="user1",
                code_extern="EXT123",
                email="test@example.com",
                firstname="John",
                lastname="Doe",
                street="Street",
                zipcode="12345",
                city="City",
                country_code="US",
                province_code="CA",
                password="password123",
                birth_date="1990-01-01",
                phone="123456789",
                company="",
                vat_number="",
                wholesaler=False,
                client_type=ClientTypeEnum.PERSON,
                language="en",
                shops=[1],
                block_autosigning_to_shops=False,
                currency="USD",
                delivery_dates=["2023-01-01"],
                external_balance_value=0.0,
                external_trade_credit_limit_value=0.0,
                email_newsletter=BooleanStrShortEnum.YES,
                sms_newsletter=BooleanStrShortEnum.NO,
                client_group=0,  # Invalid
                request_reference="ref",
                newsletter_email_approvals=[],
                newsletter_sms_approvals=[],
                block_group_auto_assignment=False
            )

class TestPutCrmClientsClientsModel:
    def test_valid(self):
        dto = PutCrmClientsClientsModel(
            clientLogin="user1",
            clientEmail="test@example.com",
            clientFirstName="John",
            clientLastName="Doe",
            clientStreet="Street",
            clientZipCode="12345",
            clientCity="City",
            clientCountryId="US",
            clientProvinceId="CA",
            clientPassword="password123",
            clientBirthDate="1990-01-01",
            clientPhone1="123456789",
            clientFirm="",
            clientNip="",
            clientIsWholesaler=False,
            clientType=ClientTypeEnum.PERSON,
            langId="en",
            blockLoginToOtherShops=False,
            shopsIds=[1],
            currencyId="USD",
            clientCodeExternal="EXT123",
            deliveryDates=[DeliveryDateModel(deliveryDate="2023-01-01", deliveryHours=["08:00"])],
            clientBalanceAmountExternal=0.0,
            clientTradeCreditLimitExternal=0.0,
            newsletterEmailApproval=True,
            newsletterSmsApproval=False,
            clientGroupDiscountNumber=1,
            requestReference="ref",
            newsletterEmailApprovalsData=[],
            newsletterSmsApprovalsData=[],
            clientActive=True,
            numberOfDaysToPay=1,
            affiliateLogin="",
            clientNote=""
        )
        assert dto.clientLogin == "user1"
        assert dto.clientEmail == "test@example.com"
        assert dto.clientBalanceAmountExternal == 0.0

    def test_invalid_client_group_zero(self):
        with pytest.raises(ValidationError):
            PutCrmClientsClientsModel(
                clientLogin="user1",
                clientEmail="test@example.com",
                clientFirstName="John",
                clientLastName="Doe",
                clientStreet="Street",
                clientZipCode="12345",
                clientCity="City",
                clientCountryId="US",
                clientProvinceId="CA",
                clientPassword="password123",
                clientBirthDate="1990-01-01",
                clientPhone1="123456789",
                clientFirm="",
                clientNip="",
                clientIsWholesaler=False,
                clientType=ClientTypeEnum.PERSON,
                langId="en",
                blockLoginToOtherShops=False,
                shopsIds=[1],
                currencyId="USD",
                clientCodeExternal="EXT123",
                deliveryDates=[DeliveryDateModel(deliveryDate="2023-01-01", deliveryHours=["08:00"])],
                clientBalanceAmountExternal=0.0,
                clientTradeCreditLimitExternal=0.0,
                newsletterEmailApproval=True,
                newsletterSmsApproval=False,
                clientGroupDiscountNumber=0,  # Invalid
                requestReference="ref",
                newsletterEmailApprovalsData=[],
                newsletterSmsApprovalsData=[],
                clientActive=True,
                numberOfDaysToPay=1,
                affiliateLogin="",
                clientNote=""
            )

class TestPostBalanceCrmClientsParamsModel:
    def test_valid(self):
        dto = PostBalanceCrmClientsParamsModel(
            clientId=1,
            operation=OperationClientsEnum.ADD,
            balance=100.0,
            currency="PLN",
            note="Test note",
            prepaidId=123
        )
        assert dto.clientId == 1

class TestPostCrmClientsParamsModel:
    def test_valid(self):
        dto = PostCrmClientsParamsModel(
            clients=[
                PostCrmClientsClientsModel(
                    login="user1",
                    code_extern="EXT1",
                    email="test@example.com",
                    firstname="John",
                    lastname="Doe",
                    street="Street",
                    zipcode="12345",
                    city="City",
                    country_code="US",
                    province_code="CA",
                    password="password123",
                    birth_date="1990-01-01",
                    phone="123456789",
                    company="",
                    vat_number="",
                    wholesaler=False,
                    client_type=ClientTypeEnum.PERSON,
                    language="en",
                    shops=[1],
                    block_autosigning_to_shops=False,
                    currency="USD",
                    delivery_dates=["2023-01-01"],
                    external_balance_value=0.0,
                    external_trade_credit_limit_value=0.0,
                    email_newsletter=BooleanStrShortEnum.YES,
                    sms_newsletter=BooleanStrShortEnum.NO,
                    client_group=1,
                    request_reference="ref1",
                    newsletter_email_approvals=[],
                    newsletter_sms_approvals=[],
                    block_group_auto_assignment=False
                )
            ]
        )
        assert len(dto.clients) == 1
        assert dto.clients[0].login == "user1"

class TestPutCrmClientsParamsModel:
    def test_valid(self):
        dto = PutCrmClientsParamsModel(
            clients=[
                PutCrmClientsClientsModel(
                    clientLogin="user1",
                    clientEmail="test@example.com",
                    clientFirstName="John",
                    clientLastName="Doe",
                    clientStreet="Street",
                    clientZipCode="12345",
                    clientCity="City",
                    clientCountryId="US",
                    clientProvinceId="CA",
                    clientPassword="password123",
                    clientBirthDate="1990-01-01",
                    clientPhone1="123456789",
                    clientFirm="",
                    clientNip="",
                    clientIsWholesaler=False,
                    clientType=ClientTypeEnum.PERSON,
                    langId="en",
                    blockLoginToOtherShops=False,
                    shopsIds=[1],
                    currencyId="USD",
                    clientCodeExternal="EXT1",
                    deliveryDates=[DeliveryDateModel(deliveryDate="2023-01-01", deliveryHours=["08:00"])],
                    clientBalanceAmountExternal=0.0,
                    clientTradeCreditLimitExternal=0.0,
                    newsletterEmailApproval=True,
                    newsletterSmsApproval=False,
                    clientGroupDiscountNumber=1,
                    requestReference="ref1",
                    newsletterEmailApprovalsData=[],
                    newsletterSmsApprovalsData=[],
                    clientActive=True,
                    numberOfDaysToPay=1,
                    affiliateLogin="",
                    clientNote=""
                )
            ]
        )
        assert len(dto.clients) == 1
        assert dto.clients[0].clientLogin == "user1"

class TestSettingsPostModel:
    def test_valid(self):
        dto = SettingsPostModel(
            send_mail=False,
            send_sms=True
        )
        assert not dto.send_mail

class TestSettingsPostPutModel:
    def test_valid(self):
        dto = SettingsPostPutModel(
            clientSettingSendMail=True,
            clientSettingSendSms=False
        )
        assert dto.clientSettingSendMail


# --- Tests for Endpoints
class TestGetBalance:
    def test_instantiate_minimal(self):
        dto = GetBalance()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestPostBalance:
    def test_instantiate(self):
        dto = PostBalance(
            params=PostBalanceCrmClientsParamsModel(
                clientId=1,
                operation=OperationClientsEnum.ADD,
                balance=100.0,
                currency="PLN",
                note="Test",
                prepaidId=123
            ),
            settings=SettingsPostPutModel(
                clientSettingSendMail=True,
                clientSettingSendSms=False
            )
        )
        assert dto.params.clientId == 1

class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCrmClientsParamsModel(
                clients=[
                    PostCrmClientsClientsModel(
                        login="user1",
                        code_extern="EXT1",
                        email="test@example.com",
                        firstname="John",
                        lastname="Doe",
                        street="Street",
                        zipcode="12345",
                        city="City",
                        country_code="US",
                        province_code="CA",
                        password="password123",
                        birth_date="1990-01-01",
                        phone="123456789",
                        company="",
                        vat_number="",
                        wholesaler=False,
                        client_type=ClientTypeEnum.PERSON,
                        language="en",
                        shops=[1],
                        block_autosigning_to_shops=False,
                        currency="USD",
                        delivery_dates=["2023-01-01"],
                        external_balance_value=0.0,
                        external_trade_credit_limit_value=0.0,
                        email_newsletter=BooleanStrShortEnum.YES,
                        sms_newsletter=BooleanStrShortEnum.NO,
                        client_group=1,
                        request_reference="ref1",
                        newsletter_email_approvals=[],
                        newsletter_sms_approvals=[],
                        block_group_auto_assignment=False
                    )
                ]
            ),
            settings=SettingsPostModel(
                send_mail=False,
                send_sms=True
            )
        )
        assert len(dto.params.clients) == 1
        assert dto.params.clients[0].login == "user1"

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCrmClientsParamsModel(
                clients=[
                    PutCrmClientsClientsModel(
                        clientLogin="user1",
                        clientEmail="test@example.com",
                        clientFirstName="John",
                        clientLastName="Doe",
                        clientStreet="Street",
                        clientZipCode="12345",
                        clientCity="City",
                        clientCountryId="US",
                        clientProvinceId="CA",
                        clientPassword="password123",
                        clientBirthDate="1990-01-01",
                        clientPhone1="123456789",
                        clientFirm="",
                        clientNip="",
                        clientIsWholesaler=False,
                        clientType=ClientTypeEnum.PERSON,
                        langId="en",
                        blockLoginToOtherShops=False,
                        shopsIds=[1],
                        currencyId="USD",
                        clientCodeExternal="EXT1",
                        deliveryDates=[DeliveryDateModel(deliveryDate="2023-01-01", deliveryHours=["08:00"])],
                        clientBalanceAmountExternal=0.0,
                        clientTradeCreditLimitExternal=0.0,
                        newsletterEmailApproval=True,
                        newsletterSmsApproval=False,
                        clientGroupDiscountNumber=1,
                        requestReference="ref1",
                        newsletterEmailApprovalsData=[],
                        newsletterSmsApprovalsData=[],
                        clientActive=True,
                        numberOfDaysToPay=1,
                        affiliateLogin="",
                        clientNote=""
                    )
                ]
            ),
            clientsSettings=SettingsPostPutModel(
                clientSettingSendMail=True,
                clientSettingSendSms=False
            )
        )
        assert len(dto.params.clients) == 1
        assert dto.params.clients[0].clientLogin == "user1"
