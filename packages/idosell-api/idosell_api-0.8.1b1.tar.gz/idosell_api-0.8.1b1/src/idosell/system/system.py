from typing import List
from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import AppendableGateway, Gateway
from src.idosell.system._common import CurrenciesModel, OrdersModel, PanelSettingsModel, UnitsModel, UserTypeEnum


# --- DTOs
class PutUnitsSystemSystemParamsModel(BaseModel):
    units: List[UnitsModel] = Field(..., description="List of system units")

class PutProcessesAutomationSystemSystemParamsModel(BaseModel):
    shopId: StrictInt = Field(..., ge=1, description="Shop Id")
    orders: OrdersModel = Field(..., description="Orders")

class PutConfigSystemSystemParamsModel(BaseModel):
    panelSettings: PanelSettingsModel = Field(..., description="Panel settings")


# --- ENDPOINTS
class GetConfig(Gateway):
    """
    Method is used for extracting information about a shop and its most important configuration settings
    DOCS_URL: https://idosell.readme.io/reference/systemconfigget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/config')

class PutConfig(Gateway):
    """
    The method is used to manage the most important settings in the store and in the panel. It enables, among others, configuration of tax and billing settings and configuration of warehouse management
    DOCS_URL: https://idosell.readme.io/reference/systemconfigput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/config')

    params: PutConfigSystemSystemParamsModel = Field(..., description="Parameters transmitted to method")

class GetCurrencies(Gateway):
    """
    This method returns the current exchange rate in relation to the currency set in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/systemcurrenciesget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/currencies')

    symbol: str = Field(..., description="Currency symbol in ISO-4217 (3 letters)")
    date: str = Field(..., description="Date in format YYYY-MM-DD-HH MM:SS")

class PutCurrencies(AppendableGateway):
    """
    Method that allows for setting currency exchange rates in relation to the currency set in the administration panel
    DOCS_URL: https://idosell.readme.io/reference/systemcurrenciesput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/currencies')

    currencies: List[CurrenciesModel] = Field(..., description="List of currencies")

class GetProcessesAutomation(Gateway):
    """
    It allows you to download the current automation processes configuration
    DOCS_URL: https://idosell.readme.io/reference/systemprocessesautomationget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/processesAutomation')

    shopId: StrictInt | None = Field(None, ge=1, description="Shop Id")

class PutProcessesAutomation(Gateway):
    """
    The method is used for edit of processes automation settings
    DOCS_URL: https://idosell.readme.io/reference/systemprocessesautomationput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/processesAutomation')

    params: PutProcessesAutomationSystemSystemParamsModel = Field(..., description="Parameters transmitted to method")

class GetServerLoad(Gateway):
    """
    This method returns server status information which is useful in determining whether the server is currently overloaded
    DOCS_URL: https://idosell.readme.io/reference/systemserverloadget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/serverLoad')

class GetServerTime(Gateway):
    """
    Method that returns the current server time, which is essential for authentication
    DOCS_URL: https://idosell.readme.io/reference/systemservertimeget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/serverTime')

class GetShopsData(Gateway):
    """
    Method is used for extracting information about a shop and its most important configuration settings
    DOCS_URL: https://idosell.readme.io/reference/systemshopsdataget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/shopsData')

class GetUnits(Gateway):
    """
    The method allows units of measurement to be downloaded from the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/systemunitsget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/units')

    languagesIds: List[str] | None = Field(None, description="List of languages")

class PutUnits(AppendableGateway):
    """
    The method allows existing units of measurement to be updated to the IdoSell administration panel
    DOCS_URL: https://idosell.readme.io/reference/systemunitsput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/units')

    params: PutUnitsSystemSystemParamsModel = Field(..., description="Parameters transmitted to method")

class GetUsers(Gateway):
    """
    Method that returns information about IdoSell Shop administration panel users
    DOCS_URL: https://idosell.readme.io/reference/systemusersget
    """

    _method: str = PrivateAttr(default='GET')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/system/users')

    userType: UserTypeEnum = Field(UserTypeEnum.ALL, description="User type. List of options 'all' - All users, 'active' - Only active users")
