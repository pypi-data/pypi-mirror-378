import pytest
from pydantic import ValidationError

from src.idosell.system.deliveries import (
    GetProfiles, GetRegions, PostRegions, PutDefaultProfiles,
    PostRegionsSystemDeliveriesParamsModel, PutDefaultProfilesSystemDeliveriesParamsModel
)


# --- Tests for DTOs
class TestPostRegionsSystemDeliveriesParamsModel:
    def test_valid(self):
        dto = PostRegionsSystemDeliveriesParamsModel(
            regionName="Test Region",
            shopId=1,
            postCodeFrom="00-000",
            postCodeTo="99-999",
            parentRegionId=1
        )
        assert dto.regionName == "Test Region"

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            PostRegionsSystemDeliveriesParamsModel(
                regionName="Test Region",
                shopId=0,
                postCodeFrom="00-000",
                postCodeTo="99-999",
                parentRegionId=1
            )

    def test_invalid_parent_region_id(self):
        with pytest.raises(ValidationError):
            PostRegionsSystemDeliveriesParamsModel(
                regionName="Test Region",
                shopId=1,
                postCodeFrom="00-000",
                postCodeTo="99-999",
                parentRegionId=0
            )

class TestPutDefaultProfilesSystemDeliveriesParamsModel:
    def test_valid(self):
        dto = PutDefaultProfilesSystemDeliveriesParamsModel(
            regionId=1,
            shopId=1,
            retailProfileId=1,
            wholesaleProfileId=1
        )
        assert dto.regionId == 1

    def test_invalid_region_id(self):
        with pytest.raises(ValidationError):
            PutDefaultProfilesSystemDeliveriesParamsModel(
                regionId=0,
                shopId=1,
                retailProfileId=1,
                wholesaleProfileId=1
            )

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            PutDefaultProfilesSystemDeliveriesParamsModel(
                regionId=1,
                shopId=0,
                retailProfileId=1,
                wholesaleProfileId=1
            )

    def test_invalid_retail_profile_id(self):
        with pytest.raises(ValidationError):
            PutDefaultProfilesSystemDeliveriesParamsModel(
                regionId=1,
                shopId=1,
                retailProfileId=0,
                wholesaleProfileId=1
            )

    def test_invalid_wholesale_profile_id(self):
        with pytest.raises(ValidationError):
            PutDefaultProfilesSystemDeliveriesParamsModel(
                regionId=1,
                shopId=1,
                retailProfileId=1,
                wholesaleProfileId=0
            )


# --- Tests for Endpoints
class TestPutDefaultProfiles:
    def test_instantiate(self):
        dto = PutDefaultProfiles(
            params=PutDefaultProfilesSystemDeliveriesParamsModel(
                regionId=1,
                shopId=1,
                retailProfileId=1,
                wholesaleProfileId=1
            )
        )
        assert dto.params.regionId == 1

class TestGetProfiles:
    def test_instantiate(self):
        dto = GetProfiles()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestGetRegions:
    def test_instantiate_without_params(self):
        dto = GetRegions()
        assert dto.shopId is None

    def test_instantiate_with_params(self):
        dto = GetRegions(shopId=1)
        assert dto.shopId == 1

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            GetRegions(shopId=0)

class TestPostRegions:
    def test_instantiate(self):
        dto = PostRegions(
            params=PostRegionsSystemDeliveriesParamsModel(
                regionName="Test Region",
                shopId=1,
                postCodeFrom="00-000",
                postCodeTo="99-999",
                parentRegionId=1
            )
        )
        assert dto.params.regionName == "Test Region"
