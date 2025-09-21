"""
Robotics-oriented wrappers

High-level, robot-first APIs that internally use peaq_robot core modules.
These modules do not change underlying logic; they organize functionality
to feel more like a robotics SDK.
"""

from .base_robot import BaseRobotController
from .identity_service import IdentityService
from .data_vault import DataVault
from .events import on_event, query_state
from .unitree_g1 import UnitreeG1Robot
from .triggers import wire_default_triggers
from .access_control import AccessControl

__all__ = [
    "BaseRobotController",
    "IdentityService",
    "DataVault",
    "on_event",
    "query_state",
    "UnitreeG1Robot",
    "wire_default_triggers",
    "AccessControl",
]


