from shared.mongo_service import save_annotation
from shared.embedding_service import compute_embedding
from shared.faiss_index import FaissIndex
from shared.simulator import generate_random_image
from shared.events import subscribe_to, parse_message
from shared.logger import get_logger

# Logger for debugging and tracing service behavior
logger = get_logger(__name__)

# Initialize FAISS index (vector DB)
IMAGE_DIM = 64 * 64 * 3
index = FaissIndex(dim=IMAGE_DIM)


def main():
    """
    Annotation Service:
    - Listens for completed inference events
    - Generates annotations
    - Computes embeddings
    - Stores embeddings in FAISS for similarity search
    - Saves annotations to MongoDB
    """

    # Subscribe to Redis pub/sub channel
    pubsub = subscribe_to("inference.completed")

    logger.info("Annotation Service listening on inference.completed...")

    for message in pubsub.listen():
        try:
            event = parse_message(message)

            # Skip invalid / empty messages
            if event is None:
                continue

            logger.info("Received event: %s", event)

            # --- STEP 1: Generate or load image ---
            image = generate_random_image()

            # --- STEP 2: Compute embedding ---
            embedding = compute_embedding(image)

            # --- STEP 3: Store in FAISS ---
            index.add(embedding)
            logger.info("Stored embedding in FAISS index")

            # --- STEP 4: Create annotation ---
            annotation = {
                "event_id": event["event_id"],
                "image_id": event["image_id"],
                "path": event["path"],
                "annotation": f"{event['label']} ({event['confidence']:.2f})",
                "status": "annotation_completed"
            }

            logger.info("Final annotation: %s", annotation)

            # --- STEP 5: Save to MongoDB (SAFE) ---
            try:
                save_annotation(annotation)
                logger.info("Saved annotation to MongoDB")
            except Exception as db_error:
                logger.warning("MongoDB not available: %s", db_error)

            # --- OPTIONAL: similarity search demo ---
            distances, indices = index.search(embedding, k=3)
            logger.info("Nearest neighbors (FAISS): %s", indices.tolist())

        except Exception as e:
            logger.exception("Annotation Service failed: %s", e)


if __name__ == "__main__":
    main()