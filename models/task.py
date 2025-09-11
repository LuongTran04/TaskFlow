from dataclasses import dataclass, field
from datetime import time
from typing import List

@dataclass
class Task:
    title: str
    start_time: time
    end_time: time
    description: str = ""
    completed: bool = False
    id: int = None
    notification_time: int = 30
    attachments: List[str] = field(default_factory=list)