import pytest
from pydantic import ValidationError

from src.idosell.wms.suppliers import (
    Delete, DeleteWmsSuppliersParamsModel, Get, Put, PutWmsSuppliersParamsModel
)
from src.idosell.wms._common import SuppliersModel


# --- Tests for DTOs
class TestDeleteWmsSuppliersParamsModel:
    def test_valid(self):
        dto = DeleteWmsSuppliersParamsModel(ids=[1, 2, 3])
        assert dto.ids == [1, 2, 3]

class TestPutWmsSuppliersParamsModel:
    def test_valid(self):
        from src.idosell.wms._common import AverageDeliveryTimeModel, OrderCompletionTimeModel, WorkDaysModel as SuppliersWorkDaysModel
        supplier = SuppliersModel(
            id=1,
            name="Test Supplier",
            email="test@example.com",
            phone="123456789",
            fax="123456789",
            street="Test Street",
            zipCode="12345",
            city="Test City",
            country=1,
            taxCode="123456789",
            averageDeliveryTime=AverageDeliveryTimeModel(value=1, unit="days"),
            description="Test description",
            orderCompletionTime=OrderCompletionTimeModel(value=1, unit="hours"),
            workDays=[SuppliersWorkDaysModel(
                day=1,
                type="work",
                **{"from": "09:00", "to": "17:00"}
            )]  # type: ignore
        )
        dto = PutWmsSuppliersParamsModel(suppliers=[supplier])
        assert len(dto.suppliers) == 1
        assert dto.suppliers[0].name == "Test Supplier"


# --- Tests for Endpoints
class TestDelete:
    def test_valid(self):
        dto = Delete(params=DeleteWmsSuppliersParamsModel(ids=[1, 2]))
        assert dto.params.ids == [1, 2]

    def test_build_body(self):
        dto = Delete(params=DeleteWmsSuppliersParamsModel(ids=[123]))
        body = dto.build_body()
        expected = {"params": {"params": {"ids": [123]}}}
        assert body == expected


class TestGet:
    def test_instantiate_without_params(self):
        dto = Get()
        assert dto.returnProductsCount is None
        assert dto.names is None
        assert dto.ids is None

    def test_instantiate_with_params(self):
        dto = Get(
            returnProductsCount=True,
            names=["Supplier1", "Supplier2"],
            ids=[1, 2],
            resultsPage=0,
            resultsLimit=10
        )
        assert dto.returnProductsCount is True
        assert dto.names == ["Supplier1", "Supplier2"]
        assert dto.ids == [1, 2]
        assert dto.resultsPage == 0

    def test_names_list_min_length(self):
        with pytest.raises(ValidationError):
            Get(names=[])

    def test_ids_list_min_length(self):
        with pytest.raises(ValidationError):
            Get(ids=[])

    def test_results_page_validation(self):
        with pytest.raises(ValidationError):
            Get(resultsPage=-1)

    def test_results_limit_validation(self):
        with pytest.raises(ValidationError):
            Get(resultsLimit=0)
        with pytest.raises(ValidationError):
            Get(resultsLimit=101)


class TestPut:
    def test_valid(self):
        from src.idosell.wms._common import AverageDeliveryTimeModel, OrderCompletionTimeModel, WorkDaysModel as SuppliersWorkDaysModel
        supplier = SuppliersModel(
            id=1,
            name="Test Supplier",
            email="test@example.com",
            phone="123456789",
            fax="123456789",
            street="Test Street",
            zipCode="12345",
            city="Test City",
            country=1,
            taxCode="123456789",
            averageDeliveryTime=AverageDeliveryTimeModel(value=1, unit="days"),
            description="Test description",
            orderCompletionTime=OrderCompletionTimeModel(value=1, unit="hours"),
            workDays=[SuppliersWorkDaysModel(
                day=1,
                type="work",
                **{"from": "09:00", "to": "17:00"}
            )]  # type: ignore
        )
        dto = Put(params=PutWmsSuppliersParamsModel(suppliers=[supplier]))
        assert len(dto.params.suppliers) == 1

    def test_build_body(self):
        from src.idosell.wms._common import AverageDeliveryTimeModel, OrderCompletionTimeModel, WorkDaysModel as SuppliersWorkDaysModel
        supplier = SuppliersModel(
            id=1,
            name="Test Supplier",
            email="test@example.com",
            phone="123456789",
            fax="123456789",
            street="Test Street",
            zipCode="12345",
            city="Test City",
            country=1,
            taxCode="123456789",
            averageDeliveryTime=AverageDeliveryTimeModel(value=1, unit="days"),
            description="Test description",
            orderCompletionTime=OrderCompletionTimeModel(value=1, unit="hours"),
            workDays=[SuppliersWorkDaysModel(
                day=1,
                type="work",
                **{"from": "09:00", "to": "17:00"}
            )]  # type: ignore
        )
        dto = Put(params=PutWmsSuppliersParamsModel(suppliers=[supplier]))
        body = dto.build_body()
        assert body["params"]["params"]["suppliers"][0]["name"] == "Test Supplier"
