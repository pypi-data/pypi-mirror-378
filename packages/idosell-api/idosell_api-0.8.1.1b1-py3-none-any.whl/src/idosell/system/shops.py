from pydantic import PrivateAttr

from src.idosell._common import Gateway


# --- ENDPOINTS
class GetCurrencies(Gateway):
    """
    Method is used for extracting information about a shop language templates
    DOCS_URL: https://idosell.readme.io/reference/shopscurrenciesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/shops/currencies')

class GetLanguages(Gateway):
    """
    Method is used for extracting information about a shop language templates
    DOCS_URL: https://idosell.readme.io/reference/shopslanguagesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/shops/languages')
