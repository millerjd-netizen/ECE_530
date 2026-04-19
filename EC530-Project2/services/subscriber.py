import json
from shared.redis_client import get_redis_client

r = get_redis_client()

pubsub = r.pubsub()
pubsub.subscribe("image.submitted")

print("Listening for events...")

for message in pubsub.listen():
    if message["type"] == "message":
        event = json.loads(message["data"])
        print("Received event:", event)