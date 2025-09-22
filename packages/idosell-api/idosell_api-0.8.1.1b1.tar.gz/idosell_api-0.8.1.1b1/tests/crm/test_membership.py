import pytest
from pydantic import ValidationError

from src.idosell.crm.membership import (
    ErrorModel, FaultCodeEnum, GetCards, MembershipCardsModel, PutCards,
    PutCardsCrmMembershipParamsModel, SettingsModel
)


# --- Tests for Enums
class TestFaultCodeEnum:
    def test_valid_values(self):
        assert FaultCodeEnum.OPERATION_WAS_SUCCESSFUL == 0
        assert FaultCodeEnum.LOGIN_FAILURE_INVALID_USERNAME_OR_KEY == 1
        assert FaultCodeEnum.EMPTY_RESULT == 2
        assert FaultCodeEnum.NO_PARAMETERS_WERE_RECEIVED == 3
        assert FaultCodeEnum.SHOP_HAS_BEEN_BLOCKED_DUE_TO_NUMBER_OF_OVERDUE_INVOICES_OWED_TO_IAI_COMPANY == 4


# --- Tests for DTOs
class TestErrorModel:
    def test_valid(self):
        dto = ErrorModel(
            faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL,
            faultString="Success"
        )
        assert dto.faultCode == 0
        assert dto.faultString == "Success"


class TestMembershipCardsModel:
    def test_valid(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        dto = MembershipCardsModel(
            ordinal_number=1,
            card_type=1,
            number="MC123456",
            pin=1234,
            creation_date="2023-01-01",
            deactivate=False,
            set_rebate_group=True,
            errors=error
        )
        assert dto.ordinal_number == 1
        assert dto.card_type == 1
        assert dto.number == "MC123456"
        assert dto.pin == 1234

    def test_invalid_ordinal_number_zero(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        with pytest.raises(ValidationError):
            MembershipCardsModel(
                ordinal_number=0,
                card_type=1,
                number="MC123456",
                pin=1234,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )

    def test_invalid_card_type_zero(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        with pytest.raises(ValidationError):
            MembershipCardsModel(
                ordinal_number=1,
                card_type=0,
                number="MC123456",
                pin=1234,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )

    def test_invalid_pin_zero(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        with pytest.raises(ValidationError):
            MembershipCardsModel(
                ordinal_number=1,
                card_type=1,
                number="MC123456",
                pin=0,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )


class TestSettingsModel:
    def test_valid(self):
        dto = SettingsModel(
            sendMail=True,
            sendSms=False
        )
        assert dto.sendMail is True
        assert dto.sendSms is False


class TestPutCardsCrmMembershipParamsModel:
    def test_valid(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        cards = [
            MembershipCardsModel(
                ordinal_number=1,
                card_type=1,
                number="MC1",
                pin=1234,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )
        ]
        settings = SettingsModel(sendMail=True, sendSms=False)
        dto = PutCardsCrmMembershipParamsModel(
            id=1,
            login="user1",
            membership_cards=cards,
            settings=settings
        )
        assert dto.id == 1
        assert dto.login == "user1"
        assert len(dto.membership_cards) == 1

    def test_invalid_id_zero(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        cards = [
            MembershipCardsModel(
                ordinal_number=1,
                card_type=1,
                number="MC1",
                pin=1234,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )
        ]
        settings = SettingsModel(sendMail=True, sendSms=False)
        with pytest.raises(ValidationError):
            PutCardsCrmMembershipParamsModel(
                id=0,
                login="user1",
                membership_cards=cards,
                settings=settings
            )

    def test_empty_login(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        cards = [
            MembershipCardsModel(
                ordinal_number=1,
                card_type=1,
                number="MC1",
                pin=1234,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )
        ]
        settings = SettingsModel(sendMail=True, sendSms=False)
        with pytest.raises(ValidationError):
            PutCardsCrmMembershipParamsModel(
                id=1,
                login="",
                membership_cards=cards,
                settings=settings
            )

    def test_empty_membership_cards(self):
        settings = SettingsModel(sendMail=True, sendSms=False)
        with pytest.raises(ValidationError):
            PutCardsCrmMembershipParamsModel(
                id=1,
                login="user1",
                membership_cards=[],
                settings=settings
            )


# --- Tests for Endpoints
class TestGetCards:
    def test_instantiate_without_params(self):
        endpoint = GetCards()
        assert endpoint.id is None
        assert endpoint.login is None
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')

    def test_instantiate_with_params(self):
        endpoint = GetCards(id=1, login="user1")
        assert endpoint.id == 1
        assert endpoint.login == "user1"

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            GetCards(id=0)

    def test_empty_login(self):
        with pytest.raises(ValidationError):
            GetCards(login="")


class TestPutCards:
    def test_instantiate(self):
        error = ErrorModel(faultCode=FaultCodeEnum.OPERATION_WAS_SUCCESSFUL, faultString="OK")
        cards = [
            MembershipCardsModel(
                ordinal_number=1,
                card_type=1,
                number="MC1",
                pin=1234,
                creation_date="2023-01-01",
                deactivate=False,
                set_rebate_group=True,
                errors=error
            )
        ]
        settings = SettingsModel(sendMail=True, sendSms=False)
        params = PutCardsCrmMembershipParamsModel(
            id=1,
            login="user1",
            membership_cards=cards,
            settings=settings
        )
        endpoint = PutCards(params=params)
        assert endpoint.params.id == 1
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')
