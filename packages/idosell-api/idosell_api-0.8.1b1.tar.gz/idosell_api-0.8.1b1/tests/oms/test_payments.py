"""
Basic tests for idosell/oms/payments.py

This test file covers the core functionality of the payments module,
focusing on basic data models and endpoint classes that can be tested
without complex dependencies.
"""

import pytest
from src.idosell.oms.payments import (
    # Enums
    EventSourceTypeEnum,
    PaymentsTypeEnum,
    SourceTypePaymentsEnum,
    # DTOs
    OtherPostModel,
    OtherPutModel,
    ParamsPaymentsPutModel,
    SettingsPaymentsPutModel,
    PostCancelOmsPaymentsParamsModel,
    PostCashbackOmsPaymentsParamsModel,
    PostOmsPaymentsParamsModel,
    PutOmsPaymentsParamsModel,
    PostRepaymentOmsPaymentsParamsModel,
    # Endpoints
    PostCancel,
    PostCashback,
    PutConfirm,
    GetForms,
    Get,
    Post,
    Put,
    GetProfiles,
    PostRepayment,
)
from src.idosell._common import BooleanStrLongEnum


class TestEnums:
    """Test the enum classes in the payments module."""

    def test_event_source_type_enum_values(self):
        """Test EventSourceTypeEnum values."""
        assert EventSourceTypeEnum.ORDER == 'order'
        assert EventSourceTypeEnum.RETURN == 'return'
        assert EventSourceTypeEnum.RMA == 'rma'

    def test_payments_type_enum_values(self):
        """Test PaymentsTypeEnum values."""
        assert PaymentsTypeEnum.PAYMENT == 'payment'
        assert PaymentsTypeEnum.ADVANCE == 'advance'
        assert PaymentsTypeEnum.REPAYMENT == 'repayment'
        assert PaymentsTypeEnum.FEE == 'fee'

    def test_source_type_payments_enum_values(self):
        """Test SourceTypePaymentsEnum values."""
        assert SourceTypePaymentsEnum.ORDER == 'order'
        assert SourceTypePaymentsEnum.RETURN == 'return'


