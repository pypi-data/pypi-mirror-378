import pytest
from pydantic import ValidationError

from src.idosell.crm.deliveryaddress import (
    ClientDeliveryAddressModel, ClientSettingsDeliveryAddressModel,
    ClientsDeliveryAddressPostModel, ClientsDeliveryAddressPutModel, ClientsPostPutModel,
    DeleteCrmDeliveryaddressParamsModel, PostCrmDeliveryaddressParamsModel, PutCrmDeliveryaddressParamsModel,
    Delete, Get, Post, Put
)


# --- Tests for DTOs
class TestClientsPostPutModel:
    def test_valid(self):
        dto = ClientsPostPutModel(
            clientLogin="testuser",
            clientCodeExternal="EXT123",
            shopsIds=[1, 2],
            currencyId="USD",
            clientDeliveryAddressFirstName="John",
            clientDeliveryAddressLastName="Doe",
            clientDeliveryAddressAdditional="Apt 123",
            clientDeliveryAddressPhone1="123456789",
            clientDeliveryAddressCity="New York",
            clientDeliveryAddressStreet="Main St 456",
            clientDeliveryAddressRegionId="NY",
            clientDeliveryAddressProvinceId="Province",
            clientDeliveryAddressZipCode="10001",
            clientDeliveryAddressCountry="USA"
        )
        assert dto.clientLogin == "testuser"
        assert dto.clientCodeExternal == "EXT123"
        assert dto.shopsIds == [1, 2]
        assert dto.currencyId == "USD"
        assert dto.clientDeliveryAddressFirstName == "John"
        assert dto.clientDeliveryAddressLastName == "Doe"
        assert dto.clientDeliveryAddressAdditional == "Apt 123"
        assert dto.clientDeliveryAddressPhone1 == "123456789"
        assert dto.clientDeliveryAddressCity == "New York"
        assert dto.clientDeliveryAddressStreet == "Main St 456"
        assert dto.clientDeliveryAddressRegionId == "NY"
        assert dto.clientDeliveryAddressProvinceId == "Province"
        assert dto.clientDeliveryAddressZipCode == "10001"
        assert dto.clientDeliveryAddressCountry == "USA"

    def test_invalid_shops_ids_non_int(self):
        with pytest.raises(ValidationError):
            ClientsPostPutModel(
                clientLogin="testuser",
                clientCodeExternal="EXT123",
                shopsIds=["invalid"],  # Not int
                currencyId="USD",
                clientDeliveryAddressFirstName="John",
                clientDeliveryAddressLastName="Doe",
                clientDeliveryAddressAdditional="Apt 123",
                clientDeliveryAddressPhone1="123456789",
                clientDeliveryAddressCity="New York",
                clientDeliveryAddressStreet="Main St 456",
                clientDeliveryAddressRegionId="NY",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="10001",
                clientDeliveryAddressCountry="USA"
            )


class TestClientsDeliveryAddressPostModel:
    def test_valid(self):
        dto = ClientsDeliveryAddressPostModel(
            clientLogin="testuser",
            clientCodeExternal="EXT123",
            shopsIds=[1, 2],
            currencyId="USD",
            clientDeliveryAddressFirstName="John",
            clientDeliveryAddressLastName="Doe",
            clientDeliveryAddressAdditional="Apt 123",
            clientDeliveryAddressPhone1="123456789",
            clientDeliveryAddressCity="New York",
            clientDeliveryAddressStreet="Main St 456",
            clientDeliveryAddressRegionId="NY",
            clientDeliveryAddressProvinceId="Province",
            clientDeliveryAddressZipCode="10001",
            clientDeliveryAddressCountry="USA"
        )
        assert dto.clientLogin == "testuser"
        # Since it inherits, check a field
        assert dto.clientDeliveryAddressCountry == "USA"


