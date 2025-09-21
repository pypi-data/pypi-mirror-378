"""
Access Control (robot-first wrapper)

Simple wrapper over RobotAccess that feels like robotics domain.
"""

from typing import Optional, Dict, Any
from substrateinterface.keypair import Keypair

from ..wallet import RobotWallet
from ..access import RobotAccess


class AccessControl:
    """Robot-first access control on top of RobotAccess."""
    def __init__(self, wallet: RobotWallet, keypair: Keypair):
        self._access = RobotAccess(wallet, keypair)

    def create_role(self, role_name: str, description: str = "") -> str:
        return self._access.create_role(role_name, description)

    def read_role(self, role_name: str) -> Optional[Dict[str, Any]]:
        return self._access.read_role(role_name)









