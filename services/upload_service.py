from shared.events import publish_event
from shared.logger import get_logger

logger = get_logger(__name__)


def main():
    event = {
        "event_id": "evt_1001",
        "image_id": "img_1001",
        "path": "images/sample.jpg",
        "status": "submitted"
    }

    publish_event("image.submitted", event)
    logger.info("Upload Service published: %s", event)


if __name__ == "__main__":
    main()