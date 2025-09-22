
from src.idosell.system.shops import GetCurrencies, GetLanguages


# --- Tests for Endpoints
class TestGetCurrencies:
    def test_instantiate(self):
        dto = GetCurrencies()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')

class TestGetLanguages:
    def test_instantiate(self):
        dto = GetLanguages()
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
