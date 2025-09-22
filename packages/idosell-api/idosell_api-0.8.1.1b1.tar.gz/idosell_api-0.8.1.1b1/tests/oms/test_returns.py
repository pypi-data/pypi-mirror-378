"""
Basic tests for idosell/oms/returns.py

This test file covers the core functionality of the returns module,
focusing on basic data models and endpoint classes that can be tested
without complex dependencies.
"""

import pytest
from src.idosell.oms.returns import (
    # Enums
    ApiFlagReturnsEnum,
    DatesTypeEnum,
    StatusEnum,
    # DTOs
    DateModel,
    RangeModel,
    ProductsReturnsPostModel,
    ReturnProductsPutModel,
    ReturnsPutModel,
    PostOmsReturnsParamsModel,
    PutOmsReturnsParamsModel,
    SerialNumberProductsPutModel,
    PutSerialNumberOmsReturnsParamsModel,
    # Endpoints
    Get,
    Post,
    Put,
    PutSerialNumber,
    GetStatuses,
)


class TestEnums:
    """Test the enum classes in the returns module."""

    def test_api_flag_returns_enum_values(self):
        """Test ApiFlagReturnsEnum values."""
        assert ApiFlagReturnsEnum.NONE == 'none'
        assert ApiFlagReturnsEnum.REGISTERED == 'registered'
        assert ApiFlagReturnsEnum.REALIZED == 'realized'
        assert ApiFlagReturnsEnum.REGISTERED_POS == 'registered_pos'
        assert ApiFlagReturnsEnum.REALIZED_POS == 'realized_pos'

    def test_dates_type_enum_values(self):
        """Test DatesTypeEnum values."""
        assert DatesTypeEnum.DATE_ADD == 'date_add'
        assert DatesTypeEnum.DATE_END == 'date_end'

    def test_status_enum_values(self):
        """Test StatusEnum integer values."""
        assert StatusEnum.RETURN_NOT_HANDLED == 1
        assert StatusEnum.RETURN_ACCEPTED == 2
        assert StatusEnum.RETURN_NOT_ACCEPTED == 3
        assert StatusEnum.RETURN_CANCELED_BY_THE_CUSTOMER == 13
        assert StatusEnum.RETURN_CANCELED == 14
        assert StatusEnum.RESEND_THE_ORDER == 15
        assert StatusEnum.ABORT_RESENDING_ORDER == 16
        assert StatusEnum.A_CUSTOMER_GENERATED_A_RETURN_IT_WILL_BE_DELIVERED_PERSONALLY == 17
        assert StatusEnum.A_CUSTOMER_GENERATED_A_RETURN_IT_WILL_BE_SENT_BY_THE_CUSTOMER == 18


