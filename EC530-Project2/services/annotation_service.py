from shared.events import subscribe_to, parse_message
from shared.logger import get_logger

logger = get_logger(__name__)


def main():
    pubsub = subscribe_to("inference.completed")
    logger.info("Annotation Service listening on inference.completed...")

    for message in pubsub.listen():
        try:
            event = parse_message(message)
            if event is None:
                continue

            logger.info("Annotation Service received: %s", event)

            annotation = {
                "event_id": event["event_id"],
                "image_id": event["image_id"],
                "path": event["path"],
                "annotation": f"{event['label']} ({event['confidence']:.2f})",
                "status": "annotation_completed"
            }

            logger.info("Final annotation: %s", annotation)

        except Exception as e:
            logger.exception("Annotation Service failed: %s", e)


if __name__ == "__main__":
    main()