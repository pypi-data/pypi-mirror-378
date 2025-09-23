from dataclasses import dataclass
from enum import Enum, IntEnum, unique
from typing import Optional

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_LANDED_STATE_IN_AIR,
    MAV_LANDED_STATE_LANDING,
    MAV_LANDED_STATE_ON_GROUND,
    MAV_LANDED_STATE_TAKEOFF,
    MAV_LANDED_STATE_UNDEFINED,
    MAV_RESULT_ACCEPTED,
    MAV_RESULT_COMMAND_INT_ONLY,
    MAV_RESULT_COMMAND_LONG_ONLY,
    MAV_RESULT_DENIED,
    MAV_RESULT_FAILED,
    MAV_RESULT_IN_PROGRESS,
    MAV_RESULT_TEMPORARILY_REJECTED,
    MAV_RESULT_UNSUPPORTED,
)

# Domain message classes with protobuf conversions


@dataclass
class Position:
    x: float
    y: float
    z: float

    @classmethod
    def from_proto(cls, proto_position) -> "Position":
        # Lazy import to avoid import cycles at module load
        return cls(x=proto_position.x, y=proto_position.y, z=proto_position.z)

    def to_proto(self):
        # Lazy import to avoid import cycles at module load
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.Position()
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        return msg


@dataclass
class Velocity:
    v_x: float
    v_y: float
    v_z: float

    @classmethod
    def from_proto(cls, proto_velocity) -> "Velocity":
        return cls(v_x=proto_velocity.v_x, v_y=proto_velocity.v_y, v_z=proto_velocity.v_z)

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.Velocity()
        msg.v_x = self.v_x
        msg.v_y = self.v_y
        msg.v_z = self.v_z
        return msg


@dataclass
class Attitude:
    roll_rad: float
    pitch_rad: float
    yaw_rad: float

    @classmethod
    def from_proto(cls, proto_attitude) -> "Attitude":
        return cls(roll_rad=proto_attitude.roll_rad, pitch_rad=proto_attitude.pitch_rad, yaw_rad=proto_attitude.yaw_rad)

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.Attitude()
        msg.roll_rad = self.roll_rad
        msg.pitch_rad = self.pitch_rad
        msg.yaw_rad = self.yaw_rad
        return msg


class Frame(Enum):
    LOCAL = 1
    BODY = 2
    GLOBAL = 3
    GENERIC = 4
    UNKNOWN = 0


class StatusText:
    def __init__(self, severity, msg):
        self.severity = severity
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.severity}: {self.msg}"


@unique
class PminiState(Enum):
    UNDEFINED = MAV_LANDED_STATE_UNDEFINED  # pmini landed state is unknown
    ON_GROUND = MAV_LANDED_STATE_ON_GROUND  # pmini is landed (on ground)
    IN_AIR = MAV_LANDED_STATE_IN_AIR  # pmini is in air
    TAKEOFF = MAV_LANDED_STATE_TAKEOFF  # pmini currently taking off
    LANDING = MAV_LANDED_STATE_LANDING  # pmini currently landing

    def is_flight(self) -> bool:
        return self == PminiState.IN_AIR or self == PminiState.TAKEOFF or self == PminiState.LANDING

    def is_on_ground(self) -> bool:
        return self == PminiState.ON_GROUND

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_msg(msg) -> "PminiState":
        if msg.get_type() != "EXTENDED_SYS_STATE":
            raise ValueError(f"Cannot convert {msg.get_type()} to PminiState")
        try:
            return PminiState(msg.landed_state)
        except ValueError:
            return PminiState.UNDEFINED


class Yaw:
    class Frame(Enum):
        ANGLE = 1
        ANG_VEL = 2

    def __init__(self, value: float = 0.0, frame: Frame = Frame.ANGLE):
        self.value = value
        self.frame = frame

    def __add__(self, other):
        if not isinstance(other, Yaw):
            return NotImplemented

        if self.frame != other.frame:
            raise ValueError("Cannot add Yaw instances with different frames")

        return Yaw(self.value + other.value, self.frame)


class Quaternion:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @classmethod
    def from_proto(cls, proto_quaternion) -> "Quaternion":
        return cls(x=proto_quaternion.x, y=proto_quaternion.y, z=proto_quaternion.z, w=proto_quaternion.w)

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.Quaternion()
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        msg.w = self.w
        return msg


