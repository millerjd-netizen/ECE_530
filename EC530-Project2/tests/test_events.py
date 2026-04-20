from shared.events import parse_message


def test_parse_message_valid():
    message = {
        "type": "message",
        "data": '{"key": "value"}'
    }

    result = parse_message(message)
    assert result == {"key": "value"}


def test_parse_message_ignore_non_message():
    message = {
        "type": "subscribe",
        "data": ""
    }

    result = parse_message(message)
    assert result is None