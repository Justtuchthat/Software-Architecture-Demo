from typing import Callable, Dict, List

class MessageBroker:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[str, str], None]]] = {}

    def subscribe(self, topic: str, callback: Callable[[str, str], None]):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
    
    def publish(self, topic: str, message: str):
        if topic not in self.subscribers:
            return
        for callback in self.subscribers[topic]:
            callback(topic, message)
    
    def reset(self):
        self.subscribers = {}