@dataclass
class AngularVelocity:
    roll_rate_rad_s: float
    pitch_rate_rad_s: float
    yaw_rate_rad_s: float

    @classmethod
    def from_proto(cls, proto_angular_velocity) -> "AngularVelocity":
        return cls(
            roll_rate_rad_s=proto_angular_velocity.roll_rate_rad_s,
            pitch_rate_rad_s=proto_angular_velocity.pitch_rate_rad_s,
            yaw_rate_rad_s=proto_angular_velocity.yaw_rate_rad_s,
        )

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.AngularVelocity()
        msg.roll_rate_rad_s = self.roll_rate_rad_s
        msg.pitch_rate_rad_s = self.pitch_rate_rad_s
        msg.yaw_rate_rad_s = self.yaw_rate_rad_s
        return msg


@dataclass
class Acceleration:
    ax: float  # X acceleration in m/s²
    ay: float  # Y acceleration in m/s²
    az: float  # Z acceleration in m/s²

    @classmethod
    def from_proto(cls, proto_acceleration) -> "Acceleration":
        return cls(ax=proto_acceleration.ax, ay=proto_acceleration.ay, az=proto_acceleration.az)

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.Acceleration()
        msg.ax = self.ax
        msg.ay = self.ay
        msg.az = self.az
        return msg


@dataclass
class LidarRange:
    distance_m: float  # Distance in meters
    quality: int  # Quality/signal strength (0-100)
    sensor_id: int  # Sensor ID

    @classmethod
    def from_proto(cls, proto_lidar_range) -> "LidarRange":
        return cls(
            distance_m=proto_lidar_range.distance_m, quality=proto_lidar_range.quality, sensor_id=proto_lidar_range.sensor_id
        )

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.LidarRange()
        msg.distance_m = self.distance_m
        msg.quality = self.quality
        msg.sensor_id = self.sensor_id
        return msg


