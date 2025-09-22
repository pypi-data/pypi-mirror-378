import pytest
from pydantic import ValidationError

from src.idosell.pim.products.opinions import (
    # DTOs
    DeletePimProductsOpinionsParamsModel,
    PostPimProductsOpinionsParamsModel,
    PutPimProductsOpinionsParamsModel,
    # Endpoints
    Delete,
    Get,
    Post,
    Put,
    GetRate,
)
from src.idosell.pim.products._common import (
    OpinionGetModel,
    OrdersByGetModel,
    OpinionsPostModel,
    RateEnum,
    ClientsOpinionsModel,
    ProductsModel,
    ElementNameEnum,
    SortDirectionEnum,
    TypeProductsEnum,
)



# --- Tests for DTOs
class TestDeletePimProductsOpinionsParamsModel:
    def test_valid(self):
        dto = DeletePimProductsOpinionsParamsModel(
            id=123
        )
        assert dto.id == 123

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            DeletePimProductsOpinionsParamsModel(id=0)


class TestPostPimProductsOpinionsParamsModel:
    def test_valid(self):
        dto = PostPimProductsOpinionsParamsModel(
            opinions=OpinionsPostModel(
                createDate="2023-01-01",
                confirmed=True,
                rating="5",
                content="Great product!",
                language="en",
                picture="img.png",
                shopId=1,
                host="example.com",
clients=ClientsOpinionsModel(
    type="text",  # type: ignore
    value="test@example.com",
    name="Test User",
    email="test@example.com"
),
                scorePositive=10,
                scoreNegative=0,
                products=ProductsModel(
                    type=TypeProductsEnum.ID,
                    value="123"
                ),
                orderSerialNumber=456,
                shopAnswer="Thank you!",
                opinionConfirmedByPurchase=True
            )
        )
        assert dto.opinions.rating == "5"


class TestPutPimProductsOpinionsParamsModel:
    def test_valid(self):
        dto = PutPimProductsOpinionsParamsModel(
            id=123,
            confirmed='y',  # type: ignore
            rating=5,
            content="Updated content",
            language="en",
            shopAnswer="Shop answer",
            picture="img.png",
            opinionConfirmedByPurchase=True
        )
        assert dto.id == 123


# --- Tests for Endpoints
class TestDelete:
    def test_instantiate_minimal(self):
        dto = Delete(
            params=DeletePimProductsOpinionsParamsModel(
                id=123
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/opinions/opinions/delete'
        assert dto.params.id == 123

    def test_invalid_id(self):
        with pytest.raises(ValidationError):
            Delete(params=DeletePimProductsOpinionsParamsModel(id=0))


class TestGet:
    def test_instantiate_minimal(self):
        dto = Get()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/opinions/opinions'
        assert dto.opinion is None

    def test_instantiate_with_opinion(self):
        dto = Get(
            opinion=OpinionGetModel(
                id=123,
                language="en",
                confirmed=True,
                shopId=1,
                host="example.com"
            )
        )
        if dto.opinion:
            assert dto.opinion.id == 123
        # type: ignore

    def test_instantiate_with_orders_by(self):
        dto = Get(
            ordersBy=[
                OrdersByGetModel(
                    elementName=ElementNameEnum.DATE,
                    sortDirection=SortDirectionEnum.DESC
                )
            ]
        )
        if dto.ordersBy:
            assert len(dto.ordersBy) == 1

    def test_invalid_orders_by_empty(self):
        with pytest.raises(ValidationError):
            Get(ordersBy=[])


class TestPost:
    def test_instantiate_minimal(self):
        dto = Post(
            params=PostPimProductsOpinionsParamsModel(
                opinions=OpinionsPostModel(
                    createDate="2023-01-01",
                    confirmed=True,
                    rating="5",
                    content="Great product!",
                    language="en",
                    picture="img.png",
                    shopId=1,
                    host="example.com",
                clients=ClientsOpinionsModel(
                    type="text",  # type: ignore
                    value="test@example.com",
                    name="Test User",
                    email="test@example.com"
                ),
                    scorePositive=10,
                    scoreNegative=0,
                    products=ProductsModel(
                        type=TypeProductsEnum.ID,
                        value="123"
                    ),
                    orderSerialNumber=456,
                    shopAnswer="Thank you!",
                    opinionConfirmedByPurchase=True
                )
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/opinions/opinions'
        assert dto.params.opinions.rating == "5"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Post()


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsOpinionsParamsModel(
                id=123,
                confirmed='y',
                rating=5,
                content="Updated content",
                language="en",
                shopAnswer="Shop answer",
                picture="img.png",
                opinionConfirmedByPurchase=True
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/opinions/opinions'
        assert dto.params.id == 123

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()


class TestGetRate:
    def test_instantiate_minimal(self):
        dto = GetRate(
            id=123,
            operation=RateEnum.POSITIVE
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/opinions/rate'
        assert dto.id == 123
        assert dto.operation == RateEnum.POSITIVE

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            GetRate(id=0, operation=RateEnum.POSITIVE)
