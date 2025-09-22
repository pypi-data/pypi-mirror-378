import pytest
from pydantic import ValidationError

from src.idosell.wms.stocks import (
    DeleteDocuments, DeleteDocumentsWmsStocksParamsModel, DeleteProducts, DeleteProductsWmsStocksParamsModel,
    GetDocuments, GetOpenedDocuments, GetProducts, PostDocuments, PostDocumentsWmsStocksParamsModel,
    PostProducts, PostProductsWmsStocksParamsModel, PutAcceptMM, PutAcceptMMWmsStocksParamsModel,
    PutClose, PutCloseWmsStocksParamsModel, PutDocuments, PutDocumentsWmsStocksParamsModel,
    PutProducts, PutProductsWmsStocksParamsModel, PutRejectMM, PutRejectMMWmsStocksParamsModel
)
from src.idosell.wms._common import (
    DocumentTypeEnum, DocumentTypeFullEnum, DocumentsConfirmedEnum, DocumentsPriceTypeEnum,
    DocumentsQueueTypeEnum, DocumentsWntEnum, OpenedDocumentsStatusEnum, StockDocumentStatusEnum
)
from src.idosell._common import BooleanStrShortEnum


# --- Tests for DTOs
class TestDeleteDocumentsWmsStocksParamsModel:
    def test_valid(self):
        dto = DeleteDocumentsWmsStocksParamsModel(
            type=DocumentTypeEnum.PZ,
            id=1
        )
        assert dto.type == DocumentTypeEnum.PZ
        assert dto.id == 1


class TestDeleteProductsWmsStocksParamsModel:
    def test_valid(self):
        from src.idosell.wms._common import ProductsDeleteModel
        dto = DeleteProductsWmsStocksParamsModel(
            products=[ProductsDeleteModel(product=1, size="1")],
            type=DocumentTypeEnum.PZ,
            id=1
        )
        assert len(dto.products) == 1
        assert dto.type == DocumentTypeEnum.PZ
        assert dto.id == 1


class TestPostDocumentsWmsStocksParamsModel:
    def test_valid(self):
        dto = PostDocumentsWmsStocksParamsModel(
            type=DocumentTypeEnum.PZ,
            stockId=1,
            stockDocumentNumber="DOC001",
            stockSourceId=1,
            note="Test note",
            productsInPreorder=BooleanStrShortEnum.NO,
            delivererId=1,
            wnt=DocumentsWntEnum.NATIONAL_VAT_INVOICE,
            saleDocumentCreationDate="2023-01-01",
            deliveryOnTheWayPlannedDeliveryDate="2023-01-02",
            confirmed=DocumentsConfirmedEnum.OPEN,
            currencyForPurchasePrice="PLN",
            priceType=DocumentsPriceTypeEnum.NETTO,
            queueType=DocumentsQueueTypeEnum.FIFO
        )
        assert dto.type == DocumentTypeEnum.PZ


class TestPutCloseWmsStocksParamsModel:
    def test_valid(self):
        dto = PutCloseWmsStocksParamsModel(
            type=DocumentTypeEnum.PZ,
            id=1
        )
        assert dto.type == DocumentTypeEnum.PZ
        assert dto.id == 1


# --- Tests for Endpoints
class TestPutAcceptMM:
    def test_valid(self):
        dto = PutAcceptMM(params=PutAcceptMMWmsStocksParamsModel(id=1))
        assert dto.params.id == 1
        body = dto.build_body()
        assert body["params"]["params"]["id"] == 1

    def test_build_body(self):
        dto = PutAcceptMM(params=PutAcceptMMWmsStocksParamsModel(id=123))
        body = dto.build_body()
        expected = {"params": {"params": {"id": 123}}}
        assert body == expected


class TestPutClose:
    def test_valid(self):
        dto = PutClose(params=PutCloseWmsStocksParamsModel(type=DocumentTypeEnum.PZ, id=1))
        assert dto.params.type == DocumentTypeEnum.PZ
        assert dto.params.id == 1


class TestDeleteDocuments:
    def test_valid(self):
        dto = DeleteDocuments(params=DeleteDocumentsWmsStocksParamsModel(type=DocumentTypeEnum.PZ, id=1))
        assert dto.params.type == DocumentTypeEnum.PZ


class TestGetDocuments:
    def test_instantiate_without_params(self):
        dto = GetDocuments()
        assert dto.stockDocumentType is None
        assert dto.stockDocumentStatus is None

    def test_instantiate_with_params(self):
        dto = GetDocuments(
            stockDocumentType=DocumentTypeFullEnum.PZ,
            stockDocumentStatus=StockDocumentStatusEnum.OPEN,
            stockDocumentsIds=[1, 2],
            resultsPage=0,
            resultsLimit=10
        )
        assert dto.stockDocumentType == DocumentTypeFullEnum.PZ
        assert dto.resultsPage == 0

    def test_results_page_validation(self):
        with pytest.raises(ValidationError):
            GetDocuments(resultsPage=-1)