class BatteryStatus:
    """Battery status information from MAVLink BATTERY_STATUS message."""

    def __init__(
        self,
        voltage_battery: float = 0.0,
        current_battery: float = 0.0,
        battery_remaining: int = -1,
        voltage_cell_1: float = 0.0,
        voltage_cell_2: float = 0.0,
        voltage_cell_3: float = 0.0,
        voltage_cell_4: float = 0.0,
        voltage_cell_5: float = 0.0,
        voltage_cell_6: float = 0.0,
        battery_id: int = 0,
        current_consumed: int = -1,
        energy_consumed: int = -1,
        temperature: int = -1,
    ):
        self.voltage_battery = voltage_battery  # Battery voltage in V
        self.current_battery = current_battery  # Battery current in A (negative for discharging)
        self.battery_remaining = battery_remaining  # Battery remaining percentage (-1 if unknown)
        self.voltage_cell_1 = voltage_cell_1  # Cell 1 voltage in V
        self.voltage_cell_2 = voltage_cell_2  # Cell 2 voltage in V
        self.voltage_cell_3 = voltage_cell_3  # Cell 3 voltage in V
        self.voltage_cell_4 = voltage_cell_4  # Cell 4 voltage in V
        self.voltage_cell_5 = voltage_cell_5  # Cell 5 voltage in V
        self.voltage_cell_6 = voltage_cell_6  # Cell 6 voltage in V
        self.battery_id = battery_id  # Battery ID (for multiple batteries)
        self.current_consumed = current_consumed  # Consumed charge in mAh (-1 if unknown)
        self.energy_consumed = energy_consumed  # Consumed energy in hJ (-1 if unknown)
        self.temperature = temperature  # Battery temperature in centidegrees Celsius (-1 if unknown)

    def get_cell_voltages(self) -> list[float]:
        """Get list of cell voltages, excluding zero values."""
        cells = [
            self.voltage_cell_1,
            self.voltage_cell_2,
            self.voltage_cell_3,
            self.voltage_cell_4,
            self.voltage_cell_5,
            self.voltage_cell_6,
        ]
        return [v for v in cells if v > 0.0]

    def get_voltage_percentage(self) -> float:
        """Get battery voltage as percentage (assuming 3.7V per cell as 100%).

        This is a fallback method for multi-cell batteries.
        For single-cell drones, use calculate_single_cell_percentage() instead.
        """
        cell_voltages = self.get_cell_voltages()
        if not cell_voltages:
            return 0.0
        avg_cell_voltage = sum(cell_voltages) / len(cell_voltages)
        # Assume 3.7V per cell is 100%, 3.0V per cell is 0%
        percentage = max(0.0, min(100.0, (avg_cell_voltage - 3.0) / (3.7 - 3.0) * 100.0))
        return percentage

    def calculate_single_cell_percentage(self, voltage: float, max_voltage: float = 8.4, min_voltage: float = 6.4) -> int:
        """Calculate battery percentage based on voltage for single-cell drones.

        Args:
            voltage: Current battery voltage in volts
            max_voltage: Maximum voltage for 100% charge (default: 8.4V)
            min_voltage: Minimum voltage for 0% charge (default: 6.4V)

        Returns:
            Battery percentage (0-100)
        """
        if voltage <= 0.0:
            return 0

        # Calculate percentage based on voltage range
        # Linear interpolation between min and max voltages
        voltage_range = max_voltage - min_voltage
        voltage_above_min = voltage - min_voltage

        # Calculate percentage (0-100)
        percentage = max(0.0, min(100.0, (voltage_above_min / voltage_range) * 100.0))

        return int(percentage)

    def is_low_battery(self, threshold: float = 20.0) -> bool:
        """Check if battery is low based on remaining percentage."""
        if self.battery_remaining == -1:
            # Fall back to voltage-based estimation
            return self.get_voltage_percentage() < threshold
        return self.battery_remaining < threshold

    def get_temperature_celsius(self) -> float:
        """Get battery temperature in Celsius."""
        return self.temperature / 100.0 if self.temperature != -1 else 0.0

    def get_current_consumed_ah(self) -> float:
        """Get consumed current in Ah."""
        return self.current_consumed / 1000.0 if self.current_consumed != -1 else 0.0

    def get_energy_consumed_wh(self) -> float:
        """Get consumed energy in Wh."""
        return self.energy_consumed / 100.0 if self.energy_consumed != -1 else 0.0

    def __str__(self) -> str:
        return f"Battery: {self.voltage_battery:.2f}V, " f"{self.battery_remaining}%, " f"{self.current_battery:.2f}A"

    @classmethod
    def from_proto(cls, proto_battery_status) -> "BatteryStatus":
        # Map simple proto fields into richer internal representation
        return cls(
            voltage_battery=getattr(proto_battery_status, "voltage", 0.0),
            current_battery=getattr(proto_battery_status, "current", 0.0),
            battery_remaining=getattr(proto_battery_status, "percentage", -1),
        )

    def to_proto(self):
        from .generated import drone_pb2  # type: ignore

        msg = drone_pb2.BatteryStatus()
        msg.voltage = float(self.voltage_battery)
        msg.current = float(self.current_battery)
        # Clamp to int range expected by proto (0-100 or -1)
        percent = int(self.battery_remaining if self.battery_remaining >= 0 else 0)
        msg.percentage = percent
        return msg


