import pytest
from pydantic import ValidationError

from src.idosell.wms.locations import GetLocations
from src.idosell.wms._common import ReturnElementsEnum


class TestGetLocations:
    """Test cases for GetWmsLocations model."""

    def test_instantiate_without_params(self):
        """Test creating instance with default (None) values."""
        dto = GetLocations()
        assert dto.locationId is None
        assert dto.locationCode is None
        assert dto.stockId is None
        assert dto.returnElements is None
        assert dto.resultsPage is None
        assert dto.resultsLimit is None

    def test_instantiate_with_valid_params(self):
        """Test creating instance with valid parameters."""
        dto = GetLocations(
            locationId=1,
            locationCode="LOC001",
            stockId=2,
            returnElements=[ReturnElementsEnum.LOCATIONNAME, ReturnElementsEnum.LOCATIONCODE],
            resultsPage=0,
            resultsLimit=10
        )
        assert dto.locationId == 1
        assert dto.locationCode == "LOC001"
        assert dto.stockId == 2
        assert dto.returnElements == [ReturnElementsEnum.LOCATIONNAME, ReturnElementsEnum.LOCATIONCODE]
        assert dto.resultsPage == 0
        assert dto.resultsLimit == 10

    def test_location_id_validation_min(self):
        """Test locationId must be >= 1."""
        with pytest.raises(ValidationError):
            GetLocations(locationId=0)
        with pytest.raises(ValidationError):
            GetLocations(locationId=-1)

    def test_location_code_validation_min_length(self):
        """Test locationCode must have min_length 1."""
        with pytest.raises(ValidationError):
            GetLocations(locationCode="")

    def test_stock_id_validation_min(self):
        """Test stockId must be >= 1."""
        with pytest.raises(ValidationError):
            GetLocations(stockId=0)

    def test_results_page_validation_min(self):
        """Test resultsPage must be >= 0."""
        with pytest.raises(ValidationError):
            GetLocations(resultsPage=-1)

    def test_results_limit_validation_range(self):
        """Test resultsLimit must be between 1 and 100."""
        with pytest.raises(ValidationError):
            GetLocations(resultsLimit=0)
        with pytest.raises(ValidationError):
            GetLocations(resultsLimit=101)

    def test_build_body(self):
        """Test build_body method returns correct structure."""
        dto = GetLocations(
            locationId=1,
            locationCode="LOC001"
        )
        body = dto.build_body()
        expected = {
            "params": {
                "locationId": 1,
                "locationCode": "LOC001"
            }
        }
        assert body == expected

    def test_build_body_exclude_none(self):
        """Test build_body excludes None values."""
        dto = GetLocations(locationId=1)
        body = dto.build_body()
        assert "locationCode" not in body["params"]
        assert "stockId" not in body["params"]
        assert "returnElements" not in body["params"]
        assert "resultsPage" not in body["params"]
        assert "resultsLimit" not in body["params"]

    def test_build_body_with_return_elements(self):
        """Test build_body with list of enums."""
        dto = GetLocations(returnElements=[ReturnElementsEnum.LOCATIONNAME])
        body = dto.build_body()
        expected = {
            "params": {
                "returnElements": ["locationName"]
            }
        }
        assert body == expected

    def test_build_body_with_multiple_return_elements(self):
        """Test build_body with multiple enums in list."""
        dto = GetLocations(returnElements=[ReturnElementsEnum.LOCATIONNAME, ReturnElementsEnum.STOCKID])
        body = dto.build_body()
        expected = {
            "params": {
                "returnElements": ["locationName", "stockId"]
            }
        }
        assert body == expected

    def test_inheritance_from_pageable_camel_gateway(self):
        """Test that it correctly inherits from PageableCamelGateway."""
        assert 'resultsPage' in GetLocations.model_fields
        assert 'resultsLimit' in GetLocations.model_fields
