from math_tools import add, subtract, multiply, divide, average
import pytest

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(4, 5) == 20

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_zero():
    with pytest.raises(ValueError):
        divide(5, 0)

def test_average():
    assert average([1, 2, 3]) == 2