@unique
class FlightMode(Enum):
    STABILIZE = 0
    ACRO = 1
    ALT_HOLD = 2
    AUTO = 3
    GUIDED = 4
    LOITER = 5
    RTL = 6
    CIRCLE = 7
    LAND = 9
    DRIFT = 11
    SPORT = 13
    FLIP = 14
    AUTO_TUNE = 15
    POS_HOLD = 16
    BREAK = 17
    THROW = 18
    AVOID_ADBS = 19
    GUIDED_NO_GPS = 20
    SMART_RTL = 21
    FLOW_HOLD = 22
    FOLLOW = 23
    ZIGZAG = 24
    SYSTEM_ID = 25
    AUTO_ROTATE = 26
    AUTO_RTL = 27
    TURTLE = 28
    UNKNOWN = 100

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_msg(msg) -> "FlightMode":
        if msg.get_type() != "HEARTBEAT":
            raise ValueError(f"Cannot convert {msg.get_type()} to FlightMode")
        return FlightMode(msg.custom_mode)

    @staticmethod
    def from_proto(proto_msg) -> "FlightMode":
        # Map proto FlightMode enum values to SDK FlightMode enum values
        proto_to_sdk = {
            0: FlightMode.STABILIZE,
            1: FlightMode.ACRO,
            2: FlightMode.ALT_HOLD,
            3: FlightMode.AUTO,
            4: FlightMode.GUIDED,
            5: FlightMode.LOITER,
            6: FlightMode.RTL,
            7: FlightMode.CIRCLE,
            8: FlightMode.LAND,
            9: FlightMode.DRIFT,
            10: FlightMode.SPORT,
            11: FlightMode.FLIP,
            12: FlightMode.AUTO_TUNE,
            13: FlightMode.POS_HOLD,
            14: FlightMode.BREAK,
            15: FlightMode.THROW,
            16: FlightMode.AVOID_ADBS,
            17: FlightMode.GUIDED_NO_GPS,
            18: FlightMode.SMART_RTL,
            19: FlightMode.FLOW_HOLD,
            20: FlightMode.FOLLOW,
            21: FlightMode.ZIGZAG,
            22: FlightMode.SYSTEM_ID,
            23: FlightMode.AUTO_ROTATE,
            24: FlightMode.AUTO_RTL,
            25: FlightMode.TURTLE,
            26: FlightMode.UNKNOWN,
        }
        # Handle proto enum value type (can be ProtoFlightMode object or ValueType)
        if hasattr(proto_msg, "value"):
            value = proto_msg.value
        else:
            # ValueType is a NewType based on int, so we can use it directly as an int
            value = proto_msg
        return proto_to_sdk.get(value, FlightMode.UNKNOWN)

    def to_proto_value(self) -> int:
        """Convert SDK FlightMode to proto FlightMode numeric value.

        This uses the inverse mapping of from_proto to ensure correct IDs.
        """
        sdk_to_proto = {
            FlightMode.STABILIZE: 0,
            FlightMode.ACRO: 1,
            FlightMode.ALT_HOLD: 2,
            FlightMode.AUTO: 3,
            FlightMode.GUIDED: 4,
            FlightMode.LOITER: 5,
            FlightMode.RTL: 6,
            FlightMode.CIRCLE: 7,
            FlightMode.LAND: 8,
            FlightMode.DRIFT: 9,
            FlightMode.SPORT: 10,
            FlightMode.FLIP: 11,
            FlightMode.AUTO_TUNE: 12,
            FlightMode.POS_HOLD: 13,
            FlightMode.BREAK: 14,
            FlightMode.THROW: 15,
            FlightMode.AVOID_ADBS: 16,
            FlightMode.GUIDED_NO_GPS: 17,
            FlightMode.SMART_RTL: 18,
            FlightMode.FLOW_HOLD: 19,
            FlightMode.FOLLOW: 20,
            FlightMode.ZIGZAG: 21,
            FlightMode.SYSTEM_ID: 22,
            FlightMode.AUTO_ROTATE: 23,
            FlightMode.AUTO_RTL: 24,
            FlightMode.TURTLE: 25,
            FlightMode.UNKNOWN: 26,
        }
        return sdk_to_proto.get(self, 26)

    @staticmethod
    def from_id(id: int) -> "FlightMode":
        for mode in FlightMode:
            if mode.value == id:
                return mode
        return FlightMode.UNKNOWN

    def to_id(self) -> int:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FlightMode):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, FlightMode):
            return NotImplemented
        return self.value != other.value

    def is_armable(self) -> bool:
        return self not in {FlightMode.LAND, FlightMode.RTL, FlightMode.AUTO_RTL, FlightMode.AUTO, FlightMode.UNKNOWN}


