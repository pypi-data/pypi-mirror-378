"""
Base robot controller interfaces (WIP)

Defines abstract interfaces for robot control. These do not change any
blockchain logic; they provide a robotics-first structure.
"""

from typing import Any


class BaseRobotController:
    """Abstract interface for robot controllers (placeholder)."""
    def execute(self, action: str, **kwargs: Any) -> bool:
        """Execute a named action on the robot. WIP: returns True as placeholder."""
        return True


