"""
Basic tests for idosell/oms/refunds.py

This test file covers the core functionality of the refunds module,
focusing on basic data models and endpoint classes that can be tested
without complex dependencies.
"""

import pytest
from src.idosell.oms.refunds import (
    # Enums
    SourceTypeAllEnum,
    RefundsSourceTypeEnum,
    SourceTypeWithOrderEnum,
    # DTOs
    RefundDetailsPostModel,
    PostAddAutomaticOmsRefundsParamsModel,
    PostAddAutomaticForOrderOmsRefundsParamsModel,
    PostAddManualOmsRefundsParamsModel,
    PutCancelRefundOmsRefundsParamsModel,
    PutConfirmOmsRefundsParamsModel,
    PutOmsRefundsParamsModel,
    # Endpoints
    PostAddAutomatic,
    PostAddAutomaticForOrder,
    PostAddManual,
    PutCancelRefund,
    PutConfirm,
    GetPossibleAuto,
    GetStatus,
    GetRetrieveList,
    PutUpdate,
)


class TestEnums:
    """Test the enum classes in the refunds module."""

    def test_source_type_all_enum_values(self):
        """Test SourceTypeAllEnum values."""
        assert SourceTypeAllEnum.ORDER == 'order'
        assert SourceTypeAllEnum.RETURN == 'return'
        assert SourceTypeAllEnum.RMA == 'rma'
        assert SourceTypeAllEnum.ALL == 'all'

    def test_refunds_source_type_enum_values(self):
        """Test RefundsSourceTypeEnum values."""
        assert RefundsSourceTypeEnum.RETURN == 'return'
        assert RefundsSourceTypeEnum.RMA == 'rma'

    def test_source_type_with_order_enum_values(self):
        """Test SourceTypeWithOrderEnum values."""
        assert SourceTypeWithOrderEnum.ORDER == 'order'
        assert SourceTypeWithOrderEnum.RETURN == 'return'
        assert SourceTypeWithOrderEnum.RMA == 'rma'