class TestReturnsDTOs:
    """Test the basic data transfer objects in the returns module."""

    def test_date_model(self):
        """Test DateModel validation."""
        model = DateModel(
            date_begin="2023-10-01 00:00:00",
            date_end="2023-10-31 23:59:59",
            dates_type=DatesTypeEnum.DATE_ADD
        )
        assert model.date_begin == "2023-10-01 00:00:00"
        assert model.date_end == "2023-10-31 23:59:59"
        assert model.dates_type == DatesTypeEnum.DATE_ADD

    def test_range_model(self):
        """Test RangeModel validation."""
        date_range = DateModel(
            date_begin="2023-12-01 00:00:00",
            date_end="2023-12-31 23:59:59",
            dates_type=DatesTypeEnum.DATE_END
        )
        model = RangeModel(date=date_range)
        assert model.date.date_begin == "2023-12-01 00:00:00"
        assert model.date.dates_type == DatesTypeEnum.DATE_END

    def test_products_returns_post_model(self):
        """Test ProductsReturnsPostModel validation."""
        model = ProductsReturnsPostModel(
            id=1001,
            size="M",
            quantity=2.5,
            price=29.99,
            serialNumbers=["SN001", "SN002"],
            productOrderAdditional="Defective item"
        )
        assert model.id == 1001
        assert model.size == "M"
        assert model.quantity == 2.5
        assert model.price == 29.99
        assert model.serialNumbers == ["SN001", "SN002"]
        assert model.productOrderAdditional == "Defective item"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            ProductsReturnsPostModel(
                id=0,
                size="M",
                quantity=2.5,
                price=29.99,
                serialNumbers=[],
                productOrderAdditional=""
            )

    def test_return_products_put_model(self):
        """Test ReturnProductsPutModel validation."""
        model = ReturnProductsPutModel(
            id=2001,
            size="L",
            quantity=1.0,
            price=39.99,
            serialNumbers=["RTN001"],
            productOrderAdditional="Wrong size"
        )
        assert model.id == 2001
        assert model.size == "L"
        assert model.quantity == 1.0
        assert model.price == 39.99
        assert model.serialNumbers == ["RTN001"]

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            ReturnProductsPutModel(
                id=0,
                size="L",
                quantity=1.0,
                price=39.99,
                serialNumbers=[],
                productOrderAdditional=""
            )

    def test_returns_put_model(self):
        """Test ReturnsPutModel validation."""
        return_product = ReturnProductsPutModel(
            id=3001,
            size="XL",
            quantity=3.0,
            price=49.99,
            serialNumbers=["UPD001", "UPD002", "UPD003"],
            productOrderAdditional="Package damaged"
        )
        model = ReturnsPutModel(
            id=456,
            status=2,
            apiFlag=ApiFlagReturnsEnum.REGISTERED,
            products=[return_product],
            userNote="Processing return",
            clientNote="Thanks for fast handling",
            tryCorrectInvoice=True
        )
        assert model.id == 456
        assert model.status == 2
        assert model.apiFlag == ApiFlagReturnsEnum.REGISTERED
        assert len(model.products) == 1
        assert model.tryCorrectInvoice

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            ReturnsPutModel(
                id=0,
                status=2,
                apiFlag=ApiFlagReturnsEnum.REGISTERED,
                products=[],
                userNote="",
                clientNote="",
                tryCorrectInvoice=False
            )

    def test_post_oms_returns_params_model(self):
        """Test PostOmsReturnsParamsModel validation."""
        return_product = ProductsReturnsPostModel(
            id=4001,
            size="S",
            quantity=1.0,
            price=19.99,
            serialNumbers=["PST001"],
            productOrderAdditional="Color not as expected"
        )
        model = PostOmsReturnsParamsModel(
            order_sn=12345,
            stock_id=10,
            products=[return_product],
            status=1,
            client_received=True,
            change_status=False,
            courier_id=100,
            return_operator="operator@company.com",
            tryCorrectInvoice=True,
            include_shipping_cost="Y",
            additional_payment_cost="0.00",
            emptyReturn="N"
        )
        assert model.order_sn == 12345
        assert model.stock_id == 10
        assert len(model.products) == 1
        assert model.status == 1
        assert model.client_received
        assert model.courier_id == 100
        assert model.tryCorrectInvoice

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            PostOmsReturnsParamsModel(
                order_sn=0,
                stock_id=10,
                products=[],
                status=1,
                client_received=False,
                change_status=False,
                courier_id="",
                return_operator="",
                tryCorrectInvoice=False,
                include_shipping_cost="",
                additional_payment_cost="",
                emptyReturn=""
            )

    def test_put_oms_returns_params_model(self):
        """Test PutOmsReturnsParamsModel validation."""
        return_product = ReturnProductsPutModel(
            id=5001,
            size="M",
            quantity=2.0,
            price=24.99,
            serialNumbers=["PUT001", "PUT002"],
            productOrderAdditional="Changed mind"
        )
        return_request = ReturnsPutModel(
            id=789,
            status=3,
            apiFlag=ApiFlagReturnsEnum.REALIZED,
            products=[return_product],
            userNote="Return processed",
            clientNote="Refund processed successfully",
            tryCorrectInvoice=False
        )
        model = PutOmsReturnsParamsModel(returns=[return_request])
        assert len(model.returns) == 1
        assert model.returns[0].status == 3

    def test_serial_number_products_put_model(self):
        """Test SerialNumberProductsPutModel validation."""
        model = SerialNumberProductsPutModel(
            id=6001,
            size="L",
            serialNumbers=["SER001", "SER002", "SER003"]
        )
        assert model.id == 6001
        assert model.size == "L"
        assert model.serialNumbers == ["SER001", "SER002", "SER003"]

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            SerialNumberProductsPutModel(
                id=0,
                size="L",
                serialNumbers=[]
            )

    def test_put_serial_number_oms_returns_params_model(self):
        """Test PutSerialNumberOmsReturnsParamsModel validation."""
        serial_product = SerialNumberProductsPutModel(
            id=7001,
            size="XL",
            serialNumbers=["FIN001", "FIN002"]
        )
        model = PutSerialNumberOmsReturnsParamsModel(
            return_id=123,
            products=[serial_product]
        )
        assert model.return_id == 123
        assert len(model.products) == 1

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            PutSerialNumberOmsReturnsParamsModel(
                return_id=0,
                products=[]
            )


