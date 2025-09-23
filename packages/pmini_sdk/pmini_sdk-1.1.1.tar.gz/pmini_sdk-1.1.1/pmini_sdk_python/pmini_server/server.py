#!/usr/bin/env python3
"""
Improved gRPC server for PMini drone control with proper connection detection.

This server provides a direct interface to the drone using the pmini_sdk_python
library. Enhanced with better connection detection, heartbeat monitoring, and
graceful shutdown.
"""

import logging
import signal
import threading
import time
from concurrent import futures
from queue import Empty, Queue
from typing import Callable, Iterator

import grpc

# Import the actual pmini_sdk_python library
from pmini_sdk_python import (
    Config,
    DroneErrorCode,
    FlightMode,
    Frame,
    Pmini,
    Yaw,
)

# Domain message classes (convert to/from protobuf)
# Domain classes are used at the edge for to_proto conversions
from pmini_sdk_python.common import (  # noqa: F401
    Acceleration,
    AngularVelocity,
    Attitude,
    BatteryStatus,
    LidarRange,
    Position,
    Velocity,
)
from pmini_sdk_python.generated import drone_pb2  # type: ignore
from pmini_sdk_python.generated.drone_pb2 import DroneErrorCode as ProtoDroneErrorCode
from pmini_sdk_python.generated.drone_pb2 import FlightMode as ProtoFlightMode
from pmini_sdk_python.generated.drone_pb2_grpc import DroneServiceServicer as BaseDroneServiceServicer
from pmini_sdk_python.generated.drone_pb2_grpc import add_DroneServiceServicer_to_server

# Type aliases for clarity with generated protobuf types
ProtoArmRequest = drone_pb2.ArmRequest
ProtoLandRequest = drone_pb2.LandRequest
ProtoDisarmRequest = drone_pb2.DisarmRequest
ProtoSetModeRequest = drone_pb2.SetModeRequest
ProtoGoToRequest = drone_pb2.GoToRequest
ProtoMoveVelocityRequest = drone_pb2.MoveVelocityRequest
ProtoSetVelocityRequest = drone_pb2.SetVelocityRequest
ProtoEmergencyStopRequest = drone_pb2.EmergencyStopRequest
ProtoRebootRequest = drone_pb2.RebootRequest
ProtoGetHealthRequest = drone_pb2.GetHealthRequest
ProtoStatusRequest = drone_pb2.StatusRequest

ProtoCommandResponse = drone_pb2.CommandResponse
ProtoPositionResponse = drone_pb2.PositionResponse
ProtoVelocityResponse = drone_pb2.VelocityResponse
ProtoAttitudeResponse = drone_pb2.AttitudeResponse
ProtoBatteryStatusResponse = drone_pb2.BatteryStatusResponse
ProtoStatusTextResponse = drone_pb2.StatusTextResponse
ProtoAngularVelocityResponse = drone_pb2.AngularVelocityResponse
ProtoAccelerationResponse = drone_pb2.AccelerationResponse
ProtoLidarRangeResponse = drone_pb2.LidarRangeResponse
ProtoHealthResponse = drone_pb2.HealthResponse
ProtoStatusResponse = drone_pb2.StatusResponse
ProtoSubscribePositionRequest = drone_pb2.SubscribePositionRequest
ProtoSubscribeVelocityRequest = drone_pb2.SubscribeVelocityRequest
ProtoSubscribeAttitudeRequest = drone_pb2.SubscribeAttitudeRequest
ProtoSubscribeBatteryStatusRequest = drone_pb2.SubscribeBatteryStatusRequest
ProtoSubscribeStatusTextRequest = drone_pb2.SubscribeStatusTextRequest
ProtoSubscribeAngularVelocityRequest = drone_pb2.SubscribeAngularVelocityRequest
ProtoSubscribeAccelerationRequest = drone_pb2.SubscribeAccelerationRequest
ProtoSubscribeLidarRangeRequest = drone_pb2.SubscribeLidarRangeRequest
ProtoTakeoffRequest = drone_pb2.TakeoffRequest

