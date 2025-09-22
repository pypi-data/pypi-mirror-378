import pytest
from src.idosell.oms._common import (
    # Enums
    ApiFlagEnum,
    ApplicationTypeEnum,
    AuctionsServicesNamesEnum,
    ClientRequestInvoiceEnum,
    ClientRequestInvoiceSearchUnfinishedEnum,
    ClientsSearchTypeEnum,
    ClientSearchingModeEnum,
    DocumentTypeOrdersGetEnum,
    DocumentTypePostEnum,
    DocumentTypeEppEnum,
    DocumentTypeJpkEnum,
    DropshippingOrderStatusEnum,
    ElementNameOrdersBySearchUnfinshedEnum,
    EmailProcessingConsentEnum,
    EventTypeEnum,
    ExternalStockIdEnum,
    IdentTypeEnum,
    ImagesTypeEnum,
    LoyaltyPointsModeEnum,
    OpinionsRateEnum,
    OrderPaymentTypeEnum,
    OrderPrepaidStatusEnum,
    OrdersDateTypeEnum,
    OrdersDatesTypesEnum,
    OrdersSearchTypeEnum,
    OrderSettledAtPriceEnum,
    OrderStatusEnum,
    OrdersStatusesEnum,
    OrdersStatusesSearchUnfinishedEnum,
    OrderTypeEnum,
    OrderTypeSearchUnfinishedEnum,
    ProductIdentTypeEnum,
    ProductQuantityOperationTypeEnum,
    SearchingOperatorTypeMatchEnum,
    ShippmentStatusEnum,
    SourceTypeEnum,
    TypeEnum,
    # DTOs
    ShippingStoreCostsModel,
    AdditionalDataModel,
    AuctionsParamsModel,
    AuctionsAccountsModel,
    AuctionsClientsModel,
    CampaignSearchModel,
    ClientDeliveryAddressModel,
    ClientWithoutAccountDataModel,
    ClientsModel,
    ClientsSearchModel,
    ClientsSearchUnfinishedModel,
    DateRangeSearchModel,
    DeliveryPackageParametersModel,
    DevideProductsPutModel,
    DiscountCodeModel,
    DocumentsDeleteModel,
    DocumentsPostModel,
    ErrorsModel,
    ImagesDeleteModel,
    ImagesOrderModel,
    ImagesImagesPostModel,
    ImagesSettingsPostModel,
    OpinionSearchModel,
    OrdersSearchModel,
    OrderBySearchModel,
    OrderProductsModel,
    OrderSourceModel,
    OrderSourceSearchUnfinishedModel,
    OrdersDateRangeModel,
    OrdersSerialNumberRangeModel,
    OrdersRangeModel,
    OrdersBySearchUnfinishedModel,
    PackagesPostPutModel,
    PackagesSearchModel,
    PackagesSearchUnfinishedModel,
    ParameterValuesModel,
    PayerAddressModel,
    ProductBundleItemsModel,
    PriceFormulaParametersModel,
    ProductsModel,
    ProductsPutModel,
    ProductsSerialNumbersOrdersPutModel,
    ProductIdentModel,
    ProductsProfitMarginOrdersPutModel,
    ProfitMarginOrdersPutModel,
    ProductsSearchModel,
    SettingsModel,
    SettingsPutModel,
    StocksSearachModel,
)
from src.idosell._common import BooleanStrShortEnum, ElementNameSearchEnum, SortDirectionSearchEnum


