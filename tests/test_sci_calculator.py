import math

import pytest

from SciCalculator import format_number, safe_calculate


def test_safe_calculate_basic_arithmetic():
    assert safe_calculate("2 + 3 * 4") == 14
    assert safe_calculate("10 / 2") == 5
    assert safe_calculate("2^8") == 256


def test_safe_calculate_scientific_functions():
    assert safe_calculate("sqrt(144)") == 12
    assert safe_calculate("factorial(5)") == 120
    assert safe_calculate("sin(30)") == pytest.approx(0.5)
    assert safe_calculate("log(100)") == pytest.approx(2.0)


def test_safe_calculate_constants_and_unary_operations():
    assert safe_calculate("-5 + pi") == pytest.approx(math.pi - 5)
    assert safe_calculate("e^2") == pytest.approx(math.e**2)


def test_format_number_adds_thousands_separator():
    assert format_number(1234.5) == "1,234.5"
    assert format_number(1000000) == "1,000,000"
    assert format_number(0.000001) == "1e-06"
