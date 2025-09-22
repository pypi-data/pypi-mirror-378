"""
Basic tests for idosell/oms/rma.py

This test file covers the core functionality of the RMA (Return Merchandise Authorization) module,
focusing on basic data models and endpoint classes that can be tested
without complex dependencies.
"""

import pytest
from src.idosell.oms.rma import (
    # Enums
    StatusIdEnum,
    # DTOs
    RmaDateModel,
    RmaChatModel,
    RmasModel,
    PutOmsRmaParamsModel,
    # Endpoints
    Get,
    Put,
    GetStatuses,
)


class TestEnums:
    """Test the enum classes in the RMA module."""

    def test_status_id_enum_values(self):
        """Test StatusIdEnum integer values."""
        assert StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_PRODUCT_WAS_SENT_FOR_TESTIN == 4
        assert StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_PRODUCT_SENT_TO_THE_PRODUCE == 5
        assert StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_REPAIR_IN_PROGRES == 6
        assert StatusIdEnum.COMPLAINT_DIDNT_ARRIV == 14
        assert StatusIdEnum.COMPLAINT_NOT_CONFIRMED_BY_THE_SHOP_SERVIC == 15
        assert StatusIdEnum.THE_COMPLAINT_HAS_BEEN_CANCELLE == 17
        assert StatusIdEnum.COMPLAINT_CANCELED_BY_THE_CUSTOME == 18
        assert StatusIdEnum.COMPLAINT_CONFIRME == 19
        assert StatusIdEnum.COMPLAINT_NOT_HANDLE == 20
        assert StatusIdEnum.COMPLAINT_REJECTED_NO_FAULT_WAS_FOUN == 22
        assert StatusIdEnum.COMPLAINT_REJECTED_THE_WARRANTY_PERIOD_HAS_EXPIRED == 23
        assert StatusIdEnum.COMPLAINT_REJECTED_DEFECT_CAUSED_BY_IMPROPER_US == 24
        assert StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_REPAIR_COMPLETE == 28
        assert StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_THE_COMPLAINT_REQUIRES_ADDITIONAL_INFORMATION_FROM_THE_CUSTOMER == 29


class TestRmaDTOs:
    """Test the basic data transfer objects in the RMA module."""

    def test_rma_date_model(self):
        """Test RmaDateModel validation."""
        model = RmaDateModel(
            dateFrom="2023-10-01",
            dateTo="2023-10-31"
        )
        assert model.dateFrom == "2023-10-01"
        assert model.dateTo == "2023-10-31"

    def test_rma_chat_model(self):
        """Test RmaChatModel validation."""
        model = RmaChatModel(
            message="Customer is requesting a repair due to manufacturing defect"
        )
        assert model.message == "Customer is requesting a repair due to manufacturing defect"

    def test_rmas_model(self):
        """Test RmasModel validation."""
        chat_messages = [
            RmaChatModel(message="Product stopped working after 2 months"),
            RmaChatModel(message="Thank you for your quick response")
        ]
        model = RmasModel(
            rmaId=12345,
            rmaStatusId=StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_PRODUCT_WAS_SENT_FOR_TESTIN,
            rmaChat=chat_messages
        )
        assert model.rmaId == 12345
        assert model.rmaStatusId == StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_PRODUCT_WAS_SENT_FOR_TESTIN
        assert len(model.rmaChat) == 2
        assert model.rmaChat[0].message == "Product stopped working after 2 months"

    def test_put_oms_rma_params_model(self):
        """Test PutOmsRmaParamsModel validation."""
        rma_request = RmasModel(
            rmaId=67890,
            rmaStatusId=StatusIdEnum.COMPLAINT_CONFIRME,
            rmaChat=[RmaChatModel(message="Complaint confirmed, proceeding with repair")]
        )
        model = PutOmsRmaParamsModel(rmas=[rma_request])
        assert len(model.rmas) == 1
        assert model.rmas[0].rmaId == 67890
        assert model.rmas[0].rmaStatusId == StatusIdEnum.COMPLAINT_CONFIRME


class TestRmaEndpoints:
    """Test the API endpoint classes in the RMA module."""

    def test_get_endpoint(self):
        """Test the Get endpoint (PageableCamelGateway)."""
        date_range = RmaDateModel(
            dateFrom="2023-11-01",
            dateTo="2023-11-30"
        )
        endpoint = Get(
            rmaIds=[111, 222, 333],
            stockId=10,
            operatorLogin="technician@company.com",
            clientId=12345,
            creationDate=date_range,
            modificationDate=RmaDateModel(dateFrom="2023-12-01", dateTo="2023-12-31"),
            endDate=None,
            resultsPage=1,
            resultsLimit=20
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/rma/rma'
        assert endpoint.rmaIds == [111, 222, 333]
        assert endpoint.stockId == 10
        assert endpoint.operatorLogin == "technician@company.com"
        assert endpoint.clientId == 12345
        if endpoint.creationDate is not None:
            assert endpoint.creationDate.dateFrom == "2023-11-01"

        # Test with None values
        endpoint_none = Get(
            resultsPage=1,
            resultsLimit=10
        )
        assert endpoint_none.rmaIds is None
        assert endpoint_none.stockId is None
        assert endpoint_none.operatorLogin is None
        assert endpoint_none.clientId is None
        assert endpoint_none.creationDate is None
        assert endpoint_none.modificationDate is None
        assert endpoint_none.endDate is None

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            Get(stockId=0, resultsPage=1, resultsLimit=10)

        with pytest.raises(ValueError):
            Get(clientId=0, resultsPage=1, resultsLimit=10)

    def test_put_endpoint(self):
        """Test the Put endpoint."""
        rma_chat = RmaChatModel(message="Issue resolved, complaint closed successfully")
        rma_request = RmasModel(
            rmaId=9999,
            rmaStatusId=StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_REPAIR_COMPLETE,
            rmaChat=[rma_chat]
        )
        params = PutOmsRmaParamsModel(rmas=[rma_request])
        endpoint = Put(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/rma/rma'
        assert len(endpoint.params.rmas) == 1
        assert endpoint.params.rmas[0].rmaId == 9999
        assert endpoint.params.rmas[0].rmaStatusId == StatusIdEnum.COMPLAINT_IS_BEING_CONSIDERED_REPAIR_COMPLETE

    def test_get_statuses_endpoint(self):
        """Test the GetStatuses endpoint."""
        endpoint = GetStatuses()
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/rma/statuses'
