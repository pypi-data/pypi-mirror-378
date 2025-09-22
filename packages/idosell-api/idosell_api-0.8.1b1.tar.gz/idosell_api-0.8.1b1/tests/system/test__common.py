import pytest
from pydantic import ValidationError

from src.idosell.system._common import (
    OperatingModeEnum, PaymentFormsEnum, ServiceStatusEnum,
    CurrencyRateEnum, MainStockSystemEnum, UserTypeEnum, SaleDateEnum, StockStateConfigEnum,
    AddressModel, CoordinatesModel, DescriptionsCouriersModel, OperatingDaysModel,
    PickupPointDeleteRequestsPostModel, PickupPointsPostModel, PickupPointsPutModel,
    BlockIfIncorrectStockQuantitiesModel, CurrenciesModel, DescriptionsSystemModel,
    RestrictionsModel, OrdersModel, TaxSettingsModel, ShopsModel, PanelSettingsModel,
    UnitsModel
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for Enums
class TestOperatingModeEnum:
    def test_valid_values(self):
        assert OperatingModeEnum.OPEN_IN == 'open_in'
        assert OperatingModeEnum.CLOSED == 'closed'
        assert OperatingModeEnum.H24 == '24h'

class TestPaymentFormsEnum:
    def test_valid_values(self):
        assert PaymentFormsEnum.CASH == 'cash'
        assert PaymentFormsEnum.CARD == 'card'

class TestServiceStatusEnum:
    def test_valid_values(self):
        assert ServiceStatusEnum.AVAILABLE == 'available'
        assert ServiceStatusEnum.OUT_OF_SERVICE == 'out_of_service'

class TestCurrencyRateEnum:
    def test_valid_values(self):
        assert CurrencyRateEnum.CURRENTDAY == 'currentDay'
        assert CurrencyRateEnum.PREVIOUSDAY == 'previousDay'

class TestMainStockSystemEnum:
    def test_valid_values(self):
        assert MainStockSystemEnum.IAI == 'iai'
        assert MainStockSystemEnum.OTHER == 'other'

class TestUserTypeEnum:
    def test_valid_values(self):
        assert UserTypeEnum.ALL == 'all'
        assert UserTypeEnum.ACTIVE == 'active'

class TestSaleDateEnum:
    def test_valid_values(self):
        assert SaleDateEnum.SALEDATEFROMORDER == 'saleDateFromOrder'
        assert SaleDateEnum.SALEDATEFROMPAYMENT == 'saleDateFromPayment'
        assert SaleDateEnum.SALEDATEFROMDOCUMENT == 'saleDateFromDocument'

class TestStockStateConfigEnum:
    def test_valid_values(self):
        assert StockStateConfigEnum.BRIDGE == 'bridge'
        assert StockStateConfigEnum.OUTSIDE == 'outside'
        assert StockStateConfigEnum.UNCONTROLLED == 'uncontrolled'


# --- Tests for DTOs
class TestAddressModel:
    def test_valid(self):
        dto = AddressModel(
            street="Test Street",
            zipCode="12345",
            city="Test City",
            provinceCode="TC"
        )
        assert dto.street == "Test Street"

class TestCoordinatesModel:
    def test_valid(self):
        dto = CoordinatesModel(
            longitude=10.5,
            latitude=20.3
        )
        assert dto.longitude == 10.5

class TestDescriptionsCouriersModel:
    def test_valid(self):
        dto = DescriptionsCouriersModel(
            languageId="pl",
            name="Test Name",
            description="Test Description"
        )
        assert dto.languageId == "pl"

class TestOperatingDaysModel:
    def test_valid(self):
        dto = OperatingDaysModel(
            weekday=1,
            opening="08:00",
            closing="17:00",
            operatingMode=OperatingModeEnum.OPEN_IN
        )
        assert dto.weekday == 1

    def test_invalid_weekday(self):
        with pytest.raises(ValidationError):
            OperatingDaysModel(
                weekday=0,
                opening="08:00",
                closing="17:00",
                operatingMode=OperatingModeEnum.OPEN_IN
            )

        with pytest.raises(ValidationError):
            OperatingDaysModel(
                weekday=8,
                opening="08:00",
                closing="17:00",
                operatingMode=OperatingModeEnum.OPEN_IN
            )

class TestPickupPointDeleteRequestsPostModel:
    def test_valid(self):
        dto = PickupPointDeleteRequestsPostModel(
            pickupPointId="123",
            pickupPointExternalId="ext123",
            courierId=1
        )
        assert dto.pickupPointId == "123"

class TestPickupPointsPostModel:
    def test_valid(self):
        dto = PickupPointsPostModel(
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
        assert dto.courierId == 1

class TestPickupPointsPutModel:
    def test_valid(self):
        dto = PickupPointsPutModel(
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
        assert dto.pickupPointId == "123"

class TestBlockIfIncorrectStockQuantitiesModel:
    def test_valid(self):
        dto = BlockIfIncorrectStockQuantitiesModel(finished=BooleanStrShortEnum.YES)
        assert dto.finished == BooleanStrShortEnum.YES

class TestCurrenciesModel:
    def test_valid(self):
        dto = CurrenciesModel(
            id="PLN",
            rate=3.5,
            scale=2
        )
        assert dto.id == "PLN"

    def test_invalid_rate(self):
        with pytest.raises(ValidationError):
            CurrenciesModel(
                id="PLN",
                rate=10001.0,
                scale=2
            )

class TestDescriptionsSystemModel:
    def test_valid(self):
        dto = DescriptionsSystemModel(
            language="pol",
            nameSingular="Test",
            namePlural="Tests",
            nameFractions="Test"
        )
        assert dto.language == "pol"

    def test_name_length_violation(self):
        with pytest.raises(ValidationError):
            DescriptionsSystemModel(
                language="pol",
                nameSingular="A" * 31,
                namePlural="Tests",
                nameFractions="Test"
            )

class TestRestrictionsModel:
    def test_valid(self):
        dto = RestrictionsModel(
            blockIfIncorrectStockQuantities=BlockIfIncorrectStockQuantitiesModel(finished=BooleanStrShortEnum.YES)
        )
        assert dto.blockIfIncorrectStockQuantities.finished == BooleanStrShortEnum.YES

class TestOrdersModel:
    def test_valid(self):
        dto = OrdersModel(
            alwaysAllowSentStatus=BooleanStrShortEnum.YES,
            restrictions=RestrictionsModel(
                blockIfIncorrectStockQuantities=BlockIfIncorrectStockQuantitiesModel(finished=BooleanStrShortEnum.NO)
            )
        )
        assert dto.alwaysAllowSentStatus == BooleanStrShortEnum.YES

class TestTaxSettingsModel:
    def test_valid(self):
        dto = TaxSettingsModel(
            saleDatePrepaid=SaleDateEnum.SALEDATEFROMORDER,
            saleDateCashOnDelivery=SaleDateEnum.SALEDATEFROMPAYMENT,
            saleDateTradeCredit=SaleDateEnum.SALEDATEFROMDOCUMENT,
            currencyRate=CurrencyRateEnum.CURRENTDAY
        )
        assert dto.currencyRate == CurrencyRateEnum.CURRENTDAY

class TestShopsModel:
    def test_valid(self):
        dto = ShopsModel(
            shopId=1,
            salesDocumentsAreCreatedByClient=BooleanStrShortEnum.NO
        )
        assert dto.shopId == 1

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            ShopsModel(
                shopId=0,
                salesDocumentsAreCreatedByClient=BooleanStrShortEnum.NO
            )

class TestPanelSettingsModel:
    def test_valid(self):
        dto = PanelSettingsModel(
            mainStockSystem=MainStockSystemEnum.OTHER,
            stockStateConfig=StockStateConfigEnum.OUTSIDE,
            taxSettings=TaxSettingsModel(
                saleDatePrepaid=SaleDateEnum.SALEDATEFROMORDER,
                saleDateCashOnDelivery=SaleDateEnum.SALEDATEFROMPAYMENT,
                saleDateTradeCredit=SaleDateEnum.SALEDATEFROMDOCUMENT,
                currencyRate=CurrencyRateEnum.CURRENTDAY
            ),
            shops=[
                ShopsModel(
                    shopId=1,
                    salesDocumentsAreCreatedByClient=BooleanStrShortEnum.NO
                )
            ]
        )
        assert dto.mainStockSystem == MainStockSystemEnum.OTHER

class TestUnitsModel:
    def test_valid(self):
        dto = UnitsModel(
            id=1,
            nameInPanel="Test Unit",
            precisionUnit=2,
            visible=True,
            descriptions=[
                DescriptionsSystemModel(
                    language="eng",
                    nameSingular="Unit",
                    namePlural="Units",
                    nameFractions="Fraction"
                )
            ]
        )
        assert dto.id == 1

    def test_name_in_panel_length_violation(self):
        with pytest.raises(ValidationError):
            UnitsModel(
                id=1,
                nameInPanel="A" * 31,
                precisionUnit=2,
                visible=True,
                descriptions=[DescriptionsSystemModel(
                    language="eng",
                    nameSingular="Unit",
                    namePlural="Units",
                    nameFractions="Fraction"
                )]
            )
