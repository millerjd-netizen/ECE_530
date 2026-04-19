from shared.events import parse_message

def test_parse_message_returns_none_for_non_message():
    msg = {"type": "subscribe", "data": 1}
    assert parse_message(msg) is None

def test_parse_message_parses_json_message():
    msg = {"type": "message", "data": '{"x": 1, "y": "ok"}'}
    result = parse_message(msg)
    assert result["x"] == 1
    assert result["y"] == "ok"