class TestRefundsDTOs:
    """Test the basic data transfer objects in the refunds module."""

    def test_refund_details_post_model(self):
        """Test RefundDetailsPostModel validation."""
        model = RefundDetailsPostModel(
            paymentFormId=1,
            paymentSystem=2,
            account="1234567890123456",
            clientAccount="client@bank.com"
        )
        assert model.paymentFormId == 1
        assert model.paymentSystem == 2
        assert model.account == "1234567890123456"
        assert model.clientAccount == "client@bank.com"

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            RefundDetailsPostModel(
                paymentFormId=0,
                paymentSystem=2,
                account="1234567890123456",
                clientAccount="client@bank.com"
            )

        with pytest.raises(ValueError):
            RefundDetailsPostModel(
                paymentFormId=1,
                paymentSystem=0,
                account="1234567890123456",
                clientAccount="client@bank.com"
            )

    def test_post_add_automatic_oms_refunds_params_model(self):
        """Test PostAddAutomaticOmsRefundsParamsModel validation."""
        model = PostAddAutomaticOmsRefundsParamsModel(
            sourceType=RefundsSourceTypeEnum.RETURN,
            sourceId=12345
        )
        assert model.sourceType == RefundsSourceTypeEnum.RETURN
        assert model.sourceId == 12345

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            PostAddAutomaticOmsRefundsParamsModel(
                sourceType=RefundsSourceTypeEnum.RETURN,
                sourceId=0
            )

    def test_post_add_automatic_for_order_oms_refunds_params_model(self):
        """Test PostAddAutomaticForOrderOmsRefundsParamsModel validation."""
        model = PostAddAutomaticForOrderOmsRefundsParamsModel(
            sourceId=999,
            refundValue=75.50,
            paymentId=4567,
            refundCurrency="USD"
        )
        assert model.sourceId == 999
        assert model.refundValue == 75.50
        assert model.paymentId == 4567
        assert model.refundCurrency == "USD"

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            PostAddAutomaticForOrderOmsRefundsParamsModel(
                sourceId=0,
                refundValue=75.50,
                paymentId=4567,
                refundCurrency="USD"
            )

        with pytest.raises(ValueError):
            PostAddAutomaticForOrderOmsRefundsParamsModel(
                sourceId=999,
                refundValue=75.50,
                paymentId=0,
                refundCurrency="USD"
            )

    def test_post_add_manual_oms_refunds_params_model(self):
        """Test PostAddManualOmsRefundsParamsModel validation."""
        refund_details = RefundDetailsPostModel(
            paymentFormId=3,
            paymentSystem=1,
            account="9876543210987654",
            clientAccount="manual@example.com"
        )
        model = PostAddManualOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.ORDER,
            sourceId=500,
            refundValue=45.25,
            refundCurrency="EUR",
            refundDetails=refund_details
        )
        assert model.sourceType == SourceTypeWithOrderEnum.ORDER
        assert model.sourceId == 500
        assert model.refundValue == 45.25
        assert model.refundCurrency == "EUR"
        assert model.refundDetails.paymentFormId == 3

        # Test string sourceId - but ge=1 constraint doesn't work with strings
        # so let's test with integer instead
        model_int = PostAddManualOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.RETURN,
            sourceId=1001,
            refundValue=100.00,
            refundCurrency="PLN",
            refundDetails=refund_details
        )
        assert model_int.sourceId == 1001

    def test_put_cancel_refund_oms_refunds_params_model(self):
        """Test PutCancelRefundOmsRefundsParamsModel validation."""
        model = PutCancelRefundOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.RMA,
            sourceId=678,
            paymentId="PAY-890"
        )
        assert model.sourceType == SourceTypeWithOrderEnum.RMA
        assert model.sourceId == 678
        assert model.paymentId == "PAY-890"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            PutCancelRefundOmsRefundsParamsModel(
                sourceType=SourceTypeWithOrderEnum.RMA,
                sourceId=0,
                paymentId="PAY-890"
            )

    def test_put_confirm_oms_refunds_params_model(self):
        """Test PutConfirmOmsRefundsParamsModel validation."""
        model = PutConfirmOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.RETURN,
            sourceId=345,
            paymentId="CONFIRM-678"
        )
        assert model.sourceType == SourceTypeWithOrderEnum.RETURN
        assert model.sourceId == 345
        assert model.paymentId == "CONFIRM-678"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            PutConfirmOmsRefundsParamsModel(
                sourceType=SourceTypeWithOrderEnum.RETURN,
                sourceId=0,
                paymentId="CONFIRM-678"
            )

    def test_put_oms_refunds_params_model(self):
        """Test PutOmsRefundsParamsModel validation."""
        model = PutOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.ORDER,
            sourceId=234,
            paymentId="UPDATE-901",
            refundValue=150.75,
            refundCurrency="GBP"
        )
        assert model.sourceType == SourceTypeWithOrderEnum.ORDER
        assert model.sourceId == 234
        assert model.paymentId == "UPDATE-901"
        assert model.refundValue == 150.75
        assert model.refundCurrency == "GBP"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            PutOmsRefundsParamsModel(
                sourceType=SourceTypeWithOrderEnum.ORDER,
                sourceId=0,
                paymentId="UPDATE-901",
                refundValue=150.75,
                refundCurrency="GBP"
            )


