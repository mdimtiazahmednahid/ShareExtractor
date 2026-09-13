from dataclasses import dataclass, field
import datetime
import uuid
from typing import Optional

@dataclass
class ShareProfile:
    name: str
    source: str
    confidence: float
    session_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    profile_url: Optional[str] = None
    share_url: Optional[str] = None
    first_seen_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    last_seen_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "profile_url": self.profile_url,
            "share_url": self.share_url,
            "source": self.source,
            "confidence": self.confidence,
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "session_id": self.session_id,
        }
