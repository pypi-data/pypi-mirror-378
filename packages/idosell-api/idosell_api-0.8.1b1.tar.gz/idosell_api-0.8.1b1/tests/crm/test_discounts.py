import pytest
from pydantic import ValidationError

from src.idosell.crm.discounts import (
    ReturnElementsEnum, CategoriesModel, ProductsDiscountsModel, ProducersModel, SeriesModel,
    MenuItemsModel, DeleteGroupsCrmDiscountsParamsModel, PostGroupsCrmDiscountsParamsModel,
    PutGroupsCrmDiscountsParamsModel, DeleteGroupsProductsCrmDiscountsParamsModel,
    PutGroupsProductsCrmDiscountsParamsModel, GetGroupsClients, DeleteGroups, GetGroups,
    PostGroups, PutGroups, DeleteGroupsProducts, PutGroupsProducts, PutRebatesBlockCard,
    DeleteRebatesCard, PostRebatesCard, DeleteRebatesCode, PostRebatesCode, PutRebatesUnblockCard
)


# --- Tests for Enums
class TestReturnElementsEnum:
    def test_valid_values(self):
        assert ReturnElementsEnum.GROUPNUMBER == 'groupNumber'
        assert ReturnElementsEnum.GROUPCOMBINED == 'groupCombined'
        assert ReturnElementsEnum.GROUPTYPE == 'groupType'
        assert ReturnElementsEnum.GROUPREBATE == 'groupRebate'
        assert ReturnElementsEnum.GROUPNAME == 'groupName'


# --- Tests for DTOs
class TestCategoriesModel:
    def test_valid(self):
        dto = CategoriesModel(
            id=1,
            price=100.50,
            currency="PLN"
        )
        assert dto.id == 1
        assert dto.price == 100.50

    def test_invalid_id(self):
        with pytest.raises(ValidationError):
            CategoriesModel(
                id=0,
                price=100.50,
                currency="PLN"
            )

    def test_invalid_price(self):
        with pytest.raises(ValidationError):
            CategoriesModel(
                id=1,
                price=0.0,
                currency="PLN"
            )

class TestProductsDiscountsModel:
    def test_valid(self):
        dto = ProductsDiscountsModel(
            id=1,
            price=75.25,
            currency="USD"
        )
        assert dto.id == 1

class TestProducersModel:
    def test_valid(self):
        dto = ProducersModel(
            id=2,
            price=200.00,
            currency="EUR"
        )
        assert dto.id == 2

class TestSeriesModel:
    def test_valid(self):
        dto = SeriesModel(
            id=3,
            price=150.75,
            currency="GBP"
        )
        assert dto.id == 3

class TestMenuItemsModel:
    def test_valid(self):
        dto = MenuItemsModel(
            id=4,
            price=25.00,
            currency="PLN"
        )
        assert dto.id == 4

class TestDeleteGroupsCrmDiscountsParamsModel:
    def test_valid(self):
        dto = DeleteGroupsCrmDiscountsParamsModel(
            discountGroupId=1
        )
        assert dto.discountGroupId == 1

class TestPostGroupsCrmDiscountsParamsModel:
    def test_valid(self):
        dto = PostGroupsCrmDiscountsParamsModel(
            discountGroupName="VIP customers"
        )
        assert dto.discountGroupName == "VIP customers"

class TestPutGroupsCrmDiscountsParamsModel:
    def test_valid(self):
        dto = PutGroupsCrmDiscountsParamsModel(
            discountGroupId=1,
            discountGroupName="Updated VIP customers"
        )
        assert dto.discountGroupId == 1
        assert dto.discountGroupName == "Updated VIP customers"

    def test_invalid_discount_group_id(self):
        with pytest.raises(ValidationError):
            PutGroupsCrmDiscountsParamsModel(
                discountGroupId=0,
                discountGroupName="Invalid group"
            )

class TestDeleteGroupsProductsCrmDiscountsParamsModel:
    def test_valid_with_discount_group_ids(self):
        dto = DeleteGroupsProductsCrmDiscountsParamsModel(
            discountGroupId=1
        )
        assert dto.discountGroupId == 1

    def test_valid_with_products(self):
        dto = DeleteGroupsProductsCrmDiscountsParamsModel(
            products=[1, 2, 3]
        )
        assert dto.products == [1, 2, 3]

    def test_valid_none(self):
        # Test that all None values should raise validation error
        with pytest.raises(ValidationError, match="At least one field must be provided"):
            DeleteGroupsProductsCrmDiscountsParamsModel()

