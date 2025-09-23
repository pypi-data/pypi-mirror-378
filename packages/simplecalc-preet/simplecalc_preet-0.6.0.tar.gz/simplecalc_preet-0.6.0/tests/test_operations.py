import pytest

from mycalculator import add, subtract, multiply, divide

def test_operations():
    assert add(2, 3) == 5
    assert subtract(5, 3) == 2
    assert multiply(4, 5) == 20
    assert divide(10, 2) == 5

test_operations()
print("All tests passed!")