class TestEnums:
    def test_api_flag_enum_values(self):
        expected = {'NONE', 'REGISTERED', 'REALIZED', 'REGISTERED_POS', 'REALIZED_POS', 'REGISTRATION_FAULT'}
        assert set(ApiFlagEnum.__members__.keys()) == expected

    def test_application_type_enum_values(self):
        expected = {'SUBIEKTGT', 'RACHMISTRZ', 'WFIRMA'}
        assert set(ApplicationTypeEnum.__members__.keys()) == expected

    def test_auctions_services_names_enum_values(self):
        expected = {'ALLEGRO', 'TESTWEBAPI', 'EBAY'}
        assert set(AuctionsServicesNamesEnum.__members__.keys()) == expected

    def test_client_request_invoice_enum_values(self):
        expected = {'Y', 'E', 'N'}
        assert set(ClientRequestInvoiceEnum.__members__.keys()) == expected

    def test_client_request_invoice_search_unfinished_enum_values(self):
        expected = {'INVOICE', 'E_INVOICE', 'N'}
        assert set(ClientRequestInvoiceSearchUnfinishedEnum.__members__.keys()) == expected

    def test_clients_search_type_enum_values(self):
        expected = {'ID', 'LOGIN', 'CODEEXTERN'}
        assert set(ClientsSearchTypeEnum.__members__.keys()) == expected

    def test_client_searching_mode_enum_values(self):
        expected = {'BILLING_DATA', 'DELIVERY_DATA', 'BILLING_DELIVERY_DATA'}
        assert set(ClientSearchingModeEnum.__members__.keys()) == expected

    def test_document_type_orders_get_enum_values(self):
        expected = {'SALES_CONFIRMATION', 'VAT_INVOICE', 'CORRECTIVE_VAT_INVOICE', 'ADVANCE_VAT_INVOICE',
                   'FINAL_ADVANCE_VAT_INVOICE', 'PRO_FORMA_INVOICE', 'ADVANCE_PRO_FORMA_INVOICE',
                   'FINAL_ADVANCE_PRO_FORMA_INVOICE', 'DELIVERY_NOTE', 'FISCAL_RECEIPT', 'FISCAL_INVOICE', 'OTHER'}
        assert set(DocumentTypeOrdersGetEnum.__members__.keys()) == expected

    def test_document_type_post_enum_values(self):
        expected = {'VAT_INVOICE', 'FISCAL_INVOICE', 'CORRECTIVE_VAT_INVOICE', 'FISCAL_RECEIPT', 'SALES_CONFIRMATION'}
        assert set(DocumentTypePostEnum.__members__.keys()) == expected

    def test_document_type_epp_enum_values(self):
        expected = {'ALL', 'STOCKS', 'INVOICE', 'PAYMENTS'}
        assert set(DocumentTypeEppEnum.__members__.keys()) == expected

    def test_document_type_jpk_enum_values(self):
        expected = {'JPK_FA', 'JPK_MAG', 'JPK_VAT'}
        assert set(DocumentTypeJpkEnum.__members__.keys()) == expected

    def test_dropshipping_order_status_enum_values(self):
        expected = {'ALL', 'FINISHED', 'CANCELED', 'NOTCANCELED'}
        assert set(DropshippingOrderStatusEnum.__members__.keys()) == expected

    def test_element_name_orders_by_search_unfinished_enum_values(self):
        expected = ['ID', 'SN', 'ORDER_TIME', 'STATUS', 'ORDER_SOURCE', 'ORDER_COST',
                   'DISCOUNT_CODE', 'READY_TO_SEND_DATE']
        assert sorted(list(ElementNameOrdersBySearchUnfinshedEnum.__members__.keys())) == sorted(expected)

    def test_email_processing_consent_enum_values(self):
        expected = {'YES', 'NO', 'DISABLED'}
        assert set(EmailProcessingConsentEnum.__members__.keys()) == expected

    def test_event_type_enum_values(self):
        expected = {'ORDER', 'RMA', 'RETURN'}
        assert set(EventTypeEnum.__members__.keys()) == expected

    def test_external_stock_id_enum_values(self):
        expected = ['AMAZONDE', 'AMAZONES', 'AMAZONFR', 'AMAZONIT', 'AMAZONCOUK', 'AMAZONNL', 'AMAZONSE',
                   'AMAZONCOMTR', 'AMAZONAE', 'AMAZONUS', 'AMAZONPL']
        assert sorted(list(ExternalStockIdEnum.__members__.keys())) == sorted(expected)

    def test_ident_type_enum_values(self):
        expected = {'ORDERS_ID', 'ORDERS_SN'}
        assert set(IdentTypeEnum.__members__.keys()) == expected

    def test_images_type_enum_values(self):
        expected = {'PRODUCT', 'PACKAGE'}
        assert set(ImagesTypeEnum.__members__.keys()) == expected

    def test_loyalty_points_mode_enum_values(self):
        expected = {'ALL', 'GIVEN', 'TAKEN', 'GIVEN_OR_TAKEN', 'GIVEN_AND_TAKEN', 'NOT_GIVEN_NOR_TAKEN'}
        assert set(LoyaltyPointsModeEnum.__members__.keys()) == expected

    def test_opinions_rate_enum_values(self):
        expected = {'POSITIVE', 'NEGATIVE'}
        assert set(OpinionsRateEnum.__members__.keys()) == expected

    def test_order_payment_type_enum_values(self):
        expected = {'CASH_ON_DELIVERY', 'PREPAID', 'TRADECREDIT'}
        assert set(OrderPaymentTypeEnum.__members__.keys()) == expected

    def test_order_prepay_status_enum_values(self):
        expected = {'UNPAID', 'RESTORED', 'WAITING'}
        assert set(OrderPrepaidStatusEnum.__members__.keys()) == expected

    def test_orders_date_type_enum_values(self):
        expected = {'ADD', 'MODIFIED', 'DISPATCH', 'PAYMENT', 'LAST_PAYMENTS_OPERATION', 'DECLARED_PAYMENTS'}
        assert set(OrdersDateTypeEnum.__members__.keys()) == expected

    def test_orders_dates_types_enum_values(self):
        expected = {'ADD', 'MODIFIED', 'DISPATCH', 'PAYMENT', 'LAST_PAYMENTS_OPERATION', 'DECLARED_PAYMENTS'}
        assert set(OrdersDatesTypesEnum.__members__.keys()) == expected

    def test_orders_search_type_enum_values(self):
        expected = {'ID', 'SERIALNUMBER'}
        assert set(OrdersSearchTypeEnum.__members__.keys()) == expected

    def test_order_settled_at_price_enum_values(self):
        expected = {'GROSS', 'NET', 'NET_WITHOUT_VAT'}
        assert set(OrderSettledAtPriceEnum.__members__.keys()) == expected

    def test_order_status_enum_values(self):
        expected = ['FINISHED_EXT', 'FINISHED', 'NEW', 'PAYMENT_WAITING', 'DELIVERY_WAITING',
                   'ON_ORDER', 'PACKED', 'PACKED_FULFILLMENT', 'PACKED_READY', 'READY',
                   'WAIT_FOR_DISPATCH', 'SUSPENDED', 'JOINED', 'MISSING', 'LOST', 'FALSE', 'CANCELED']
        assert sorted(list(OrderStatusEnum.__members__.keys())) == sorted(expected)

    def test_orders_statuses_enum_values(self):
        expected = ['NEW', 'FINISHED', 'FALSE', 'LOST', 'ON_ORDER', 'PACKED', 'READY',
                   'CANCELED', 'PAYMENT_WAITING', 'DELIVERY_WAITING', 'SUSPENDED', 'JOINED', 'FINISHED_EXT']
        assert sorted(list(OrdersStatusesEnum.__members__.keys())) == sorted(expected)

    def test_order_type_enum_values(self):
        expected = {'RETAIL', 'WHOLESALE'}
        assert set(OrderTypeEnum.__members__.keys()) == expected

    def test_order_type_search_unfinished_enum_values(self):
        expected = {'RETAIL', 'WHOLESALE', 'DROPSHIPPING', 'DELIVERER'}
        assert set(OrderTypeSearchUnfinishedEnum.__members__.keys()) == expected

    def test_product_ident_type_enum_values(self):
        expected = {'ID', 'INDEX', 'CODEEXTERN'}
        assert set(ProductIdentTypeEnum.__members__.keys()) == expected

    def test_product_quantity_operation_type_enum_values(self):
        expected = {'ADD', 'SUBTRACT'}
        assert set(ProductQuantityOperationTypeEnum.__members__.keys()) == expected

    def test_searching_operator_type_match_enum_values(self):
        expected = {'NO_ASSIGNMENT', 'NO_EMPTY', 'EMPTY'}
        assert set(SearchingOperatorTypeMatchEnum.__members__.keys()) == expected

    def test_shippment_status_enum_values(self):
        expected = {'ALL', 'RECEIVED', 'NON_RECEIVED'}
        assert set(ShippmentStatusEnum.__members__.keys()) == expected

    def test_source_type_enum_values(self):
        expected = {'BASE64', 'URL'}
        assert set(SourceTypeEnum.__members__.keys()) == expected

    def test_type_enum_values(self):
        expected = {'VAT_INVOICE', 'CORRECTIVE_VAT_INVOICE', 'OTHER'}
        assert set(TypeEnum.__members__.keys()) == expected

    def test_orders_statuses_search_unfinished_enum_values(self):
        expected = ['NEW', 'ON_ORDER', 'PACKED', 'PACKED_FULLFILMENT', 'PACKED_READY', 'READY',
                   'PAYMENT_WAITING', 'DELIVERY_WAITING', 'WAIT_FOR_DISPATCH', 'SUSPENDED', 'FINISHED_EXT']
        assert sorted(list(OrdersStatusesSearchUnfinishedEnum.__members__.keys())) == sorted(expected)