class TestPutGroupsProductsCrmDiscountsParamsModel:
    def test_valid(self):
        dto = PutGroupsProductsCrmDiscountsParamsModel(
            discountGroupId=1,
            products=[
                ProductsDiscountsModel(
                    id=1,
                    price=50.00,
                    currency="PLN"
                )
            ],
            producers=[
                ProducersModel(
                    id=1,
                    price=75.00,
                    currency="PLN"
                )
            ],
            series=[
                SeriesModel(
                    id=1,
                    price=60.00,
                    currency="PLN"
                )
            ],
            categories=[
                CategoriesModel(
                    id=1,
                    price=70.00,
                    currency="PLN"
                )
            ],
            menuItems=[
                MenuItemsModel(
                    id=1,
                    price=45.00,
                    currency="PLN"
                )
            ]
        )
        assert dto.discountGroupId == 1
        assert len(dto.products) == 1

    def test_invalid_discount_group_id(self):
        with pytest.raises(ValidationError):
            PutGroupsProductsCrmDiscountsParamsModel(
                discountGroupId=0,
                products=[],
                producers=[],
                series=[],
                categories=[],
                menuItems=[]
            )


# --- Tests for Endpoints
class TestGetGroupsClients:
    def test_instantiate(self):
        dto = GetGroupsClients(discountGroupId=1)
        assert dto.discountGroupId == 1

    def test_invalid_discount_group_id(self):
        with pytest.raises(ValidationError):
            GetGroupsClients(discountGroupId=-1)

class TestDeleteGroups:
    def test_instantiate(self):
        dto = DeleteGroups(
            params=DeleteGroupsCrmDiscountsParamsModel(discountGroupId=1)
        )
        assert dto.params.discountGroupId == 1

class TestGetGroups:
    def test_instantiate_minimal(self):
        dto = GetGroups()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

    def test_instantiate_with_params(self):
        dto = GetGroups(
            groupNumbers=[1, 2, 3],
            returnElements=[ReturnElementsEnum.GROUPNUMBER, ReturnElementsEnum.GROUPNAME]
        )
        assert dto.groupNumbers == [1, 2, 3]
        assert ReturnElementsEnum.GROUPNUMBER in dto.returnElements

class TestPostGroups:
    def test_instantiate(self):
        dto = PostGroups(
            params=PostGroupsCrmDiscountsParamsModel(discountGroupName="Test Group")
        )
        assert dto.params.discountGroupName == "Test Group"

class TestPutGroups:
    def test_instantiate(self):
        dto = PutGroups(
            params=PutGroupsCrmDiscountsParamsModel(
                discountGroupId=1,
                discountGroupName="Updated Group"
            )
        )
        assert dto.params.discountGroupId == 1

class TestDeleteGroupsProducts:
    def test_instantiate(self):
        dto = DeleteGroupsProducts(
            params=DeleteGroupsProductsCrmDiscountsParamsModel(discountGroupId=1)
        )
        assert dto.params.discountGroupId == 1

class TestPutGroupsProducts:
    def test_instantiate(self):
        dto = PutGroupsProducts(
            params=PutGroupsProductsCrmDiscountsParamsModel(
                discountGroupId=1,
                products=[ProductsDiscountsModel(id=1, price=50.00, currency="PLN")],
                producers=[ProducersModel(id=1, price=75.00, currency="PLN")],
                series=[SeriesModel(id=1, price=60.00, currency="PLN")],
                categories=[CategoriesModel(id=1, price=70.00, currency="PLN")],
                menuItems=[MenuItemsModel(id=1, price=45.00, currency="PLN")]
            )
        )
        assert dto.params.discountGroupId == 1

class TestPutRebatesBlockCard:
    def test_instantiate(self):
        dto = PutRebatesBlockCard(card_number="CARD123")
        assert dto.card_number == "CARD123"

class TestDeleteRebatesCard:
    def test_instantiate(self):
        dto = DeleteRebatesCard(campaign_id=1)
        assert dto.campaign_id == 1

    def test_invalid_campaign_id(self):
        with pytest.raises(ValidationError):
            DeleteRebatesCard(campaign_id=0)

class TestPostRebatesCard:
    def test_instantiate(self):
        dto = PostRebatesCard(
            campaign_id=1,
            card_number="NEW123"
        )
        assert dto.campaign_id == 1
        assert dto.card_number == "NEW123"

class TestDeleteRebatesCode:
    def test_instantiate(self):
        dto = DeleteRebatesCode(campaign_id=1)
        assert dto.campaign_id == 1

class TestPostRebatesCode:
    def test_instantiate(self):
        dto = PostRebatesCode(
            campaign_id=1,
            code_number="DISCOUNT50"
        )
        assert dto.campaign_id == 1
        assert dto.code_number == "DISCOUNT50"

class TestPutRebatesUnblockCard:
    def test_instantiate(self):
        dto = PutRebatesUnblockCard(card_number="CARD123")
        assert dto.card_number == "CARD123"
