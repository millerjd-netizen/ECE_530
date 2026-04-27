from src.broker import Broker
from src.event import Event


def sample_handler(event):
    return {"received": event.event_type}


def test_broker_subscribe_adds_handler_to_topic():
    broker = Broker()
    broker.subscribe("math.addition", sample_handler)

    assert "math.addition" in broker.list_topics()
    assert sample_handler in broker.list_subscribers("math.addition")


def test_broker_publish_calls_subscriber():
    broker = Broker()
    broker.subscribe("math.addition", sample_handler)

    event = Event.create("math.addition", "AdditionRequested", {"a": 1, "b": 2})
    results = broker.publish(event)

    assert results == [{"received": "AdditionRequested"}]


def test_broker_publish_with_no_subscribers_returns_empty_list():
    broker = Broker()
    event = Event.create("math.unknown", "UnknownRequested", {})

    results = broker.publish(event)

    assert results == []