class TestPostDocuments:
    def test_valid(self):
        dto = PostDocuments(params=PostDocumentsWmsStocksParamsModel(
            type=DocumentTypeEnum.PZ,
            stockId=1,
            stockDocumentNumber="DOC001",
            stockSourceId=1,
            note="Test",
            productsInPreorder=BooleanStrShortEnum.NO,
            delivererId=1,
            wnt=DocumentsWntEnum.NATIONAL_VAT_INVOICE,
            saleDocumentCreationDate="2023-01-01",
            deliveryOnTheWayPlannedDeliveryDate="2023-01-02",
            confirmed=DocumentsConfirmedEnum.OPEN,
            currencyForPurchasePrice="PLN",
            priceType=DocumentsPriceTypeEnum.NETTO,
            queueType=DocumentsQueueTypeEnum.FIFO
        ))
        assert dto.params.type == DocumentTypeEnum.PZ


class TestPutDocuments:
    def test_valid(self):
        from src.idosell.wms._common import DocumentsCurrencyForPurchasePriceRateTypeEnum
        dto = PutDocuments(params=PutDocumentsWmsStocksParamsModel(
            stockDocumentId=1,
            stockDocumentType=DocumentTypeEnum.PZ,
            stockDocumentNumber="DOC001",
            stockId=1,
            stockSourceId=1,
            note="Test",
            productsInPreorder=BooleanStrShortEnum.NO,
            delivererId=1,
            wnt=DocumentsWntEnum.NATIONAL_VAT_INVOICE,
            saleDocumentCreationDate="2023-01-01",
            deliveryOnTheWayPlannedDeliveryDate="2023-01-02",
            confirmed=DocumentsConfirmedEnum.OPEN,
            currencyForPurchasePrice="PLN",
            currencyForPurchasePriceRate=1.0,
            currencyForPurchasePriceRateType=DocumentsCurrencyForPurchasePriceRateTypeEnum.CURRENTDAY,
            currencyForPurchasePriceRateDate="2023-01-01",
            priceType=DocumentsPriceTypeEnum.NETTO,
            queueType=DocumentsQueueTypeEnum.FIFO,
            verificationDate="2023-01-01",
            verificationUser="testuser"
        ))
        assert dto.params.stockDocumentId == 1


class TestGetOpenedDocuments:
    def test_instantiate_with_params(self):
        dto = GetOpenedDocuments(
            type=DocumentTypeEnum.PZ,
            status=OpenedDocumentsStatusEnum.OPEN,
            stockId=1
        )
        assert dto.type == DocumentTypeEnum.PZ
        assert dto.stockId == 1


class TestDeleteProducts:
    def test_valid(self):
        from src.idosell.wms._common import ProductsDeleteModel
        dto = DeleteProducts(params=DeleteProductsWmsStocksParamsModel(
            products=[ProductsDeleteModel(product=1, size="1")],
            type=DocumentTypeEnum.PZ,
            id=1
        ))
        assert len(dto.params.products) == 1


class TestGetProducts:
    def test_instantiate_with_params(self):
        dto = GetProducts(type=DocumentTypeFullEnum.PZ, id=1)
        assert dto.type == DocumentTypeFullEnum.PZ
        assert dto.id == 1


class TestPostProducts:
    def test_valid(self):
        from src.idosell.wms._common import ProductsPostPutModel
        dto = PostProducts(params=PostProductsWmsStocksParamsModel(
            products=[ProductsPostPutModel(
                product=1,
                size="1",
                quantity=10,
                productPurchasePrice=100.0,
                locationId=1,
                locationCode="LOC",
                locationTextId="M1\\Section"
            )],
            id=1,
            type=DocumentTypeEnum.PZ
        ))
        assert len(dto.params.products) == 1


class TestPutProducts:
    def test_valid(self):
        from src.idosell.wms._common import ProductsPostPutModel
        dto = PutProducts(params=PutProductsWmsStocksParamsModel(
            products=[ProductsPostPutModel(
                product=1,
                size="1",
                quantity=10,
                productPurchasePrice=100.0,
                locationId=1,
                locationCode="LOC",
                locationTextId="M1\\Section"
            )],
            type=DocumentTypeEnum.PZ,
            id=1
        ))
        assert dto.params.type == DocumentTypeEnum.PZ


class TestPutRejectMM:
    def test_valid(self):
        dto = PutRejectMM(params=PutRejectMMWmsStocksParamsModel(id=1))
        assert dto.params.id == 1
