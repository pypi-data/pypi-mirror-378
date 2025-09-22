"""
Basic tests for idosell/oms/subscriptions.py

This test file covers the core functionality of the subscriptions module,
focusing on basic data models and endpoint classes that can be tested
without complex dependencies.
"""

from datetime import date, datetime, time
import pytest
from src.idosell.oms.subscriptions import (
    # Enums
    DirectionTypeEnum, OrderByDirectionEnum, OrderByPropertyEnum, PriceChangeModeEnum, PropertyTypeEnum, SubscriptionsStatusEnum, SubscriptionsTypeEnum,
    # DTOs
    DateTimeModel,
    DateRangeModel,
    DateTimeRangeModel,
    ValueModel,
    DeliveryCostModel,
    OrderDeliveryModel,
    OrderDataModel,
    QuantityModel,
    BundledProductsModel,
    ProductAddModel,
    AddProductProductsPostModel,
    AddProducts,
    SubscriptionsDeliveryDatesModel,
    SubscriptionsAutoPriceModel,
    SubscriptionDeleteProducts,
    RebatesThresholdModel,
    PaymentDataModel,
    SubscriptionModel,
    SubscriptionsEditRequest,
    PriceModel,
    NetPriceModel,
    FilterModel,
    EditProductPostModel,
    SubscriptionEditProducts,
    OrderByModel,
    PaginationModel,
    ItemsListRequestPostModel,
    ListViewFetchIdsFilterPostModel,
    SetRebateCodeRequestPostModel,
    UnsetRebateCodeRequestPostModel,
    SubscriptionsStatusModel,
    # Endpoints
    PostAddProduct,
    PostChangeDeliveryDates,
    PostChangePriceAutoUpdate,
    PostChangeStatus,
    DeleteProduct,
    PostEdit,
    PostEditProduct,
    PostItemsList,
    PostListViewFetchIds,
    PostSetRebateCode,
    PostUnsetRebateCode,
)


class TestEnums:
    """Test the enum classes in the subscriptions module."""

    def test_direction_type_enum_values(self):
        """Test DirectionTypeEnum values."""
        assert DirectionTypeEnum.ASC == 'asc'
        assert DirectionTypeEnum.DESC == 'desc'

    def test_order_by_direction_enum_values(self):
        """Test OrderByDirectionEnum values."""
        assert OrderByDirectionEnum.ASC == 'asc'
        assert OrderByDirectionEnum.DESC == 'desc'

    def test_order_by_property_enum_values(self):
        """Test OrderByPropertyEnum values."""
        assert OrderByPropertyEnum.ID == 'id'
        assert OrderByPropertyEnum.STATUS == 'status'
        assert OrderByPropertyEnum.NUMBEROFORDERS == 'numberOfOrders'
        assert OrderByPropertyEnum.CREATEDATETIME == 'createDateTime'
        assert OrderByPropertyEnum.UPCOMINGDELIVERYDATE == 'upcomingDeliveryDate'
        assert OrderByPropertyEnum.NEXTDELIVERYDATE == 'nextDeliveryDate'
        assert OrderByPropertyEnum.CLIENTBILLINGDATA == 'clientBillingData'

    def test_price_change_mode_enum_values(self):
        """Test PriceChangeModeEnum values."""
        assert PriceChangeModeEnum.AUTO == 'auto'
        assert PriceChangeModeEnum.MANUAL == 'manual'

    def test_property_type_enum_values(self):
        """Test PropertyTypeEnum values."""
        assert PropertyTypeEnum.ID == 'id'
        assert PropertyTypeEnum.PRICE == 'price'
        assert PropertyTypeEnum.NETPRICE == 'netPrice'

    def test_subscriptions_status_enum_values(self):
        """Test SubscriptionsStatusEnum values."""
        assert SubscriptionsStatusEnum.ACTIVE == 'active'
        assert SubscriptionsStatusEnum.HOLD == 'hold'
        assert SubscriptionsStatusEnum.NONPAYMENT == 'nonpayment'
        assert SubscriptionsStatusEnum.FINISHED == 'finished'

    def test_subscriptions_type_enum_values(self):
        """Test SubscriptionsTypeEnum values."""
        assert SubscriptionsTypeEnum.PERCENTAGE == 'percentage'
        assert SubscriptionsTypeEnum.QUOTA == 'quota'


