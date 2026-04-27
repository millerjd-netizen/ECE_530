from src.broker import Broker
from src.event import Event
from src.math_handlers import (
    handle_addition,
    handle_division,
    handle_multiplication,
)


def run_demo():
    broker = Broker()

    broker.subscribe("math.addition", handle_addition)
    broker.subscribe("math.multiplication", handle_multiplication)
    broker.subscribe("math.division", handle_division)

    events = [
        Event.create("math.addition", "AdditionRequested", {"a": 5, "b": 17}),
        Event.create("math.multiplication", "MultiplicationRequested", {"a": 9, "b": 5}),
        Event.create("math.division", "DivisionRequested", {"a": 7, "b": 9}),
        Event.create("math.division", "DivisionRequested", {"a": 10, "b": 0}),
    ]

    for event in events:
        results = broker.publish(event)
        print(f"Published {event.event_type} to {event.topic}")
        print(results)


if __name__ == "__main__":
    run_demo()
