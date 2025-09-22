from datetime import datetime, date, time
from typing import List, Any

from src.idosell._common import BooleanStrShortEnum
from src.idosell.oms._common import (
    ApiFlagEnum, ApplicationTypeEnum, ClientDeliveryAddressModel, ClientRequestInvoiceEnum, ClientWithoutAccountDataModel, DeliveryPackageParametersModel,
    DevideProductsPutModel, DiscountCodeModel, DocumentTypeEppEnum, DocumentTypeOrdersGetEnum, DocumentTypePostEnum, DocumentsDeleteModel, DocumentsPostModel,
    EmailProcessingConsentEnum, ErrorsModel, EventTypeEnum, ImagesDeleteModel, ImagesImagesPostModel, ImagesOrderModel, ImagesSettingsPostModel, ImagesTypeEnum,
    OpinionsRateEnum, OrderPackagesPostPutModel, OrderPaymentTypeEnum, OrderProductsModel, OrderSettledAtPriceEnum, OrderStatusEnum, OrderTypeEnum, OrdersPostModel,
    OrdersPutModel, PackagesPostPutModel, ParameterValuesModel, PayerAddressModel, PriceFormulaParametersModel, ProductBundleItemsModel, ProductIdentModel, ProductIdentTypeEnum, ProductQuantityOperationTypeEnum, ProductsModel, ProductsProfitMarginOrdersPutModel, ProductsPutModel, ProductsSerialNumbersOrdersPutModel,
    ProfitMarginOrdersPutModel, SettingsModel, SettingsPutModel, ShippingStoreCostsModel, TypeEnum, SourceTypeEnum, ExternalStockIdEnum
)
from src.idosell.oms.orders import (
    DeleteDocuments as OmsOrdersDeleteDocuments, DeleteDocumentsOmsOrdersParamsModel, DeleteImages as OmsOrdersDeleteImages, DeleteImagesOmsOrdersParamsModel,
    GetAnalytics as OmsOrdersGetAnalytics, GetAuctionDetails as OmsOrdersGetAuctionDetails,
    GetDocuments as OmsOrdersGetDocuments, GetExportdocumentsEPP as OmsOrdersGetExportdocumentsEPP,
    GetExportdocumentsJPK as OmsOrdersGetExportdocumentsJPK, GetHandler as OmsOrdersGetHandler,
    GetHistory as OmsOrdersGetHistory, GetImages as OmsOrdersGetImages,
    GetLabels as OmsOrdersGetLabels,GetOpinionsRate as OmsOrdersGetOpinionsRate,
    Get as OmsOrdersGet, GetPackages as OmsOrdersGetPackages,
    GetPrinterDocuments as OmsOrdersGetPrinterDocuments, GetProfitability as OmsOrdersGetProfitability,
    GetWarehouse as OmsOrdersGetWarehouse,
    PostDocumentsCreate as OmsOrdersPostDocumentsCreate, PostDocuments as OmsOrdersPostDocuments, PostImages as OmsOrdersPostImages, Post as OmsOrdersPost, PostPackages as OmsOrdersPostPackages,
    PutClient as OmsOrdersPutClient, PutCourier as OmsOrdersPutCourier, PutDeliveryAddress as OmsOrdersPutDeliveryAddress, PutDevide as OmsOrdersPutDevide,
    PutHandler as OmsOrdersPutHandler, Put as OmsOrdersPut, PutPackages as OmsOrdersPutPackages, PutPickupPoint as OmsOrdersPutPickupPoint,
    PutProductsSerialNumbers as OmsOrdersPutProductsSerialNumbers, PutProfitMargin as OmsOrdersPutProfitMargin, PutShippingCosts as OmsOrdersPutShippingCosts,
    PutWarehouse as OmsOrdersPutWarehouse, SearchOmsOrdersParamsModel,
    SearchOpinions as OmsOrdersSearchOpinions, Search as OmsOrdersSearch, SearchOpinionsOmsOrdersParamsModel, SearchUnfinished as OmsOrdersSearchUnfinished,
    SearchUnfinishedOmsOrdersParamsModel,
    PostDocumentsCreateOmsOrdersParamsModel, PostDocumentsOmsOrdersParamsModel, PostImagesOmsOrdersParamsModel, PostOmsOrdersParamsModel,
    PostPackagesOmsOrdersParamsModel, PutClientOmsOrdersParamsModel, PutCourierOmsOrdersParamsModel, PutDeliveryAddressOmsOrdersParamsModel, PutDevideOmsOrdersParamsModel,
    PutHandlerOmsOrdersParamsModel, PutOmsOrdersParamsModel, PutPackagesOmsOrdersParamsModel, PutPickupPointOmsOrdersParamsModel,
    PutProductsSerialNumbersOmsOrdersParamsModel, PutProfitMarginOmsOrdersParamsModel, PutShippingCostsOmsOrdersParamsModel,
    PutWarehouseOmsOrdersParamsModel
)
from src.idosell.oms.packages import (
    EventOrderTypeEnum, GetLabels as OmsPackagesGetLabels, OrderPackagesPackagesPostModel, OrderPackagesPackagesPutModel, PackagesPackagesModel, ParcelParametersByPackagesModel,
    ParcelParametersModel, Search as OmsPackagesSearch, PostLabels as OmsPackagesPostLabels, Post as OmsPackagesPost, Put as OmsPackagesPut, SearchOmsPackagesParamsModel,
    PostLabelsOmsPackagesParamsModel, PostOmsPackagesParamsModel, PutOmsPackagesParamsModel
)
from src.idosell.oms.payments import (
    EventSourceTypeEnum, GetForms as OmsPaymentsGetForms, Get as OmsPaymentsGet, GetProfiles as OmsPaymentsGetProfiles, OtherPostModel, OtherPutModel, PaymentsTypeEnum,
    PostCancel as OmsPaymentsPostCancel, PostCashback as OmsPaymentsPostCashback, Post as OmsPaymentsPost, PostRepayment as OmsPaymentsPostRepayment,
    PutConfirm as OmsPaymentsPutConfirm, Put as OmsPaymentsPut, PostCancelOmsPaymentsParamsModel,
    PostCashbackOmsPaymentsParamsModel, PostOmsPaymentsParamsModel, PostRepaymentOmsPaymentsParamsModel, ParamsPaymentsPutModel, SettingsPaymentsPutModel,
    PutOmsPaymentsParamsModel, SourceTypePaymentsEnum
)
from src.idosell.oms.refunds import (
    GetPossibleAuto as OmsRefundsGetPossibleAuto, GetStatus as OmsRefundsGetStatus, GetRetrieveList as OmsRefundsGetRetrieveList,
    PostAddAutomatic as OmsRefundsPostAddAutomatic, PostAddAutomaticForOrder as OmsRefundsPostAddAutomaticForOrder, PostAddManual as OmsRefundsPostAddManual,
    PutCancelRefund as OmsRefundsPutCancelRefund, PutConfirm as OmsRefundsPutConfirm, PutUpdate as OmsRefundsPutUpdate, RefundDetailsPostModel, RefundsSourceTypeEnum, SourceTypeAllEnum, SourceTypeWithOrderEnum,
    PostAddAutomaticOmsRefundsParamsModel, PostAddAutomaticForOrderOmsRefundsParamsModel, PostAddManualOmsRefundsParamsModel, PutCancelRefundOmsRefundsParamsModel,
    PutConfirmOmsRefundsParamsModel, PutOmsRefundsParamsModel
)
from src.idosell.oms.returns import (
    ApiFlagReturnsEnum, Get as OmsReturnsGet, GetStatuses as OmsReturnsGetStatuses,
    Post as OmsReturnsPost, ProductsReturnsPostModel, Put as OmsReturnsPut, PutSerialNumber as OmsReturnsPutSerialNumber,
    PostOmsReturnsParamsModel, PutOmsReturnsParamsModel, PutSerialNumberOmsReturnsParamsModel, ReturnProductsPutModel, ReturnsPutModel, SerialNumberProductsPutModel
)
from src.idosell.oms.rma import Get as OmsRmaGet, GetStatuses as OmsRmaGetStatuses, Put as OmsRmaPut, PutOmsRmaParamsModel, RmaChatModel, RmasModel, StatusIdEnum
from src.idosell.oms.subscriptions import (
    AddProductProductsPostModel,
    BundledProductsModel,
    DateRangeModel,
    DateTimeModel,
    DateTimeRangeModel,
    DeleteProduct as OmsSubscriptionsDeleteProduct,
    DeliveryCostModel,
    DirectionTypeEnum,
    EditProductPostModel,
    FilterModel,
    ListViewFilterModel,
    ListViewOrderByModel,
    ListViewPaginationModel,
    ListViewSelectModel,
    NetPriceModel,
    OrderByDirectionEnum,
    OrderByModel,
    OrderByPropertyEnum,
    OrderDataModel,
    OrderDeliveryModel,
    PaginationModel,
    PaymentDataModel,
    PostAddProduct as OmsSubscriptionsPostAddProduct, PostChangeDeliveryDates as OmsSubscriptionsPostChangeDeliveryDates, PostChangePriceAutoUpdate as OmsSubscriptionsPostChangePriceAutoUpdate,
    PostChangeStatus as OmsSubscriptionsPostChangeStatus, PostEdit as OmsSubscriptionsPostEdit, PostEditProduct as OmsSubscriptionsPostEditProduct,
    PostItemsList as OmsSubscriptionsPostItemsList, PostListViewFetchIds as OmsSubscriptionsPostListViewFetchIds, PostListViewList as OmsSubscriptionsPostListViewList,
    PostSetRebateCode as OmsSubscriptionsPostSetRebateCode, PostUnsetRebateCode as OmsSubscriptionsPostUnsetRebateCode,
    PriceChangeModeEnum,
    PriceModel,
    ProductAddModel,
    PropertyTypeEnum,
    QuantityModel,
    RebatesThresholdModel,
    SetRebateCodeRequestPostModel,
    SubscriptionDeleteProducts, AddProducts,
    SubscriptionModel, SubscriptionsDeliveryDatesModel, SubscriptionsAutoPriceModel,
    SubscriptionsStatusEnum, SubscriptionsStatusModel, SubscriptionsEditRequest,
    SubscriptionEditProducts, ItemsListRequestPostModel, ListViewFetchIdsFilterPostModel, ListViewListRequestPostModel,
    SubscriptionsTypeEnum, UnsetRebateCodeRequestPostModel,
    ValueModel
)