class TestClientsDeliveryAddressPutModel:
    def test_valid(self):
        dto = ClientsDeliveryAddressPutModel(
            clientLogin="testuser",
            clientCodeExternal="EXT123",
            shopsIds=[1, 2],
            currencyId="USD",
            clientDeliveryAddressFirstName="John",
            clientDeliveryAddressLastName="Doe",
            clientDeliveryAddressAdditional="Apt 123",
            clientDeliveryAddressPhone1="123456789",
            clientDeliveryAddressCity="New York",
            clientDeliveryAddressStreet="Main St 456",
            clientDeliveryAddressRegionId="NY",
            clientDeliveryAddressProvinceId="Province",
            clientDeliveryAddressZipCode="10001",
            clientDeliveryAddressCountry="USA",
            clientDeliveryAddressId="DA123"
        )
        assert dto.clientDeliveryAddressId == "DA123"

    def test_missing_client_delivery_address_id(self):
        with pytest.raises(ValidationError):
            ClientsDeliveryAddressPutModel(
                clientLogin="testuser",
                clientCodeExternal="EXT123",
                shopsIds=[1, 2],
                currencyId="USD",
                clientDeliveryAddressFirstName="John",
                clientDeliveryAddressLastName="Doe",
                clientDeliveryAddressAdditional="Apt 123",
                clientDeliveryAddressPhone1="123456789",
                clientDeliveryAddressCity="New York",
                clientDeliveryAddressStreet="Main St 456",
                clientDeliveryAddressRegionId="NY",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="10001",
                clientDeliveryAddressCountry="USA"
                # Missing clientDeliveryAddressId
            )


class TestClientSettingsDeliveryAddressModel:
    def test_valid(self):
        dto = ClientSettingsDeliveryAddressModel(
            clientSettingSendMail=True,
            clientSettingSendSms=False
        )
        assert dto.clientSettingSendMail is True
        assert dto.clientSettingSendSms is False


class TestClientDeliveryAddressModel:
    def test_valid(self):
        dto = ClientDeliveryAddressModel(
            clientLogin="testuser",
            clientCodeExternal="EXT123",
            clientDeliveryAddressId=1
        )
        assert dto.clientLogin == "testuser"
        assert dto.clientDeliveryAddressId == 1

    def test_invalid_delivery_address_id(self):
        with pytest.raises(ValidationError):
            ClientDeliveryAddressModel(
                clientLogin="testuser",
                clientCodeExternal="EXT123",
                clientDeliveryAddressId=0  # Must be >=1
            )


class TestDeleteCrmDeliveryaddressParamsModel:
    def test_valid(self):
        client = ClientDeliveryAddressModel(
            clientLogin="testuser",
            clientCodeExternal="EXT123",
            clientDeliveryAddressId=1
        )
        dto = DeleteCrmDeliveryaddressParamsModel(clients=client)
        assert dto.clients.clientLogin == "testuser"


class TestPostCrmDeliveryaddressParamsModel:
    def test_valid(self):
        clients_list = [
            ClientsDeliveryAddressPostModel(
                clientLogin="user1",
                clientCodeExternal="EXT1",
                shopsIds=[1],
                currencyId="EUR",
                clientDeliveryAddressFirstName="Jane",
                clientDeliveryAddressLastName="Smith",
                clientDeliveryAddressAdditional="",
                clientDeliveryAddressPhone1="987654321",
                clientDeliveryAddressCity="London",
                clientDeliveryAddressStreet="London Rd 789",
                clientDeliveryAddressRegionId="LDN",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="E1 6AN",
                clientDeliveryAddressCountry="UK"
            )
        ]
        settings = ClientSettingsDeliveryAddressModel(
            clientSettingSendMail=True,
            clientSettingSendSms=True
        )
        dto = PostCrmDeliveryaddressParamsModel(
            clients=clients_list,
            clientsSettings=settings
        )
        assert len(dto.clients) == 1
        assert dto.clientsSettings.clientSettingSendMail is True

    def test_empty_clients_list_allowed(self):
        settings = ClientSettingsDeliveryAddressModel(
            clientSettingSendMail=False,
            clientSettingSendSms=False
        )
        dto = PostCrmDeliveryaddressParamsModel(
            clients=[],  # Empty list is allowed as per model definition
            clientsSettings=settings
        )
        assert len(dto.clients) == 0


