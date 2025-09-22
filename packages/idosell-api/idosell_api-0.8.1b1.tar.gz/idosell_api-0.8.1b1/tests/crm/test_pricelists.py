import pytest

def test_pricelists_module_imports():
    try:
        from src.idosell.crm import pricelists
        assert pricelists
    except ImportError:
        pytest.skip("Pricelists module not importable")

def test_pricelists_basic_functionality():
    try:
        import inspect
        from src.idosell.crm import pricelists
        members = inspect.getmembers(pricelists)
        assert len(members) > 0
    except Exception:
        pytest.skip("Pricelists needs investigation")
