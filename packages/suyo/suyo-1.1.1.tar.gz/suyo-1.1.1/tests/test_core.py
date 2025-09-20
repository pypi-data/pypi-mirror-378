import pytest
from suyo.core import greet


def test_greet_basic():
    assert greet("Alice") == "Hello, Alice!"


def test_greet_empty():
    with pytest.raises(ValueError):
        greet("")
