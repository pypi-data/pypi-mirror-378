from typing import List, Any

from src.idosell._common import BooleanStrShortEnum
from src.idosell.wms._common import AverageDeliveryTimeModel, DocumentTypeEnum, DocumentsConfirmedEnum, DocumentsCurrencyForPurchasePriceRateTypeEnum, DocumentsPriceTypeEnum, DocumentsQueueTypeEnum, DocumentsWntEnum, OrderCompletionTimeModel, ProductsDeleteModel, ProductsPostPutModel, SuppliersModel, WorkDaysModel
from src.idosell.wms.locations import GetLocations as WmsGetWmsLocations
from src.idosell.wms.stocks import (
    DeleteDocuments as WmsStocksDeleteDocuments, DeleteDocumentsWmsStocksParamsModel, DeleteProducts as WmsStocksDeleteProducts, DeleteProductsWmsStocksParamsModel,
    GetDocuments as WmsGetDocuments, GetOpenedDocuments as WmsGetOpenedDocuments, GetProducts as WmsGetProducts,
    PostDocuments as WmsStocksPostDocuments, PostDocumentsWmsStocksParamsModel, PostProducts as WmsStocksPostProducts, PostProductsWmsStocksParamsModel,
    PutAcceptMM as WmsStocksPutAcceptMM, PutAcceptMMWmsStocksParamsModel, PutClose as WmsStocksPutClose, PutCloseWmsStocksParamsModel, PutDocuments as WmsStocksPutDocuments, PutDocumentsWmsStocksParamsModel, PutProducts as WmsStocksPutProducts, PutProductsWmsStocksParamsModel, PutRejectMM as WmsStocksPutRejectMM, PutRejectMMWmsStocksParamsModel
)
from src.idosell.wms.suppliers import DeleteWmsSuppliersParamsModel, Get as WmsGet, Delete as WmsSuppliersDelete, Put as WmsSuppliersPut, PutWmsSuppliersParamsModel

wms_delete: List[Any] = [
    WmsSuppliersDelete(
        params = DeleteWmsSuppliersParamsModel(ids = [1])
    ),
    WmsStocksDeleteDocuments(
        params = DeleteDocumentsWmsStocksParamsModel(
            type = DocumentTypeEnum.PZ,
            id = 1
        )
    ),
    WmsStocksDeleteProducts(
        params = DeleteProductsWmsStocksParamsModel(
            products = [ProductsDeleteModel(
                product = 1,
                size = '1'
            )],
            type = DocumentTypeEnum.PZ,
            id = 1
        )
    ),
]

wms_get: List[Any] = [
    WmsGetWmsLocations(
        # type: ignore
        locationId = 1,
        # locationCode=location_code,
        # stockId=stock_id,
        # returnElements=return_elements
    ),
    WmsGetDocuments(), # type: ignore
    WmsGetOpenedDocuments(), # type: ignore
    WmsGetProducts(), # type: ignore
    WmsGet() # type: ignore
]

wms_post: List[Any] = [
    WmsStocksPostDocuments(
        params = PostDocumentsWmsStocksParamsModel(
            type = DocumentTypeEnum.PZ,
            stockId = 1,
            stockDocumentNumber = "DOC001",
            stockSourceId = 1,
            note = "Test note",
            productsInPreorder = BooleanStrShortEnum.NO,
            delivererId = 1,
            wnt = DocumentsWntEnum.NATIONAL_VAT_INVOICE,
            saleDocumentCreationDate = "2023-01-01",
            deliveryOnTheWayPlannedDeliveryDate = "2023-01-02",
            confirmed = DocumentsConfirmedEnum.OPEN,
            currencyForPurchasePrice = "PLN",
            priceType = DocumentsPriceTypeEnum.NETTO,
            queueType = DocumentsQueueTypeEnum.FIFO
        )
    ),
    WmsStocksPostProducts(
        params = PostProductsWmsStocksParamsModel(
            products = [ProductsPostPutModel(
                product = 1,
                size = "1",
                quantity = 10,
                productPurchasePrice = 100.0,
                locationId = 1,
                locationCode = "LOC001",
                locationTextId = "M1\\Section\\Location"
            )],
            id = 1,
            type = DocumentTypeEnum.PZ
        )
    ),
]

wms_put: List[Any] = [
    WmsStocksPutAcceptMM(
        params = PutAcceptMMWmsStocksParamsModel(
            id = 1
        )
    ),
    WmsStocksPutClose(
        params = PutCloseWmsStocksParamsModel(
            type = DocumentTypeEnum.PZ,
            id = 1
        )
    ),
    WmsStocksPutDocuments(
        params = PutDocumentsWmsStocksParamsModel(
            stockDocumentId = 1,
            stockDocumentType = DocumentTypeEnum.PZ,
            stockDocumentNumber = "DOC001",
            stockId = 1,
            stockSourceId = 1,
            note = "Test note",
            productsInPreorder = BooleanStrShortEnum.NO,
            delivererId = 1,
            wnt = DocumentsWntEnum.NATIONAL_VAT_INVOICE,
            saleDocumentCreationDate = "2023-01-01",
            deliveryOnTheWayPlannedDeliveryDate = "2023-01-02",
            confirmed = DocumentsConfirmedEnum.OPEN,
            currencyForPurchasePrice = "PLN",
            currencyForPurchasePriceRate = 1.0,
            currencyForPurchasePriceRateType = DocumentsCurrencyForPurchasePriceRateTypeEnum.CURRENTDAY,
            currencyForPurchasePriceRateDate = "2023-01-01",
            priceType = DocumentsPriceTypeEnum.NETTO,
            queueType = DocumentsQueueTypeEnum.FIFO,
            verificationDate = "2023-01-01",
            verificationUser = "testuser"
        )
    ),
    WmsStocksPutProducts(
        params = PutProductsWmsStocksParamsModel(
            products = [ProductsPostPutModel(
                product = 1,
                size = "1",
                quantity = 10,
                productPurchasePrice = 100.0,
                locationId = 1,
                locationCode = "LOC001",
                locationTextId = "M1\\Section\\Location"
            )],
            type = DocumentTypeEnum.PZ,
            id = 1
        )
    ),
    WmsStocksPutRejectMM(
        params = PutRejectMMWmsStocksParamsModel(
            id = 1
        )
    ),
    WmsSuppliersPut(
        params = PutWmsSuppliersParamsModel(
            suppliers = [SuppliersModel(
                id = 1,
                name = "Test Supplier",
                email = "test@example.com",
                phone = "123456789",
                fax = "123456789",
                street = "Test Street",
                zipCode = "12345",
                city = "Test City",
                country = 1,
                taxCode = "123456789",
                averageDeliveryTime = AverageDeliveryTimeModel(
                    value = 1,
                    unit = "days"
                ),
                description = "Test description",
                orderCompletionTime = OrderCompletionTimeModel(
                    value = 1,
                    unit = "hours"
                ),
                workDays = [WorkDaysModel(
                    day = 1,
                    type = "work",
                    **{"from": "09:00", "to": "17:00"}
                )] # type: ignore
            )]
        )
    ),
]