class TestRefundsEndpoints:
    """Test the API endpoint classes in the refunds module."""

    def test_post_add_automatic_endpoint(self):
        """Test the PostAddAutomatic endpoint."""
        params = PostAddAutomaticOmsRefundsParamsModel(
            sourceType=RefundsSourceTypeEnum.RETURN,
            sourceId=1111
        )
        endpoint = PostAddAutomatic(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/refunds/addAutomaticRefund'
        assert endpoint.params.sourceType == RefundsSourceTypeEnum.RETURN
        assert endpoint.params.sourceId == 1111

    def test_post_add_automatic_for_order_endpoint(self):
        """Test the PostAddAutomaticForOrder endpoint."""
        params = PostAddAutomaticForOrderOmsRefundsParamsModel(
            sourceId=9999,
            refundValue=199.99,
            paymentId=7777,
            refundCurrency="CAD"
        )
        endpoint = PostAddAutomaticForOrder(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/refunds/addAutomaticRefundForOrder'
        assert endpoint.params.sourceId == 9999
        assert endpoint.params.refundValue == 199.99

    def test_post_add_manual_endpoint(self):
        """Test the PostAddManual endpoint."""
        refund_details = RefundDetailsPostModel(
            paymentFormId=4,
            paymentSystem=3,
            account="5555666677778888",
            clientAccount="manual-refund@example.com"
        )
        params = PostAddManualOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.RMA,
            sourceId=2000,
            refundValue=299.50,
            refundCurrency="JPY",
            refundDetails=refund_details
        )
        endpoint = PostAddManual(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/refunds/addManualRefund'
        assert endpoint.params.sourceType == SourceTypeWithOrderEnum.RMA
        assert endpoint.params.refundValue == 299.50

    def test_put_cancel_refund_endpoint(self):
        """Test the PutCancelRefund endpoint."""
        params = PutCancelRefundOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.ORDER,
            sourceId=3000,
            paymentId="CANCEL-111"
        )
        endpoint = PutCancelRefund(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/refunds/cancelRefund'
        assert endpoint.params.sourceType == SourceTypeWithOrderEnum.ORDER
        assert endpoint.params.paymentId == "CANCEL-111"

    def test_put_confirm_endpoint(self):
        """Test the PutConfirm endpoint."""
        params = PutConfirmOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.RETURN,
            sourceId=4000,
            paymentId="CONFIRM-222"
        )
        endpoint = PutConfirm(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/refunds/confirmRefund'
        assert endpoint.params.paymentId == "CONFIRM-222"

    def test_get_possible_auto_endpoint(self):
        """Test the GetPossibleAuto endpoint."""
        endpoint = GetPossibleAuto(
            sourceId=5000,
            sourceType=SourceTypeWithOrderEnum.RMA
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/refunds/getPossibleAutoRefunds'
        assert endpoint.sourceId == 5000
        assert endpoint.sourceType == SourceTypeWithOrderEnum.RMA

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            GetPossibleAuto(
                sourceId=0,
                sourceType=SourceTypeWithOrderEnum.RMA
            )

    def test_get_status_endpoint(self):
        """Test the GetStatus endpoint."""
        endpoint = GetStatus(
            sourceId=6000,
            paymentId=1234,
            sourceType=SourceTypeWithOrderEnum.ORDER
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/refunds/getRefundStatus'
        assert endpoint.sourceId == 6000
        assert endpoint.paymentId == 1234

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            GetStatus(
                sourceId=0,
                paymentId=1234,
                sourceType=SourceTypeWithOrderEnum.ORDER
            )

        with pytest.raises(ValueError):
            GetStatus(
                sourceId=6000,
                paymentId=0,
                sourceType=SourceTypeWithOrderEnum.ORDER
            )

    def test_get_retrieve_list_endpoint(self):
        """Test the GetRetrieveList endpoint (PageableCamelGateway)."""
        endpoint = GetRetrieveList(
            sourceType=SourceTypeAllEnum.ALL,
            resultsPage=1,
            resultsLimit=10
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/refunds/retrieveRefundsList'
        assert endpoint.sourceType == SourceTypeAllEnum.ALL

    def test_put_update_endpoint(self):
        """Test the PutUpdate endpoint."""
        params = PutOmsRefundsParamsModel(
            sourceType=SourceTypeWithOrderEnum.RETURN,
            sourceId=7000,
            paymentId="UPDATE-333",
            refundValue=250.00,
            refundCurrency="AUD"
        )
        endpoint = PutUpdate(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/refunds/updateRefund'
        assert endpoint.params.sourceType == SourceTypeWithOrderEnum.RETURN
        assert endpoint.params.refundValue == 250.00
