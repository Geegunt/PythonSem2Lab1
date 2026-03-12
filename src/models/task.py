from typing import Any
from dataclasses import dataclass


@dataclass
class Task:
    id: int
    payload: Any
