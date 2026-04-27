def handle_addition(event):
    a = event.payload["a"]
    b = event.payload["b"]
    return {
        "operation": "addition",
        "result": a + b,
        "event_id": event.event_id
    }


def handle_multiplication(event):
    a = event.payload["a"]
    b = event.payload["b"]
    return {
        "operation": "multiplication",
        "result": a * b,
        "event_id": event.event_id
    }


def handle_division(event):
    a = event.payload["a"]
    b = event.payload["b"]

    if b == 0:
        return {
            "operation": "division",
            "error": "division by zero",
            "event_id": event.event_id
        }

    return {
        "operation": "division",
        "result": a / b,
        "event_id": event.event_id
    }
