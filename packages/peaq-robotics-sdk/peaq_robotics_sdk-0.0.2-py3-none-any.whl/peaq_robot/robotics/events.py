"""
Events (WIP)

Placeholders for chain event subscriptions and state queries to fit robotics UX.
"""

from typing import Callable, Dict


def on_event(event_type: str, callback: Callable[[Dict], None]) -> None:
    """Subscribe to chain events (WIP placeholder)."""
    # In future: wire WebSocket subscriptions and filter
    _ = (event_type, callback)


def query_state(query: str) -> Dict:
    """Query chain state (WIP placeholder)."""
    _ = query
    return {}


