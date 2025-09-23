"""
Pmini SDK Python - Python SDK for Pmini quadcopter.

This package provides both MAVLink and gRPC interfaces for controlling
Pmini quadcopters with full type safety and comprehensive documentation.
"""

from .common import (
    Attitude,
    BatteryStatus,
    DroneErrorCode,
    FlightMode,
    Frame,
    MAVResult,
    PminiState,
    Position,
    StatusText,
    Velocity,
    Yaw,
)
from .drone_client import CommandError, ConnectionError, DroneClient, DroneError

# Expose raw protobuf API modules for convenience
from .generated import drone_pb2, drone_pb2_grpc  # noqa: F401
from .high_level_commander import HighLevelCommander
from .low_level_commander import LowLevelCommander
from .mavlink_client import Config, MavlinkClient
from .pmini import Pmini
from .sync_drone_client import SyncDroneClient

__version__ = "0.0.0"

__all__ = [
    # Main classes
    "Pmini",
    "Config",
    "MavlinkClient",
    # Commanders
    "HighLevelCommander",
    "LowLevelCommander",
    # Client classes
    "DroneClient",
    "SyncDroneClient",
    "DroneError",
    "ConnectionError",
    "CommandError",
    # Common types
    "FlightMode",
    "Frame",
    "MAVResult",
    "PminiState",
    "Yaw",
    "DroneErrorCode",
    "StatusText",
    # Domain classes
    "Attitude",
    "Position",
    "Velocity",
    "BatteryStatus",
    # Protobuf modules
    "drone_pb2",
    "drone_pb2_grpc",
]
