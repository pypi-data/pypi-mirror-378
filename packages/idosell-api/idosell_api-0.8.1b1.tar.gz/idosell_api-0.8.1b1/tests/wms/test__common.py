import pytest
from pydantic import ValidationError
from src.idosell.wms._common import (
    DateTypeEnum,
    DateRangeOpenedDocumentsModel,
    DocumentTypeEnum,
    DocumentTypeFullEnum,
    StockDocumentStatusEnum,
    DocumentsWntEnum,
    DocumentsConfirmedEnum,
    DocumentsPriceTypeEnum,
    DocumentsQueueTypeEnum,
    DocumentsCurrencyForPurchasePriceRateTypeEnum,
    OpenedDocumentsStatusEnum,
    ReturnElementsEnum,
    DateRangeModel,
    ProductsDeleteModel,
    ProductsModel,
    ProductsPostPutModel,
    AverageDeliveryTimeModel,
    OrderCompletionTimeModel,
    WorkDaysModel,
    SuppliersModel,
)


# Test Enums
class TestDateTypeEnum:
    def test_enum_values(self):
        assert DateTypeEnum.OPEN == 'open'
        assert DateTypeEnum.MODIFY == 'modify'
        assert DateTypeEnum.CLOSE == 'close'
        assert DateTypeEnum.STOCKOPERATION == 'stockOperation'

    def test_enum_members(self):
        assert len(DateTypeEnum) == 4
        assert str(DateTypeEnum.OPEN) == 'open'


class TestDateRangeOpenedDocumentsModel:
    def test_enum_values(self):
        assert DateRangeOpenedDocumentsModel.OPEN == 'open'
        assert DateRangeOpenedDocumentsModel.MODIFY == 'modify'

    def test_enum_members(self):
        assert len(DateRangeOpenedDocumentsModel) == 2


class TestDocumentTypeEnum:
    def test_enum_values(self):
        assert DocumentTypeEnum.PZ == 'pz'
        assert DocumentTypeEnum.PW == 'pw'
        assert DocumentTypeEnum.PX == 'px'
        assert DocumentTypeEnum.RX == 'rx'
        assert DocumentTypeEnum.RW == 'rw'
        assert DocumentTypeEnum.MM == 'mm'

    def test_enum_members(self):
        assert len(DocumentTypeEnum) == 6


class TestDocumentTypeFullEnum:
    def test_enum_values(self):
        assert DocumentTypeFullEnum.PZ == 'pz'
        assert DocumentTypeFullEnum.WZ == 'wz'
        assert DocumentTypeFullEnum.ZW == 'zw'

    def test_enum_members(self):
        assert len(DocumentTypeFullEnum) == 8


class TestStockDocumentStatusEnum:
    def test_enum_values(self):
        assert StockDocumentStatusEnum.OPEN == 'open'
        assert StockDocumentStatusEnum.ON_THE_WAY == 'on_the_way'
        assert StockDocumentStatusEnum.CLOSE == 'close'

    def test_enum_members(self):
        assert len(StockDocumentStatusEnum) == 3


class TestDocumentsWntEnum:
    def test_enum_values(self):
        assert DocumentsWntEnum.NATIONAL_VAT_INVOICE == 'national_VAT_invoice'
        assert DocumentsWntEnum.OTHER_PURCHASE_DOCUMENT == 'other_purchase_document'
        assert DocumentsWntEnum.INVOICE_WITHOUT_VAT == 'invoice_without_VAT'
        assert DocumentsWntEnum.IMPORTS_FROM_OUTSIDE_THE_EU == 'imports_from_outside_the_EU'

    def test_enum_members(self):
        assert len(DocumentsWntEnum) == 4


class TestDocumentsConfirmedEnum:
    def test_enum_values(self):
        assert DocumentsConfirmedEnum.OPEN == 'open'
        assert DocumentsConfirmedEnum.ON_THE_WAY == 'on_the_way'

    def test_enum_members(self):
        assert len(DocumentsConfirmedEnum) == 2


class TestDocumentsPriceTypeEnum:
    def test_enum_values(self):
        assert DocumentsPriceTypeEnum.BRUTTO == 'brutto'
        assert DocumentsPriceTypeEnum.NETTO == 'netto'

    def test_enum_members(self):
        assert len(DocumentsPriceTypeEnum) == 2


class TestDocumentsQueueTypeEnum:
    def test_enum_values(self):
        assert DocumentsQueueTypeEnum.FIFO == 'fifo'
        assert DocumentsQueueTypeEnum.LIFO == 'lifo'

    def test_enum_members(self):
        assert len(DocumentsQueueTypeEnum) == 2


