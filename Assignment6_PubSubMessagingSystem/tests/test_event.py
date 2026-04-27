from src.event import Event


def test_event_create_sets_required_fields():
    event = Event.create("math.addition", "AdditionRequested", {"a": 1, "b": 2})

    assert event.topic == "math.addition"
    assert event.event_type == "AdditionRequested"
    assert event.payload == {"a": 1, "b": 2}
    assert event.event_id is not None
    assert event.timestamp is not None
