import importlib
from pathlib import Path


def test_import_resolves_to_src_package():
    module = importlib.import_module("IServAPI")
    assert Path(module.__file__).as_posix().endswith("src/IServAPI/__init__.py")