class TestSubscriptionsDTOs:
    """Test the basic data transfer objects in the subscriptions module."""

    def test_date_time_model(self):
        """Test DateTimeModel validation."""
        from_time = time(9, 0, 0)  # 9:00:00
        to_time = time(17, 30, 0)  # 17:30:00
        model = DateTimeModel(**{"from": from_time, "to": to_time})
        assert isinstance(model.from_, time)
        assert isinstance(model.to, time)

    def test_date_range_model(self):
        """Test DateRangeModel validation."""
        from_date = date(2023, 10, 1)
        to_date = date(2023, 10, 31)
        model = DateRangeModel(**{"from": from_date, "to": to_date})
        assert isinstance(model.from_, date)
        assert isinstance(model.to, date)

    def test_date_time_range_model(self):
        """Test DateTimeRangeModel validation."""
        from_dt = datetime(2023, 10, 1, 9, 0, 0)
        to_dt = datetime(2023, 10, 31, 17, 30, 0)
        model = DateTimeRangeModel(**{"from": from_dt, "to": to_dt})
        assert isinstance(model.from_, datetime)
        assert isinstance(model.to, datetime)

    def test_value_model(self):
        """Test ValueModel validation."""
        model = ValueModel(value="15.50")
        assert model.value == "15.50"

    def test_delivery_cost_model(self):
        """Test DeliveryCostModel validation."""
        model = DeliveryCostModel(value="9.99")
        assert model.value == "9.99"

    def test_order_delivery_model(self):
        """Test OrderDeliveryModel validation."""
        model = OrderDeliveryModel(
            courierNote="Handle with care",
            pickupPointId="POINT123",
            deliveryFormId=1,
            deliveryAddressId=456
        )
        assert model.deliveryFormId == 1
        assert model.deliveryAddressId == 456

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            OrderDeliveryModel(
                courierNote="",
                pickupPointId="",
                deliveryFormId=0,
                deliveryAddressId=456
            )

        with pytest.raises(ValueError):
            OrderDeliveryModel(
                courierNote="",
                pickupPointId="",
                deliveryFormId=1,
                deliveryAddressId=0
            )

    def test_order_data_model(self):
        """Test OrderDataModel validation."""
        delivery_cost = DeliveryCostModel(value="7.50")
        order_delivery = OrderDeliveryModel(
            courierNote="Leave at door",
            pickupPointId="PICK001",
            deliveryFormId=2,
            deliveryAddressId=789
        )
        model = OrderDataModel(
            deliveryCost=delivery_cost,
            orderDelivery=order_delivery,
            payerAddressId=101,
            noteToStaff="Customer prefers morning delivery"
        )
        assert model.payerAddressId == 101
        assert model.deliveryCost.value == "7.50"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            OrderDataModel(
                deliveryCost=delivery_cost,
                orderDelivery=order_delivery,
                payerAddressId=0,
                noteToStaff=""
            )

    def test_quantity_model(self):
        """Test QuantityModel validation."""
        model = QuantityModel(value="2.5")
        assert model.value == "2.5"

    def test_bundled_products_model(self):
        """Test BundledProductsModel validation."""
        quantity = QuantityModel(value="1.0")
        model = BundledProductsModel(
            productId=1001,
            sizeId="M",
            quantity=quantity,
            bundledProducts=None,
            comment="Main product",
            splitBundleInOrderDocuments=False
        )
        assert model.productId == 1001
        assert model.sizeId == "M"
        assert model.splitBundleInOrderDocuments == False

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            BundledProductsModel(
                productId=0,
                sizeId="M",
                quantity=quantity,
                bundledProducts=None,
                comment="",
                splitBundleInOrderDocuments=False
            )

    def test_product_add_model(self):
        """Test ProductAddModel validation."""
        quantity = QuantityModel(value="3.0")
        bundled_product = BundledProductsModel(
            productId=2001,
            sizeId="L",
            quantity=QuantityModel(value="1.0"),
            bundledProducts=None,
            comment="Bundle item",
            splitBundleInOrderDocuments=True
        )
        model = ProductAddModel(
            productId=3001,
            sizeId="XL",
            quantity=quantity,
            bundledProducts=[bundled_product],
            comment="New subscription product",
            splitBundleInOrderDocuments=False
        )
        assert model.productId == 3001
        assert len(model.bundledProducts) == 1
        assert model.bundledProducts[0].comment == "Bundle item"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            ProductAddModel(
                productId=0,
                sizeId="XL",
                quantity=quantity,
                bundledProducts=[],
                comment="",
                splitBundleInOrderDocuments=False
            )

    def test_add_product_products_post_model(self):
        """Test AddProductProductsPostModel validation."""
        quantity1 = QuantityModel(value="1.0")
        quantity2 = QuantityModel(value="2.0")
        product1 = ProductAddModel(
            productId=4001,
            sizeId="S",
            quantity=quantity1,
            bundledProducts=[],
            comment="Product 1",
            splitBundleInOrderDocuments=False
        )
        product2 = ProductAddModel(
            productId=4002,
            sizeId="M",
            quantity=quantity2,
            bundledProducts=[],
            comment="Product 2",
            splitBundleInOrderDocuments=False
        )
        model = AddProductProductsPostModel(
            subscriptionId=100,
            products=[product1, product2]
        )
        assert model.subscriptionId == 100
        assert len(model.products) == 2

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            AddProductProductsPostModel(
                subscriptionId=0,
                products=[]
            )

    def test_add_products(self):
        """Test AddProducts validation."""
        # First create a nested structure
        inner_product = AddProductProductsPostModel(
            subscriptionId=200,
            products=[]  # Empty for this test
        )
        model = AddProducts(
            subscriptionId=150,
            products=[inner_product]
        )
        assert model.subscriptionId == 150
        assert len(model.products) == 1

        # Test validation
        with pytest.raises(ValueError):
            AddProducts(
                subscriptionId=0,
                products=[]
            )

    def test_subscriptions_delivery_dates_model(self):
        """Test SubscriptionsDeliveryDatesModel validation."""
        model = SubscriptionsDeliveryDatesModel(
            subscriptionIds=[123, 456, 789],
            upcomingDeliveryDate="2023-11-15",
            changeNextDeliveryDate=True
        )
        assert len(model.subscriptionIds) == 3
        assert model.upcomingDeliveryDate == "2023-11-15"
        assert model.changeNextDeliveryDate

    def test_subscriptions_auto_price_model(self):
        """Test SubscriptionsAutoPriceModel validation."""
        model = SubscriptionsAutoPriceModel(
            subscriptionIds=[100, 200, 300],
            autoPriceUpdate=True
        )
        assert len(model.subscriptionIds) == 3
        assert model.autoPriceUpdate

    def test_subscription_delete_products(self):
        """Test SubscriptionDeleteProducts validation."""
        model = SubscriptionDeleteProducts(
            subscriptionId=456,
            idsToDelete=[10, 20, 30, 40]
        )
        assert model.subscriptionId == 456
        assert len(model.idsToDelete) == 4

        # Test validation
        with pytest.raises(ValueError):
            SubscriptionDeleteProducts(
                subscriptionId=0,
                idsToDelete=[]
            )

    def test_rebates_threshold_model(self):
        """Test RebatesThresholdModel validation."""
        value = ValueModel(value="10.00")
        model = RebatesThresholdModel(
            numberFrom=5,
            numberTo=10,
            type=SubscriptionsTypeEnum.PERCENTAGE,
            value=value
        )
        assert model.numberFrom == 5
        assert model.numberTo == 10
        assert model.type == SubscriptionsTypeEnum.PERCENTAGE

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            RebatesThresholdModel(
                numberFrom=0,
                numberTo=10,
                type=SubscriptionsTypeEnum.PERCENTAGE,
                value=value
            )

    def test_payment_data_model(self):
        """Test PaymentDataModel validation."""
        model = PaymentDataModel(
            externalPaymentId="EXT_PAY_123",
            externalPaymentHandle="handle_123"
        )
        assert model.externalPaymentId == "EXT_PAY_123"
        assert model.externalPaymentHandle == "handle_123"

    def test_subscription_model(self):
        """Test SubscriptionModel validation."""
        delivery_cost = DeliveryCostModel(value="12.50")
        order_delivery = OrderDeliveryModel(
            courierNote="Friday delivery preferred",
            pickupPointId="PICKUP_001",
            deliveryFormId=1,
            deliveryAddressId=999
        )
        order_data = OrderDataModel(
            deliveryCost=delivery_cost,
            orderDelivery=order_delivery,
            payerAddressId=888,
            noteToStaff="VIP customer - excellent service required"
        )
        rebate_threshold = RebatesThresholdModel(
            numberFrom=10,
            numberTo=20,
            type=SubscriptionsTypeEnum.QUOTA,
            value=ValueModel(value="25.00")
        )
        payment_data = PaymentDataModel(
            externalPaymentId="SUB_PAY_789",
            externalPaymentHandle="handle_sub_789"
        )

        model = SubscriptionModel(
            id=777,
            externalId="EXT_SUB_777",
            status=SubscriptionsStatusEnum.ACTIVE,
            subscriptionNote="Monthly subscription for health supplements",
            upcomingDeliveryDate=date(2023, 11, 15),
            priceAutoUpdate=True,
            nextDeliveryDate=date(2023, 11, 30),
            daysInPeriod=30,
            sendMailAfterStatusChange=True,
            sendSMSAfterStatusChange=False,
            orderData=order_data,
            rebatesThresholds=[rebate_threshold],
            paymentData=payment_data
        )
        assert model.id == 777
        assert model.externalId == "EXT_SUB_777"
        assert model.status == SubscriptionsStatusEnum.ACTIVE
        assert model.daysInPeriod == 30
        assert model.rebatesThresholds is not None and len(model.rebatesThresholds) == 1

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            SubscriptionModel(
                id=0,
                externalId=None,
                status=None,
                subscriptionNote=None,
                upcomingDeliveryDate=None,
                priceAutoUpdate=None,
                nextDeliveryDate=None,
                daysInPeriod=None,
                sendMailAfterStatusChange=None,
                sendSMSAfterStatusChange=None,
                orderData=None,
                rebatesThresholds=None,
                paymentData=None
            )

    def test_price_model(self):
        """Test PriceModel validation."""
        model = PriceModel(value="299.99")
        assert model.value == "299.99"

    def test_net_price_model(self):
        """Test NetPriceModel validation."""
        model = NetPriceModel(value="240.00")
        assert model.value == "240.00"

    def test_filter_model(self):
        """Test FilterModel validation."""
        model = FilterModel(id=12345)
        assert model.id == 12345

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            FilterModel(id=0)

    def test_edit_product_post_model(self):
        """Test EditProductPostModel validation."""
        quantity = QuantityModel(value="4.0")
        price = PriceModel(value="349.99")
        net_price = NetPriceModel(value="280.00")

        model = EditProductPostModel(
            id=5001,
            variantId=501,
            variantSizeId="XL",
            quantity=quantity,
            price=price,
            netPrice=net_price,
            label="Premium subscription product"
        )
        assert model.id == 5001
        assert model.variantId == 501
        assert model.price.value == "349.99"

        # Test validation - ge=1 constraints
        with pytest.raises(ValueError):
            EditProductPostModel(
                id=0,
                variantId=501,
                variantSizeId="XL",
                quantity=quantity,
                price=price,
                netPrice=net_price,
                label=""
            )

    def test_subscriptions_edit_request(self):
        """Test SubscriptionsEditRequest validation."""
        order_data = OrderDataModel(
            deliveryCost=DeliveryCostModel(value="15.00"),
            orderDelivery=OrderDeliveryModel(
                courierNote="Call on arrival",
                pickupPointId="PICK_123",
                deliveryFormId=3,
                deliveryAddressId=666
            ),
            payerAddressId=555,
            noteToStaff="Handle delicately"
        )

        subscription = SubscriptionModel(
            id=999,
            externalId="SUB_EXT_999",
            status=SubscriptionsStatusEnum.HOLD,
            subscriptionNote="Subscription on hold due to payment issue",
            upcomingDeliveryDate=None,
            priceAutoUpdate=False,
            nextDeliveryDate=date(2023, 12, 15),
            daysInPeriod=30,
            sendMailAfterStatusChange=True,
            sendSMSAfterStatusChange=True,
            orderData=order_data,
            rebatesThresholds=None,
            paymentData=None
        )

        model = SubscriptionsEditRequest(subscriptionModels=[subscription])
        assert len(model.subscriptionModels) == 1
        assert model.subscriptionModels[0].id == 999
        assert model.subscriptionModels[0].status == SubscriptionsStatusEnum.HOLD