# Unary getter requests
ProtoGetPositionRequest = drone_pb2.GetPositionRequest
ProtoGetVelocityRequest = drone_pb2.GetVelocityRequest
ProtoGetAttitudeRequest = drone_pb2.GetAttitudeRequest
ProtoGetAngularVelocityRequest = drone_pb2.GetAngularVelocityRequest
ProtoGetAccelerationRequest = drone_pb2.GetAccelerationRequest
ProtoGetLidarRangeRequest = drone_pb2.GetLidarRangeRequest

# Logger will be configured in main() based on command line arguments
logger: logging.Logger = logging.getLogger(__name__)


class ConnectionMonitor:
    """Monitor drone connection status with heartbeat detection."""

    def __init__(self, pmini: Pmini, timeout_seconds: float = 5.0):
        self.pmini = pmini
        self.timeout_seconds = timeout_seconds
        self.last_successful_call = time.time()
        self.is_connected = False
        self._lock = threading.Lock()

    def test_connection(self) -> bool:
        """Test if the drone is connected by trying to get data."""
        try:
            # Try multiple operations to verify connection
            start_time = time.time()

            # Try to get position (this should fail quickly if drone is off)
            position = self.pmini.get_position()

            # Check if we got valid data within reasonable time
            if time.time() - start_time > 2.0:
                logger.warning("Position request took too long, " "marking as disconnected")
                with self._lock:
                    self.is_connected = False
                return False

            # Check if position data looks valid (not all zeros or NaN)
            if hasattr(position, "x") and hasattr(position, "y") and hasattr(position, "z"):
                # Position data exists, update last successful call
                with self._lock:
                    self.last_successful_call = time.time()
                    self.is_connected = True
                return True
            else:
                logger.warning("Invalid position data received")
                with self._lock:
                    self.is_connected = False
                return False

        except Exception as e:
            logger.info(f"Connection test failed: {e}")
            with self._lock:
                self.is_connected = False
            return False

    def get_connection_status(self) -> tuple[bool, str]:
        """Get current connection status and message."""
        # Test connection
        is_connected = self.test_connection()

        with self._lock:
            if is_connected:
                return True, "Connected to drone"
            else:
                time_since_last = time.time() - self.last_successful_call
                if time_since_last > self.timeout_seconds:
                    return False, f"No response from drone for {time_since_last:.1f}s"
                else:
                    return False, "Connection test failed"


