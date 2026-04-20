from shared.events import subscribe_to, parse_message, publish_event
from shared.logger import get_logger

logger = get_logger(__name__)


def main():
    pubsub = subscribe_to("image.submitted")
    logger.info("Inference Service listening on image.submitted...")

    for message in pubsub.listen():
        try:
            event = parse_message(message)
            if event is None:
                continue

            logger.info("Inference Service received: %s", event)

            result = {
                "event_id": event["event_id"],
                "image_id": event["image_id"],
                "path": event["path"],
                "label": "example_object",
                "confidence": 0.98,
                "status": "inference_completed"
            }

            publish_event("inference.completed", result)
            logger.info("Inference Service published: %s", result)

        except Exception as e:
            logger.exception("Inference Service failed: %s", e)


if __name__ == "__main__":
    main()