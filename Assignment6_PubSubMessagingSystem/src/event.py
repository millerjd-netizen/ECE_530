from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
import uuid


@dataclass
class Event:
    topic: str
    event_type: str
    payload: Dict[str, Any]
    event_id: str
    timestamp: str

    @classmethod
    def create(cls, topic: str, event_type: str, payload: Dict[str, Any]):
        return cls(
            topic=topic,
            event_type=event_type,
            payload=payload,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat()
        )
