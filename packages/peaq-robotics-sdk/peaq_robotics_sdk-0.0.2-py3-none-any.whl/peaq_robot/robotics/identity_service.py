"""
Identity service (robot-first wrapper, WIP)

Provides a robotics-oriented facade over the core RobotIdentity.
Uses peaq_robot.identity internally without altering its logic.
"""

from typing import Optional, Dict, Any
from substrateinterface.keypair import Keypair

from ..wallet import RobotWallet
from ..identity import RobotIdentity


class IdentityService:
    """Robot-first DID wrapper over RobotIdentity (WIP)."""
    def __init__(self, wallet: RobotWallet, keypair: Keypair):
        self._identity = RobotIdentity(wallet, keypair)

    @property
    def address(self) -> str:
        return self._identity.address

    def create(self, name: Optional[str] = None, did_document: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """Create a DID via core identity. Mirrors create_identity signature."""
        return self._identity.create_identity(name=name, did_document=did_document, **kwargs)

    def resolve(self, did_account: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Resolve DID using chainstate via core identity read."""
        return self._identity.read_identity(did_account)