class TestPaymentsDTOs:
    """Test the basic data transfer objects in the payments module."""

    def test_other_post_model(self):
        """Test OtherPostModel validation."""
        model = OtherPostModel(
            system=1,
            number="4111111111111111",
            month=12,
            year=2025,
            securityCode="123",
            name="John Doe"
        )
        assert model.system == 1
        assert model.number == "4111111111111111"
        assert model.month == 12
        assert model.year == 2025
        assert model.securityCode == "123"
        assert model.name == "John Doe"

        # Test validation - system ge=1
        with pytest.raises(ValueError):
            OtherPostModel(
                system=0,
                number="4111111111111111",
                month=12,
                year=2025,
                securityCode="123",
                name="John Doe"
            )

        # Test validation - year ge=1
        with pytest.raises(ValueError):
            OtherPostModel(
                system=1,
                number="4111111111111111",
                month=12,
                year=0,
                securityCode="123",
                name="John Doe"
            )

    def test_other_put_model(self):
        """Test OtherPutModel validation."""
        model = OtherPutModel(
            system=2
        )
        assert model.system == 2

        # Test validation - system ge=1
        with pytest.raises(ValueError):
            OtherPutModel(system=0)

    def test_params_payments_put_model(self):
        """Test ParamsPaymentsPutModel validation."""
        model = ParamsPaymentsPutModel(
            sourceType=EventSourceTypeEnum.ORDER,
            paymentNumber="1234-1",
            accountingDate="2023-10-15"
        )
        assert model.sourceType == EventSourceTypeEnum.ORDER
        assert model.paymentNumber == "1234-1"
        assert model.accountingDate == "2023-10-15"

    def test_settings_payments_put_model(self):
        """Test SettingsPaymentsPutModel validation."""
        model = SettingsPaymentsPutModel(
            sendMail=True,
            sendSms=False
        )
        assert model.sendMail
        assert not model.sendSms

    def test_post_cancel_oms_payments_params_model(self):
        """Test PostCancelOmsPaymentsParamsModel validation."""
        model = PostCancelOmsPaymentsParamsModel(
            sourceType=EventSourceTypeEnum.RETURN,
            paymentNumber="5678-2"
        )
        assert model.sourceType == EventSourceTypeEnum.RETURN
        assert model.paymentNumber == "5678-2"

    def test_post_cashback_oms_payments_params_model(self):
        """Test PostCashbackOmsPaymentsParamsModel validation."""
        model = PostCashbackOmsPaymentsParamsModel(
            sourceType=SourceTypePaymentsEnum.ORDER,
            paymentNumber="9999-1",
            value=25.50
        )
        assert model.sourceType == SourceTypePaymentsEnum.ORDER
        assert model.paymentNumber == "9999-1"
        assert model.value == 25.50

    def test_post_oms_payments_params_model(self):
        """Test PostOmsPaymentsParamsModel validation."""
        model = PostOmsPaymentsParamsModel(
            sourceId=12345,
            sourceType=EventSourceTypeEnum.ORDER,
            value=99.99,
            account="1234567890123456",
            type=PaymentsTypeEnum.PAYMENT,
            paymentFormId=1,
            paymentVoucherKey="VOUCHER123",
            giftCardPIN=1234,
            externalPaymentId="EXT123456"
        )
        assert model.sourceId == 12345
        assert model.sourceType == EventSourceTypeEnum.ORDER
        assert model.value == 99.99
        assert model.account == "1234567890123456"
        assert model.type == PaymentsTypeEnum.PAYMENT
        assert model.paymentFormId == 1
        assert model.paymentVoucherKey == "VOUCHER123"
        assert model.giftCardPIN == 1234
        assert model.externalPaymentId == "EXT123456"

    def test_put_oms_payments_params_model(self):
        """Test PutOmsPaymentsParamsModel validation."""
        other_put = OtherPutModel(system=3)
        model = PutOmsPaymentsParamsModel(
            sourceType=EventSourceTypeEnum.RMA,
            paymentNumber="2468-3",
            paymentFormId=2,
            value=150.75,
            accountingDate="2023-11-20",
            account="9876543210987654",
            clientAccount="client@bank.com",
            other=other_put,
            externalPaymentId="EXT789012"
        )
        assert model.sourceType == EventSourceTypeEnum.RMA
        assert model.paymentNumber == "2468-3"
        assert model.paymentFormId == 2
        assert model.value == 150.75
        assert model.accountingDate == "2023-11-20"
        assert model.account == "9876543210987654"
        assert model.clientAccount == "client@bank.com"
        assert model.other.system == 3
        assert model.externalPaymentId == "EXT789012"

    def test_post_repayment_oms_payments_params_model(self):
        """Test PostRepaymentOmsPaymentsParamsModel validation."""
        other_post = OtherPostModel(
            system=1,
            number="4111111111111111",
            month=12,
            year=2024,
            securityCode="456",
            name="Jane Smith"
        )
        model = PostRepaymentOmsPaymentsParamsModel(
            sourceId=999,
            source_type="return",
            value=75.25,
            payment_form_id=3,
            account="1111222233334444",
            client_account="return@example.com",
            other=other_post
        )
        assert model.sourceId == 999
        assert model.source_type == "return"
        assert model.value == 75.25
        assert model.payment_form_id == 3
        assert model.account == "1111222233334444"
        assert model.client_account == "return@example.com"
        assert model.other.name == "Jane Smith"


