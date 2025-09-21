"""
Data Vault (robot-first wrapper, WIP)

High-level storage wrapper over RobotStorage. Keeps existing logic intact.
"""

from typing import Dict, Any, Optional, Union
from substrateinterface.keypair import Keypair

from ..wallet import RobotWallet
from ..storage import RobotStorage


class DataVault:
    """Robot-first data vault API built on RobotStorage (WIP)."""
    def __init__(self, wallet: RobotWallet, keypair: Keypair):
        self._storage = RobotStorage(wallet, keypair)

    def put(self, item_type: str, data: Union[Dict[str, Any], str]) -> str:
        """Store item using core storage add_data."""
        return self._storage.add_data(item_type, data)

    def get(self, item_type: str, account: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch item using core storage read_data."""
        return self._storage.read_data(item_type, account)


