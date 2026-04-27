from collections import defaultdict


class Broker:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, topic, handler):
        self.subscribers[topic].append(handler)

    def publish(self, event):
        if event.topic not in self.subscribers:
            return []

        results = []
        for handler in self.subscribers[event.topic]:
            result = handler(event)
            results.append(result)

        return results

    def list_topics(self):
        return list(self.subscribers.keys())

    def list_subscribers(self, topic):
        return self.subscribers.get(topic, [])
