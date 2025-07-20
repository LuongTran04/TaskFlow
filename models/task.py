from dataclasses import dataclass
from datetime import time

@dataclass
class Task:
    title: str
    start_time: time
    end_time: time
    description: str = ""
    completed: bool = False
    id: int = None 