class TestDocumentsCurrencyForPurchasePriceRateTypeEnum:
    def test_enum_values(self):
        assert DocumentsCurrencyForPurchasePriceRateTypeEnum.CUSTOM == 'custom'
        assert DocumentsCurrencyForPurchasePriceRateTypeEnum.CURRENTDAY == 'currentDay'
        assert DocumentsCurrencyForPurchasePriceRateTypeEnum.CUSTOMDAY == 'customDay'
        assert DocumentsCurrencyForPurchasePriceRateTypeEnum.PREVIOUSDAY == 'previousDay'

    def test_enum_members(self):
        assert len(DocumentsCurrencyForPurchasePriceRateTypeEnum) == 4


class TestOpenedDocumentsStatusEnum:
    def test_enum_values(self):
        assert OpenedDocumentsStatusEnum.OPEN == 'open'
        assert OpenedDocumentsStatusEnum.ON_THE_WAY == 'on_the_way'
        assert OpenedDocumentsStatusEnum.ALL == 'all'

    def test_enum_members(self):
        assert len(OpenedDocumentsStatusEnum) == 3


class TestReturnElementsEnum:
    def test_enum_values(self):
        assert ReturnElementsEnum.LOCATIONNAME == 'locationName'
        assert ReturnElementsEnum.LOCATIONPATH == 'locationPath'
        assert ReturnElementsEnum.LOCATIONCODE == 'locationCode'
        assert ReturnElementsEnum.STOCKID == 'stockId'
        assert ReturnElementsEnum.PRODUCTS == 'products'

    def test_enum_members(self):
        assert len(ReturnElementsEnum) == 5


# Test Models
class TestDateRangeModel:
    def test_valid_model(self):
        data = {
            'dateType': 'open',
            'dateBegin': '2023-01-01 00:00:00',
            'dateEnd': '2023-01-02 00:00:00'
        }
        model = DateRangeModel(**data)
        assert model.dateType == DateTypeEnum.OPEN
        assert model.dateBegin == '2023-01-01 00:00:00'
        assert model.dateEnd == '2023-01-02 00:00:00'

    def test_invalid_date_type(self):
        data = {
            'dateType': 'invalid',
            'dateBegin': '2023-01-01 00:00:00',
            'dateEnd': '2023-01-02 00:00:00'
        }
        with pytest.raises(ValidationError):
            DateRangeModel(**data)

    def test_missing_required_field(self):
        data = {
            'dateType': 'open',
            'dateEnd': '2023-01-02 00:00:00'
        }
        with pytest.raises(ValidationError):
            DateRangeModel(**data)


class TestProductsDeleteModel:
    def test_valid_model(self):
        data = {
            'product': 1,
            'size': 'M'
        }
        model = ProductsDeleteModel(**data)
        assert model.product == 1
        assert model.size == 'M'

    def test_invalid_product(self):
        data = {
            'product': 0,
            'size': 'M'
        }
        with pytest.raises(ValidationError):
            ProductsDeleteModel(**data)


class TestProductsModel:
    def test_valid_model(self):
        data = {
            'type': 'some_type',
            'id': 123
        }
        model = ProductsModel(**data)
        assert model.type == 'some_type'
        assert model.id == 123

    def test_invalid_id(self):
        data = {
            'type': 'some_type',
            'id': 'not_an_int'
        }
        with pytest.raises(ValidationError):
            ProductsModel(**data)


class TestProductsPostPutModel:
    def test_valid_model(self):
        data = {
            'product': 1,
            'size': 'M',
            'quantity': 10,
            'productPurchasePrice': 100.0,
            'locationId': 1,
            'locationCode': 'LOC1',
            'locationTextId': 'M1\\Section\\Location'
        }
        model = ProductsPostPutModel(**data)
        assert model.product == 1
        assert model.size == 'M'
        assert model.quantity == 10
        assert model.productPurchasePrice == 100.0
        assert model.locationId == 1
        assert model.locationCode == 'LOC1'
        assert model.locationTextId == 'M1\\Section\\Location'

    def test_invalid_product(self):
        data = {
            'product': 0,
            'size': 'M',
            'quantity': 10,
            'productPurchasePrice': 100.0,
            'locationId': 1,
            'locationCode': 'LOC1',
            'locationTextId': 'M1\\Section\\Location'
        }
        with pytest.raises(ValidationError):
            ProductsPostPutModel(**data)

    def test_invalid_quantity(self):
        data = {
            'product': 1,
            'size': 'M',
            'quantity': 0,
            'productPurchasePrice': 100.0,
            'locationId': 1,
            'locationCode': 'LOC1',
            'locationTextId': 'M1\\Section\\Location'
        }
        with pytest.raises(ValidationError):
            ProductsPostPutModel(**data)

    def test_invalid_price(self):
        data = {
            'product': 1,
            'size': 'M',
            'quantity': 10,
            'productPurchasePrice': 0.0,
            'locationId': 1,
            'locationCode': 'LOC1',
            'locationTextId': 'M1\\Section\\Location'
        }
        with pytest.raises(ValidationError):
            ProductsPostPutModel(**data)


