from shared.events import publish_event


def main():
    event = {
        "event_id": "evt_1001",
        "image_id": "img_1001",
        "path": "images/sample.jpg",
        "status": "submitted"
    }

    publish_event("image.submitted", event)
    print("Upload Service published:", event)


if __name__ == "__main__":
    main()