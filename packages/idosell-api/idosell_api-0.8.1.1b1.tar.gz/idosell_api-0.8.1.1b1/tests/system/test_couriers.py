import pytest
from pydantic import ValidationError

from src.idosell.system.couriers import (
    Get, GetAssignedToShippingProfiles, GetPickupPoints, PostPickupPoints, DeletePickupPoint, PutPickupPoints,
    DeletePickupPointSystemCouriersParamsModel, PostPickupPointsSystemCouriersParamsModel, PutPickupPointsSystemCouriersParamsModel
)
from src.idosell.system._common import (
    AddressModel, CoordinatesModel, DescriptionsCouriersModel, OperatingDaysModel, PickupPointDeleteRequestsPostModel, PickupPointsPostModel, PickupPointsPutModel,
    OperatingModeEnum, ServiceStatusEnum, PaymentFormsEnum
)


# --- Tests for DTOs
class TestDeletePickupPointSystemCouriersParamsModel:
    def test_valid(self):
        dto = DeletePickupPointSystemCouriersParamsModel(
            pickupPointDeleteRequests=[
                PickupPointDeleteRequestsPostModel(
                    pickupPointId="123",
                    pickupPointExternalId="ext123",
                    courierId=1
                )
            ]
        )
        assert len(dto.pickupPointDeleteRequests) == 1

class TestPostPickupPointsSystemCouriersParamsModel:
    def test_valid(self):
        dto = PostPickupPointsSystemCouriersParamsModel(
            pickupPoints=[
                PickupPointsPostModel(
                    pickupPointExternalId="ext123",
                    courierId=1,
                    descriptions=[
                        DescriptionsCouriersModel(
                            languageId="pl",
                            name="Name",
                            description="Desc"
                        )
                    ],
                    paymentForms=["cash"],
                    serviceStatus=ServiceStatusEnum.AVAILABLE,
                    address=AddressModel(
                        street="Street",
                        zipCode="12345",
                        city="City",
                        provinceCode="PC"
                    ),
                    coordinates=CoordinatesModel(
                        longitude=10.0,
                        latitude=20.0
                    ),
                    operatingDays=[
                        OperatingDaysModel(
                            weekday=1,
                            opening="08:00",
                            closing="17:00",
                            operatingMode=OperatingModeEnum.OPEN_IN
                        )
                    ]
                )
            ]
        )
        assert len(dto.pickupPoints) == 1

class TestPutPickupPointsSystemCouriersParamsModel:
    def test_valid(self):
        dto = PutPickupPointsSystemCouriersParamsModel(
            pickupPoints=[
                PickupPointsPutModel(
                    pickupPointId="123",
                    pickupPointExternalId="ext123",
                    courierId=1,
                    descriptions=[
                        DescriptionsCouriersModel(
                            languageId="pl",
                            name="Name",
                            description="Desc"
                        )
                    ],
                    paymentForms=[PaymentFormsEnum.CASH],
                    serviceStatus=ServiceStatusEnum.AVAILABLE,
                    address=AddressModel(
                        street="Street",
                        zipCode="12345",
                        city="City",
                        provinceCode="PC"
                    ),
                    coordinates=CoordinatesModel(
                        longitude=10.0,
                        latitude=20.0
                    ),
                    operatingDays=[
                        OperatingDaysModel(
                            weekday=1,
                            opening="08:00",
                            closing="17:00",
                            operatingMode=OperatingModeEnum.OPEN_IN
                        )
                    ]
                )
            ]
        )
        assert len(dto.pickupPoints) == 1


# --- Tests for Endpoints
class TestGetAssignedToShippingProfiles:
    def test_instantiate(self):
        dto = GetAssignedToShippingProfiles()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestGet:
    def test_instantiate_with_required_params(self):
        dto = Get(countryCode="PL")
        assert dto.countryCode == "PL"

    def test_invalid_country_code(self):
        with pytest.raises(ValidationError):
            Get(countryCode="ABC")

        with pytest.raises(ValidationError):
            Get(countryCode="poland")

class TestDeletePickupPoint:
    def test_instantiate(self):
        dto = DeletePickupPoint(
            params=DeletePickupPointSystemCouriersParamsModel(
                pickupPointDeleteRequests=[
                    PickupPointDeleteRequestsPostModel(
                        pickupPointId="123",
                        pickupPointExternalId="ext123",
                        courierId=1
                    )
                ]
            )
        )
        assert len(dto.params.pickupPointDeleteRequests) == 1

class TestGetPickupPoints:
    def test_instantiate_with_required_params(self):
        dto = GetPickupPoints(
            courierId=1
        )
        assert dto.courierId == 1

    def test_invalid_courier_id(self):
        with pytest.raises(ValidationError):
            GetPickupPoints(courierId=0)

class TestPostPickupPoints:
    def test_instantiate(self):
        dto = PostPickupPoints(
            params=PostPickupPointsSystemCouriersParamsModel(
                pickupPoints=[
                    PickupPointsPostModel(
                        pickupPointExternalId="ext123",
                        courierId=1,
                        descriptions=[
                            DescriptionsCouriersModel(
                                languageId="pl",
                                name="Name",
                                description="Desc"
                            )
                        ],
                        paymentForms=["cash"],
                        serviceStatus=ServiceStatusEnum.AVAILABLE,
                        address=AddressModel(
                            street="Street",
                            zipCode="12345",
                            city="City",
                            provinceCode="PC"
                        ),
                        coordinates=CoordinatesModel(
                            longitude=10.0,
                            latitude=20.0
                        ),
                        operatingDays=[
                            OperatingDaysModel(
                                weekday=1,
                                opening="08:00",
                                closing="17:00",
                                operatingMode=OperatingModeEnum.OPEN_IN
                            )
                        ]
                    )
                ]
            )
        )
        assert len(dto.params.pickupPoints) == 1

class TestPutPickupPoints:
    def test_instantiate(self):
        dto = PutPickupPoints(
            params=PutPickupPointsSystemCouriersParamsModel(
                pickupPoints=[
                    PickupPointsPutModel(
                        pickupPointId="123",
                        pickupPointExternalId="ext123",
                        courierId=1,
                        descriptions=[
                            DescriptionsCouriersModel(
                                languageId="pl",
                                name="Name",
                                description="Desc"
                            )
                        ],
                        paymentForms=[PaymentFormsEnum.CASH],
                        serviceStatus=ServiceStatusEnum.AVAILABLE,
                        address=AddressModel(
                            street="Street",
                            zipCode="12345",
                            city="City",
                            provinceCode="PC"
                        ),
                        coordinates=CoordinatesModel(
                            longitude=10.0,
                            latitude=20.0
                        ),
                        operatingDays=[
                            OperatingDaysModel(
                                weekday=1,
                                opening="08:00",
                                closing="17:00",
                                operatingMode=OperatingModeEnum.OPEN_IN
                            )
                        ]
                    )
                ]
            )
        )
        assert len(dto.params.pickupPoints) == 1
