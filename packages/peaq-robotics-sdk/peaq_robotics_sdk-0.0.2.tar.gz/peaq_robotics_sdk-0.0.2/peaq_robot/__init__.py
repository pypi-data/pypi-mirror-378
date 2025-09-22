"""
Peaq Robot SDK - Main Package

Provides standardized access to peaq blockchain functions for robotics applications.

Usage:
    from peaq_robot import PeaqRobot
    
    robot_sdk = PeaqRobot(mnemonic="your mnemonic here")
    
    # Create robot identity
    tx_hash = robot_sdk.id.create_identity("ROBOT_001", robot_config)
    
    # Store robot data  
    tx_hash = robot_sdk.store.add_data("TELEMETRY_001", telemetry_data)
"""

from .core import PeaqRobot
from .robotics import (
    BaseRobotController,
    IdentityService,
    DataVault,
    on_event,
    query_state,
    UnitreeG1Robot,
    wire_default_triggers,
    AccessControl,
)

__version__ = "0.0.0"
__all__ = [
    "PeaqRobot",
    "BaseRobotController",
    "IdentityService",
    "DataVault",
    "on_event",
    "query_state",
    "UnitreeG1Robot",
    "wire_default_triggers",
    "AccessControl",
]