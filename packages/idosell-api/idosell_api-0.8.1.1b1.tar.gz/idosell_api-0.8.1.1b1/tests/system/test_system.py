import pytest
from pydantic import ValidationError

from src.idosell.system.system import (
    GetConfig, PutConfig, GetCurrencies, PutCurrencies, GetProcessesAutomation, PutProcessesAutomation,
    GetServerLoad, GetServerTime, GetShopsData, GetUnits, PutUnits, GetUsers,
    PutConfigSystemSystemParamsModel, PutProcessesAutomationSystemSystemParamsModel, PutUnitsSystemSystemParamsModel
)
from src.idosell.system._common import (
    PanelSettingsModel, CurrenciesModel, OrdersModel, UnitsModel, DescriptionsSystemModel
)
from src.idosell._common import BooleanStrShortEnum
from src.idosell.system._common import (
    MainStockSystemEnum, StockStateConfigEnum, TaxSettingsModel, ShopsModel, UserTypeEnum
)


# --- Tests for DTOs
class TestPutConfigSystemSystemParamsModel:
    def test_valid(self):
        from src.idosell.system._common import CurrencyRateEnum, SaleDateEnum
        dto = PutConfigSystemSystemParamsModel(
            panelSettings=PanelSettingsModel(
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
        )
        assert dto.panelSettings.mainStockSystem == MainStockSystemEnum.OTHER

class TestPutProcessesAutomationSystemSystemParamsModel:
    def test_valid(self):
        dto = PutProcessesAutomationSystemSystemParamsModel(
            shopId=1,
            orders=OrdersModel(
                alwaysAllowSentStatus=BooleanStrShortEnum.NO,
                restrictions={
                    "blockIfIncorrectStockQuantities": {
                        "finished": "n"
                    }
                }
            )
        )
        assert dto.shopId == 1

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            PutProcessesAutomationSystemSystemParamsModel(
                shopId=0,
                orders=OrdersModel(
                    alwaysAllowSentStatus=BooleanStrShortEnum.NO,
                    restrictions={
                        "blockIfIncorrectStockQuantities": {
                            "finished": "n"
                        }
                    }
                )
            )

class TestPutUnitsSystemSystemParamsModel:
    def test_valid(self):
        dto = PutUnitsSystemSystemParamsModel(
            units=[
                UnitsModel(
                    id=1,
                    nameInPanel="Test Unit",
                    precisionUnit=2,
                    visible=True,
                    descriptions=[
                        DescriptionsSystemModel(
                            language="pol",
                            nameSingular="Jednostka",
                            namePlural="Jednostki",
                            nameFractions="Jednostki"
                        )
                    ]
                )
            ]
        )
        assert len(dto.units) == 1


# --- Tests for Endpoints
class TestGetConfig:
    def test_instantiate(self):
        dto = GetConfig()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

    def test_build_body(self):
        dto = GetConfig()
        body = dto.build_body()
        expected = {"params": {}}
        assert body == expected

class TestPutConfig:
    def test_instantiate(self):
        dto = PutConfig(
            params=PutConfigSystemSystemParamsModel(
                panelSettings=PanelSettingsModel(
                    mainStockSystem="other",
                    stockStateConfig="outside",
                    taxSettings={
                        "saleDatePrepaid": "saleDateFromOrder",
                        "saleDateCashOnDelivery": "saleDateFromPayment",
                        "saleDateTradeCredit": "saleDateFromDocument",
                        "currencyRate": "currentDay"
                    },
                    shops=[
                        {
                            "shopId": 1,
                            "salesDocumentsAreCreatedByClient": "n"
                        }
                    ]
                )
            )
        )
        assert dto.params.panelSettings.mainStockSystem == "other"

class TestGetCurrencies:
    def test_instantiate_with_params(self):
        dto = GetCurrencies(
            symbol="PLN",
            date="2025-08-26"
        )
        assert dto.symbol == "PLN"
        assert dto.date == "2025-08-26"

class TestPutCurrencies:
    def test_instantiate(self):
        dto = PutCurrencies(
            currencies=[
                CurrenciesModel(
                    id="PLN",
                    rate=3.5,
                    scale=2
                )
            ]
        )
        assert len(dto.currencies) == 1

class TestGetProcessesAutomation:
    def test_instantiate_without_params(self):
        dto = GetProcessesAutomation()
        assert dto.shopId is None

    def test_instantiate_with_params(self):
        dto = GetProcessesAutomation(shopId=1)
        assert dto.shopId == 1

    def test_invalid_shop_id(self):
        with pytest.raises(ValidationError):
            GetProcessesAutomation(shopId=0)

class TestPutProcessesAutomation:
    def test_instantiate(self):
        dto = PutProcessesAutomation(
            params=PutProcessesAutomationSystemSystemParamsModel(
                shopId=1,
                orders=OrdersModel(
                    alwaysAllowSentStatus=BooleanStrShortEnum.NO,
                    restrictions={
                        "blockIfIncorrectStockQuantities": {
                            "finished": "n"
                        }
                    }
                )
            )
        )
        assert dto.params.shopId == 1

class TestGetServerLoad:
    def test_instantiate(self):
        dto = GetServerLoad()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestGetServerTime:
    def test_instantiate(self):
        dto = GetServerTime()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestGetShopsData:
    def test_instantiate(self):
        dto = GetShopsData()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestGetUnits:
    def test_instantiate_without_params(self):
        dto = GetUnits()
        assert dto.languagesIds is None

    def test_instantiate_with_params(self):
        dto = GetUnits(languagesIds=["pl", "en"])
        assert dto.languagesIds == ["pl", "en"]

class TestPutUnits:
    def test_instantiate(self):
        dto = PutUnits(
            params=PutUnitsSystemSystemParamsModel(
                units=[
                    UnitsModel(
                        id=1,
                        nameInPanel="Test Unit",
                        precisionUnit=2,
                        visible=True,
                        descriptions=[
                            DescriptionsSystemModel(
                                language="pol",
                                nameSingular="Jednostka",
                                namePlural="Jednostki",
                                nameFractions="Jednostki"
                            )
                        ]
                    )
                ]
            )
        )
        assert len(dto.params.units) == 1

class TestGetUsers:
    def test_instantiate_with_default_params(self):
        dto = GetUsers()
        assert dto.userType == UserTypeEnum.ALL

    def test_instantiate_with_custom_params(self):
        dto = GetUsers(userType=UserTypeEnum.ACTIVE)
        assert dto.userType == UserTypeEnum.ACTIVE
