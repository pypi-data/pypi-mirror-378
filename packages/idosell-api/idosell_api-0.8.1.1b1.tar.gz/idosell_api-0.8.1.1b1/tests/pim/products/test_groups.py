import pytest
from pydantic import ValidationError

from src.idosell.pim.products.groups import (
    # DTOs
    PutMainProductPimProductsGroupsParamsModel,
    PutOrderPimProductsGroupsParamsModel,
    PutSettingsPimProductsGroupsParamsModel,
    # Endpoints
    PutMainProduct,
    PutOrder,
    PutSettings,
)
from src.idosell.pim.products._common import (
    ProductIdentModel,
    ProductsInOrderModel,
    GroupsPutSettingsModel,
    IdentTypeEnum,
    DisplayInPanelEnum,
    DisplayOnPageEnum,
)


# --- Tests for DTOs
class TestPutMainProductPimProductsGroupsParamsModel:
    def test_valid(self):
        dto = PutMainProductPimProductsGroupsParamsModel(
            groups=[
                ProductIdentModel(
                    identValue="123",
                    productIdentType=IdentTypeEnum.ID
                )
            ]
        )
        assert len(dto.groups) == 1
        assert dto.groups[0].identValue == "123"

    def test_multiple_groups(self):
        dto = PutMainProductPimProductsGroupsParamsModel(
            groups=[
                ProductIdentModel(
                    identValue="123",
                    productIdentType=IdentTypeEnum.ID
                ),
                ProductIdentModel(
                    identValue="456",
                    productIdentType=IdentTypeEnum.INDEX
                )
            ]
        )
        assert len(dto.groups) == 2

    def test_empty_groups(self):
        # Should raise ValidationError due to min_length=1
        with pytest.raises(ValidationError):
            PutMainProductPimProductsGroupsParamsModel(groups=[])


class TestPutOrderPimProductsGroupsParamsModel:
    def test_valid(self):
        dto = PutOrderPimProductsGroupsParamsModel(
            groups=[
                ProductsInOrderModel(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    priority=1
                )
            ]
        )
        assert len(dto.groups) == 1
        assert dto.groups[0].priority == 1

    def test_multiple_groups(self):
        dto = PutOrderPimProductsGroupsParamsModel(
            groups=[
                ProductsInOrderModel(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    priority=1
                ),
                ProductsInOrderModel(
                    productIdent=ProductIdentModel(
                        identValue="456",
                        productIdentType=IdentTypeEnum.INDEX
                    ),
                    priority=2
                )
            ]
        )
        assert len(dto.groups) == 2

    def test_empty_groups(self):
        # Should raise ValidationError due to min_length=1
        with pytest.raises(ValidationError):
            PutOrderPimProductsGroupsParamsModel(groups=[])

    def test_invalid_priority_zero(self):
        with pytest.raises(ValidationError):
            PutOrderPimProductsGroupsParamsModel(
                groups=[
                    ProductsInOrderModel(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        priority=0
                    )
                ]
            )


class TestPutSettingsPimProductsGroupsParamsModel:
    def test_valid(self):
        dto = PutSettingsPimProductsGroupsParamsModel(
            groups=[
                GroupsPutSettingsModel(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    displayInPanel=DisplayInPanelEnum.ALL,
                    displayOnPage=DisplayOnPageEnum.ALL,
                    specifiedProductIdent=ProductIdentModel(
                        identValue="456",
                        productIdentType=IdentTypeEnum.ID
                    )
                )
            ]
        )
        assert len(dto.groups) == 1
        assert dto.groups[0].displayInPanel == DisplayInPanelEnum.ALL

    def test_multiple_groups(self):
        dto = PutSettingsPimProductsGroupsParamsModel(
            groups=[
                GroupsPutSettingsModel(
                    productIdent=ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    ),
                    displayInPanel=DisplayInPanelEnum.ALL,
                    displayOnPage=DisplayOnPageEnum.ALL,
                    specifiedProductIdent=ProductIdentModel(
                        identValue="456",
                        productIdentType=IdentTypeEnum.ID
                    )
                ),
                GroupsPutSettingsModel(
                    productIdent=ProductIdentModel(
                        identValue="789",
                        productIdentType=IdentTypeEnum.INDEX
                    ),
                    displayInPanel=DisplayInPanelEnum.FIRSTAVAILABLE,
                    displayOnPage=DisplayOnPageEnum.SPECIFIED,
                    specifiedProductIdent=ProductIdentModel(
                        identValue="101",
                        productIdentType=IdentTypeEnum.ID
                    )
                )
            ]
        )
        assert len(dto.groups) == 2

    def test_empty_groups(self):
        # Should raise ValidationError due to min_length=1
        with pytest.raises(ValidationError):
            PutSettingsPimProductsGroupsParamsModel(groups=[])


# --- Tests for Endpoints
class TestPutMainProduct:
    def test_instantiate_minimal(self):
        dto = PutMainProduct(
            params=PutMainProductPimProductsGroupsParamsModel(
                groups=[
                    ProductIdentModel(
                        identValue="123",
                        productIdentType=IdentTypeEnum.ID
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/groups/mainProduct'
        assert len(dto.params.groups) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutMainProduct()

    def test_invalid_params_empty_groups(self):
        with pytest.raises(ValidationError):
            PutMainProduct(
                params=PutMainProductPimProductsGroupsParamsModel(groups=[])
            )


class TestPutOrder:
    def test_instantiate_minimal(self):
        dto = PutOrder(
            params=PutOrderPimProductsGroupsParamsModel(
                groups=[
                    ProductsInOrderModel(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        priority=1
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/groups/order'
        assert len(dto.params.groups) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutOrder()

    def test_invalid_params_empty_groups(self):
        with pytest.raises(ValidationError):
            PutOrder(
                params=PutOrderPimProductsGroupsParamsModel(groups=[])
            )


class TestPutSettings:
    def test_instantiate_minimal(self):
        dto = PutSettings(
            params=PutSettingsPimProductsGroupsParamsModel(
                groups=[
                    GroupsPutSettingsModel(
                        productIdent=ProductIdentModel(
                            identValue="123",
                            productIdentType=IdentTypeEnum.ID
                        ),
                        displayInPanel=DisplayInPanelEnum.ALL,
                        displayOnPage=DisplayOnPageEnum.ALL,
                        specifiedProductIdent=ProductIdentModel(
                            identValue="456",
                            productIdentType=IdentTypeEnum.ID
                        )
                    )
                ]
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/groups/settings'
        assert len(dto.params.groups) == 1

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutSettings()

    def test_invalid_params_empty_groups(self):
        with pytest.raises(ValidationError):
            PutSettings(
                params=PutSettingsPimProductsGroupsParamsModel(groups=[])
            )
