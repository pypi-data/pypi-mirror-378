from __future__ import annotations
from typing import List

from pydantic import Field, PrivateAttr, StrictInt, StrictStr

from src.idosell._common import PageableCamelGateway
from src.idosell.wms._common import ReturnElementsEnum


# --- Locations DTOs ---
class GetLocations(PageableCamelGateway):
    """
    The method allows to download information about a selected location or all locations in a given warehouse together with a list of product IDs located in these locations.
    DOCS_URL: https://idosell.readme.io/reference/wmslocationsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/wms/locations')

    locationId: StrictInt | None = Field(None, ge=1, description="Warehouse location ID")
    locationCode: StrictStr | None = Field(None, min_length=1, description="Storage location code")
    stockId: StrictInt | None = Field(None, ge=1, description="Stock ID")
    returnElements: List[ReturnElementsEnum] | None = Field(None, description="Elements to be returned by the endpoint. By default all elements are returned. Available values: locationName, locationPath, locationCode, stockId, products")
