"""
Validation helpers (no side effects, internal use)
"""

def ensure_max_length(value: str, max_len: int, label: str) -> None:
	if len(value) > max_len:
		raise ValueError(f"{label} '{value}' exceeds {max_len} character limit")

def not_empty(value: str, label: str) -> None:
	if not value:
		raise ValueError(f"{label} must not be empty")


