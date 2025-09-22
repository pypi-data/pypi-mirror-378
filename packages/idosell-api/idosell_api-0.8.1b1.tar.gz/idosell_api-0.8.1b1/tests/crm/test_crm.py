
from src.idosell.crm.crm import (
    ClientAffiliateProgramEnum, ClientHasLoyaltyCardEnum, SearchByShopEnum,
    ClientLastLoginDateModel, ClientLoyaltyCardModel, NewsletterEmailApprovalsDataModel,
    NewsletterSmsApprovalsDataModel, OrderSerialNumberRangeModel, OrderAddDateModel,
    OrderModel, PostParamsSearchModel, Search
)
from src.idosell._common import BooleanStrLongEnum
from src.idosell._common import BooleanStrShortEnum


# --- Tests for Enums
class TestClientAffiliateProgramEnum:
    def test_valid_values(self):
        assert ClientAffiliateProgramEnum.YES_VOUCHER == 'yes_voucher'
        assert ClientAffiliateProgramEnum.YES_CLIENTS == 'yes_clients'

class TestClientHasLoyaltyCardEnum:
    def test_valid_values(self):
        assert ClientHasLoyaltyCardEnum.YES_ACTIVE == 'yes_active'
        assert ClientHasLoyaltyCardEnum.YES_NOT_ACTIVE == 'yes_not_active'
        assert ClientHasLoyaltyCardEnum.NO == 'no'

class TestSearchByShopEnum:
    def test_valid_values(self):
        assert SearchByShopEnum.ONE_OF_SELECTED == 'one_of_selected'
        assert SearchByShopEnum.EXACTLY_SELECTED == 'exactly_selected'


# --- Tests for DTOs
class TestClientLastLoginDateModel:
    def test_valid(self):
        dto = ClientLastLoginDateModel(
            clientLastLoginDateBegin="2023-01-01",
            clientLastLoginDateEnd="2023-12-31"
        )
        assert dto.clientLastLoginDateBegin == "2023-01-01"

class TestClientLoyaltyCardModel:
    def test_valid_active(self):
        dto = ClientLoyaltyCardModel(
            clientHasLoyaltyCard=ClientHasLoyaltyCardEnum.YES_ACTIVE,
            clientLoyaltyCardId=1,
            clientLoyaltyCardNumber="CARD123"
        )
        assert dto.clientHasLoyaltyCard == ClientHasLoyaltyCardEnum.YES_ACTIVE

    def test_valid_no(self):
        dto = ClientLoyaltyCardModel(
            clientHasLoyaltyCard=ClientHasLoyaltyCardEnum.NO
        )
        assert dto.clientHasLoyaltyCard == ClientHasLoyaltyCardEnum.NO
        assert dto.clientLoyaltyCardId is None
        assert dto.clientLoyaltyCardNumber is None

class TestNewsletterEmailApprovalsDataModel:
    def test_valid(self):
        dto = NewsletterEmailApprovalsDataModel(
            inNewsletterEmailApproval=BooleanStrShortEnum.YES,
            shopId=1
        )
        assert dto.shopId == 1

class TestNewsletterSmsApprovalsDataModel:
    def test_valid(self):
        dto = NewsletterSmsApprovalsDataModel(
            inNewsletterSmsApproval=BooleanStrShortEnum.NO,
            shopId=2
        )
        assert dto.shopId == 2

class TestOrderSerialNumberRangeModel:
    def test_valid(self):
        dto = OrderSerialNumberRangeModel(
            ordersSerialNumberBegin="1000",
            ordersSerialNumberEnd="1999"
        )
        assert dto.ordersSerialNumberBegin == "1000"

class TestOrderAddDateModel:
    def test_valid(self):
        dto = OrderAddDateModel(
            ordersAddDateBegin="2023-01-01",
            ordersAddDateEnd="2023-12-31"
        )
        assert dto.ordersAddDateBegin == "2023-01-01"

class TestOrderModel:
    def test_valid_with_orders(self):
        dto = OrderModel(
            clientHasOrders=BooleanStrLongEnum.YES,
            ordersMinimalValue=100.0,
            ordersSerialNumberRange=OrderSerialNumberRangeModel(
                ordersSerialNumberBegin="1000",
                ordersSerialNumberEnd="1999"
            ),
            ordersAddDate=OrderAddDateModel(
                ordersAddDateBegin="2023-01-01",
                ordersAddDateEnd="2023-12-31"
            )
        )
        assert dto.clientHasOrders == BooleanStrLongEnum.YES

    def test_valid_no_orders(self):
        dto = OrderModel(
            clientHasOrders=BooleanStrLongEnum.NO
        )
        assert dto.clientHasOrders == BooleanStrLongEnum.NO
        assert dto.ordersMinimalValue is None

class TestPostParamsSearchModel:
    def test_valid_minimal(self):
        dto = PostParamsSearchModel(
            clientIsWholesaler=BooleanStrLongEnum.NO,
            clientCountryId="PL"
        )
        assert dto.clientCountryId == "PL"

    def test_valid_maximal(self):
        dto = PostParamsSearchModel(
            clientLogin="testuser",
            clientIsWholesaler=BooleanStrLongEnum.YES,
            clientCountryId="PL",
            langId="pl",
            clientCustomerServiceRepresentativeLogin="rep",
            clientDiscountGroupNumber=1,
            newsletterEmailApproval="y",
            searchByShops=SearchByShopEnum.ONE_OF_SELECTED,
            clientLoyaltyCard=ClientLoyaltyCardModel(
                clientHasLoyaltyCard=ClientHasLoyaltyCardEnum.NO
            ),
            orders=OrderModel(
                clientHasOrders=BooleanStrLongEnum.YES,
                ordersMinimalValue=50.0,
                ordersSerialNumberRange=OrderSerialNumberRangeModel(
                    ordersSerialNumberBegin="100",
                    ordersSerialNumberEnd="999"
                ),
                ordersAddDate=OrderAddDateModel(
                    ordersAddDateBegin="2023-01-01",
                    ordersAddDateEnd="2023-12-31"
                )
            )
        )
        assert dto.clientLogin == "testuser"
        assert dto.clientIsWholesaler == BooleanStrLongEnum.YES
        assert dto.searchByShops == SearchByShopEnum.ONE_OF_SELECTED


# --- Tests for Endpoints
class TestSearch:
    def test_instantiate_minimal(self):
        dto = Search()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

    def test_instantiate_with_params(self):
        dto = Search(
            params=PostParamsSearchModel(
                clientLogin="testuser"
            )
        )
        assert dto.params.clientLogin == "testuser"
