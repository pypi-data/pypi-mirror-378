import pytest
from pydantic import ValidationError

from src.idosell.cms._common import (
    ClientTypeEnum, PageEnum, ZoneEnum,
    BodyModel, DisplayBaseModel, SourceFilterModel, SourceModel
)
from src.idosell._common import AllYNEnum, BooleanStrShortEnum


# --- Tests for Enums
class TestClientTypeEnum:
    def test_valid_values(self):
        assert ClientTypeEnum.ALL == 'all'
        assert ClientTypeEnum.UNREGISTERED == 'unregistered'
        assert ClientTypeEnum.REGISTERED == 'registered'
        assert ClientTypeEnum.RETAILER == 'retailer'
        assert ClientTypeEnum.WHOLESALER == 'wholesaler'

class TestPageEnum:
    def test_valid_values(self):
        assert PageEnum.HOME == 'home'
        assert PageEnum.BASKET == 'basket'
        assert PageEnum.CHECKOUT_PAYMENT_DELIVERY == 'checkout_payment_delivery'
        assert PageEnum.CHECKOUT_CONFIRMATION == 'checkout_confirmation'
        assert PageEnum.NEW_ORDER_PLACEMENT == 'new_order_placement'
        assert PageEnum.ORDER_DETAILS == 'order_details'
        assert PageEnum.NAVIGATION == 'navigation'
        assert PageEnum.PRODUCT_DETAILS == 'product_details'
        assert PageEnum.SEARCH_RESULTS == 'search_results'
        assert PageEnum.AFTER_ORDER_PLACE == 'after_order_place'
        assert PageEnum.MAILING_SUBSCRIBE == 'mailing_subscribe'
        assert PageEnum.PAYMENT_SUCCESS == 'payment_success'
        assert PageEnum.PAYMENT_ERROR == 'payment_error'
        assert PageEnum.PAYMENT_PENDING == 'payment_pending'
        assert PageEnum.OTHER_PAGES == 'other_pages'

class TestZoneEnum:
    def test_valid_values(self):
        assert ZoneEnum.HEAD == 'head'
        assert ZoneEnum.BODYBEGIN == 'bodyBegin'
        assert ZoneEnum.BODYEND == 'bodyEnd'


# --- Tests for DTOs
class TestBodyModel:
    def test_valid(self):
        dto = BodyModel(
            lang="eng",
            body="<html></html>"
        )
        assert dto.lang == "eng"
        assert dto.body == "<html></html>"

    def test_invalid_lang_length_short(self):
        with pytest.raises(ValidationError):
            BodyModel(
                lang="en",
                body="test"
            )

    def test_invalid_lang_length_long(self):
        with pytest.raises(ValidationError):
            BodyModel(
                lang="engg",
                body="test"
            )

class TestDisplayBaseModel:
    def test_valid(self):
        dto = DisplayBaseModel(
            clientType=ClientTypeEnum.ALL,
            newsletter=AllYNEnum.ALL,
            hasOrders=AllYNEnum.NO,
            useRebateCode=AllYNEnum.YES
        )
        assert dto.clientType == ClientTypeEnum.ALL
        assert dto.newsletter == AllYNEnum.ALL

class TestSourceFilterModel:
    def test_valid(self):
        dto = SourceFilterModel(
            active=BooleanStrShortEnum.YES,
            id=1
        )
        assert dto.active == BooleanStrShortEnum.YES
        assert dto.id == 1

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            SourceFilterModel(
                active=BooleanStrShortEnum.YES,
                id=0
            )

    def test_invalid_id_negative(self):
        with pytest.raises(ValidationError):
            SourceFilterModel(
                active=BooleanStrShortEnum.YES,
                id=-1
            )

class TestSourceModel:
    def test_valid(self):
        dto = SourceModel(
            direct=SourceFilterModel(active=BooleanStrShortEnum.YES, id=1),
            search=SourceFilterModel(active=BooleanStrShortEnum.NO, id=2),
            advert=SourceFilterModel(active=BooleanStrShortEnum.YES, id=3),
            priceComparers=SourceFilterModel(active=BooleanStrShortEnum.NO, id=4),
            affiliate=SourceFilterModel(active=BooleanStrShortEnum.YES, id=5),
            cpa=SourceFilterModel(active=BooleanStrShortEnum.NO, id=6),
            newsletter=SourceFilterModel(active=BooleanStrShortEnum.YES, id=7),
            social=SourceFilterModel(active=BooleanStrShortEnum.NO, id=8),
            page=SourceFilterModel(active=BooleanStrShortEnum.YES, id=9)
        )
        assert dto.direct.id == 1
        assert dto.social.active == BooleanStrShortEnum.NO