oms_delete: List[Any] = [ # type: ignore
    OmsOrdersDeleteDocuments(
        params = DeleteDocumentsOmsOrdersParamsModel(
            documents = [DocumentsDeleteModel(orderSerialNumber = 1, id = 1)]
        )
    ),
    OmsOrdersDeleteImages(
        params = DeleteImagesOmsOrdersParamsModel(
            order = ImagesOrderModel(orderId = '1', orderSerialNumber = 1),
            images = [ImagesDeleteModel(id = 1)]
        )
    ),
    OmsSubscriptionsDeleteProduct(
        subscriptionDeleteProducts = SubscriptionDeleteProducts(subscriptionId = 1, idsToDelete = [1])
    ),
]

oms_get: List[Any] = [ # type: ignore
    OmsOrdersGetAnalytics(), # type: ignore
    OmsOrdersGetAuctionDetails(), # type: ignore
    OmsOrdersGetDocuments(
        orderSerialNumber = ['1'],
        documentType = DocumentTypeOrdersGetEnum.SALES_CONFIRMATION
    ), # type: ignore
    # OmsOrdersGetExportdocumentsEPP( # TODO check it out (takes too long time to respond)
    #     dateBegin = '2025-08-25 17:00:00',
    #     dateEnd = '2025-08-26 17:00:00',
    #     applicationType = ApplicationTypeEnum.WFIRMA,
    #     documentType = DocumentTypeEppEnum.INVOICE
    # ), # type: ignore
    OmsOrdersGetExportdocumentsJPK(), # type: ignore
    OmsOrdersGetHandler(
        orderSerialNumber = 1
    ),
    OmsOrdersGetHistory(
        orderSerialNumber = 1
    ),
    OmsOrdersGetImages(
        imageId = 1,
        orderSerialNumber = None
    ),
    OmsOrdersGetLabels(
        orderSerialNumber = 1
    ),
    OmsOrdersGetOpinionsRate(
        id = 1,
        operation = OpinionsRateEnum.POSITIVE
    ),
    OmsOrdersGet(), # type: ignore
    OmsOrdersGetPackages(), # type: ignore
    OmsOrdersGetPrinterDocuments(
        user = 'user',
        printScenarioAction = 'printScenarioAction',
        objectNumber = 'objectNumber',
        objectType = 'objectType',
        printerAccessKey = 'printerAccessKey'
    ), # type: ignore
    OmsOrdersGetProfitability(
        orderSerialNumber = 1
    ),
    OmsOrdersGetWarehouse(
        orderSerialNumber = 1
    ),
    OmsPackagesGetLabels(
        eventId = 1,
        eventType = EventOrderTypeEnum.ORDER
    ),
    OmsPaymentsGetForms(), # type: ignore
    OmsPaymentsGet(
        paymentNumber = '1234-1',
        sourceType = EventSourceTypeEnum.ORDER
    ),
    OmsPaymentsGetProfiles(), # type: ignore
    OmsRefundsGetPossibleAuto(
        sourceId = 1,
        sourceType = SourceTypeWithOrderEnum.ORDER
    ),
    OmsRefundsGetStatus(
        sourceId = 1,
        paymentId = 1,
        sourceType = SourceTypeWithOrderEnum.ORDER
    ),
    OmsRefundsGetRetrieveList(
        sourceType = SourceTypeAllEnum.ORDER
    ), # type: ignore
    OmsReturnsGet(), # type: ignore
    OmsReturnsGetStatuses(), # type: ignore
    OmsRmaGet(), # type: ignore
    OmsRmaGetStatuses(), # type: ignore
]