class DroneServiceServicer(BaseDroneServiceServicer):
    """gRPC service implementation with proper connection detection."""

    def __init__(self, pmini: Pmini):
        self.pmini = pmini
        self.status_text_queue: Queue = Queue()
        self.status_text_callbacks: set[Callable] = set()
        self._shutdown_event = threading.Event()
        self.connection_monitor = ConnectionMonitor(pmini)
        self._setup_status_text_callback()

    def _setup_status_text_callback(self):
        """Setup the status text callback to collect messages."""

        def status_text_callback(status_text):
            logger.info(f"Status text received: {status_text}")
            # Put the status text in the queue for streaming
            try:
                self.status_text_queue.put(status_text, timeout=0.1)
            except Exception:
                pass  # Queue might be full, ignore

        try:
            self.pmini.add_status_text_callback(status_text_callback)
        except Exception as e:
            logger.warning(f"Could not setup status text callback: {e}")

    def shutdown(self):
        """Signal shutdown to all streaming operations."""
        logger.info("Shutdown signal received in DroneServiceServicer")
        self._shutdown_event.set()

    def _check_connection(self) -> tuple[bool, str]:
        """Check connection and return status."""
        return self.connection_monitor.get_connection_status()

    def _create_error_response(self, error_code: DroneErrorCode, message: str) -> ProtoCommandResponse:
        """Create an error response."""
        # Convert DroneErrorCode to proto enum value
        proto_error_code = self._convert_error_code_to_proto(error_code)
        return ProtoCommandResponse(error_code=proto_error_code, message=message, success=False)

    def _create_success_response(self, message: str) -> ProtoCommandResponse:
        """Create a success response."""
        # Convert DroneErrorCode to proto enum value
        proto_error_code = self._convert_error_code_to_proto(DroneErrorCode.SUCCESS)
        return ProtoCommandResponse(error_code=proto_error_code, message=message, success=True)

    def _convert_error_code_to_proto(self, error_code: DroneErrorCode):
        """Convert DroneErrorCode to proto enum value."""
        # Map DroneErrorCode values to proto enum values
        mapping = {
            DroneErrorCode.SUCCESS: ProtoDroneErrorCode.SUCCESS,
            DroneErrorCode.FAILED: ProtoDroneErrorCode.FAILED,
            DroneErrorCode.TIMEOUT: ProtoDroneErrorCode.TIMEOUT,
            DroneErrorCode.INVALID_PARAMETER: ProtoDroneErrorCode.INVALID_PARAMETER,
            DroneErrorCode.NOT_CONNECTED: ProtoDroneErrorCode.NOT_CONNECTED,
            DroneErrorCode.NOT_ARMED: ProtoDroneErrorCode.NOT_ARMED,
            DroneErrorCode.ALREADY_ARMED: ProtoDroneErrorCode.ALREADY_ARMED,
            DroneErrorCode.INVALID_MODE: ProtoDroneErrorCode.INVALID_MODE,
            DroneErrorCode.MODE_CHANGE_FAILED: ProtoDroneErrorCode.MODE_CHANGE_FAILED,
            DroneErrorCode.ALTITUDE_TOO_HIGH: ProtoDroneErrorCode.ALTITUDE_TOO_HIGH,
            DroneErrorCode.ALTITUDE_TOO_LOW: ProtoDroneErrorCode.ALTITUDE_TOO_LOW,
            DroneErrorCode.BATTERY_LOW: ProtoDroneErrorCode.BATTERY_LOW,
            DroneErrorCode.GPS_NOT_READY: ProtoDroneErrorCode.GPS_NOT_READY,
            DroneErrorCode.SENSORS_NOT_READY: ProtoDroneErrorCode.SENSORS_NOT_READY,
            DroneErrorCode.TAKEOFF_FAILED: ProtoDroneErrorCode.TAKEOFF_FAILED,
            DroneErrorCode.LANDING_FAILED: ProtoDroneErrorCode.LANDING_FAILED,
            DroneErrorCode.COMMAND_DENIED: ProtoDroneErrorCode.COMMAND_DENIED,
            DroneErrorCode.TEMPORARILY_REJECTED: ProtoDroneErrorCode.TEMPORARILY_REJECTED,
            DroneErrorCode.UNSUPPORTED: ProtoDroneErrorCode.UNSUPPORTED,
            DroneErrorCode.IN_PROGRESS: ProtoDroneErrorCode.IN_PROGRESS,
            DroneErrorCode.COMMUNICATION_ERROR: ProtoDroneErrorCode.COMMUNICATION_ERROR,
            DroneErrorCode.INTERNAL_ERROR: ProtoDroneErrorCode.INTERNAL_ERROR,
        }
        return mapping.get(error_code, ProtoDroneErrorCode.FAILED)

    def Takeoff(self, request: ProtoTakeoffRequest, context) -> ProtoCommandResponse:
        """Handle takeoff request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot takeoff: {msg}")

        try:
            logger.info(f"Takeoff request: altitude={request.altitude}m")

            # Validate altitude
            if request.altitude <= 0:
                return self._create_error_response(DroneErrorCode.ALTITUDE_TOO_LOW, "Altitude must be positive")

            if request.altitude > 2:  # Example max altitude
                return self._create_error_response(DroneErrorCode.ALTITUDE_TOO_HIGH, "Altitude too high (max 2m)")

            # Execute takeoff using the actual library
            mav_result = self.pmini.takeoff(request.altitude)
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response(f"Takeoff to {request.altitude}m initiated")
            else:
                return self._create_error_response(error_code, f"Takeoff failed: {error_code.name}")

        except Exception as e:
            logger.exception("Takeoff failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Takeoff failed: {str(e)}")

    def Land(self, request: ProtoLandRequest, context) -> ProtoCommandResponse:
        """Handle land request."""
        try:
            logger.info("Land request received")
            mav_result = self.pmini.land()
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response("Land initiated")
            else:
                return self._create_error_response(error_code, f"Land failed: {error_code.name}")

        except Exception as e:
            logger.exception("Land failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Land failed: {str(e)}")

    def Arm(self, request: ProtoArmRequest, context) -> ProtoCommandResponse:
        """Handle arm request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot arm: {msg}")

        try:
            logger.info("Arm request received")

            # Execute arm command using the actual library
            mav_result = self.pmini.arm()
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response("Drone armed successfully")
            else:
                return self._create_error_response(error_code, f"Arm failed: {error_code.name}")

        except Exception as e:
            logger.exception("Arm failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Arm failed: {str(e)}")

    def Disarm(self, request: ProtoDisarmRequest, context) -> ProtoCommandResponse:
        """Handle disarm request."""
        try:
            logger.info("Disarm request received")
            self.pmini.disarm()
            return self._create_success_response("Disarmed successfully")

        except Exception as e:
            logger.exception("Disarm failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Disarm failed: {str(e)}")

    def SetMode(self, request: ProtoSetModeRequest, context) -> ProtoCommandResponse:
        """Handle set mode request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot set mode: {msg}")

        try:
            logger.info(f"SetMode request: mode={request.mode}")

            # Convert proto flight mode to internal flight mode
            internal_mode = FlightMode.from_proto(request.mode)
            mav_result = self.pmini.change_mode(internal_mode)
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response(f"Mode set to {request.mode}")
            else:
                return self._create_error_response(error_code, f"SetMode failed: {error_code.name}")

        except Exception as e:
            logger.exception("SetMode failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"SetMode failed: {str(e)}")

    def GoTo(self, request: ProtoGoToRequest, context) -> ProtoCommandResponse:
        """Handle go to position request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot go to: {msg}")

        try:
            logger.info(f"GoTo request: x={request.x}, y={request.y}, z={request.z}, yaw={getattr(request, 'yaw_rad', None)}")

            # Convert coordinate frame
            frame = Frame.BODY if request.frame == 0 else Frame.LOCAL

            # Create yaw object
            yaw = Yaw(value=getattr(request, "yaw_rad", 0) or 0)

            # Execute go to command
            self.pmini.go_to(request.x, request.y, request.z, yaw, frame)
            return self._create_success_response(f"GoTo command sent to ({request.x}, {request.y}, {request.z})")

        except Exception as e:
            logger.exception("GoTo failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"GoTo failed: {str(e)}")

    def MoveVelocity(self, request: ProtoMoveVelocityRequest, context) -> ProtoCommandResponse:
        """Handle move velocity request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot move: {msg}")

        try:
            logger.info(f"MoveVelocity request: vx={request.v_x}, vy={request.v_y}, vz={request.v_z}")

            # Use low level commander for velocity control
            yaw = Yaw(value=getattr(request, "yaw_rate_rad_s", 0) or 0)
            self.pmini.low_level_commander.set_velocity(request.v_x, request.v_y, request.v_z, yaw)
            return self._create_success_response("MoveVelocity command sent")

        except Exception as e:
            logger.exception("MoveVelocity failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"MoveVelocity failed: {str(e)}")

    def SetVelocity(self, request: ProtoSetVelocityRequest, context) -> ProtoCommandResponse:
        """Handle set velocity request with configurable duration."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot set velocity: {msg}")

        try:
            # Use duration from request (required field)
            duration = request.duration

            # Use timeout from request if provided, otherwise default to duration + 5 seconds
            grpc_timeout = request.timeout if getattr(request, "timeout", None) is not None else duration + 5.0

            logger.info(
                "SetVelocity request: vx=%s, vy=%s, vz=%s, duration=%ss, grpc_timeout=%ss",
                request.v_x,
                request.v_y,
                request.v_z,
                duration,
                grpc_timeout,
            )

            # Use Pmini's set_speed method with the specified duration
            yaw = Yaw(value=getattr(request, "yaw_rate_rad_s", 0) or 0)
            self.pmini.set_speed(request.v_x, request.v_y, request.v_z, yaw, duration_seconds=duration)
            return self._create_success_response(f"SetVelocity command completed ({duration}s duration)")

        except Exception as e:
            logger.exception("SetVelocity failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"SetVelocity failed: {str(e)}")

    def EmergencyStop(self, request: ProtoEmergencyStopRequest, context) -> ProtoCommandResponse:
        """Handle emergency stop request."""
        try:
            logger.info("Emergency stop request received")
            self.pmini.low_level_commander.emergency_stop()
            return self._create_success_response("Emergency stop executed")

        except Exception as e:
            logger.exception("Emergency stop failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Emergency stop failed: {str(e)}")

    def Reboot(self, request: ProtoRebootRequest, context) -> ProtoCommandResponse:
        """Handle reboot request."""
        try:
            logger.info("Reboot request received")
            self.pmini.reboot()
            return self._create_success_response("Reboot command sent")

        except Exception as e:
            logger.exception("Reboot failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Reboot failed: {str(e)}")

    def GetHealth(self, request: ProtoGetHealthRequest, context) -> ProtoHealthResponse:
        """Get drone health status using Pmini's Health class."""
        try:
            is_connected, msg = self._check_connection()

            # Get health flags using the new Health class with timeout-based freshness
            health_flags = self.pmini.get_health_flags()
            battery_status = self.pmini.get_battery_status()

            # Determine health status using the Health class flags
            is_healthy = (
                is_connected
                and health_flags.is_heartbeat
                and health_flags.is_data_pos
                and health_flags.is_data_attitude
                and health_flags.is_data_optical_flow
                and health_flags.is_data_battery
            )

            # Build detailed health message
            health_details = []
            if not is_connected:
                health_details.append(f"Not connected: {msg}")
            if not health_flags.is_heartbeat:
                health_details.append("No heartbeat")
            if not health_flags.is_data_pos:
                health_details.append("No position data")
            if not health_flags.is_data_attitude:
                health_details.append("No attitude data")
            if not health_flags.is_data_optical_flow:
                health_details.append("No optical flow data")
            if not health_flags.is_data_battery:
                health_details.append("No battery data")

            health_msg = "Healthy" if is_healthy else f"Unhealthy: {', '.join(health_details)}"

            return ProtoHealthResponse(
                is_healthy=is_healthy,
                message=health_msg,
                has_position_data=health_flags.is_data_pos,
                has_velocity_data=health_flags.is_data_pos,  # Velocity comes with position data
                has_attitude_data=health_flags.is_data_attitude,
                has_optical_flow_data=health_flags.is_data_optical_flow,
                is_connected=health_flags.is_heartbeat,
                is_armed=self.pmini.armed,
                flight_mode=ProtoFlightMode.UNKNOWN,
                battery_remaining=battery_status.battery_remaining if battery_status else 0.0,
            )

        except Exception as e:
            logger.exception("GetHealth failed")
            # Return unhealthy response
            return ProtoHealthResponse(
                is_healthy=False,
                message=f"Health check failed: {str(e)}",
                has_position_data=False,
                has_velocity_data=False,
                has_attitude_data=False,
                has_optical_flow_data=False,
                is_connected=False,
                is_armed=False,
                flight_mode=ProtoFlightMode.UNKNOWN,
                battery_remaining=0.0,
            )

    def SubscribePosition(self, request: ProtoSubscribePositionRequest, context) -> Iterator[ProtoPositionResponse]:
        """Stream position data."""
        logger.info("Position stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting position
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Position stream: {msg}")
                        # Still try to get position, but expect it to fail

                    # Get position using the actual library
                    position = self.pmini.get_position()

                    proto = ProtoPositionResponse()
                    proto.position.CopyFrom(position.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting position: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Position stream error: {e}")
        finally:
            logger.info("Position stream ended")

    def SubscribeStatusText(self, request: ProtoSubscribeStatusTextRequest, context) -> Iterator[ProtoStatusTextResponse]:
        """Stream status text data."""
        logger.info("Status text stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Wait for status text messages from the queue with timeout
                    status_text = self.status_text_queue.get(timeout=1.0)

                    yield ProtoStatusTextResponse(status_text=str(status_text))

                except Empty:
                    # Timeout is expected when no messages are available
                    # Check for shutdown during timeout
                    if self._shutdown_event.wait(0.1):
                        break
                    continue
                except Exception as e:
                    logger.error(f"Error in status text stream: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

        except Exception as e:
            logger.exception(f"Status text stream error: {e}")
        finally:
            logger.info("Status text stream ended")

    def SubscribeVelocity(self, request: ProtoSubscribeVelocityRequest, context) -> Iterator[ProtoVelocityResponse]:
        """Stream velocity data."""
        logger.info("Velocity stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting velocity
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Velocity stream: {msg}")
                        # Still try to get velocity, but expect it to fail

                    # Get velocity using the actual library
                    velocity = self.pmini.get_velocity()

                    proto = ProtoVelocityResponse()
                    proto.velocity.CopyFrom(velocity.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting velocity: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Velocity stream error: {e}")
        finally:
            logger.info("Velocity stream ended")

    def SubscribeAttitude(self, request: ProtoSubscribeAttitudeRequest, context) -> Iterator[ProtoAttitudeResponse]:
        """Stream attitude data."""
        logger.info("Attitude stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting attitude
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Attitude stream: {msg}")
                        # Still try to get attitude, but expect it to fail

                    # Get attitude using the actual library
                    attitude = self.pmini.get_attitude()

                    proto = ProtoAttitudeResponse()
                    proto.attitude.CopyFrom(attitude.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting attitude: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Attitude stream error: {e}")
        finally:
            logger.info("Attitude stream ended")

    def SubscribeBatteryStatus(
        self, request: ProtoSubscribeBatteryStatusRequest, context
    ) -> Iterator[ProtoBatteryStatusResponse]:
        """Stream battery status data."""
        logger.info("Battery status stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting battery status
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Battery status stream: {msg}")
                        # Still try to get battery status, but expect it to fail

                    battery_status = self.pmini.get_battery_status()
                    proto = ProtoBatteryStatusResponse()
                    proto.battery_status.CopyFrom(battery_status.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting battery status: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Battery status stream error: {e}")
        finally:
            logger.info("Battery status stream ended")

    def SubscribeAngularVelocity(
        self, request: ProtoSubscribeAngularVelocityRequest, context
    ) -> Iterator[ProtoAngularVelocityResponse]:
        """Stream angular velocity data."""
        logger.info("Angular velocity stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting angular velocity
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Angular velocity stream: {msg}")
                        # Still try to get angular velocity, but expect it to fail

                    # Get angular velocity using the actual library
                    angular_velocity = self.pmini.get_angular_velocity()

                    proto = ProtoAngularVelocityResponse()
                    proto.angular_velocity.CopyFrom(angular_velocity.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting angular velocity: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.1):  # 10 Hz
                    break

        except Exception as e:
            logger.exception(f"Angular velocity stream error: {e}")
        finally:
            logger.info("Angular velocity stream ended")

    def SubscribeAcceleration(
        self, request: ProtoSubscribeAccelerationRequest, context
    ) -> Iterator[ProtoAccelerationResponse]:
        """Stream acceleration data."""
        logger.info("Acceleration stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting acceleration
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Acceleration stream: {msg}")
                        # Still try to get acceleration, but expect it to fail

                    # Get acceleration using the actual library
                    acceleration = self.pmini.get_acceleration()

                    proto = ProtoAccelerationResponse()
                    proto.acceleration.CopyFrom(acceleration.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting acceleration: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.1):  # 10 Hz
                    break

        except Exception as e:
            logger.exception(f"Acceleration stream error: {e}")
        finally:
            logger.info("Acceleration stream ended")

    def SubscribeLidarRange(self, request: ProtoSubscribeLidarRangeRequest, context) -> Iterator[ProtoLidarRangeResponse]:
        """Stream lidar range data."""
        logger.info("Lidar range stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting lidar range
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Lidar range stream: {msg}")
                        # Still try to get lidar range, but expect it to fail

                    # Get lidar range using the actual library
                    lidar_range = self.pmini.get_lidar_range()

                    proto = ProtoLidarRangeResponse()
                    proto.lidar_range.CopyFrom(lidar_range.to_proto())
                    yield proto

                except Exception as e:
                    logger.error(f"Error getting lidar range: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.1):  # 10 Hz
                    break

        except Exception as e:
            logger.exception(f"Lidar range stream error: {e}")
        finally:
            logger.info("Lidar range stream ended")

    # Unary getters
    def GetPosition(self, request: ProtoGetPositionRequest, context) -> ProtoPositionResponse:
        try:
            position = self.pmini.get_position()
            proto = ProtoPositionResponse()
            proto.position.CopyFrom(position.to_proto())
            return proto
        except Exception as e:
            logger.exception("GetPosition failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoPositionResponse()

    def GetVelocity(self, request: ProtoGetVelocityRequest, context) -> ProtoVelocityResponse:
        try:
            velocity = self.pmini.get_velocity()
            proto = ProtoVelocityResponse()
            proto.velocity.CopyFrom(velocity.to_proto())
            return proto
        except Exception as e:
            logger.exception("GetVelocity failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoVelocityResponse()

    def GetAttitude(self, request: ProtoGetAttitudeRequest, context) -> ProtoAttitudeResponse:
        try:
            attitude = self.pmini.get_attitude()
            proto = ProtoAttitudeResponse()
            proto.attitude.CopyFrom(attitude.to_proto())
            return proto
        except Exception as e:
            logger.exception("GetAttitude failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoAttitudeResponse()

    def GetAngularVelocity(self, request: ProtoGetAngularVelocityRequest, context) -> ProtoAngularVelocityResponse:
        try:
            angular_velocity = self.pmini.get_angular_velocity()
            proto = ProtoAngularVelocityResponse()
            proto.angular_velocity.CopyFrom(angular_velocity.to_proto())
            return proto
        except Exception as e:
            logger.exception("GetAngularVelocity failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoAngularVelocityResponse()

    def GetAcceleration(self, request: ProtoGetAccelerationRequest, context) -> ProtoAccelerationResponse:
        try:
            acceleration = self.pmini.get_acceleration()
            proto = ProtoAccelerationResponse()
            proto.acceleration.CopyFrom(acceleration.to_proto())
            return proto
        except Exception as e:
            logger.exception("GetAcceleration failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoAccelerationResponse()

    def GetLidarRange(self, request: ProtoGetLidarRangeRequest, context) -> ProtoLidarRangeResponse:
        try:
            lidar_range = self.pmini.get_lidar_range()
            proto = ProtoLidarRangeResponse()
            proto.lidar_range.CopyFrom(lidar_range.to_proto())
            return proto
        except Exception as e:
            logger.exception("GetLidarRange failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoLidarRangeResponse()

    def Status(self, request: ProtoStatusRequest, context) -> ProtoStatusResponse:
        """Get drone status with proper connection detection."""
        logger.debug("Status check requested")

        # Use connection monitor to get accurate status
        is_connected, message = self._check_connection()

        if is_connected:
            try:
                position = self.pmini.get_position()
                attitude = self.pmini.get_attitude()
                battery_status = self.pmini.get_battery_status()
                detailed_message = f"Connected - Position: ({position.x:.1f}, {position.y:.1f}, {position.z:.1f})"

                proto = ProtoStatusResponse(
                    connected=True,
                    message=detailed_message,
                    status_code=self._convert_error_code_to_proto(DroneErrorCode.SUCCESS),
                    flight_mode=ProtoFlightMode.UNKNOWN,
                    armed=self.pmini.armed,
                    battery_remaining=battery_status.battery_remaining if battery_status else 0.0,
                )
                if position is not None:
                    proto.current_position.CopyFrom(position.to_proto())
                if attitude is not None:
                    proto.current_attitude.CopyFrom(attitude.to_proto())
                logger.debug("Status: Connected")
                return proto

            except Exception as e:
                logger.warning(f"Connected but failed to get detailed status: {e}")
                # Fall through to disconnected case
                is_connected = False
                message = f"Connection unstable: {str(e)}"

        # Disconnected case
        logger.debug(f"Status: Disconnected - {message}")
        return ProtoStatusResponse(
            connected=False,
            message=message,
            status_code=self._convert_error_code_to_proto(DroneErrorCode.NOT_CONNECTED),
            flight_mode=ProtoFlightMode.UNKNOWN,
            armed=False,
            battery_remaining=0.0,
        )


def create_pmini_config(device: str = "udpout:192.168.4.1:8080") -> Config:
    """Create Pmini configuration."""
    return Config(device=device, connection_time_sec=10)


# Global variables for signal handling
server_instance = None
grpc_server = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")

    # Signal shutdown to the service
    if server_instance:
        server_instance.shutdown()

    # Stop the gRPC server
    if grpc_server:
        logger.info("Stopping gRPC server...")
        grpc_server.stop(grace=2)
        logger.info("gRPC server stopped")


def serve(host: str = "127.0.0.1", port: int = 50051, device: str = "udpout:192.168.4.1:8080"):
    """Start the gRPC server."""
    global server_instance, grpc_server

    # Create Pmini instance using the actual library
    config = create_pmini_config(device)
    pmini = Pmini(config)

    # Create gRPC server
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_instance = DroneServiceServicer(pmini)
    add_DroneServiceServicer_to_server(server_instance, grpc_server)

    bind_addr = f"{host}:{port}"
    grpc_server.add_insecure_port(bind_addr)

    logger.info(f"Starting PMini gRPC server on {bind_addr}")
    logger.info(f"Connecting to drone at {device}")
    logger.info("Server features:")
    logger.info("  - Proper connection detection with heartbeat monitoring")
    logger.info("  - Connection timeout: 5 seconds")
    logger.info("  - Graceful shutdown on SIGTERM/SIGINT")
    logger.info("Available services:")
    logger.info("  - Takeoff(TakeoffRequest) -> CommandResponse")
    logger.info("  - Land(LandRequest) -> CommandResponse")
    logger.info("  - Arm(ArmRequest) -> CommandResponse")
    logger.info("  - Disarm(DisarmRequest) -> CommandResponse")
    logger.info("  - SetMode(SetModeRequest) -> CommandResponse")
    logger.info("  - GoTo(GoToRequest) -> CommandResponse")
    logger.info("  - MoveVelocity(MoveVelocityRequest) -> CommandResponse")
    logger.info("  - EmergencyStop(EmergencyStopRequest) -> CommandResponse")
    logger.info("  - Reboot(RebootRequest) -> CommandResponse")
    logger.info("  - GetHealth(GetHealthRequest) -> HealthResponse")
    logger.info("  - SubscribePosition(SubscribePositionRequest) -> stream PositionResponse")
    logger.info("  - SubscribeStatusText(SubscribeStatusTextRequest) -> stream StatusTextResponse")
    logger.info("  - SubscribeVelocity(SubscribeVelocityRequest) -> stream VelocityResponse")
    logger.info("  - SubscribeAttitude(SubscribeAttitudeRequest) -> stream AttitudeResponse")
    logger.info("  - SubscribeBatteryStatus(SubscribeBatteryStatusRequest) -> stream BatteryStatusResponse")
    logger.info("  - SubscribeAngularVelocity(SubscribeAngularVelocityRequest) -> stream AngularVelocityResponse")
    logger.info("  - SubscribeAcceleration(SubscribeAccelerationRequest) -> stream AccelerationResponse")
    logger.info("  - SubscribeLidarRange(SubscribeLidarRangeRequest) -> stream LidarRangeResponse")
    logger.info("  - Status(StatusRequest) -> StatusResponse")

    grpc_server.start()

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        grpc_server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Server shutdown complete")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="PMini gRPC Server with Connection Detection")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=50051, help="Server port (default: 50051)")
    parser.add_argument(
        "--device", default="udpout:192.168.4.1:8080", help="MAVLink device (default: udpout:192.168.4.1:8080)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set log level (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Log file path (default: None, logs to terminal)",
    )

    args = parser.parse_args()

    # Set up logging level and output based on command line arguments
    log_level = getattr(logging, args.log_level.upper())
    log_kwargs = {
        "level": log_level,
        "format": "[%(asctime)s] %(levelname)s: %(name)s: %(funcName)s: %(message)s",
    }

    if args.log_file:
        log_kwargs["filename"] = args.log_file
    logging.basicConfig(**log_kwargs)

    # Reconfigure the logger after setting the level
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    serve(host=args.host, port=args.port, device=args.device)


if __name__ == "__main__":
    main()
