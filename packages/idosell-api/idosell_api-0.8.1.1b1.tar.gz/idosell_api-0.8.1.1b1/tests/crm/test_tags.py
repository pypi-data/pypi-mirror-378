import pytest
from pydantic import ValidationError

from src.idosell.crm.tags import (
    OperationTagsEnum, ClientTagsModel, DeleteClearCrmTagsParamsModel,
    DeleteCrmTagsParamsModel, PostCrmTagsParamsModel, PutCrmTagsParamsModel,
    DeleteClear, Delete as DeleteTags, Get, Post, Put
)


# --- Tests for Enums
class TestOperationTagsEnum:
    def test_valid_values(self):
        assert OperationTagsEnum.ADD == 'add'
        assert OperationTagsEnum.SET == 'set'
        assert OperationTagsEnum.SUBSTRACT == 'substract'


# --- Tests for DTOs
class TestClientTagsModel:
    def test_valid(self):
        dto = ClientTagsModel(
            tagId=1,
            operation=OperationTagsEnum.ADD,
            tagValue=10
        )
        assert dto.tagId == 1
        assert dto.operation == OperationTagsEnum.ADD
        assert dto.tagValue == 10

    def test_invalid_tag_id(self):
        with pytest.raises(ValidationError):
            ClientTagsModel(
                tagId=0,
                operation=OperationTagsEnum.ADD,
                tagValue=10
            )

    def test_invalid_tag_value(self):
        with pytest.raises(ValidationError):
            ClientTagsModel(
                tagId=1,
                operation=OperationTagsEnum.ADD,
                tagValue=0
            )

class TestDeleteClearCrmTagsParamsModel:
    def test_valid(self):
        dto = DeleteClearCrmTagsParamsModel(clientId=1)
        assert dto.clientId == 1

    def test_invalid_client_id(self):
        with pytest.raises(ValidationError):
            DeleteClearCrmTagsParamsModel(clientId=0)

class TestDeleteCrmTagsParamsModel:
    def test_valid(self):
        dto = DeleteCrmTagsParamsModel(
            clientId=1,
            tagId=1
        )
        assert dto.clientId == 1
        assert dto.tagId == 1

    def test_invalid_client_id(self):
        with pytest.raises(ValidationError):
            DeleteCrmTagsParamsModel(
                clientId=0,
                tagId=1
            )

    def test_invalid_tag_id(self):
        with pytest.raises(ValidationError):
            DeleteCrmTagsParamsModel(
                clientId=1,
                tagId=0
            )

class TestPostCrmTagsParamsModel:
    def test_valid(self):
        dto = PostCrmTagsParamsModel(
            clientId=1,
            tagName="VIP Customer",
            tagValue=5
        )
        assert dto.clientId == 1
        assert dto.tagName == "VIP Customer"
        assert dto.tagValue == 5

    def test_invalid_client_id(self):
        with pytest.raises(ValidationError):
            PostCrmTagsParamsModel(
                clientId=0,
                tagName="Test",
                tagValue=1
            )

    def test_invalid_tag_value(self):
        with pytest.raises(ValidationError):
            PostCrmTagsParamsModel(
                clientId=1,
                tagName="Test",
                tagValue=0
            )

class TestPutCrmTagsParamsModel:
    def test_valid(self):
        dto = PutCrmTagsParamsModel(
            clientId=1,
            clientTags=[
                ClientTagsModel(
                    tagId=1,
                    operation=OperationTagsEnum.SET,
                    tagValue=100
                ),
                ClientTagsModel(
                    tagId=2,
                    operation=OperationTagsEnum.ADD,
                    tagValue=50
                )
            ]
        )
        assert dto.clientId == 1
        assert len(dto.clientTags) == 2

    def test_invalid_client_id(self):
        with pytest.raises(ValidationError):
            PutCrmTagsParamsModel(
                clientId=0,
                clientTags=[
                    ClientTagsModel(
                        tagId=1,
                        operation=OperationTagsEnum.SET,
                        tagValue=100
                    )
                ]
            )


# --- Tests for Endpoints
class TestDeleteClear:
    def test_instantiate(self):
        dto = DeleteClear(
            params=DeleteClearCrmTagsParamsModel(clientId=1)
        )
        assert dto.params.clientId == 1
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestDeleteTags:
    def test_instantiate(self):
        dto = DeleteTags(
            params=[
                DeleteCrmTagsParamsModel(clientId=1, tagId=1),
                DeleteCrmTagsParamsModel(clientId=1, tagId=2)
            ]
        )
        assert len(dto.params) == 2
        assert dto.params[0].clientId == 1

class TestGet:
    def test_instantiate_without_params(self):
        dto = Get()
        assert dto.clientId is None
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

    def test_instantiate_with_params(self):
        dto = Get(clientId=1)
        assert dto.clientId == 1

    def test_invalid_client_id(self):
        with pytest.raises(ValidationError):
            Get(clientId=0)

class TestPost:
    def test_instantiate(self):
        dto = Post(
            params=PostCrmTagsParamsModel(
                clientId=1,
                tagName="New Tag",
                tagValue=10
            )
        )
        assert dto.params.clientId == 1
        assert dto.params.tagName == "New Tag"

class TestPut:
    def test_instantiate(self):
        dto = Put(
            params=PutCrmTagsParamsModel(
                clientId=1,
                clientTags=[
                    ClientTagsModel(
                        tagId=1,
                        operation=OperationTagsEnum.SET,
                        tagValue=25
                    )
                ]
            )
        )
        assert dto.params.clientId == 1
        assert len(dto.params.clientTags) == 1
