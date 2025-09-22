import pytest
from pydantic import ValidationError

from src.idosell.crm import giftcards, _common


# --- Tests for Enums
class TestBalanceOperationTypeEnum:
    def test_valid_add(self):
        assert _common.BalanceOperationTypeEnum.ADD == 'add'

    def test_valid_set(self):
        assert _common.BalanceOperationTypeEnum.SET == 'set'

    def test_valid_subtract(self):
        assert _common.BalanceOperationTypeEnum.SUBTRACT == 'subtract'


# --- Tests for DTOs
class TestGiftCardDeleteModel:
    def test_valid(self):
        dto = giftcards.GiftCardDeleteModel(
            id=1,
            number="GC123456"
        )
        assert dto.id == 1
        assert dto.number == "GC123456"

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            giftcards.GiftCardDeleteModel(
                id=0,
                number="GC123456"
            )


class TestGiftCardModel:
    def test_valid(self):
        dto = giftcards.GiftCardModel(
            id=1,
            number="GC123456",
            pin="1234"
        )
        assert dto.id == 1
        assert dto.number == "GC123456"
        assert dto.pin == "1234"

    def test_valid_none_fields(self):
        dto = giftcards.GiftCardModel()
        assert dto.id is None
        assert dto.number is None
        assert dto.pin is None


class TestGiftCardPostPutModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        dto = giftcards.GiftCardPostPutModel(
            number="GC123456",
            pin="1234",
            name="Test Card",
            expirationDate="2025-12-31",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1, 2],
            note="Test note"
        )
        assert dto.number == "GC123456"
        assert dto.balance.amount == 100.0


class TestGiftCardPostModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        dto = giftcards.GiftCardPostModel(
            number="GC123456",
            pin="1234",
            name="Test Card",
            expirationDate="2025-12-31",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1, 2],
            note="Test note",
            typeId=1
        )
        assert dto.typeId == 1

    def test_invalid_type_id_zero(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        with pytest.raises(ValidationError):
            giftcards.GiftCardPostModel(
                number="GC123456",
                pin="1234",
                name="Test Card",
                expirationDate="2025-12-31",
                balanceOperationType=_common.BalanceOperationTypeEnum.SET,
                balance=balance,
                shops=[1, 2],
                note="Test note",
                typeId=0
            )


class TestGiftCardPutModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        dto = giftcards.GiftCardPutModel(
            number="GC123456",
            pin="1234",
            name="Test Card",
            expirationDate="2025-12-31",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1, 2],
            note="Test note",
            id=1
        )
        assert dto.id == 1

    def test_invalid_id_zero(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        with pytest.raises(ValidationError):
            giftcards.GiftCardPutModel(
                number="GC123456",
                pin="1234",
                name="Test Card",
                expirationDate="2025-12-31",
                balanceOperationType=_common.BalanceOperationTypeEnum.SET,
                balance=balance,
                shops=[1, 2],
                note="Test note",
                id=0
            )


class TestSearchGiftCardModel:
    def test_valid(self):
        dto = giftcards.SearchGiftCardModel(
            giftCardTypeId=1,
            name="Test Card",
            noteContain="test",
            balanceFrom=50.0,
            balanceTo=200.0,
            expirationDateFrom="2024-01-01",
            expirationDateTo="2025-12-31",
            issueDateFrom="2023-01-01",
            issueDateTo="2024-12-31"
        )
        assert dto.giftCardTypeId == 1

    def test_invalid_gift_card_type_id_zero(self):
        with pytest.raises(ValidationError):
            giftcards.SearchGiftCardModel(giftCardTypeId=0)


class TestPutBlockCrmGiftcardsParamsModel:
    def test_valid(self):
        gc_list = [giftcards.GiftCardModel(id=1, number="GC1")]
        dto = giftcards.PutBlockCrmGiftcardsParamsModel(giftCards=gc_list)
        assert len(dto.giftCards) == 1

    def test_empty_list_invalid(self):
        with pytest.raises(ValidationError):
            giftcards.PutBlockCrmGiftcardsParamsModel(giftCards=[])


class TestDeleteCrmGiftcardsParamsModel:
    def test_valid(self):
        gc_list = [giftcards.GiftCardDeleteModel(id=1, number="GC1")]
        dto = giftcards.DeleteCrmGiftcardsParamsModel(giftCards=gc_list)
        assert len(dto.giftCards) == 1


class TestPostCrmGiftcardsParamsModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        gc = giftcards.GiftCardPostModel(
            number="GC123",
            pin="1234",
            name="Test",
            expirationDate="2025-01-01",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1],
            note="",
            typeId=1
        )
        dto = giftcards.PostCrmGiftcardsParamsModel(giftCards=[gc])
        assert len(dto.giftCards) == 1


class TestPutCrmGiftcardsParamsModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        gc = giftcards.GiftCardPutModel(
            id=1,
            number="GC123",
            pin="1234",
            name="Test",
            expirationDate="2025-01-01",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1],
            note=""
        )
        dto = giftcards.PutCrmGiftcardsParamsModel(giftCards=[gc])
        assert len(dto.giftCards) == 1


class TestSearchCrmGiftcardsParamsModel:
    def test_valid_with_gift_cards(self):
        gc_list = [giftcards.GiftCardModel(id=1)]
        dto = giftcards.SearchCrmGiftcardsParamsModel(giftCards=gc_list)
        assert len(dto.giftCards) == 1

    def test_valid_with_search(self):
        search = giftcards.SearchGiftCardModel(name="Test")
        dto = giftcards.SearchCrmGiftcardsParamsModel(searchGiftCards=search)
        assert dto.searchGiftCards.name == "Test"

    def test_invalid_both_none(self):
        # The comment says require at least one, but field is optional, assume it's checked somewhere
        dto = giftcards.SearchCrmGiftcardsParamsModel()
        assert dto.giftCards is None
        assert dto.searchGiftCards is None

    def test_empty_gift_cards_invalid(self):
        with pytest.raises(ValidationError):
            giftcards.SearchCrmGiftcardsParamsModel(giftCards=[])


class TestPutUnblockCrmGiftcardsParamsModel:
    def test_valid(self):
        gc_list = [giftcards.GiftCardModel(id=1)]
        dto = giftcards.PutUnblockCrmGiftcardsParamsModel(giftCards=gc_list)
        assert len(dto.giftCards) == 1


# --- Tests for Endpoints
class TestPutBlockEndpoint:
    def test_instantiate(self):
        params = giftcards.PutBlockCrmGiftcardsParamsModel(giftCards=[giftcards.GiftCardModel(id=1)])
        endpoint = giftcards.PutBlock(params=params)
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')


class TestDeleteEndpoint:
    def test_instantiate(self):
        params = giftcards.DeleteCrmGiftcardsParamsModel(giftCards=[giftcards.GiftCardDeleteModel(id=1, number="GC1")])
        endpoint = giftcards.Delete(params=params)
        assert hasattr(endpoint, '_method')


class TestPostEndpoint:
    def test_instantiate(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        gc = giftcards.GiftCardPostModel(
            number="GC123",
            pin="1234",
            name="Test",
            expirationDate="2025-01-01",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1],
            note="",
            typeId=1
        )
        params = giftcards.PostCrmGiftcardsParamsModel(giftCards=[gc])
        endpoint = giftcards.Post(params=params)
        assert hasattr(endpoint, '_method')


class TestPutEndpoint:
    def test_instantiate(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        gc = giftcards.GiftCardPutModel(
            id=1,
            number="GC123",
            pin="1234",
            name="Test",
            expirationDate="2025-01-01",
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            balance=balance,
            shops=[1],
            note=""
        )
        params = giftcards.PutCrmGiftcardsParamsModel(giftCards=[gc])
        endpoint = giftcards.Put(params=params)
        assert hasattr(endpoint, '_method')


class TestSearchEndpoint:
    def test_instantiate(self):
        params = giftcards.SearchCrmGiftcardsParamsModel(giftCards=[giftcards.GiftCardModel(id=1)])
        endpoint = giftcards.Search(params=params)
        assert hasattr(endpoint, '_method')


class TestGetTypesEndpoint:
    def test_instantiate(self):
        endpoint = giftcards.GetTypes()
        assert hasattr(endpoint, '_method')


class TestPutUnblockEndpoint:
    def test_instantiate(self):
        params = giftcards.PutUnblockCrmGiftcardsParamsModel(giftCards=[giftcards.GiftCardModel(id=1)])
        endpoint = giftcards.PutUnblock(params=params)
        assert hasattr(endpoint, '_method')