class TestCommonDTOs:
    def test_shipping_store_costs_model(self):
        model = ShippingStoreCostsModel(amount=10.0, tax=2.0)
        assert model.amount == 10.0
        assert model.tax == 2.0

    def test_shipping_store_costs_model_validation_negative(self):
        with pytest.raises(ValueError):
            ShippingStoreCostsModel(amount=-1.0, tax=2.0)

    def test_additional_data_model(self):
        model = AdditionalDataModel(
            documentId="DOC123",
            documentIssuedDate="2023-01-01"
        )
        assert model.documentId == "DOC123"
        assert model.documentIssuedDate == "2023-01-01"

    def test_discount_code_model(self):
        model = DiscountCodeModel(name="DISCOUNT10")
        assert model.name == "DISCOUNT10"

    def test_images_delete_model(self):
        model = ImagesDeleteModel(id=1)
        assert model.id == 1

        with pytest.raises(ValueError):
            ImagesDeleteModel(id=0)  # ge=1

    def test_images_images_post_model(self):
        model = ImagesImagesPostModel(
            type=ImagesTypeEnum.PRODUCT,
            source="base64string",
            name="test.jpg"
        )
        assert model.type == ImagesTypeEnum.PRODUCT
        assert model.source == "base64string"
        assert model.name == "test.jpg"

    def test_orders_search_model(self):
        model = OrdersSearchModel(
            type=OrdersSearchTypeEnum.ID,
            value="123"
        )
        assert model.type == OrdersSearchTypeEnum.ID
        assert model.value == "123"

    def test_date_range_search_model(self):
        model = DateRangeSearchModel(
            begin="2023-01-01",
            end="2023-12-31"
        )
        assert model.begin == "2023-01-01"
        assert model.end == "2023-12-31"

    def test_devide_products_put_model(self):
        model = DevideProductsPutModel(basketPosition=1, quantity=2.5)
        assert model.basketPosition == 1
        assert model.quantity == 2.5

        with pytest.raises(ValueError):
            DevideProductsPutModel(basketPosition=1, quantity=-1.0)  # gt=0

    def test_packets_search_model(self):
        model = PackagesSearchModel(
            packagesNumbers=["PKG1", "PKG2"],
            orderHasPackageNumbers=BooleanStrShortEnum.YES,
            hasMultiPackages=BooleanStrShortEnum.NO
        )
        assert model.packagesNumbers == ["PKG1", "PKG2"]
        assert model.orderHasPackageNumbers == BooleanStrShortEnum.YES
        assert model.hasMultiPackages == BooleanStrShortEnum.NO

    def test_stocks_search_model(self):
        model = StocksSearachModel(stockId=1)
        assert model.stockId == 1

        with pytest.raises(ValueError):
            StocksSearachModel(stockId=0)  # ge=1

    def test_auctions_params_model(self):
        model = AuctionsParamsModel(auctionsServicesNames=[])
        assert model.auctionsServicesNames == []

    def test_auctions_accounts_model(self):
        model = AuctionsAccountsModel(
            auctionsAccountId=1,
            auctionsAccountLogin="test@example.com"
        )
        assert model.auctionsAccountId == 1
        assert model.auctionsAccountLogin == "test@example.com"

    def test_auctions_clients_model(self):
        model = AuctionsClientsModel(
            auctionClientId="CL123",
            auctionClientLogin="auction_user"
        )
        assert model.auctionClientId == "CL123"
        assert model.auctionClientLogin == "auction_user"

    def test_campaign_search_model(self):
        model = CampaignSearchModel(
            campaignId=123,
            discountCodes=["DISC1", "DISC2"]
        )
        assert model.campaignId == 123
        assert model.discountCodes == ["DISC1", "DISC2"]

    def test_client_delivery_address_model(self):
        model = ClientDeliveryAddressModel(
            clientDeliveryAddressFirstName="John",
            clientDeliveryAddressLastName="Doe",
            clientDeliveryAddressAdditional="Apt 1",
            clientDeliveryAddressStreet="Main St 123",
            clientDeliveryAddressZipCode="12345",
            clientDeliveryAddressCity="Warsaw",
            clientDeliveryAddressCountry="PL",
            clientDeliveryAddressPhone="123-456-789"
        )
        assert model.clientDeliveryAddressFirstName == "John"
        assert model.clientDeliveryAddressLastName == "Doe"

    def test_delivery_package_parameters_model(self):
        model = DeliveryPackageParametersModel(
            productWeight=100,
            packagingWeight=50
        )
        assert model.productWeight == 100
        assert model.packagingWeight == 50

    def test_documents_delete_model(self):
        model = DocumentsDeleteModel(orderSerialNumber=123, id=456)
        assert model.orderSerialNumber == 123
        assert model.id == 456

        with pytest.raises(ValueError):
            DocumentsDeleteModel(orderSerialNumber=0, id=1)  # ge=1

    def test_errors_model(self):
        model = ErrorsModel(faultCode=500, faultString="Internal Server Error")
        assert model.faultCode == 500
        assert model.faultString == "Internal Server Error"

    def test_images_order_model(self):
        model = ImagesOrderModel(
            orderId="ORD123",
            orderSerialNumber=123
        )
        assert model.orderId == "ORD123"
        assert model.orderSerialNumber == 123

    def test_images_settings_post_model(self):
        model = ImagesSettingsPostModel(sourceType=SourceTypeEnum.BASE64)
        assert model.sourceType == SourceTypeEnum.BASE64

    def test_opinion_search_model(self):
        model = OpinionSearchModel(
            id=1,
            language="pl",
            confirmed=True,
            host="example.com",
            shopId=1
        )
        assert model.id == 1
        assert model.language == "pl"
        assert model.confirmed

    def test_order_by_search_model(self):
        model = OrderBySearchModel(
            elementName=ElementNameSearchEnum.ID,
            sortDirection=SortDirectionSearchEnum.ASC
        )
        assert model.elementName == ElementNameSearchEnum.ID
        assert model.sortDirection == SortDirectionSearchEnum.ASC

    def test_order_products_model(self):
        model = OrderProductsModel(
            productId=1,
            sizeId="S",
            productSerialNumbers=["SN1", "SN2"]
        )
        assert model.productId == 1
        assert model.sizeId == "S"
        assert model.productSerialNumbers == ["SN1", "SN2"]

    def test_orders_date_range_model(self):
        model = OrdersDateRangeModel(
            ordersDateType=OrdersDateTypeEnum.ADD,
            ordersDatesTypes=[OrdersDatesTypesEnum.ADD, OrdersDatesTypesEnum.MODIFIED]
        )
        assert model.ordersDateType == OrdersDateTypeEnum.ADD
        assert len(model.ordersDatesTypes) == 2

    def test_orders_serial_number_range_model(self):
        model = OrdersSerialNumberRangeModel(
            ordersSerialNumberBegin=1,
            ordersSerialNumberEnd=100
        )
        assert model.ordersSerialNumberBegin == 1
        assert model.ordersSerialNumberEnd == 100

        with pytest.raises(ValueError):
            OrdersSerialNumberRangeModel(ordersSerialNumberBegin=0, ordersSerialNumberEnd=100)  # ge=1

    def test_orders_range_model(self):
        date_range = OrdersDateRangeModel(
            ordersDateType=OrdersDateTypeEnum.ADD,
            ordersDatesTypes=[OrdersDatesTypesEnum.ADD]
        )
        serial_range = OrdersSerialNumberRangeModel(
            ordersSerialNumberBegin=1,
            ordersSerialNumberEnd=100
        )
        model = OrdersRangeModel(
            ordersDateRange=date_range,
            ordersSerialNumberRange=serial_range
        )
        assert model.ordersDateRange.ordersDateType == OrdersDateTypeEnum.ADD

    def test_packages_post_put_model(self):
        shipping_costs = ShippingStoreCostsModel(amount=10.0, tax=2.0)
        packaging_params = DeliveryPackageParametersModel(productWeight=100, packagingWeight=50)
        model = PackagesPostPutModel(
            deliveryPackageId=1,
            courierId="COURIER123",
            deliveryPackageNumber="PKG001",
            deliveryShippingNumber="SHIP001",
            deliveryPackageParameters=packaging_params,
            shippingStoreCosts=shipping_costs
        )
        assert model.deliveryPackageId == 1
        assert model.courierId == "COURIER123"

    def test_parameter_values_model(self):
        model = ParameterValuesModel(valueId="VAL123")
        assert model.valueId == "VAL123"

    def test_payer_address_model(self):
        model = PayerAddressModel(
            payerAddressId=1,
            payerAddressFirstName="John",
            payerAddressLastName="Doe",
            payerAddressFirm="ABC Corp",
            payerAddressNip="123456789",
            payerAddressStreet="Main St 123",
            payerAddressZipCode="12345",
            payerAddressCity="Warsaw",
            payerAddressCountryId="PL",
            payerAddressPhone="123-456-789"
        )
        assert model.payerAddressId == 1
        assert model.payerAddressFirstName == "John"

    def test_product_ident_model(self):
        model = ProductIdentModel(
            identValue="123",
            productIdentType=ProductIdentTypeEnum.ID
        )
        assert model.identValue == "123"
        assert model.productIdentType == ProductIdentTypeEnum.ID

    def test_products_search_model(self):
        model = ProductsSearchModel(
            productId=1,
            productName="Test Product",
            sizeId="M",
            sizePanelName="Medium"
        )
        assert model.productId == 1
        assert model.productName == "Test Product"

    def test_settings_model(self):
        model = SettingsModel(settingSendMail=True, settingSendSMS=False)
        assert model.settingSendMail
        assert not model.settingSendSMS

    def test_settings_put_model(self):
        model = SettingsPutModel(
            dontSendMail=BooleanStrShortEnum.YES,
            dontSendSMS=BooleanStrShortEnum.NO
        )
        assert model.dontSendMail == BooleanStrShortEnum.YES
        assert model.dontSendSMS == BooleanStrShortEnum.NO

    def test_client_without_account_data_model(self):
        model = ClientWithoutAccountDataModel(
            clientFirstName="John",
            clientLastName="Doe",
            clientFirm="ABC Corp",
            clientNip="123456789",
            clientStreet="Main St 123",
            clientZipCode="12345",
            clientCity="Warsaw",
            clientCountry="PL",
            clientEmail="john@example.com",
            clientPhone1="123-456-789",
            clientPhone2="987-654-321",
            langId="pl"
        )
        assert model.clientFirstName == "John"
        assert model.clientLastName == "Doe"
        assert model.clientEmail == "john@example.com"

    def test_clients_model(self):
        model = ClientsModel(
            clientLogin="john_doe",
            clientId=123,
            clientFirstName="John",
            clientLastName="Doe",
            clientCity="Warsaw",
            clientEmail="john@example.com",
            clientHasTaxNumber=BooleanStrShortEnum.YES,
            clientSearchingMode=ClientSearchingModeEnum.BILLING_DATA,
            clientFirm="ABC Corp",
            clientNip="123456789",
            clientCountryId="PL",
            clientCountryName="Poland"
        )
        assert model.clientLogin == "john_doe"
        assert model.clientId == 123
        assert model.clientHasTaxNumber == BooleanStrShortEnum.YES

    def test_clients_search_model(self):
        model = ClientsSearchModel(
            type=ClientsSearchTypeEnum.LOGIN,
            value="john_doe"
        )
        assert model.type == ClientsSearchTypeEnum.LOGIN
        assert model.value == "john_doe"

    def test_clients_search_unfinished_model(self):
        model = ClientsSearchUnfinishedModel(
            clientLogin="john_doe",
            clientFirstName="John",
            clientLastName="Doe",
            clientCity="Warsaw",
            clientEmail="john@example.com",
            clientHasTaxNumber=BooleanStrShortEnum.YES,
            clientSearchingMode=ClientSearchingModeEnum.BILLING_DATA,
            clientFirm="ABC Corp",
            clientCountryId="PL",
            clientCountryName="Poland"
        )
        assert model.clientLogin == "john_doe"
        assert model.clientFirstName == "John"

    def test_documents_post_model(self):
        additional_data = AdditionalDataModel(
            documentId="DOC123",
            documentIssuedDate="2023-01-01"
        )
        model = DocumentsPostModel(
            orderSerialNumber=123,
            name="invoice.pdf",
            pdfBase64="base64content",
            type=TypeEnum.VAT_INVOICE,
            returnedInOrderDetails=BooleanStrShortEnum.YES,
            additionalData=additional_data
        )
        assert model.orderSerialNumber == 123
        assert model.name == "invoice.pdf"
        assert model.type == TypeEnum.VAT_INVOICE

    def test_order_source_model(self):
        auctions_params = AuctionsParamsModel(auctionsServicesNames=[AuctionsServicesNamesEnum.ALLEGRO])
        auctions_accounts = [AuctionsAccountsModel(
            auctionsAccountId=1,
            auctionsAccountLogin="test@example.com"
        )]
        auctions_clients = [AuctionsClientsModel(
            auctionClientId="CL123",
            auctionClientLogin="auction_user"
        )]
        model = OrderSourceModel(
            shopsMask=1,
            shopsIds=[1],
            auctionsParams=auctions_params,
            auctionsItemsIds=[123],
            auctionsAccounts=auctions_accounts,
            auctionsClients=auctions_clients
        )
        assert model.shopsMask == 1
        assert len(model.auctionsAccounts) == 1
        assert model.auctionsAccounts[0].auctionsAccountId == 1

    def test_order_source_search_unfinished_model(self):
        auctions_params = AuctionsParamsModel(auctionsServicesNames=[AuctionsServicesNamesEnum.EBAY])
        auctions_accounts = [AuctionsAccountsModel(
            auctionsAccountId=2,
            auctionsAccountLogin="ebay@example.com"
        )]
        model = OrderSourceSearchUnfinishedModel(
            shopsMask=2,
            shopsIds=[2],
            auctionsParams=auctions_params,
            auctionsItemsIds=[456],
            auctionsAccounts=auctions_accounts,
            auctionsClients=[]
        )
        assert model.shopsMask == 2
        assert len(model.auctionsAccounts) == 1

    def test_orders_by_search_unfinished_model(self):
        model = OrdersBySearchUnfinishedModel(
            elementName=ElementNameOrdersBySearchUnfinshedEnum.ID,
            sortDirection=SortDirectionSearchEnum.DESC
        )
        assert model.elementName == ElementNameOrdersBySearchUnfinshedEnum.ID
        assert model.sortDirection == SortDirectionSearchEnum.DESC

    def test_packages_search_unfinished_model(self):
        model = PackagesSearchUnfinishedModel(
            packagesNumbers=["PKG001", "PKG002"],
            orderHasPackageNumbers=BooleanStrShortEnum.YES
        )
        assert model.packagesNumbers == ["PKG001", "PKG002"]
        assert model.orderHasPackageNumbers == BooleanStrShortEnum.YES

    def test_product_bundle_items_model(self):
        model = ProductBundleItemsModel(
            productId=1,
            sizeId="M",
            sizePanelName="Medium",
            productIndex="IDX001"
        )
        assert model.productId == 1
        assert model.sizeId == "M"
        assert model.productIndex == "IDX001"

    def test_price_formula_parameters_model(self):
        model = PriceFormulaParametersModel(
            parameterId="PARAM1",
            parameterValue="value1",
            parameterValues=[ParameterValuesModel(valueId="VAL1")]
        )
        assert model.parameterId == "PARAM1"
        assert len(model.parameterValues) == 1

    def test_products_model(self):
        product_bundle_item = ProductBundleItemsModel(
            productId=2,
            sizeId="L",
            sizePanelName="Large",
            productIndex="IDX002"
        )
        model = ProductsModel(
            productId=1,
            sizeId="M",
            productSizeCodeExternal="EXT001",
            stockId=1,
            productQuantity=10.0,
            productRetailPrice=100.0,
            productFree=False,
            forceLoyaltyPoints=5.0,
            productVat=23.0,
            productVatFree=BooleanStrShortEnum.NO,
            discountCode=DiscountCodeModel(name="DISCOUNT10"),
            remarksToProduct="Test remarks",
            label="Test label",
            productBundleItems=product_bundle_item
        )
        assert model.productId == 1
        assert model.productQuantity == 10.0
        assert model.productVat == 23.0
        assert model.discountCode.name == "DISCOUNT10"
        assert model.productBundleItems.productId == 2

    def test_products_put_model(self):
        product_bundle_items = ProductBundleItemsModel(
            productId=2,
            sizeId="L",
            sizePanelName="Large",
            productIndex="IDX002"
        )
        price_formula = PriceFormulaParametersModel(
            parameterId="PARAM1",
            parameterValue="value1",
            parameterValues=[]
        )
        model = ProductsPutModel(
            productId=1,
            sizeId="M",
            productSizeCodeExternal="EXT001",
            basketPosition=1,
            stockId=1,
            productFree=False,
            forceLoyaltyPoints=5.0,
            productQuantity=10.0,
            productQuantityOperationType=ProductQuantityOperationTypeEnum.ADD,
            productRetailPrice=100.0,
            productVat=23.0,
            productVatFree=BooleanStrShortEnum.NO,
            remarksToProduct="Test remarks",
            label="Test label",
            productBundleItems=product_bundle_items,
            priceFormulaParameters=[price_formula]
        )
        assert model.productId == 1
        assert model.productQuantity == 10.0
        assert model.productQuantityOperationType == ProductQuantityOperationTypeEnum.ADD
        assert model.productBundleItems.productId == 2
        assert len(model.priceFormulaParameters) == 1

    def test_products_serial_numbers_orders_put_model(self):
        order_products = [OrderProductsModel(
            productId=1,
            sizeId="M",
            productSerialNumbers=["SN1", "SN2"]
        )]
        model = ProductsSerialNumbersOrdersPutModel(
            orderSerialNumber=123,
            orderProducts=order_products
        )
        assert model.orderSerialNumber == 123
        assert len(model.orderProducts) == 1
        assert model.orderProducts[0].productId == 1

    def test_products_profit_margin_orders_put_model(self):
        product_ident = ProductIdentModel(
            identValue="123",
            productIdentType=ProductIdentTypeEnum.ID
        )
        errors = ErrorsModel(faultCode=400, faultString="Bad Request")
        model = ProductsProfitMarginOrdersPutModel(
            productIdent=product_ident,
            sizeId="M",
            productProfitMargin=10.0,
            productProfitMarginNet=8.0,
            errors=errors
        )
        assert model.productProfitMargin == 10.0
        assert model.productProfitMarginNet == 8.0
        assert model.errors.faultCode == 400

    def test_profit_margin_orders_put_model(self):
        product_errors = ErrorsModel(faultCode=None, faultString=None)
        product_profit = ProductsProfitMarginOrdersPutModel(
            productIdent=ProductIdentModel(
                identValue="123",
                productIdentType=ProductIdentTypeEnum.ID
            ),
            sizeId="M",
            productProfitMargin=10.0,
            productProfitMarginNet=8.0,
            errors=product_errors
        )
        overall_errors = ErrorsModel(faultCode=None, faultString="Test error")
        model = ProfitMarginOrdersPutModel(
            orderSerialNumber=123,
            products=[product_profit],
            errors=overall_errors,
            isProductsErrors=False
        )
        assert model.orderSerialNumber == 123
        assert len(model.products) == 1
        assert not model.isProductsErrors
        assert model.errors.faultString == "Test error"