class TestPutCrmDeliveryaddressParamsModel:
    def test_valid(self):
        clients_list = [
            ClientsDeliveryAddressPutModel(
                clientLogin="user1",
                clientCodeExternal="EXT1",
                shopsIds=[1],
                currencyId="EUR",
                clientDeliveryAddressFirstName="Jane",
                clientDeliveryAddressLastName="Smith",
                clientDeliveryAddressAdditional="",
                clientDeliveryAddressPhone1="987654321",
                clientDeliveryAddressCity="London",
                clientDeliveryAddressStreet="London Rd 789",
                clientDeliveryAddressRegionId="LDN",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="E1 6AN",
                clientDeliveryAddressCountry="UK",
                clientDeliveryAddressId="DA001"
            )
        ]
        settings = ClientSettingsDeliveryAddressModel(
            clientSettingSendMail=True,
            clientSettingSendSms=False
        )
        dto = PutCrmDeliveryaddressParamsModel(
            clients=clients_list,
            clientsSettings=settings
        )
        assert len(dto.clients) == 1
        assert dto.clients[0].clientDeliveryAddressId == "DA001"


# --- Tests for Endpoints
class TestDeleteEndpoint:
    def test_instantiate(self):
        client = ClientDeliveryAddressModel(
            clientLogin="testuser",
            clientCodeExternal="EXT123",
            clientDeliveryAddressId=1
        )
        params = DeleteCrmDeliveryaddressParamsModel(clients=client)
        endpoint = Delete(params=params)
        assert endpoint.params.clients.clientLogin == "testuser"
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')


class TestGetEndpoint:
    def test_instantiate_without_params(self):
        endpoint = Get()
        assert endpoint.clientCodesExternal is None
        assert endpoint.clientIds is None
        assert endpoint.clientLogins is None
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')

    def test_instantiate_with_params(self):
        endpoint = Get(clientIds=[1, 2], clientLogins=["user1"], clientCodesExternal=["EXT1", "EXT2"])
        assert endpoint.clientIds == [1, 2]
        assert endpoint.clientLogins == ["user1"]
        assert endpoint.clientCodesExternal == ["EXT1", "EXT2"]

    def test_invalid_client_ids_empty_list(self):
        # min_length=1, can't be empty
        with pytest.raises(ValidationError):
            Get(clientIds=[])

    def test_invalid_client_logins_empty_list(self):
        with pytest.raises(ValidationError):
            Get(clientLogins=[])


class TestPostEndpoint:
    def test_instantiate(self):
        clients_list = [
            ClientsDeliveryAddressPostModel(
                clientLogin="user1",
                clientCodeExternal="EXT1",
                shopsIds=[1],
                currencyId="EUR",
                clientDeliveryAddressFirstName="Jane",
                clientDeliveryAddressLastName="Smith",
                clientDeliveryAddressAdditional="",
                clientDeliveryAddressPhone1="987654321",
                clientDeliveryAddressCity="London",
                clientDeliveryAddressStreet="London Rd 789",
                clientDeliveryAddressRegionId="LDN",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="E1 6AN",
                clientDeliveryAddressCountry="UK"
            )
        ]
        settings = ClientSettingsDeliveryAddressModel(
            clientSettingSendMail=True,
            clientSettingSendSms=True
        )
        params = PostCrmDeliveryaddressParamsModel(
            clients=clients_list,
            clientsSettings=settings
        )
        endpoint = Post(params=params)
        assert len(endpoint.params.clients) == 1
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')


class TestPutEndpoint:
    def test_instantiate(self):
        clients_list = [
            ClientsDeliveryAddressPutModel(
                clientLogin="user1",
                clientCodeExternal="EXT1",
                shopsIds=[1],
                currencyId="EUR",
                clientDeliveryAddressFirstName="Jane",
                clientDeliveryAddressLastName="Smith",
                clientDeliveryAddressAdditional="",
                clientDeliveryAddressPhone1="987654321",
                clientDeliveryAddressCity="London",
                clientDeliveryAddressStreet="London Rd 789",
                clientDeliveryAddressRegionId="LDN",
                clientDeliveryAddressProvinceId="Province",
                clientDeliveryAddressZipCode="E1 6AN",
                clientDeliveryAddressCountry="UK",
                clientDeliveryAddressId="DA001"
            )
        ]
        settings = ClientSettingsDeliveryAddressModel(
            clientSettingSendMail=False,
            clientSettingSendSms=False
        )
        params = PutCrmDeliveryaddressParamsModel(
            clients=clients_list,
            clientsSettings=settings
        )
        endpoint = Put(params=params)
        assert len(endpoint.params.clients) == 1
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')
