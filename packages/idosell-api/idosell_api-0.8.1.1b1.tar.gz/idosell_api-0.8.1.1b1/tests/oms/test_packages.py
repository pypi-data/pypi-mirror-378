"""
Basic tests for idosell/oms/packages.py

This test file covers the core functionality of the packages module,
focusing on basic data models and endpoint classes that can be tested
without complex dependencies.
"""

import pytest
from src.idosell.oms.packages import (
    # Enums
    EventOrderTypeEnum,
    # DTOs
    EventsSearchModel,
    ParcelParametersModel,
    ParcelParametersByPackagesModel,
    PackagesPackagesModel,
    OrderPackagesPackagesPostModel,
    OrderPackagesPackagesPutModel,
    PostLabelsOmsPackagesParamsModel,
    PostOmsPackagesParamsModel,
    PutOmsPackagesParamsModel,
    SearchOmsPackagesParamsModel,
    # Endpoints
    GetLabels,
    PostLabels,
    Post,
    Put,
    Search,
)
from src.idosell.oms._common import ShippingStoreCostsModel


class TestEnums:
    """Test the enum classes in the packages module."""

    def test_event_order_type_enum_values(self):
        """Test EventOrderTypeEnum values."""
        assert EventOrderTypeEnum.ORDER == 'order'
        assert EventOrderTypeEnum.RETURN == 'return'
        assert EventOrderTypeEnum.RMA == 'rma'


