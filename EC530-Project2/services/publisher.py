import json
from shared.redis_client import get_redis_client

r = get_redis_client()

event = {
    "event_id": "evt_1",
    "image_id": "img_1",
    "path": "images/test.jpg"
}

r.publish("image.submitted", json.dumps(event))

print("Published event:", event)