import pytest
from pydantic import ValidationError
from datetime import date

from src.idosell.crm._common import (
    BalanceOperationTypeEnum, ClientTypeEnum, TradeCreditEnum,
    BalanceModel, ClientRegistrationDateModel, DateModel, ShopsModel
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for Enums
class TestBalanceOperationTypeEnum:
    def test_valid_values(self):
        assert BalanceOperationTypeEnum.ADD == 'add'
        assert BalanceOperationTypeEnum.SET == 'set'
        assert BalanceOperationTypeEnum.SUBTRACT == 'subtract'

class TestClientTypeEnum:
    def test_valid_values(self):
        assert ClientTypeEnum.PERSON == 'person'
        assert ClientTypeEnum.PERSON_MALE == 'person_male'
        assert ClientTypeEnum.PERSON_FEMALE == 'person_female'
        assert ClientTypeEnum.FIRM == 'firm'

class TestTradeCreditEnum:
    def test_valid_values(self):
        assert TradeCreditEnum.NONZERO == 'nonzero'
        assert TradeCreditEnum.POSITIVE == 'positive'
        assert TradeCreditEnum.NEGATIVE == 'negative'
        assert TradeCreditEnum.ZERO == 'zero'


# --- Tests for DTOs
class TestBalanceModel:
    def test_valid(self):
        dto = BalanceModel(
            amount=100.50,
            currency="PLN"
        )
        assert dto.amount == 100.50
        assert dto.currency == "PLN"

    def test_invalid_amount(self):
        with pytest.raises(ValidationError):
            BalanceModel(
                amount=-5.0,
                currency="PLN"
            )

class TestClientRegistrationDateModel:
    def test_valid(self):
        dto = ClientRegistrationDateModel(
            clientRegistrationDateBegin=date(2023, 1, 1),
            clientRegistrationDateEnd=date(2023, 12, 31)
        )
        assert dto.clientRegistrationDateBegin == date(2023, 1, 1)

class TestDateModel:
    def test_valid(self):
        dto = DateModel(
            **{"from": "2023-01-01 10:00:00"},
            to="2023-12-31 23:59:59"
        )
        assert dto.model_dump(by_alias=True)["from"] == "2023-01-01 10:00:00"

class TestShopsModel:
    def test_valid(self):
        dto = ShopsModel(
            shop_id=1,
            approval=BooleanStrShortEnum.YES,
            registered=BooleanStrShortEnum.NO
        )
        assert dto.shop_id == 1
        assert dto.approval == BooleanStrShortEnum.YES

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            ShopsModel(
                shop_id=0,
                approval=BooleanStrShortEnum.YES,
                registered=BooleanStrShortEnum.YES
            )
