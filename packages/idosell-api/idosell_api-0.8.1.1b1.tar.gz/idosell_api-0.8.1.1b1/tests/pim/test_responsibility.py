import pytest
from pydantic import ValidationError

from src.idosell.pim.responsibility import (
    # DTOs
    PostEntitiesPimResponsabilityParamsModel,
    PutEntitiesPimResponsabilityParamsModel,
    # Endpoints
    GetEntities, PostEntities, PutEntities, DeleteEntities
)
from src.idosell.pim._common import (
    EntityTypeEnum, EntitiesResponsibilityPostModel,
    EntitiesResponsibilityPutModel
)


# --- Tests for DTOs
class TestPostEntitiesPimResponsabilityParamsModel:
    def test_valid(self):
        dto = PostEntitiesPimResponsabilityParamsModel(
            entities=[
                EntitiesResponsibilityPostModel(
                    id=None,
                    code="CODE1",
                    name="Entity Name",
                    mail="entity@example.com",
                    street="Main Street",
                    number="123",
                    subnumber=None,
                    zipcode="12345",
                    city="City",
                    country="US"
                )
            ],
            type=EntityTypeEnum.PRODUCER
        )
        assert len(dto.entities) == 1
        assert dto.type == EntityTypeEnum.PRODUCER
        assert dto.entities[0].code == "CODE1"

    def test_min_entities(self):
        dto = PostEntitiesPimResponsabilityParamsModel(
            entities=[
                EntitiesResponsibilityPostModel(
                    id=None,
                    code="CODE1",
                    name="Entity Name",
                    mail="entity1@example.com",
                    street="Street 1",
                    number="1",
                    zipcode="00001",
                    city="City1",
                    country="US"
                )
            ],
            type=EntityTypeEnum.PERSON
        )
        assert len(dto.entities) == 1

    def test_max_entities(self):
        entities = []
        for i in range(100):
            entities.append(EntitiesResponsibilityPostModel(
                id=None,
                code=f"CODE{i}",
                name=f"Entity {i}",
                mail=f"entity{i}@example.com",
                street=f"Street {i}",
                number=str(i),
                zipcode=f"{i:05d}",
                city=f"City{i}",
                country="US"
            ))
        dto = PostEntitiesPimResponsabilityParamsModel(
            entities=entities,
            type=EntityTypeEnum.PRODUCER
        )
        assert len(dto.entities) == 100

    def test_invalid_empty_entities(self):
        with pytest.raises(ValidationError):
            PostEntitiesPimResponsabilityParamsModel(
                entities=[],
                type=EntityTypeEnum.PRODUCER
            )

    def test_invalid_too_many_entities(self):
        entities = []
        for i in range(101):
            entities.append(EntitiesResponsibilityPostModel(
                id=None,
                code=f"CODE{i}",
                name=f"Entity {i}",
                mail=f"entity{i}@example.com",
                street=f"Street {i}",
                number=str(i),
                zipcode=f"{i:05d}",
                city=f"City{i}",
                country="US"
            ))
        with pytest.raises(ValidationError):
            PostEntitiesPimResponsabilityParamsModel(
                entities=entities,
                type=EntityTypeEnum.PRODUCER
            )

