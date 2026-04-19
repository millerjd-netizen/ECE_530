from shared.events import subscribe_to, parse_message


def main():
    pubsub = subscribe_to("inference.completed")
    print("Annotation Service listening on inference.completed...")

    for message in pubsub.listen():
        event = parse_message(message)
        if event is None:
            continue

        print("Annotation Service received:", event)

        annotation = {
            "image_id": event["image_id"],
            "path": event["path"],
            "annotation": f"{event['label']} ({event['confidence']:.2f})",
            "status": "annotation_completed"
        }

        print("Final annotation:", annotation)


if __name__ == "__main__":
    main()