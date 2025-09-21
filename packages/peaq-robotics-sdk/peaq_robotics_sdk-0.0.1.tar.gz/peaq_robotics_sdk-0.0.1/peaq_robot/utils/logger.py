"""
Simple structured logger (WIP)

Used by robotics modules for consistent logs without altering core logic.
"""

from typing import Any, Dict
import json


def log(level: str, message: str, **kwargs: Any) -> None:
	entry: Dict[str, Any] = {"level": level, "message": message}
	if kwargs:
		entry.update(kwargs)
	print(json.dumps(entry))
