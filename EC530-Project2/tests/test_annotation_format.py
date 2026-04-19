def test_annotation_format():
    event = {
        "event_id": "evt_1",
        "image_id": "img_1",
        "path": "images/test.jpg",
        "label": "example_object",
        "confidence": 0.98,
        "status": "inference_completed"
    }

    annotation = {
        "event_id": event["event_id"],
        "image_id": event["image_id"],
        "path": event["path"],
        "annotation": f"{event['label']} ({event['confidence']:.2f})",
        "status": "annotation_completed"
    }

    assert annotation["annotation"] == "example_object (0.98)"
    assert annotation["status"] == "annotation_completed"
