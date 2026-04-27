from collections import defaultdict


class Broker:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def list_topics(self):
        return list(self.subscribers.keys())

    def list_subscribers(self, topic):
        return self.subscribers.get(topic, [])
