import pytest
from pydantic import ValidationError

from src.idosell.pim.products.questions import (
    # DTOs
    PutPimProductsQuestionsParamsModel,
    # Endpoints
    Get,
    Put,
)
from src.idosell.pim.products._common import (
    QuestionsPutModel,
    ProductIdentQuestionsModel,
    ProductIdentTypeQuestionsEnum,
)


# --- Tests for DTOs
class TestPutPimProductsQuestionsParamsModel:
    def test_valid(self):
        dto = PutPimProductsQuestionsParamsModel(
            questions=[
                QuestionsPutModel(
                    id=1,
                    lang="pol",
                    question="VGVzdCBxdWVzdGlvbj8=",  # base64 encoded
                    answer="VGVzdCBhbnN3ZXI=",  # base64 encoded
                    dateAdd="2023-01-01 12:00:00",
                    host="example.com",
                    author="Test Author",
                    productIdent=ProductIdentQuestionsModel(
                        productId="123",
                        productIdentType=ProductIdentTypeQuestionsEnum.ID
                    ),
                    visible='y',
                    priority=1,
                    confirmed='y',
                    shopId=1,
                    answerDate="2023-01-02 12:00:00",
                    answerAuthor="Test Answer Author"
                )
            ]
        )
        assert len(dto.questions) == 1
        assert dto.questions[0].id == 1

    def test_multiple_questions(self):
        dto = PutPimProductsQuestionsParamsModel(
            questions=[
                QuestionsPutModel(
                    id=1,
                    lang="pol",
                    question="VGVzdCBxdWVzdGlvbj8=",
                    answer="VGVzdCBhbnN3ZXI=",
                    dateAdd="2023-01-01 12:00:00",
                    host="example.com",
                    author="Test Author",
                    productIdent=ProductIdentQuestionsModel(
                        productId="123",
                        productIdentType=ProductIdentTypeQuestionsEnum.ID
                    ),
                    visible='y',
                    priority=1,
                    confirmed='y',
                    shopId=1,
                    answerDate="2023-01-02 12:00:00",
                    answerAuthor="Test Answer Author"
                ),
                QuestionsPutModel(
                    id=2,
                    lang="eng",
                    question="VGVzdCBxdWVzdGlvbj8=",
                    answer="VGVzdCBhbnN3ZXI=",
                    dateAdd="2023-01-01 12:00:00",
                    host="example.com",
                    author="Test Author2",
                    productIdent=ProductIdentQuestionsModel(
                        productId="456",
                        productIdentType=ProductIdentTypeQuestionsEnum.CODEEXTERN
                    ),
                    visible='n',
                    priority=2,
                    confirmed='n',
                    shopId=1,
                    answerDate="2023-01-02 12:00:00",
                    answerAuthor="Test Answer Author2"
                )
            ]
        )
        assert len(dto.questions) == 2

    def test_empty_questions(self):
        # Empty questions list is allowed
        dto = PutPimProductsQuestionsParamsModel(questions=[])
        assert len(dto.questions) == 0


class TestQuestionsPutModel:
    def test_valid(self):
        model = QuestionsPutModel(
            id=1,
            lang="pol",
            question="VGVzdCBxdWVzdGlvbj8=",
            answer="VGVzdCBhbnN3ZXI=",
            dateAdd="2023-01-01 12:00:00",
            host="example.com",
            author="Test Author",
            productIdent=ProductIdentQuestionsModel(
                productId="123",
                productIdentType=ProductIdentTypeQuestionsEnum.ID
            ),
            visible='y',
            priority=1,
            confirmed='y',
            shopId=1,
            answerDate="2023-01-02 12:00:00",
            answerAuthor="Test Answer Author"
        )
        assert model.id == 1
        assert model.productIdent.productId == "123"

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            QuestionsPutModel(
                id=0,
                lang="pol",
                question="VGVzdCBxdWVzdGlvbj8=",
                answer="VGVzdCBhbnN3ZXI=",
                dateAdd="2023-01-01 12:00:00",
                host="example.com",
                author="Test Author",
                productIdent=ProductIdentQuestionsModel(
                    productId="123",
                    productIdentType=ProductIdentTypeQuestionsEnum.ID
                ),
                visible='y',
                priority=1,
                confirmed='y',
                shopId=1,
                answerDate="2023-01-02 12:00:00",
                answerAuthor="Test Answer Author"
            )

    def test_invalid_priority_zero(self):
        with pytest.raises(ValidationError):
            QuestionsPutModel(
                id=1,
                lang="pol",
                question="VGVzdCBxdWVzdGlvbj8=",
                answer="VGVzdCBhbnN3ZXI=",
                dateAdd="2023-01-01 12:00:00",
                host="example.com",
                author="Test Author",
                productIdent=ProductIdentQuestionsModel(
                    productId="123",
                    productIdentType=ProductIdentTypeQuestionsEnum.ID
                ),
                visible='y',
                priority=0,
                confirmed='y',
                shopId=1,
                answerDate="2023-01-02 12:00:00",
                answerAuthor="Test Answer Author"
            )

    def test_invalid_shop_id_zero(self):
        with pytest.raises(ValidationError):
            QuestionsPutModel(
                id=1,
                lang="pol",
                question="VGVzdCBxdWVzdGlvbj8=",
                answer="VGVzdCBhbnN3ZXI=",
                dateAdd="2023-01-01 12:00:00",
                host="example.com",
                author="Test Author",
                productIdent=ProductIdentQuestionsModel(
                    productId="123",
                    productIdentType=ProductIdentTypeQuestionsEnum.ID
                ),
                visible='y',
                priority=1,
                confirmed='y',
                shopId=0,
                answerDate="2023-01-02 12:00:00",
                answerAuthor="Test Answer Author"
            )