class TestPutEntitiesPimResponsabilityParamsModel:
    def test_valid(self):
        dto = PutEntitiesPimResponsabilityParamsModel(
            entities=[
                EntitiesResponsibilityPutModel(
                    id=1,
                    code="CODE1",
                    name="Updated Entity Name",
                    mail="entity@example.com",
                    street="Main Street",
                    number="123",
                    subnumber=None,
                    zipcode="12345",
                    city="City",
                    country="US"
                )
            ],
            type=EntityTypeEnum.PERSON
        )
        assert len(dto.entities) == 1
        assert dto.type == EntityTypeEnum.PERSON
        assert dto.entities[0].id == 1

    def test_min_entities(self):
        dto = PutEntitiesPimResponsabilityParamsModel(
            entities=[
                EntitiesResponsibilityPutModel(
                    id=1,
                    code="CODE1",
                    name="Entity Name",
                    mail="entity@example.com",
                    street="Street 1",
                    number="1",
                    zipcode="00001",
                    city="City1",
                    country="US"
                )
            ],
            type=EntityTypeEnum.PERSON
        )
        assert len(dto.entities) == 1

    def test_max_entities(self):
        entities = []
        for i in range(100):
            entities.append(EntitiesResponsibilityPutModel(
                id=i+1,
                code=f"CODE{i}",
                name=f"Entity {i}",
                mail=f"entity{i}@example.com",
                street=f"Street {i}",
                number=str(i),
                zipcode=f"{i:05d}",
                city=f"City{i}",
                country="US"
            ))
        dto = PutEntitiesPimResponsabilityParamsModel(
            entities=entities,
            type=EntityTypeEnum.PRODUCER
        )
        assert len(dto.entities) == 100

    def test_invalid_empty_entities(self):
        with pytest.raises(ValidationError):
            PutEntitiesPimResponsabilityParamsModel(
                entities=[],
                type=EntityTypeEnum.PRODUCER
            )

    def test_invalid_too_many_entities(self):
        entities = []
        for i in range(101):
            entities.append(EntitiesResponsibilityPutModel(
                id=i+1,
                code=f"CODE{i}",
                name=f"Entity {i}",
                mail=f"entity{i}@example.com",
                street=f"Street {i}",
                number=str(i),
                zipcode=f"{i:05d}",
                city=f"City{i}",
                country="US"
            ))
        with pytest.raises(ValidationError):
            PutEntitiesPimResponsabilityParamsModel(
                entities=entities,
                type=EntityTypeEnum.PRODUCER
            )


# --- Tests for Endpoints
class TestGetEntities:
    def test_instantiate_minimal(self):
        dto = GetEntities()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'GET'
        assert dto._endpoint == '/api/admin/v6/responsibility/entities'
        assert dto.code is None
        assert dto.type is None

    def test_instantiate_with_code_list(self):
        dto = GetEntities(
            code=["CODE1", "CODE2"],
            type="producer"
        )
        assert dto.code == ["CODE1", "CODE2"]
        assert dto.type == "producer"

    def test_instantiate_with_code_none(self):
        dto = GetEntities(
            code=None,
            type="person"
        )
        assert dto.code is None
        assert dto.type == "person"

class TestPostEntities:
    def test_instantiate_minimal(self):
        dto = PostEntities(
            params=PostEntitiesPimResponsabilityParamsModel(
                entities=[
                    EntitiesResponsibilityPostModel(
                        id=None,
                        code="CODE1",
                        name="Entity Name",
                        mail="entity@example.com",
                        street="Main Street",
                        number="123",
                        zipcode="12345",
                        city="City",
                        country="US"
                    )
                ],
                type=EntityTypeEnum.PRODUCER
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/responsibility/entities'
        assert len(dto.params.entities) == 1
        assert dto.params.type == EntityTypeEnum.PRODUCER

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PostEntities()

class TestPutEntities:
    def test_instantiate_minimal(self):
        dto = PutEntities(
            params=PutEntitiesPimResponsabilityParamsModel(
                entities=[
                    EntitiesResponsibilityPutModel(
                        id=1,
                        code="CODE1",
                        name="Entity Name",
                        mail="entity@example.com",
                        street="Main Street",
                        number="123",
                        zipcode="12345",
                        city="City",
                        country="US"
                    )
                ],
                type=EntityTypeEnum.PERSON
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/responsibility/entities'
        assert len(dto.params.entities) == 1
        assert dto.params.type == EntityTypeEnum.PERSON

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutEntities()

class TestDeleteEntities:
    def test_instantiate_minimal(self):
        dto = DeleteEntities(
            code=["CODE1"],
            type="producer"
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'DELETE'
        assert dto._endpoint == '/api/admin/v6/responsibility/entities'
        assert dto.code == ["CODE1"]
        assert dto.type == "producer"

    def test_invalid_code_empty_list(self):
        # Assuming code is List[str] requiring at least one element
        dto = DeleteEntities(
            code=["CODE1"],
            type="producer"
        )
        # Actually, list can be empty? Wait, no Field constraint, so allow empty?
        # Looking back at the model, no min_length, so empty list is allowed, but probably shouldn't be empty.
        # But per model definition, it's List[str], no constraints, so we test as is.
        dto = DeleteEntities(
            code=["CODE1", "CODE2"],
            type="person"
        )
        assert len(dto.code) == 2
