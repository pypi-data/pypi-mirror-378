"""
Encoding helpers (hex, utf-8) centralized for clarity.
"""

from typing import Optional


def to_hex_utf8(s: str) -> str:
	return "0x" + s.encode("utf-8").hex()


def from_prefixed_hex_utf8(h: str) -> Optional[str]:
	try:
		if h and h.startswith("0x"):
			return bytes.fromhex(h[2:]).decode("utf-8")
		return None
	except Exception:
		return None