oms_post: List[Any] = [ # type: ignore
    OmsOrdersPostDocumentsCreate(
        params = PostDocumentsCreateOmsOrdersParamsModel(
            orderSerialNumbers = [1],
            actualize = False,
            documentType = DocumentTypePostEnum.VAT_INVOICE,
            documentIssuedDate = 'Document issued date',
            documentPurchaseDate = 'Document purchase date',
            printerId = 1
        )
    ),
    OmsOrdersPostDocuments(
        params = PostDocumentsOmsOrdersParamsModel(
            documents = [DocumentsPostModel(
                orderSerialNumber = 1,
                name = "test.pdf",
                pdfBase64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                type = TypeEnum.VAT_INVOICE,
                returnedInOrderDetails = BooleanStrShortEnum.YES,
                additionalData = None
            )]
        )
    ),
    OmsOrdersPostImages(
        params = PostImagesOmsOrdersParamsModel(
            userName = 'Login',
            settings = ImagesSettingsPostModel(
                sourceType = SourceTypeEnum.BASE64
            ),
            order = ImagesOrderModel(
                orderId = '1',
                orderSerialNumber = 1
            ),
            images = ImagesImagesPostModel(
                type = ImagesTypeEnum.PRODUCT,
                source = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
                name = 'test_image.jpg'
            )
        )
    ),
    OmsOrdersPost(
        params = PostOmsOrdersParamsModel(
            orders = OrdersPostModel(
                orderType = OrderTypeEnum.RETAIL,
                shopId = 1,
                stockId = 1,
                orderPaymentType = OrderPaymentTypeEnum.PREPAID,
                currencyId = 'PLN',
                clientWithoutAccount = BooleanStrShortEnum.YES,
                clientWithoutAccountData = ClientWithoutAccountDataModel(
                    clientFirstName = 'John',
                    clientLastName = 'Doe',
                    clientFirm = 'Firm',
                    clientNip = 'NIP',
                    clientStreet = 'Street',
                    clientZipCode = '12345',
                    clientCity = 'City',
                    clientCountry = 'PL',
                    clientEmail = 'email@example.com',
                    clientPhone1 = '123456789',
                    clientPhone2 = '987654321',
                    langId = 'pl'
                ),
                clientLogin = 'clientLogin',
                clientNoteToOrder = 'clientNoteToOrder',
                clientNoteToCourier = 'clientNoteToCourier',
                affiliateId = 1,
                courierId = 1,
                pickupPointId = 'pickupPointId',
                deliveryCost = 1,
                clientDeliveryAddress = ClientDeliveryAddressModel(
                    clientDeliveryAddressFirstName = 'Recipients first name',
                    clientDeliveryAddressLastName = 'Recipients last name',
                    clientDeliveryAddressAdditional = 'Additional information',
                    clientDeliveryAddressStreet = 'Recipient street and number',
                    clientDeliveryAddressZipCode = 'Recipients postal code',
                    clientDeliveryAddressCity = 'Recipients city',
                    clientDeliveryAddressCountry = 'Recipients country',
                    clientDeliveryAddressPhone = 'Consignees phone number'
                ),
                payerAddress = PayerAddressModel(
                    payerAddressFirstName = 'Payer First Name',
                    payerAddressLastName = 'Payer Last Name',
                    payerAddressFirm = 'Payer Firm',
                    payerAddressNip = 'Payer NIP',
                    payerAddressStreet = 'Payer Street',
                    payerAddressZipCode = 'Payer Zip Code',
                    payerAddressCity = 'Payer City',
                    payerAddressCountryId = 'PL',
                    payerAddressPhone = 'Payer Phone',
                    payerAddressId = 1
                ),
                products = ProductsModel(
                    productId = 1,
                    sizeId = 'Size identifier',
                    productSizeCodeExternal = 'External product system code for size',
                    stockId = 1,
                    productQuantity = 1,
                    productRetailPrice = 1,
                    productFree = False,
                    forceLoyaltyPoints = 1,
                    productVat = 1,
                    productVatFree = BooleanStrShortEnum.NO,
                    discountCode = DiscountCodeModel(
                        name = 'Discount code name'
                    ),
                    remarksToProduct = 'Clients remarks on product',
                    label = 'Label for grouping products',
                    productBundleItems = ProductBundleItemsModel(
                        productId = 1,
                        sizeId = 'Size identifier',
                        sizePanelName = 'Size name',
                        productIndex = 'One of the unique, indexed product codes (IAI code / External system code / Producer code)'
                    )
                ),
                orderRebateValue = 1,
                orderOperatorLogin = 'orderOperatorLogin',
                ignoreBridge = True,
                settings = SettingsModel(
                    settingSendMail = False,
                    settingSendSMS = False
                ),
                orderSettledAtPrice = OrderSettledAtPriceEnum.NET,
                clientRequestInvoice = ClientRequestInvoiceEnum.N,
                billingCurrency = 'billingCurrency',
                billingCurrencyRate = 1,
                purchaseDate = 'Sale date. ISO 8602 format'
            )
        )
    ),
    OmsOrdersPostPackages(
        params = PostPackagesOmsOrdersParamsModel(
            orderPackages = OrderPackagesPostPutModel(
                eventId = 'Id',
                eventType = EventTypeEnum.ORDER,
                packages = [PackagesPostPutModel(
                    deliveryPackageId = 1,
                    courierId = 'Courier ID',
                    deliveryPackageNumber = 'Package number',
                    deliveryShippingNumber = 'Consignment number',
                    deliveryPackageParameters = DeliveryPackageParametersModel(
                        productWeight = 100,
                        packagingWeight = 50
                    ),
                    shippingStoreCosts = ShippingStoreCostsModel(
                        amount = 0.0,
                        tax = 0.0
                    )
                )]
            )
        )
    ),
    OmsPackagesPostLabels(
        params = PostLabelsOmsPackagesParamsModel(
            eventId = 1,
            eventType = EventOrderTypeEnum.ORDER,
            parcelParameters = [ParcelParametersModel(
                id = 'Configuration option identifier for the shipment',
                value = 'The value of the configuration option for the shipment'
            )],
            parcelParametersByPackages = [ParcelParametersByPackagesModel(
                packageId = 'Package ID in system',
                parcelParameters = [ParcelParametersModel(
                    id = 'Configuration option identifier for the shipment',
                    value = 'The value of the configuration option for the shipment'
                )]
            )]
        )
    ),
    OmsPackagesPost(
        params = PostOmsPackagesParamsModel(
            orderPackages = [OrderPackagesPackagesPostModel(
                eventId = 1,
                eventType = EventOrderTypeEnum.ORDER,
                parcelParameters = [ParcelParametersModel(
                    id = 'Configuration option identifier for the shipment',
                    value = 'The value of the configuration option for the shipment'
                )],
                parcelParametersByPackages = [ParcelParametersByPackagesModel(
                    packageId = 'Package ID in system',
                    parcelParameters = [ParcelParametersModel(
                        id = 'Configuration option identifier for the shipment',
                        value = 'The value of the configuration option for the shipment'
                    )]
                )]
            )]
        )
    ),
    OmsPaymentsPostCancel(
        params = PostCancelOmsPaymentsParamsModel(
            sourceType = EventSourceTypeEnum.ORDER,
            paymentNumber = 'Payment number - [order no.]-[payment no.], i.e. 1234-1'
        )
    ),
    OmsPaymentsPostCashback(
        params = PostCashbackOmsPaymentsParamsModel(
            sourceType = SourceTypePaymentsEnum.ORDER,
            paymentNumber = 'Payment number - [order no.]-[payment no.], i.e. 1234-1',
            value = 1
        )
    ),
    OmsPaymentsPost(
        params = PostOmsPaymentsParamsModel(
            sourceId = 1,
            sourceType = EventSourceTypeEnum.ORDER,
            value = 1,
            account = 'Number of a bank account to which a payment is sent',
            type = PaymentsTypeEnum.PAYMENT,
            paymentFormId = 1,
            paymentVoucherKey = 'Gift card or voucher number',
            giftCardPIN = 1,
            externalPaymentId = 'Transaction ID in external service'
        )
    ),
    OmsPaymentsPostRepayment(
        params = PostRepaymentOmsPaymentsParamsModel(
            sourceId = 1,
            source_type = 'Defines payment category. For the payments regarding returns...',
            value = 1,
            payment_form_id = 1, # TODO checkit out
            account = 'Number of a bank account to which a payment is sent',
            client_account = 'Customer account',
            other = OtherPostModel(
                system = 1,
                number = 'Number',
                month = 1,
                year = 2025,
                securityCode = 'Security code',
                name = 'Name'
            )
        )
    ),
    OmsRefundsPostAddAutomatic(
        params = PostAddAutomaticOmsRefundsParamsModel(
            sourceType = RefundsSourceTypeEnum.RETURN,
            sourceId = 1
        )
    ),
    OmsRefundsPostAddAutomaticForOrder(
        params = PostAddAutomaticForOrderOmsRefundsParamsModel(
            sourceId = 1,
            refundValue = 1,
            paymentId = 1,
            refundCurrency = 'Payment currency'
        )
    ),
    OmsRefundsPostAddManual(
        params = PostAddManualOmsRefundsParamsModel(
            sourceType = SourceTypeWithOrderEnum.ORDER,
            sourceId = 1,
            refundValue = 1,
            refundCurrency = 'Payment currency',
            refundDetails = RefundDetailsPostModel(
                paymentFormId = 1,
                paymentSystem = 1,
                account = 'Account number',
                clientAccount = 'Client account number'
            )
        )
    ),
    OmsReturnsPost(
        params = PostOmsReturnsParamsModel(
            order_sn = 1,
            stock_id = 1,
            products = [ProductsReturnsPostModel(
                id = 1,
                size = 'size',
                quantity = 1,
                price = 1,
                serialNumbers = ['serialNumbers'],
                productOrderAdditional = 'Additional information'
            )],
            status = 1,
            client_received = False,
            change_status = False,
            courier_id = 1,
            return_operator = 'return_operator',
            tryCorrectInvoice = False,
            include_shipping_cost = 'include_shipping_cost',
            additional_payment_cost = 'additional_payment_cost',
            emptyReturn = 'emptyReturn'
        )
    ),
    OmsSubscriptionsPostAddProduct(
        addProducts = AddProducts(
            subscriptionId = 1,
            products = [AddProductProductsPostModel(
                subscriptionId = 1,
                products = [ProductAddModel(
                    productId = 1,
                    sizeId = 'ID of size',
                    quantity = QuantityModel(
                        value = 'A decimal'
                    ),
                    bundledProducts = [BundledProductsModel(
                        productId = 1,
                        sizeId = 'ID of size',
                        quantity = QuantityModel(
                            value = 'A decimal'
                        ),
                        bundledProducts = None,
                        comment = 'Comment for product',
                        splitBundleInOrderDocuments = False
                    )],
                    comment = 'Comment for product',
                    splitBundleInOrderDocuments = False
                )]
            )]
        )
    ),
    OmsSubscriptionsPostChangeDeliveryDates(
        subscriptionsDeliveryDatesModel = SubscriptionsDeliveryDatesModel(
            subscriptionIds = [1],
            upcomingDeliveryDate = 'Settings that determinates if price should be updated automaticly',
            changeNextDeliveryDate = False
        )
    ),
    OmsSubscriptionsPostChangePriceAutoUpdate(
        subscriptionsAutoPriceModel = SubscriptionsAutoPriceModel(
            subscriptionIds = [1],
            autoPriceUpdate = False
        )
    ),
    OmsSubscriptionsPostChangeStatus(
        subscriptionsStatusModel = SubscriptionsStatusModel(
            subscriptionIds = [1],
            subscriptionStatus = SubscriptionsStatusEnum.ACTIVE,
            sendMailAfterStatusChange = False,
            sendSMSAfterStatusChange = False
        )
    ),
    OmsSubscriptionsPostEdit(
        subscriptionsEditRequest = SubscriptionsEditRequest(
            subscriptionModels = [SubscriptionModel(
                id = 1,
                externalId = 'Subscription ID for external service',
                status = SubscriptionsStatusEnum.ACTIVE,
                subscriptionNote = 'Note to subscription (internal)',
                upcomingDeliveryDate = None,
                priceAutoUpdate = False,
                nextDeliveryDate = None,
                daysInPeriod = None,
                sendMailAfterStatusChange = False,
                sendSMSAfterStatusChange = False,
                orderData = OrderDataModel(
                    deliveryCost = DeliveryCostModel(
                        value = '0.00'
                    ),
                    orderDelivery = OrderDeliveryModel(
                        courierNote = 'Note for courier',
                        pickupPointId = 'Pickup points identifier',
                        deliveryFormId = 1,
                        deliveryAddressId = 1
                    ),
                    payerAddressId = 1,
                    noteToStaff = 'Note to stuff'
                ),
                rebatesThresholds = [RebatesThresholdModel(
                    numberFrom = 1,
                    numberTo = 1,
                    type = SubscriptionsTypeEnum.PERCENTAGE,
                    value = ValueModel(
                        value = 'A decimal'
                    )
                )],
                paymentData = PaymentDataModel(
                    externalPaymentId = 'ID of external payment',
                    externalPaymentHandle = 'Handle for external payment'
                )
            )]
        )
    ),
    OmsSubscriptionsPostEditProduct(
        subscriptionEditProducts = SubscriptionEditProducts(
            subscriptionId = 1,
            products = [EditProductPostModel(
                id = 1,
                variantId = 1,
                variantSizeId = 'variantSizeId',
                quantity = QuantityModel(
                    value = 'A decimal'
                ),
                price = PriceModel(
                    value = 'A decimal'
                ),
                netPrice = NetPriceModel(
                    value = 'A decimal'
                ),
                label = 'Label to the product'
            )]
        )
    ),
    OmsSubscriptionsPostItemsList(
        request = ItemsListRequestPostModel(
            filter = FilterModel(
                id = 1
            ),
            orderBy = OrderByModel(
                property = PropertyTypeEnum.ID,
                direction = DirectionTypeEnum.DESC

            ),
            pagination = PaginationModel(
                page = 0,
                perPage = 5
            )
        )
    ),
    OmsSubscriptionsPostListViewFetchIds(
        filter = ListViewFetchIdsFilterPostModel(
            ids = [1],
            statuses = ['Subscription statuses'],
            clientId = 1,
            shopId = 1,
            priceChangeMode = PriceChangeModeEnum.MANUAL,
            createDateTime = DateTimeRangeModel(**{"from": datetime(2025, 1, 1, 0, 0, 0), "to": datetime(2025, 12, 31, 23, 59, 59)}),
            finishDateTime = DateTimeRangeModel(**{"from": datetime(2025, 1, 1, 0, 0, 0), "to": datetime(2025, 12, 31, 23, 59, 59)}),
            upcomingDeliveryDate = DateRangeModel(**{"from": date(2025, 1, 1), "to": date(2025, 12, 31)}),
            nextDeliveryDate = DateRangeModel(**{"from": date(2025, 1, 1), "to": date(2025, 12, 31)}),
            textSearch = 'Text search phrase'
        )
    ),
    OmsSubscriptionsPostListViewList(
        request = ListViewListRequestPostModel(
            select = ListViewSelectModel(
                productsData = False,
                rebatesThresholds = False,
                rebateCode = False,
                paymentData = False,
                clientBillingData = False,
                orderDeliveryAddress = False,
                courierData = False,
                payerAddress = False
            ),
            filter = ListViewFilterModel(
                ids = [1],
                statuses = ['Subscription statuses'],
                clientId = 1,
                shopId = 1,
                priceChangeMode = PriceChangeModeEnum.MANUAL,
                createDateTime = DateTimeModel(
                    **{"from": time(0, 0, 0), "to": time(23, 59, 59)}
                ),
                finishDateTime = DateTimeModel(
                    **{"from": time(0, 0, 0), "to": time(23, 59, 59)}
                ),
                upcomingDeliveryDate = DateTimeModel(
                    **{"from": time(0, 0, 0), "to": time(23, 59, 59)}
                ),
                nextDeliveryDate = DateTimeModel(
                    **{"from": time(0, 0, 0), "to": time(23, 59, 59)}
                ),
                textSearch = 'Text search phrase'
            ),
            orderBy = ListViewOrderByModel(
                property = OrderByPropertyEnum.STATUS,
                orderByDirection = OrderByDirectionEnum.DESC
            ),
            pagination = ListViewPaginationModel(
                page = 0,
                perPage = 5
            )
        )
    ),
    OmsSubscriptionsPostSetRebateCode(
        request = SetRebateCodeRequestPostModel(
            id = 1,
            code = 'code'
        )
    ),
    OmsSubscriptionsPostUnsetRebateCode(
        request = UnsetRebateCodeRequestPostModel(
            id = 1
        )
    ),
]

