import json
from shared.redis_client import get_redis_client


def publish_event(channel: str, payload: dict) -> None:
    r = get_redis_client()
    r.publish(channel, json.dumps(payload))


def subscribe_to(channel: str):
    r = get_redis_client()
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub


def parse_message(message):
    if message["type"] != "message":
        return None
    return json.loads(message["data"])