import importlib


def test_import_resolves_to_src_package():
    module = importlib.import_module("IServAPI")
    assert module.__file__.endswith("src/IServAPI/__init__.py")
