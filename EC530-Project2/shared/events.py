import json
from shared.redis_client import get_redis_client


def publish_event(channel, data):
    client = get_redis_client()
    client.publish(channel, json.dumps(data))


def subscribe_to(channel):
    client = get_redis_client()
    pubsub = client.pubsub()
    pubsub.subscribe(channel)
    return pubsub


def parse_message(message):
    if message["type"] != "message":
        return None
    return json.loads(message["data"])