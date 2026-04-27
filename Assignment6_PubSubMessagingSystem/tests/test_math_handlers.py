from src.event import Event
from src.math_handlers import (
    handle_addition,
    handle_division,
    handle_multiplication,
)


def test_addition_handler_returns_sum():
    event = Event.create("math.addition", "AdditionRequested", {"a": 5, "b": 17})

    result = handle_addition(event)

    assert result["operation"] == "addition"
    assert result["result"] == 22


def test_multiplication_handler_returns_product():
    event = Event.create("math.multiplication", "MultiplicationRequested", {"a": 9, "b": 5})

    result = handle_multiplication(event)

    assert result["operation"] == "multiplication"
    assert result["result"] == 45


def test_division_handler_returns_quotient():
    event = Event.create("math.division", "DivisionRequested", {"a": 7, "b": 2})

    result = handle_division(event)

    assert result["operation"] == "division"
    assert result["result"] == 3.5


def test_division_handler_handles_zero_division():
    event = Event.create("math.division", "DivisionRequested", {"a": 7, "b": 0})

    result = handle_division(event)

    assert result["operation"] == "division"
    assert result["error"] == "division by zero"
