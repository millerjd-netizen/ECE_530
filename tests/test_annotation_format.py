def test_annotation_format():
    event = {
        "event_id": "evt_1",
        "image_id": "img_1",
        "path": "images/test.jpg",
        "label": "cat",
        "confidence": 0.95
    }

    annotation = {
        "event_id": event["event_id"],
        "image_id": event["image_id"],
        "path": event["path"],
        "annotation": f"{event['label']} ({event['confidence']:.2f})",
        "status": "annotation_completed"
    }

    assert annotation["annotation"] == "cat (0.95)"