class TestPackagesDTOs:
    """Test the basic data transfer objects in the packages module."""

    def test_events_search_model(self):
        """Test EventsSearchModel validation."""
        model = EventsSearchModel(
            eventType=EventOrderTypeEnum.ORDER,
            eventsIds=[123, 456]
        )
        assert model.eventType == EventOrderTypeEnum.ORDER
        assert model.eventsIds == [123, 456]

    # Removed - ParcelParameterModel doesn't exist, only ParcelParametersModel

    def test_parcel_parameters_by_packages_model(self):
        """Test ParcelParametersByPackagesModel."""
        parcel_params = ParcelParametersModel(id="ship_ext1", value="value1")
        model = ParcelParametersByPackagesModel(
            packageId="PKG001",
            parcelParameters=[parcel_params]
        )
        assert model.packageId == "PKG001"
        assert len(model.parcelParameters) == 1

    def test_parcel_parameters_model(self):
        """Test ParcelParametersModel."""
        model = ParcelParametersModel(
            id="ship_ext1",
            value="value1"
        )
        assert model.id == "ship_ext1"
        assert model.value == "value1"

    def test_packages_packages_model(self):
        """Test PackagesPackagesModel."""
        shipping_costs = ShippingStoreCostsModel(amount=10.50, tax=2.00)
        model = PackagesPackagesModel(
            packageId=1,
            delivery=123,
            packageNumber="PKG001",
            shippingNumber="SHIP001",
            packageParameters="",
            shippingStoreCosts=shipping_costs
        )
        assert model.packageId == 1
        assert model.delivery == 123
        assert model.shippingNumber == "SHIP001"
        assert model.shippingStoreCosts.amount == 10.50

        # Test validation - packageId ge=1
        with pytest.raises(ValueError):
            PackagesPackagesModel(
                packageId=0,
                delivery=123,
                shippingStoreCosts=shipping_costs
            )

        # Test validation - delivery ge=1
        with pytest.raises(ValueError):
            PackagesPackagesModel(
                packageId=1,
                delivery=0,
                shippingStoreCosts=shipping_costs
            )

    def test_order_packages_packages_post_model(self):
        """Test OrderPackagesPackagesPostModel."""
        parcel_params = ParcelParametersModel(id="ship_ext1", value="value1")
        model = OrderPackagesPackagesPostModel(
            eventId=123,
            eventType=EventOrderTypeEnum.ORDER,
            parcelParameters=[parcel_params],
            parcelParametersByPackages=[]
        )
        assert model.eventId == 123
        assert model.eventType == EventOrderTypeEnum.ORDER
        assert len(model.parcelParameters) == 1

    def test_order_packages_packages_post_model_with_parcel_by_packages(self):
        """Test OrderPackagesPackagesPostModel with parcel parameters by packages."""
        parcel_params = ParcelParametersModel(id="ship_ext1", value="value1")
        parcel_by_packages = ParcelParametersByPackagesModel(
            packageId="PKG001",
            parcelParameters=[parcel_params]
        )
        model = OrderPackagesPackagesPostModel(
            eventId=124,
            eventType=EventOrderTypeEnum.RETURN,
            parcelParameters=[parcel_params],
            parcelParametersByPackages=[parcel_by_packages]
        )
        assert len(model.parcelParametersByPackages) == 1

    def test_order_packages_packages_put_model(self):
        """Test OrderPackagesPackagesPutModel."""
        shipping_costs = ShippingStoreCostsModel(amount=15.30, tax=3.00)
        package = PackagesPackagesModel(
            packageId=2,
            delivery=456,
            packageNumber="PKG002",
            shippingNumber="SHIP002",
            packageParameters="",
            shippingStoreCosts=shipping_costs
        )
        model = OrderPackagesPackagesPutModel(
            orderId="ORD123",
            orderType=EventOrderTypeEnum.ORDER,
            packages=[package]
        )
        assert model.orderId == "ORD123"
        assert model.orderType == EventOrderTypeEnum.ORDER
        assert len(model.packages) == 1

    def test_post_labels_oms_packages_params_model(self):
        """Test PostLabelsOmsPackagesParamsModel."""
        parcel_param = ParcelParametersModel(id="ship_ext1", value="value1")
        parcel_by_packages = ParcelParametersByPackagesModel(
            packageId="PKG002",
            parcelParameters=[parcel_param]
        )
        model = PostLabelsOmsPackagesParamsModel(
            eventId=125,
            eventType=EventOrderTypeEnum.ORDER,
            parcelParameters=[parcel_param],
            parcelParametersByPackages=[parcel_by_packages]
        )
        assert model.eventId == 125
        assert model.eventType == EventOrderTypeEnum.ORDER
        assert len(model.parcelParameters) == 1

    def test_post_labels_oms_packages_params_model_with_parcel_by_packages(self):
        """Test PostLabelsOmsPackagesParamsModel with parcel by packages."""
        parcel_param = ParcelParametersModel(id="ship_ext1", value="value1")
        parcel_by_packages = ParcelParametersByPackagesModel(
            packageId="PKG002",
            parcelParameters=[parcel_param]
        )
        model = PostLabelsOmsPackagesParamsModel(
            eventId=126,
            eventType=EventOrderTypeEnum.RMA,
            parcelParameters=[parcel_param],
            parcelParametersByPackages=[parcel_by_packages]
        )
        assert len(model.parcelParametersByPackages) == 1

    def test_post_oms_packages_params_model(self):
        """Test PostOmsPackagesParamsModel."""
        parcel_params = ParcelParametersModel(id="ship_ext1", value="value1")
        order_package = OrderPackagesPackagesPostModel(
            eventId=127,
            eventType=EventOrderTypeEnum.ORDER,
            parcelParameters=[parcel_params],
            parcelParametersByPackages=[]
        )
        model = PostOmsPackagesParamsModel(
            orderPackages=[order_package]
        )
        assert len(model.orderPackages) == 1

        # Test min_length constraint
        with pytest.raises(ValueError):
            PostOmsPackagesParamsModel(orderPackages=[])

    def test_put_oms_packages_params_model(self):
        """Test PutOmsPackagesParamsModel."""
        shipping_costs = ShippingStoreCostsModel(amount=20.00, tax=4.00)
        package = PackagesPackagesModel(
            packageId=3,
            delivery=789,
            packageNumber="PKG003",
            shippingNumber="SHIP003",
            packageParameters="",
            shippingStoreCosts=shipping_costs
        )
        order_package = OrderPackagesPackagesPutModel(
            orderId="ORD456",
            orderType=EventOrderTypeEnum.RETURN,
            packages=[package]
        )
        model = PutOmsPackagesParamsModel(
            orderPackages=[order_package]
        )
        assert len(model.orderPackages) == 1

        # Test min_length constraint
        with pytest.raises(ValueError):
            PutOmsPackagesParamsModel(orderPackages=[])

    def test_search_oms_packages_params_model(self):
        """Test SearchOmsPackagesParamsModel."""
        events = EventsSearchModel(
            eventType=EventOrderTypeEnum.ORDER,
            eventsIds=[200, 201]
        )
        model = SearchOmsPackagesParamsModel(
            deliveryPackageNumbers=["SHIP001", "SHIP002"],
            events=[events],
            returnLabels=True
        )
        assert model.deliveryPackageNumbers == ["SHIP001", "SHIP002"]
        assert len(model.events) == 1
        assert model.returnLabels

        # Test None defaults
        empty_model = SearchOmsPackagesParamsModel()
        assert empty_model.deliveryPackageNumbers is None
        assert empty_model.events is None
        assert empty_model.returnLabels is None


