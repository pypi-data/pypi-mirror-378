from pydantic import Field, PrivateAttr

from src.idosell._common import Gateway


# --- ENDPOINTS
class Get(Gateway):
    """
    The method allows to retrieve the list of administrative regions available in the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/clientsprovincelistget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/clients/provinceList')

    country_code: str | None = Field(None, min_length=2, max_length=2, pattern=r'^[A-Za-z]{2}$', description="Country code in ISO-3166-1 alpha-2 standard (2 letters)") # type: ignore