class TestAverageDeliveryTimeModel:
    def test_valid_model(self):
        data = {
            'value': 5,
            'unit': 'days'
        }
        model = AverageDeliveryTimeModel(**data)
        assert model.value == 5
        assert model.unit == 'days'

    def test_invalid_value(self):
        data = {
            'value': 0,
            'unit': 'days'
        }
        with pytest.raises(ValidationError):
            AverageDeliveryTimeModel(**data)


class TestOrderCompletionTimeModel:
    def test_valid_model(self):
        data = {
            'value': 2,
            'unit': 'hours'
        }
        model = OrderCompletionTimeModel(**data)
        assert model.value == 2
        assert model.unit == 'hours'

    def test_invalid_value(self):
        data = {
            'value': 0,
            'unit': 'hours'
        }
        with pytest.raises(ValidationError):
            OrderCompletionTimeModel(**data)


class TestWorkDaysModel:
    def test_valid_model(self):
        data = {
            'day': 1,
            'type': 'work',
            'from': '08:00',
            'to': '17:00'
        }
        model = WorkDaysModel(**data)
        assert model.day == 1
        assert model.type == 'work'
        assert model.start_time == '08:00'
        assert model.end_time == '17:00'

    def test_invalid_day(self):
        data = {
            'day': 0,
            'type': 'work',
            'from': '08:00',
            'to': '17:00'
        }
        with pytest.raises(ValidationError):
            WorkDaysModel(**data)


class TestSuppliersModel:
    def test_valid_model(self):
        data = {
            'id': 1,
            'name': 'Supplier Inc',
            'email': 'supplier@example.com',
            'phone': '1234567890',
            'fax': '0987654321',
            'street': 'Main St',
            'zipCode': '00000',
            'city': 'City',
            'country': 1,
            'taxCode': '1234567890123',
            'averageDeliveryTime': {'value': 3, 'unit': 'days'},
            'description': 'A supplier',
            'orderCompletionTime': {'value': 1, 'unit': 'days'},
            'workDays': [
                {'day': 1, 'type': 'work', 'from': '08:00', 'to': '17:00'}
            ]
        }
        model = SuppliersModel(**data)
        assert model.id == 1
        assert model.name == 'Supplier Inc'
        assert model.email == 'supplier@example.com'
        assert model.phone == '1234567890'
        assert model.fax == '0987654321'
        assert model.street == 'Main St'
        assert model.zipCode == '00000'
        assert model.city == 'City'
        assert model.country == 1
        assert model.taxCode == '1234567890123'
        assert model.averageDeliveryTime.value == 3
        assert model.averageDeliveryTime.unit == 'days'
        assert model.description == 'A supplier'
        assert model.orderCompletionTime.value == 1
        assert model.orderCompletionTime.unit == 'days'
        assert len(model.workDays) == 1
        assert model.workDays[0].day == 1
        assert model.workDays[0].start_time == '08:00'
        assert model.workDays[0].end_time == '17:00'

    def test_invalid_id(self):
        data = {
            'id': 0,
            'name': 'Supplier Inc',
            'email': 'supplier@example.com',
            'phone': '1234567890',
            'fax': '0987654321',
            'street': 'Main St',
            'zipCode': '00000',
            'city': 'City',
            'country': 1,
            'taxCode': '1234567890123',
            'averageDeliveryTime': {'value': 3, 'unit': 'days'},
            'description': 'A supplier',
            'orderCompletionTime': {'value': 1, 'unit': 'days'},
            'workDays': [
                {'day': 1, 'type': 'work', 'from': '08:00', 'to': '17:00'}
            ]
        }
        with pytest.raises(ValidationError):
            SuppliersModel(**data)