@unique
class MAVResult(Enum):
    ACCEPTED = MAV_RESULT_ACCEPTED  # Valid, supported, executed
    TEMPORARILY_REJECTED = MAV_RESULT_TEMPORARILY_REJECTED  # Valid, but not now
    DENIED = MAV_RESULT_DENIED  # Invalid params
    UNSUPPORTED = MAV_RESULT_UNSUPPORTED  # Unknown command
    FAILED = MAV_RESULT_FAILED  # Executed, but failed
    IN_PROGRESS = MAV_RESULT_IN_PROGRESS  # Still running
    COMMAND_LONG_ONLY = MAV_RESULT_COMMAND_LONG_ONLY  # Command is only accepted when sent as a COMMAND_LONG
    COMMAND_INT_ONLY = MAV_RESULT_COMMAND_INT_ONLY  # Command is only accepted when sent as a COMMAND_INT

    def __str__(self) -> str:
        return self.name

    def is_success(self) -> bool:
        return self == MAVResult.ACCEPTED

    def is_temporary(self) -> bool:
        return self == MAVResult.TEMPORARILY_REJECTED or self == MAVResult.IN_PROGRESS

    def is_failed(self) -> bool:
        return self in {
            MAVResult.DENIED,
            MAVResult.UNSUPPORTED,
            MAVResult.FAILED,
            MAVResult.COMMAND_LONG_ONLY,
            MAVResult.COMMAND_INT_ONLY,
        }


def parse_mav_result(code: int) -> Optional[MAVResult]:
    """Maps raw int to MAVResult enum, or None if unknown."""
    try:
        return MAVResult(code)
    except ValueError:
        return None


@unique
class DroneErrorCode(IntEnum):
    """Enhanced error codes for drone operations with MAVLink integration."""

    SUCCESS = 0
    FAILED = 1
    TIMEOUT = 2
    INVALID_PARAMETER = 3
    NOT_CONNECTED = 4
    NOT_ARMED = 5
    ALREADY_ARMED = 6
    INVALID_MODE = 7
    MODE_CHANGE_FAILED = 8
    ALTITUDE_TOO_HIGH = 9
    ALTITUDE_TOO_LOW = 10
    BATTERY_LOW = 11
    GPS_NOT_READY = 12
    SENSORS_NOT_READY = 13
    TAKEOFF_FAILED = 14
    LANDING_FAILED = 15
    COMMAND_DENIED = 16
    TEMPORARILY_REJECTED = 17
    UNSUPPORTED = 18
    IN_PROGRESS = 19
    COMMUNICATION_ERROR = 20
    INTERNAL_ERROR = 21

    def __str__(self) -> str:
        return self.name

    def is_success(self) -> bool:
        return self == DroneErrorCode.SUCCESS

    def is_temporary(self) -> bool:
        return self in {DroneErrorCode.TEMPORARILY_REJECTED, DroneErrorCode.IN_PROGRESS, DroneErrorCode.TIMEOUT}

    def is_failed(self) -> bool:
        return not self.is_success() and not self.is_temporary()

    @staticmethod
    def from_mav_result(mav_result: MAVResult) -> "DroneErrorCode":
        """Convert MAVResult to DroneErrorCode."""
        mapping = {
            MAVResult.ACCEPTED: DroneErrorCode.SUCCESS,
            MAVResult.TEMPORARILY_REJECTED: DroneErrorCode.TEMPORARILY_REJECTED,
            MAVResult.DENIED: DroneErrorCode.COMMAND_DENIED,
            MAVResult.UNSUPPORTED: DroneErrorCode.UNSUPPORTED,
            MAVResult.FAILED: DroneErrorCode.FAILED,
            MAVResult.IN_PROGRESS: DroneErrorCode.IN_PROGRESS,
            MAVResult.COMMAND_LONG_ONLY: DroneErrorCode.UNSUPPORTED,
            MAVResult.COMMAND_INT_ONLY: DroneErrorCode.UNSUPPORTED,
        }
        return mapping.get(mav_result, DroneErrorCode.FAILED)

    def to_mav_result(self) -> MAVResult:
        """Convert DroneErrorCode to MAVResult (best effort)."""
        mapping = {
            DroneErrorCode.SUCCESS: MAVResult.ACCEPTED,
            DroneErrorCode.TEMPORARILY_REJECTED: MAVResult.TEMPORARILY_REJECTED,
            DroneErrorCode.COMMAND_DENIED: MAVResult.DENIED,
            DroneErrorCode.UNSUPPORTED: MAVResult.UNSUPPORTED,
            DroneErrorCode.IN_PROGRESS: MAVResult.IN_PROGRESS,
            DroneErrorCode.TIMEOUT: MAVResult.TEMPORARILY_REJECTED,
        }
        return mapping.get(self, MAVResult.FAILED)