class TestPackagesEndpoints:
    """Test the API endpoint classes in the packages module."""

    def test_get_labels_endpoint(self):
        """Test the GetLabels endpoint."""
        endpoint = GetLabels(
            eventId=100,
            eventType=EventOrderTypeEnum.ORDER
        )
        assert endpoint._method == 'GET'
        assert endpoint._endpoint == '/api/admin/v6/packages/labels'
        assert endpoint.eventId == 100
        assert endpoint.eventType == EventOrderTypeEnum.ORDER

        # Test validation - eventId ge=1
        with pytest.raises(ValueError):
            GetLabels(eventId=0, eventType=EventOrderTypeEnum.ORDER)

    def test_post_labels_endpoint(self):
        """Test the PostLabels endpoint."""
        parcel_param = ParcelParametersModel(id="ship_ext1", value="value1")
        parcel_by_packages = ParcelParametersByPackagesModel(
            packageId="PKG001",
            parcelParameters=[parcel_param]
        )
        params = PostLabelsOmsPackagesParamsModel(
            eventId=101,
            eventType=EventOrderTypeEnum.ORDER,
            parcelParameters=[parcel_param],
            parcelParametersByPackages=[parcel_by_packages]
        )
        endpoint = PostLabels(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/packages/labels'
        assert endpoint.params.eventId == 101

    def test_post_endpoint(self):
        """Test the Post endpoint."""
        parcel_params = ParcelParametersModel(id="ship_ext1", value="value1")
        order_package = OrderPackagesPackagesPostModel(
            eventId=128,
            eventType=EventOrderTypeEnum.ORDER,
            parcelParameters=[parcel_params],
            parcelParametersByPackages=[]
        )
        params = PostOmsPackagesParamsModel(orderPackages=[order_package])
        endpoint = Post(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/packages/packages'
        assert len(endpoint.params.orderPackages) == 1

    def test_put_endpoint(self):
        """Test the Put endpoint."""
        shipping_costs = ShippingStoreCostsModel(amount=18.75, tax=3.50)
        package = PackagesPackagesModel(
            packageId=4,
            delivery=1001,
            packageNumber="PKG004",
            shippingNumber="SHIP004",
            packageParameters="",
            shippingStoreCosts=shipping_costs
        )
        order_package = OrderPackagesPackagesPutModel(
            orderId="ORD789",
            orderType=EventOrderTypeEnum.RMA,
            packages=[package]
        )
        params = PutOmsPackagesParamsModel(orderPackages=[order_package])
        endpoint = Put(params=params)
        assert endpoint._method == 'PUT'
        assert endpoint._endpoint == '/api/admin/v6/packages/packages'
        assert endpoint.params.orderPackages[0].orderId == "ORD789"

    def test_search_endpoint(self):
        """Test the Search endpoint."""
        events = EventsSearchModel(
            eventType=EventOrderTypeEnum.ORDER,
            eventsIds=[300]
        )
        params = SearchOmsPackagesParamsModel(
            deliveryPackageNumbers=None,
            events=[events],
            returnLabels=False
        )
        endpoint = Search(params=params)
        assert endpoint._method == 'POST'
        assert endpoint._endpoint == '/api/admin/v6/packages/packages/search'
        if endpoint.params.events is not None:
            assert len(endpoint.params.events) == 1
        assert not endpoint.params.returnLabels