class TestProductIdentQuestionsModel:
    def test_valid(self):
        model = ProductIdentQuestionsModel(
            productId="123",
            productIdentType=ProductIdentTypeQuestionsEnum.ID
        )
        assert model.productId == "123"
        assert model.productIdentType == ProductIdentTypeQuestionsEnum.ID

    def test_empty_product_id(self):
        # Empty productId is allowed
        model = ProductIdentQuestionsModel(
            productId="",
            productIdentType=ProductIdentTypeQuestionsEnum.ID
        )
        assert model.productId == ""


# --- Tests for Endpoints
class TestGet:
    def test_instantiate_minimal(self):
        dto = Get(
            id=None,
            productId=None
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/products/questions'
        assert dto.id is None
        assert dto.productId is None

    def test_instantiate_with_id(self):
        dto = Get(id=1)
        assert dto.id == 1

    def test_instantiate_with_product_id(self):
        dto = Get(productId=123)
        assert dto.productId == 123

    def test_instantiate_with_both(self):
        dto = Get(id=1, productId=123)
        assert dto.id == 1
        assert dto.productId == 123

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            Get(id=0)

    def test_invalid_product_id_zero(self):
        with pytest.raises(ValidationError):
            Get(productId=0)


class TestPut:
    def test_instantiate_minimal(self):
        dto = Put(
            params=PutPimProductsQuestionsParamsModel(
                questions=[
                    QuestionsPutModel(
                        id=1,
                        lang="pol",
                        question="VGVzdCBxdWVzdGlvbj8=",
                        answer="VGVzdCBhbnN3ZXI=",
                        dateAdd="2023-01-01 12:00:00",
                        host="example.com",
                        author="Test Author",
                        productIdent=ProductIdentQuestionsModel(
                            productId="123",
                            productIdentType=ProductIdentTypeQuestionsEnum.ID
                        ),
                        visible='y',
                        priority=1,
                        confirmed='y',
                        shopId=1,
                        answerDate="2023-01-02 12:00:00",
                        answerAuthor="Test Answer Author"
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/questions'
        assert len(dto.params.questions) == 1

    def test_instantiate_with_full_data(self):
        dto = Put(
            params=PutPimProductsQuestionsParamsModel(
                questions=[
                    QuestionsPutModel(
                        id=1,
                        lang="pol",
                        question="VGVzdCBxdWVzdGlvbj8=",
                        answer="VGVzdCBhbnN3ZXI=",
                        dateAdd="2023-01-01 12:00:00",
                        host="example.com",
                        author="Test Author",
                        productIdent=ProductIdentQuestionsModel(
                            productId="123",
                            productIdentType=ProductIdentTypeQuestionsEnum.ID
                        ),
                        visible='y',
                        priority=1,
                        confirmed='y',
                        shopId=1,
                        answerDate="2023-01-02 12:00:00",
                        answerAuthor="Test Answer Author"
                    ),
                    QuestionsPutModel(
                        id=2,
                        lang="eng",
                        question="VGVzdCBxdWVzdGlvbjI=",
                        answer="VGVzdCBhbnN3ZXIy",
                        dateAdd="2023-01-02 12:00:00",
                        host="example2.com",
                        author="Test Author2",
                        productIdent=ProductIdentQuestionsModel(
                            productId="456",
                            productIdentType=ProductIdentTypeQuestionsEnum.CODEEXTERN
                        ),
                        visible='n',
                        priority=2,
                        confirmed='y',
                        shopId=2,
                        answerDate="2023-01-03 12:00:00",
                        answerAuthor="Test Answer Author2"
                    )
                ]
            )
        )
        assert len(dto.params.questions) == 2
        assert dto.params.questions[1].lang == "eng"

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            Put()

    def test_params_empty_questions(self):
        # Empty questions list is allowed
        dto = Put(
            params=PutPimProductsQuestionsParamsModel(questions=[])
        )
        assert len(dto.params.questions) == 0