class TestSubscriptionsEndpoints:
    """Test the API endpoint classes in the subscriptions module."""

    def test_post_add_product_endpoint(self):
        """Test the PostAddProduct endpoint."""
        add_product_post = AddProductProductsPostModel(
            subscriptionId=111,
            products=[]
        )
        add_products = AddProducts(
            subscriptionId=222,
            products=[add_product_post]
        )
        endpoint = PostAddProduct(addProducts=add_products)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/addProduct'
        assert endpoint.addProducts.subscriptionId == 222

    def test_post_change_delivery_dates_endpoint(self):
        """Test the PostChangeDeliveryDates endpoint."""
        delivery_dates = SubscriptionsDeliveryDatesModel(
            subscriptionIds=[333, 444],
            upcomingDeliveryDate="2023-11-20",
            changeNextDeliveryDate=False
        )
        endpoint = PostChangeDeliveryDates(subscriptionsDeliveryDatesModel=delivery_dates)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/changeDeliveryDates'
        assert endpoint.subscriptionsDeliveryDatesModel.upcomingDeliveryDate == "2023-11-20"

    def test_post_change_price_auto_update_endpoint(self):
        """Test the PostChangePriceAutoUpdate endpoint."""
        auto_price = SubscriptionsAutoPriceModel(
            subscriptionIds=[555, 666],
            autoPriceUpdate=False
        )
        endpoint = PostChangePriceAutoUpdate(subscriptionsAutoPriceModel=auto_price)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/changePriceAutoUpdate'
        assert not endpoint.subscriptionsAutoPriceModel.autoPriceUpdate

    def test_post_change_status_endpoint(self):
        """Test the PostChangeStatus endpoint."""
        status_change = SubscriptionsStatusModel(
            subscriptionIds=[777, 888, 999],
            subscriptionStatus=SubscriptionsStatusEnum.FINISHED,
            sendMailAfterStatusChange=True,
            sendSMSAfterStatusChange=True
        )
        endpoint = PostChangeStatus(subscriptionsStatusModel=status_change)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/changeStatus'
        assert endpoint.subscriptionsStatusModel.subscriptionStatus == SubscriptionsStatusEnum.FINISHED

    def test_delete_product_endpoint(self):
        """Test the DeleteProduct endpoint."""
        delete_products = SubscriptionDeleteProducts(
            subscriptionId=1234,
            idsToDelete=[10, 20, 30]
        )
        endpoint = DeleteProduct(subscriptionDeleteProducts=delete_products)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/deleteProduct'
        assert endpoint.subscriptionDeleteProducts.subscriptionId == 1234

    def test_post_edit_endpoint(self):
        """Test the PostEdit endpoint."""
        order_delivery = OrderDeliveryModel(
            courierNote="Premium handling",
            pickupPointId="PREM_001",
            deliveryFormId=5,
            deliveryAddressId=1001
        )
        order_data = OrderDataModel(
            deliveryCost=DeliveryCostModel(value="25.00"),
            orderDelivery=order_delivery,
            payerAddressId=2001,
            noteToStaff="High priority subscription"
        )
        subscription_model = SubscriptionModel(
            id=5678,
            externalId="SUB_EXT_5678",
            status=SubscriptionsStatusEnum.ACTIVE,
            subscriptionNote="Premium monthly subscription",
            upcomingDeliveryDate=date(2023, 12, 10),
            priceAutoUpdate=True,
            nextDeliveryDate=date(2023, 12, 20),
            daysInPeriod=30,
            sendMailAfterStatusChange=False,
            sendSMSAfterStatusChange=False,
            orderData=order_data,
            rebatesThresholds=None,
            paymentData=None
        )
        edit_request = SubscriptionsEditRequest(
            subscriptionModels=[subscription_model]
        )
        endpoint = PostEdit(subscriptionsEditRequest=edit_request)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/edit'
        assert len(endpoint.subscriptionsEditRequest.subscriptionModels) == 1

    def test_post_edit_product_endpoint(self):
        """Test the PostEditProduct endpoint."""
        edit_product = EditProductPostModel(
            id=3001,
            variantId=301,
            variantSizeId="L",
            quantity=QuantityModel(value="5.0"),
            price=PriceModel(value="79.99"),
            netPrice=NetPriceModel(value="67.50"),
            label="Updated premium product"
        )
        edit_products = SubscriptionEditProducts(
            subscriptionId=1111,
            products=[edit_product]
        )
        endpoint = PostEditProduct(subscriptionEditProducts=edit_products)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/editProduct'
        assert endpoint.subscriptionEditProducts.subscriptionId == 1111

    def test_post_items_list_endpoint(self):
        """Test the PostItemsList endpoint."""
        filter_model = FilterModel(id=9876)
        order_by = OrderByModel(
            property=PropertyTypeEnum.PRICE,
            direction=DirectionTypeEnum.DESC
        )
        pagination = PaginationModel(
            page=0,
            perPage=25
        )
        request = ItemsListRequestPostModel(
            filter=filter_model,
            orderBy=order_by,
            pagination=pagination
        )
        endpoint = PostItemsList(request=request)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/items/list'
        assert endpoint.request.filter.id == 9876
        assert endpoint.request.pagination.perPage == 25

    def test_post_list_view_fetch_ids_endpoint(self):
        """Test the PostListViewFetchIds endpoint."""
        create_dt_range = DateTimeRangeModel(
            **{"from": datetime(2023, 9, 1, 0, 0, 0), "to": datetime(2023, 11, 30, 23, 59, 59)}
        )
        filter_model = ListViewFetchIdsFilterPostModel(
            ids=[1000, 2000],
            statuses=["active", "hold"],
            clientId=5000,
            shopId=10,
            priceChangeMode=PriceChangeModeEnum.AUTO,
            createDateTime=create_dt_range,
            finishDateTime=create_dt_range,  # Same for simplicity
            upcomingDeliveryDate=DateRangeModel(
                **{"from": date(2023, 11, 15), "to": date(2023, 12, 15)}
            ),
            nextDeliveryDate=DateRangeModel(
                **{"from": date(2023, 12, 1), "to": date(2023, 12, 31)}
            ),
            textSearch="premium subscription"
        )
        endpoint = PostListViewFetchIds(filter=filter_model)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/listView/fetchIds'
        assert endpoint.filter.clientId == 5000
        assert endpoint.filter.priceChangeMode == PriceChangeModeEnum.AUTO

    def test_post_set_rebate_code_endpoint(self):
        """Test the PostSetRebateCode endpoint."""
        request = SetRebateCodeRequestPostModel(
            id=7890,
            code="DISCOUNT2023"
        )
        endpoint = PostSetRebateCode(request=request)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/setRebateCode'
        assert endpoint.request.code == "DISCOUNT2023"

        # Test validation - ge=1 constraint
        with pytest.raises(ValueError):
            PostSetRebateCode(
                request=SetRebateCodeRequestPostModel(
                    id=0,
                    code="TEST"
                )
            )

    def test_post_unset_rebate_code_endpoint(self):
        """Test the PostUnsetRebateCode endpoint."""
        request = UnsetRebateCodeRequestPostModel(id=4567)
        endpoint = PostUnsetRebateCode(request=request)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/subscriptions/unsetRebateCode'
        assert endpoint.request.id == 4567