class TestPaymentsEndpoints:
    """Test the API endpoint classes in the payments module."""

    def test_post_cancel_endpoint(self):
        """Test the PostCancel endpoint."""
        params = PostCancelOmsPaymentsParamsModel(
            sourceType=EventSourceTypeEnum.ORDER,
            paymentNumber="5000-1"
        )
        endpoint = PostCancel(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/payments/cancel'
        assert endpoint.params.sourceType == EventSourceTypeEnum.ORDER
        assert endpoint.params.paymentNumber == "5000-1"

    def test_post_cashback_endpoint(self):
        """Test the PostCashback endpoint."""
        params = PostCashbackOmsPaymentsParamsModel(
            sourceType=SourceTypePaymentsEnum.RETURN,
            paymentNumber="6000-2",
            value=45.00
        )
        endpoint = PostCashback(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/payments/cashback'
        assert endpoint.params.value == 45.00

    def test_put_confirm_endpoint(self):
        """Test the PutConfirm endpoint."""
        params = ParamsPaymentsPutModel(
            sourceType=EventSourceTypeEnum.ORDER,
            paymentNumber="7000-1",
            accountingDate="2023-12-01"
        )
        settings = SettingsPaymentsPutModel(
            sendMail=True,
            sendSms=False
        )
        endpoint = PutConfirm(params=params, settings=settings)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/payments/confirm'
        assert endpoint.params.sourceType == EventSourceTypeEnum.ORDER
        assert endpoint.settings.sendMail

    def test_get_forms_endpoint(self):
        """Test the GetForms endpoint."""
        endpoint = GetForms(activeOnly=BooleanStrLongEnum.YES)
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/payments/forms'
        assert endpoint.activeOnly == BooleanStrLongEnum.YES

        # Test with None
        endpoint_none = GetForms()
        assert endpoint_none.activeOnly is None

    def test_get_endpoint(self):
        """Test the Get endpoint."""
        endpoint = Get(
            paymentNumber="8000-3",
            sourceType=EventSourceTypeEnum.RETURN
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/payments/payments'
        assert endpoint.paymentNumber == "8000-3"
        assert endpoint.sourceType == EventSourceTypeEnum.RETURN

    def test_post_endpoint(self):
        """Test the Post endpoint."""
        params = PostOmsPaymentsParamsModel(
            sourceId=12347,
            sourceType=EventSourceTypeEnum.ORDER,
            value=129.99,
            account="5555666677778888",
            type=PaymentsTypeEnum.ADVANCE,
            paymentFormId=2,
            paymentVoucherKey="ADV-001",
            giftCardPIN=5678,
            externalPaymentId="EXT-001"
        )
        endpoint = Post(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/payments/payments'
        assert endpoint.params.value == 129.99
        assert endpoint.params.type == PaymentsTypeEnum.ADVANCE

    def test_put_endpoint(self):
        """Test the Put endpoint."""
        other_put = OtherPutModel(system=4)
        params = PutOmsPaymentsParamsModel(
            sourceType=EventSourceTypeEnum.RMA,
            paymentNumber="9000-4",
            paymentFormId=3,
            value=200.00,
            accountingDate="2023-12-15",
            account="4444333322221111",
            clientAccount="rma@example.com",
            other=other_put,
            externalPaymentId="EXT-RMA-002"
        )
        endpoint = Put(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/payments/payments'
        assert endpoint.params.sourceType == EventSourceTypeEnum.RMA
        assert endpoint.params.value == 200.00

    def test_get_profiles_endpoint(self):
        """Test the GetProfiles endpoint (PageableCamelGateway)."""
        endpoint = GetProfiles()
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/payments/profiles'

    def test_post_repayment_endpoint(self):
        """Test the PostRepayment endpoint."""
        other_post = OtherPostModel(
            system=2,
            number="4222222222222222",
            month=6,
            year=2025,
            securityCode="789",
            name="Alice Johnson"
        )
        params = PostRepaymentOmsPaymentsParamsModel(
            sourceId=500,
            source_type="return",
            value=89.90,
            payment_form_id=1,
            account="3333444455556666",
            client_account="alice@example.com",
            other=other_post
        )
        endpoint = PostRepayment(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/payments/repayment'
        assert endpoint.params.sourceId == 500
        assert endpoint.params.value == 89.90