class TestReturnsEndpoints:
    """Test the API endpoint classes in the returns module."""

    def test_get_endpoint(self):
        """Test the Get endpoint (PageableSnakeGateway)."""
        date_range = DateModel(
            date_begin="2023-11-01 00:00:00",
            date_end="2023-11-30 23:59:59",
            dates_type=DatesTypeEnum.DATE_ADD
        )
        range_model = RangeModel(date=date_range)

        endpoint = Get(
            order_sn=999,
            return_id=444,
            return_shipping_number="SHIP123",
            range=range_model,
            status=StatusEnum.RETURN_ACCEPTED,
            return_ids=[111, 222, 333],
            stock_id=20,
            bundleAsProducts=True,
            results_page=1,
            results_limit=20
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/returns/returns'
        assert endpoint.order_sn == 999
        assert endpoint.return_id == 444
        assert endpoint.return_shipping_number == "SHIP123"
        if endpoint.range is not None and endpoint.range.date is not None:
            assert endpoint.range.date.date_begin == "2023-11-01 00:00:00"
        assert endpoint.status == StatusEnum.RETURN_ACCEPTED
        assert endpoint.return_ids == [111, 222, 333]
        assert endpoint.stock_id == 20
        assert endpoint.bundleAsProducts

        # Test None values with pagination parameters
        endpoint_none = Get(
            bundleAsProducts=False,
            results_page=1,
            results_limit=10
        )
        assert endpoint_none.order_sn is None
        assert endpoint_none.return_id is None
        assert endpoint_none.return_shipping_number is None
        assert endpoint_none.range is None
        assert endpoint_none.status is None
        assert endpoint_none.return_ids is None
        assert endpoint_none.stock_id is None

    def test_post_endpoint(self):
        """Test the Post endpoint."""
        return_product = ProductsReturnsPostModel(
            id=8001,
            size="M",
            quantity=3.0,
            price=34.99,
            serialNumbers=["PS0001", "PS0002", "PS0003"],
            productOrderAdditional="Poor quality"
        )
        params = PostOmsReturnsParamsModel(
            order_sn=11111,
            stock_id=15,
            products=[return_product],
            status=2,
            client_received=False,
            change_status=True,
            courier_id=200,
            return_operator="admin@shop.com",
            tryCorrectInvoice=False,
            include_shipping_cost="N",
            additional_payment_cost="5.99",
            emptyReturn="N"
        )
        endpoint = Post(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/returns/returns'
        assert endpoint.params.order_sn == 11111
        assert len(endpoint.params.products) == 1
        assert endpoint.params.status == 2

    def test_put_endpoint(self):
        """Test the Put endpoint."""
        return_product = ReturnProductsPutModel(
            id=9001,
            size="S",
            quantity=1.0,
            price=14.99,
            serialNumbers=["PU0001"],
            productOrderAdditional="Received different item"
        )
        return_request = ReturnsPutModel(
            id=555,
            status=14,
            apiFlag=ApiFlagReturnsEnum.REALIZED_POS,
            products=[return_product],
            userNote="Cancelling return per customer request",
            clientNote="Please keep the item",
            tryCorrectInvoice=True
        )
        params = PutOmsReturnsParamsModel(returns=[return_request])
        endpoint = Put(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/returns/returns'
        assert len(endpoint.params.returns) == 1
        assert endpoint.params.returns[0].id == 555

    def test_put_serial_number_endpoint(self):
        """Test the PutSerialNumber endpoint."""
        serial_product = SerialNumberProductsPutModel(
            id=10001,
            size="M",
            serialNumbers=["SN0001", "SN0002"]
        )
        params = PutSerialNumberOmsReturnsParamsModel(
            return_id=456,
            products=[serial_product]
        )
        endpoint = PutSerialNumber(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/returns/serialNumber'
        assert endpoint.params.return_id == 456
        assert len(endpoint.params.products) == 1

    def test_get_statuses_endpoint(self):
        """Test the GetStatuses endpoint."""
        endpoint = GetStatuses()
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/returns/statuses'
