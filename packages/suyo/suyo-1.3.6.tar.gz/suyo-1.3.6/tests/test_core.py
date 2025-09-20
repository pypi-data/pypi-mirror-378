import importlib


def test_package_exports_init_and_debug():
    # import the package and confirm new API surface
    suyo = importlib.import_module("suyo")
    assert hasattr(suyo, "init")
    assert hasattr(suyo, "debug")
    # default debug flag should be falsy
    assert not bool(suyo.debug)