oms_put: List[Any] = [ # type: ignore
    OmsOrdersPutClient(
        params = PutClientOmsOrdersParamsModel(
            orderSerialNumber = 1,
            clientId = 1
        )
    ),
    OmsOrdersPutCourier(
        params = PutCourierOmsOrdersParamsModel(
            orderSerialNumber = 1,
            courierId = 1,
            pickupPointId = 'Collection point ID'
        )
    ),
    OmsOrdersPutDeliveryAddress(
        params = PutDeliveryAddressOmsOrdersParamsModel(
            orderSerialNumber = 1,
            clientDeliveryAddressId = 1,
            clientLogin = 'Customers login'
        )
    ),
    OmsOrdersPutDevide(
        params = PutDevideOmsOrdersParamsModel(
            orderSerialNumber = 1,
            products = [DevideProductsPutModel(
                basketPosition = 1,
                quantity = 1
            )],
            splitPayments = False
        )
    ),
    OmsOrdersPutHandler(
        params = PutHandlerOmsOrdersParamsModel(
            orderSerialNumber = 1,
            orderOperatorLogin = 'Order handler'
        )
    ),
    OmsOrdersPut(
        params = PutOmsOrdersParamsModel(
            orders = OrdersPutModel(
                orderId = 'Order ID',
                orderSerialNumber = 1,
                orderStatus = OrderStatusEnum.CANCELED,
                apiFlag = ApiFlagEnum.NONE,
                apiNoteToOrder = 'API note added to order',
                clientNoteToOrder = 'Customer comments on order',
                clientNoteToCourier = 'Customer remarks for courier',
                orderNote = 'Note to the order',
                products = ProductsPutModel(
                    productId = 1,
                    sizeId = 'Size identifier',
                    productSizeCodeExternal = 'External product system code for size',
                    basketPosition = 0,
                    stockId = 1,
                    productFree = False,
                    forceLoyaltyPoints = 0,
                    productQuantity = 0,
                    productQuantityOperationType = ProductQuantityOperationTypeEnum.ADD,
                    productRetailPrice = 0,
                    productVat = 0,
                    productVatFree = BooleanStrShortEnum.YES,
                    remarksToProduct = 'Clients remarks on product',
                    label = 'Label for grouping products',
                    productBundleItems = ProductBundleItemsModel(
                        productId = 1,
                        sizeId = 'sizeId',
                        sizePanelName = 'sizePanelName',
                        productIndex = 'productIndex'
                    ),
                    priceFormulaParameters = [PriceFormulaParametersModel(
                        parameterId = 'Parameter ID',
                        parameterValue = 'parameterValue',
                        parameterValues = [ParameterValuesModel(
                            valueId = 'Value ID'
                        )]
                    )]
                ),
                orderPaymentType = OrderPaymentTypeEnum.CASH_ON_DELIVERY,
                orderSettledAtPrice = OrderSettledAtPriceEnum.GROSS,
                ignoreBridge = True,
                settings = SettingsPutModel(
                    dontSendMail = BooleanStrShortEnum.NO,
                    dontSendSMS = BooleanStrShortEnum.NO
                ),
                emailProcessingConsent = EmailProcessingConsentEnum.DISABLED,
                clientRequestInvoice = ClientRequestInvoiceEnum.Y,
                billingCurrency = 'Order settlement currency',
                billingCurrencyRate = 1,
                purchaseDate = 'Sale date. ISO 8602 format',
                estimatedDeliveryDate = 'Estimated date of shipment of the order in format Y-m-d H:i'
            )
        )
    ),
    OmsOrdersPutPackages(
        params = PutPackagesOmsOrdersParamsModel(
            orderPackages = OrderPackagesPostPutModel(
                eventId = 'Id',
                eventType = EventTypeEnum.ORDER,
                packages = [PackagesPostPutModel(
                    deliveryPackageId = 1,
                    courierId = 'Courier ID',
                    deliveryPackageNumber = 'Package number',
                    deliveryShippingNumber = 'Consignment number',
                    deliveryPackageParameters = DeliveryPackageParametersModel(
                        productWeight = 1,
                        packagingWeight = 1
                    ),
                    shippingStoreCosts = ShippingStoreCostsModel(
                        amount = 0,
                        tax = 0
                    )
                )]
            )
        )
    ),
    OmsOrdersPutPickupPoint(
        params = PutPickupPointOmsOrdersParamsModel(
            orderSerialNumber = 'Order serial number',
            pickupPointId = 'Collection point ID'
        )
    ),
    OmsOrdersPutProductsSerialNumbers(
        params = PutProductsSerialNumbersOmsOrdersParamsModel(
            orders = [ProductsSerialNumbersOrdersPutModel(
                orderSerialNumber = 1,
                orderProducts = [OrderProductsModel(
                    productId = 1,
                    sizeId = 'sizeId',
                    productSerialNumbers = ['Serial numbers']
                )]
            )]
        )
    ),
    OmsOrdersPutProfitMargin(
        params = PutProfitMarginOmsOrdersParamsModel(
            orders = [ProfitMarginOrdersPutModel(
                orderSerialNumber = 1,
                products = [ProductsProfitMarginOrdersPutModel(
                    productIdent = ProductIdentModel(
                        identValue = 'Ident value',
                        productIdentType = ProductIdentTypeEnum.ID
                    ),
                    sizeId = 'sizeId',
                    productProfitMargin = 0,
                    productProfitMarginNet = 0,
                    errors = ErrorsModel(
                        faultCode = None,
                        faultString = None
                    )
                )],
                errors = ErrorsModel(
                    faultCode = None,
                    faultString = None
                ),
                isProductsErrors = True
            )]
        )
    ),
    OmsOrdersPutShippingCosts(
        params = PutShippingCostsOmsOrdersParamsModel(
            orderSerialNumber = 1,
            deliveryCost = 0,
            orderDeliveryVat = 0
        )
    ),
    OmsOrdersPutWarehouse(
        params = PutWarehouseOmsOrdersParamsModel(
            orderSerialNumber = 1,
            stockId = 1,
            orderOperatorLogin = 'Order handler',
            externalStockId = ExternalStockIdEnum.AMAZONPL
        )
    ),
    OmsPackagesPut(
        params = PutOmsPackagesParamsModel(
            orderPackages = [OrderPackagesPackagesPutModel(
                orderId = 'Order ID',
                orderType = EventOrderTypeEnum.ORDER,
                packages = [PackagesPackagesModel(
                    packageId = 1,
                    delivery = 1,
                    packageNumber = 'Package number',
                    shippingNumber = 'shippingNumber',
                    packageParameters = 'packageParameters',
                    shippingStoreCosts = ShippingStoreCostsModel(
                        amount = 0,
                        tax = 0
                    )
                )]
            )]
        )
    ),
    OmsPaymentsPutConfirm(
        params = ParamsPaymentsPutModel(
            sourceType = EventSourceTypeEnum.ORDER,
            paymentNumber = 'Payment number - [order no.]-[payment no.], i.e. 1234-1',
            accountingDate = 'Registering date'
        ),
        settings = SettingsPaymentsPutModel(
            sendMail = False,
            sendSms = False
        )
    ),
    OmsPaymentsPut(
        params = PutOmsPaymentsParamsModel(
            sourceType = EventSourceTypeEnum.ORDER,
            paymentNumber = 'Payment number - [order no.]-[payment no.], i.e. 1234-1',
            paymentFormId = 1,
            value = 1,
            accountingDate = 'Registering date',
            account = 'Number of a bank account to which a payment is sent',
            clientAccount = 'Data of customer account in store',
            other = OtherPutModel(
                system = 1
            ),
            externalPaymentId = 'Transaction ID in external service'
        )
    ),
    OmsRefundsPutCancelRefund(
        params = PutCancelRefundOmsRefundsParamsModel(
            sourceType = SourceTypeWithOrderEnum.ORDER,
            sourceId = 1,
            paymentId = 'Payment ID'
        )
    ),
    OmsRefundsPutConfirm(
        params = PutConfirmOmsRefundsParamsModel(
            sourceType = SourceTypeWithOrderEnum.ORDER,
            sourceId = 1,
            paymentId = 'Payment ID'
        )
    ),
    OmsRefundsPutUpdate(
        params = PutOmsRefundsParamsModel(
            sourceType = SourceTypeWithOrderEnum.ORDER,
            sourceId = 1,
            paymentId = 'Payment ID',
            refundValue = 0,
            refundCurrency = 'Payment currency'
        )
    ),
    OmsReturnsPut(
        params = PutOmsReturnsParamsModel(
            returns = [ReturnsPutModel(
                id = 1,
                status = 1,
                apiFlag = ApiFlagReturnsEnum.NONE,
                products = [ReturnProductsPutModel(
                    id = 1,
                    size = 'size',
                    quantity = 1,
                    price = 1,
                    serialNumbers = ['serialNumbers'],
                    productOrderAdditional = 'productOrderAdditional'
                )],
                userNote = 'userNote',
                clientNote = 'clientNote',
                tryCorrectInvoice = False
            )]
        )
    ),
    OmsReturnsPutSerialNumber(
        params = PutSerialNumberOmsReturnsParamsModel(
            return_id = 1,
            products = [SerialNumberProductsPutModel(
                id = 1,
                size = 'size',
                serialNumbers = ['serialNumbers']
            )]
        )
    ),
    OmsRmaPut(
        params = PutOmsRmaParamsModel(
            rmas = [RmasModel(
                rmaId = 1,
                rmaStatusId = StatusIdEnum.COMPLAINT_CONFIRME,
                rmaChat = [RmaChatModel(
                    message = 'Message content'
                )]
            )]
        )
    ),
]

oms_search: List[Any] = [ # type: ignore
    OmsOrdersSearchOpinions(
        params = SearchOpinionsOmsOrdersParamsModel() # type: ignore
    ),
    OmsOrdersSearch(
        params = SearchOmsOrdersParamsModel() # type: ignore
    ),
    OmsOrdersSearchUnfinished(
        params = SearchUnfinishedOmsOrdersParamsModel() # type: ignore
    ),
    OmsPackagesSearch(
        params = SearchOmsPackagesParamsModel() # type: ignore
    ),
]
