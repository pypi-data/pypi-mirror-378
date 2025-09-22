"""
Configuration constants and helpers. Keeping defaults centralized.
"""

from typing import Optional
import os
from pathlib import Path

# Testnet (Agung) default - keep as primary default when no WSS provided
DEFAULT_TESTNET_WSS = "wss://peaq-agung.api.onfinality.io/ws"

# Mainnet (peaq) QuickNode endpoints - use any one (choose quicknode3 by default)
PEAQ_MAINNET_WSS = [
    "wss://quicknode3.peaq.xyz",
    "wss://quicknode1.peaq.xyz",
    "wss://quicknode2.peaq.xyz",
]


def resolve_network_url(network: Optional[str]) -> str:
    """Resolve a network identifier or URL to a valid WSS endpoint.

    Rules:
    - If no value provided or empty, return Agung testnet default.
    - If already a ws:// or wss:// URL, return as-is.
    - Common aliases map to:
      * "agung", "test", "testnet" -> Agung testnet
      * "peaq", "main", "mainnet" -> peaq mainnet (quicknode3)
    - If an https://quicknode*.peaq.xyz is provided, convert to wss://.
    - Otherwise return the raw value to allow custom endpoints.
    """
    if not network:
        return DEFAULT_TESTNET_WSS

    n = network.strip()
    lower = n.lower()

    # Return WSS/WS URLs as-is
    if lower.startswith("ws://") or lower.startswith("wss://"):
        return n

    # Convert QuickNode HTTPS to WSS if provided
    if lower.startswith("https://quicknode") and lower.endswith(".peaq.xyz"):
        return "wss://" + n.split("://", 1)[1]

    # Alias mapping
    if any(k in lower for k in ("agung", "testnet", "test")):
        return DEFAULT_TESTNET_WSS

    if any(k in lower for k in ("peaq", "mainnet", "main")):
        return PEAQ_MAINNET_WSS[0]

    # Fallback: pass-through
    return n

# Backward compatible name (used elsewhere previously)
DEFAULT_NETWORK = DEFAULT_TESTNET_WSS

# Keystore defaults (overridable via env var PEAQ_ROBOT_KEYSTORE)
DEFAULT_KEYSTORE_DIR = os.path.join(Path.home(), ".peaq_robot")
DEFAULT_KEYSTORE_FILE = "wallet.json"

def get_default_keystore_path() -> str:
    env_path = os.environ.get("PEAQ_ROBOT_KEYSTORE")
    if env_path:
        return env_path
    return os.path.join(DEFAULT_KEYSTORE_DIR, DEFAULT_KEYSTORE_FILE)


