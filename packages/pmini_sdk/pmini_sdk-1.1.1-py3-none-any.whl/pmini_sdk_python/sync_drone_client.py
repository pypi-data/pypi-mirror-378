#!/usr/bin/env python3
"""
Synchronous Drone Client Wrapper

This client provides a synchronous interface to the PMini drone server,
similar to mavsdk-python. It blocks until commands complete and handles
subscriptions in a separate thread for real-time updates.
"""

import asyncio
import logging
import math
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import grpc

from pmini_sdk_python.common import (
    Acceleration,
    AngularVelocity,
    Attitude,
    BatteryStatus,
    FlightMode,
    LidarRange,
    Position,
    Velocity,
)
from pmini_sdk_python.generated import drone_pb2  # type: ignore
from pmini_sdk_python.generated.drone_pb2 import CoordinateFrame
from pmini_sdk_python.generated.drone_pb2 import FlightMode as ProtoFlightMode
from pmini_sdk_python.generated.drone_pb2_grpc import DroneServiceStub

logger = logging.getLogger(__name__)


class DroneError(Exception):
    """Base exception for drone operations."""

    pass


class ConnectionError(DroneError):
    """Raised when connection to the drone server fails."""

    pass


class CommandError(DroneError):
    """Raised when a drone command fails."""

    pass


class SubscriptionCallback:
    """Callback wrapper for subscription data."""

    def __init__(self, callback: Callable, data_type: str):
        self.callback = callback
        self.data_type = data_type
        self.active = True

    def __call__(self, data: Any):
        if self.active and self.callback is not None:
            try:
                self.callback(data)
            except Exception as e:
                logger.error(f"Error in {self.data_type} callback: {e}")


class SyncDroneClient:
    """
    Synchronous client for controlling PMini drone via gRPC server.

    This client provides a synchronous interface that blocks until commands complete.
    Subscriptions are handled in a separate thread for real-time updates.
    """

    def __init__(self, server_address: str = "localhost:50051"):
        """
        Initialize the synchronous drone client.

        Args:
            server_address: Address of the drone server (host:port)
        """
        self.server_address = server_address
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[DroneServiceStub] = None
        self._connected = False
        self._connection_timeout = 10.0

        # Subscription management
        self._subscription_thread: Optional[threading.Thread] = None
        self._subscription_loop: Optional[asyncio.AbstractEventLoop] = None
        self._subscription_tasks: List[asyncio.Task] = []
        self._async_client: Optional[Any] = None
        self._subscription_callbacks: Dict[str, List[SubscriptionCallback]] = {
            "position": [],
            "velocity": [],
            "attitude": [],
            "status_text": [],
            "battery_status": [],
            "angular_velocity": [],
            "acceleration": [],
            "lidar_range": [],
        }
        self._subscription_running = False
        self._subscription_lock = threading.Lock()

    def connect(self, timeout: float = 10.0) -> None:
        """
        Connect to the drone server (synchronous).

        Args:
            timeout: Connection timeout in seconds

        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to drone server at {self.server_address}")
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = DroneServiceStub(self.channel)

            # Test connection by calling status
            self._test_connection(timeout)
            self._connected = True
            logger.info("Successfully connected to drone server")

        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    def disconnect(self) -> None:
        """Disconnect from the drone server."""
        # Stop subscription thread
        self._stop_subscription_thread()

        if self.channel:
            self.channel.close()
            self._connected = False
            logger.info("Disconnected from drone server")

    def _test_connection(self, timeout: float) -> None:
        """Test the connection by calling status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            # Use a future to handle timeout
            future = self.stub.Status.future(drone_pb2.StatusRequest())
            status = future.result(timeout=timeout)

            if not status.connected:
                raise ConnectionError("Drone not connected")
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")

    @property
    def connected(self) -> bool:
        """Check if connected to the server."""
        return self._connected

    def _execute_command(self, command_name: str, request, timeout: float = 10.0):
        """
        Execute a command and handle the response (synchronous).

        Args:
            command_name: Name of the command for logging
            request: The gRPC request object
            timeout: Command timeout in seconds

        Returns:
            CommandResponse: The command response

        Raises:
            CommandError: If command fails
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            logger.debug(f"Executing {command_name}")

            # Map request types to stub methods
            method_map = {
                drone_pb2.TakeoffRequest: self.stub.Takeoff,
                drone_pb2.LandRequest: self.stub.Land,
                drone_pb2.ArmRequest: self.stub.Arm,
                drone_pb2.DisarmRequest: self.stub.Disarm,
                drone_pb2.SetModeRequest: self.stub.SetMode,
                drone_pb2.GoToRequest: self.stub.GoTo,
                drone_pb2.MoveVelocityRequest: self.stub.MoveVelocity,
                drone_pb2.SetVelocityRequest: self.stub.SetVelocity,
                drone_pb2.EmergencyStopRequest: self.stub.EmergencyStop,
                drone_pb2.RebootRequest: self.stub.Reboot,
            }

            method = method_map.get(type(request))
            if not method:
                raise CommandError(f"Unknown request type: {type(request)}")

            # Execute synchronously with timeout
            future = method.future(request)
            response = future.result(timeout=timeout)

            if not response.success:
                raise CommandError(f"{command_name} failed: {response.message}")

            logger.debug(f"{command_name} completed successfully")
            return response

        except Exception as e:
            raise CommandError(f"{command_name} failed: {e}")

    # Basic flight commands (synchronous)
    def arm(self, timeout: float = 10.0):
        """Arm the drone (blocks until complete)."""
        request = drone_pb2.ArmRequest(timeout=timeout)
        return self._execute_command("Arm", request, timeout)

    def disarm(self, timeout: float = 10.0):
        """Disarm the drone (blocks until complete)."""
        request = drone_pb2.DisarmRequest(timeout=timeout)
        return self._execute_command("Disarm", request, timeout)

    def takeoff(self, altitude: float = 1.0, timeout: float = 30.0):
        """
        Takeoff to specified altitude (blocks until complete).

        Args:
            altitude: Takeoff altitude in meters
            timeout: Command timeout in seconds
        """
        request = drone_pb2.TakeoffRequest(altitude=altitude, timeout=timeout)
        return self._execute_command("Takeoff", request, timeout)

    def land(self, timeout: float = 30.0):
        """Land the drone (blocks until complete)."""
        request = drone_pb2.LandRequest(timeout=timeout)
        return self._execute_command("Land", request, timeout)

    def set_mode(self, mode: FlightMode, timeout: float = 10.0):
        """
        Set flight mode (blocks until complete).

        Args:
            mode: Flight mode to set
            timeout: Command timeout in seconds
        """
        # Convert to proto enum value by getting the proto enum with the numeric value
        proto_mode_value = mode.to_proto_value()
        # Convert integer to proto enum value
        proto_mode = ProtoFlightMode.ValueType(proto_mode_value)
        request = drone_pb2.SetModeRequest(mode=proto_mode, timeout=timeout)
        return self._execute_command("SetMode", request, timeout)

    # Movement commands (synchronous)
    def go_to(self, x: float, y: float, z: float, yaw: Optional[float] = None, frame: int = 0, timeout: float = 30.0):
        """
        Go to a specific position (blocks until complete).

        Args:
            x: North position in meters (or latitude if global frame)
            y: East position in meters (or longitude if global frame)
            z: Down position in meters (or altitude if global frame)
            yaw: Yaw angle in radians (optional)
            frame: Coordinate frame (0=body, 1=local, 2=global)
            timeout: Command timeout in seconds
        """
        # Convert frame to proto enum value
        proto_frame = CoordinateFrame.BODY_NED if frame == 0 else CoordinateFrame.LOCAL_NED
        request = drone_pb2.GoToRequest(x=x, y=y, z=z, yaw_rad=yaw, frame=proto_frame, timeout=timeout)
        return self._execute_command("GoTo", request, timeout)

    def move_velocity(
        self, v_x: float, v_y: float, v_z: float, yaw_rate: Optional[float] = None, frame: int = 0, timeout: float = 10.0
    ):
        """
        Move with specified velocity (blocks until complete).

        Args:
            v_x: North velocity in m/s
            v_y: East velocity in m/s
            v_z: Down velocity in m/s
            yaw_rate: Yaw rate in rad/s (optional)
            frame: Coordinate frame (0=body, 1=local)
            timeout: Command timeout in seconds
        """
        # Convert frame to proto enum value
        proto_frame = CoordinateFrame.BODY_NED if frame == 0 else CoordinateFrame.LOCAL_NED
        request = drone_pb2.MoveVelocityRequest(
            v_x=v_x,
            v_y=v_y,
            v_z=v_z,
            yaw_rate_rad_s=yaw_rate,
            frame=proto_frame,
            timeout=timeout,
        )
        return self._execute_command("MoveVelocity", request, timeout)

    def set_velocity(
        self,
        v_x: float,
        v_y: float,
        v_z: float,
        duration: float,
        yaw_rate: Optional[float] = None,
        frame: int = 0,
        timeout: Optional[float] = None,
    ):
        """
        Set velocity for a specified duration (blocks until complete).

        Args:
            v_x: North velocity in m/s
            v_y: East velocity in m/s
            v_z: Down velocity in m/s
            duration: Flight duration in seconds
            yaw_rate: Yaw rate in rad/s (optional)
            frame: Coordinate frame (0=body, 1=local)
            timeout: gRPC call timeout in seconds (default: duration + 5.0)
        """
        # Set gRPC timeout to duration + 5 seconds if not provided
        if timeout is None:
            timeout = duration + 5.0

        # Convert frame to proto enum value
        proto_frame = CoordinateFrame.BODY_NED if frame == 0 else CoordinateFrame.LOCAL_NED
        request = drone_pb2.SetVelocityRequest(
            v_x=v_x, v_y=v_y, v_z=v_z, duration=duration, yaw_rate_rad_s=yaw_rate, frame=proto_frame, timeout=timeout
        )
        return self._execute_command("SetVelocity", request, timeout)

    def set_angle(self, yaw_degrees: float, timeout: float = 10.0):
        """
        Set drone yaw angle without changing position (blocks until complete).

        Args:
            yaw_degrees: Target yaw angle in degrees (0-360)
            timeout: Command timeout in seconds

        Returns:
            CommandResponse: The command response

        Raises:
            CommandError: If command fails
        """
        # Convert degrees to radians
        yaw_radians = math.radians(yaw_degrees)

        # Use go_to with zero position and specified yaw
        return self.go_to(x=0.0, y=0.0, z=0.0, yaw=yaw_radians, frame=0, timeout=timeout)

    # Emergency commands (synchronous)
    def emergency_stop(self, timeout: float = 5.0):
        """Execute emergency stop (blocks until complete)."""
        request = drone_pb2.EmergencyStopRequest(timeout=timeout)
        return self._execute_command("EmergencyStop", request, timeout)

    def reboot(self, timeout: float = 10.0):
        """Reboot the drone (blocks until complete)."""
        request = drone_pb2.RebootRequest(timeout=timeout)
        return self._execute_command("Reboot", request, timeout)

    # Status and health (synchronous)
    def get_status(self):
        """Get current drone status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            future = self.stub.Status.future(drone_pb2.StatusRequest())
            return future.result(timeout=10.0)
        except Exception as e:
            raise CommandError(f"Failed to get status: {e}")

    def get_health(self):
        """Get drone health information."""
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            future = self.stub.GetHealth.future(drone_pb2.GetHealthRequest())
            return future.result(timeout=10.0)
        except Exception as e:
            raise CommandError(f"Failed to get health: {e}")

    # Unary getters for latest values (sync)
    def get_position_value(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            future = self.stub.GetPosition.future(drone_pb2.GetPositionRequest())
            resp = future.result(timeout=5.0)
            pos = Position.from_proto(resp.position)
            if component is None:
                return pos
            key = component.lower()
            if key == "x":
                return pos.x
            if key == "y":
                return pos.y
            if key == "z":
                return pos.z
            raise ValueError("component must be one of 'x','y','z'")
        except Exception as e:
            raise CommandError(f"Failed to get position: {e}")

    def get_velocity_value(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            future = self.stub.GetVelocity.future(drone_pb2.GetVelocityRequest())
            resp = future.result(timeout=5.0)
            vel = Velocity.from_proto(resp.velocity)
            if component is None:
                return vel
            key = component.lower()
            if key == "x":
                return vel.v_x
            if key == "y":
                return vel.v_y
            if key == "z":
                return vel.v_z
            raise ValueError("component must be one of 'x','y','z'")
        except Exception as e:
            raise CommandError(f"Failed to get velocity: {e}")

    def get_attitude_value(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            future = self.stub.GetAttitude.future(drone_pb2.GetAttitudeRequest())
            resp = future.result(timeout=5.0)
            att = Attitude.from_proto(resp.attitude)
            if component is None:
                return att
            key = component.lower()
            if key in ("roll", "roll_rad"):
                return att.roll_rad
            if key in ("pitch", "pitch_rad"):
                return att.pitch_rad
            if key in ("yaw", "yaw_rad"):
                return att.yaw_rad
            raise ValueError("component must be one of 'roll','pitch','yaw'")
        except Exception as e:
            raise CommandError(f"Failed to get attitude: {e}")

    def get_angular_velocity_value(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            future = self.stub.GetAngularVelocity.future(drone_pb2.GetAngularVelocityRequest())
            resp = future.result(timeout=5.0)
            av = AngularVelocity.from_proto(resp.angular_velocity)
            if component is None:
                return av
            key = component.lower()
            if key in ("roll", "x"):
                return av.roll_rate_rad_s
            if key in ("pitch", "y"):
                return av.pitch_rate_rad_s
            if key in ("yaw", "z"):
                return av.yaw_rate_rad_s
            raise ValueError("component must be one of 'roll','pitch','yaw' or 'x','y','z'")
        except Exception as e:
            raise CommandError(f"Failed to get angular velocity: {e}")

    def get_acceleration_value(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            future = self.stub.GetAcceleration.future(drone_pb2.GetAccelerationRequest())
            resp = future.result(timeout=5.0)
            acc = Acceleration.from_proto(resp.acceleration)
            if component is None:
                return acc
            key = component.lower()
            if key == "x":
                return acc.ax
            if key == "y":
                return acc.ay
            if key == "z":
                return acc.az
            raise ValueError("component must be one of 'x','y','z'")
        except Exception as e:
            raise CommandError(f"Failed to get acceleration: {e}")

    def get_lidar_range_value(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            future = self.stub.GetLidarRange.future(drone_pb2.GetLidarRangeRequest())
            resp = future.result(timeout=5.0)
            lr = LidarRange.from_proto(resp.lidar_range)
            if component is None:
                return lr
            key = component.lower()
            if key in ("distance", "distance_m"):
                return lr.distance_m
            if key in ("quality",):
                return lr.quality
            if key in ("sensor", "id", "sensor_id"):
                return lr.sensor_id
            raise ValueError("component must be 'distance','quality','sensor_id'")
        except Exception as e:
            raise CommandError(f"Failed to get lidar range: {e}")

    # Subscription management
    def add_position_callback(self, callback: Callable[[Position], None]) -> None:
        """
        Add a callback for position updates.

        Args:
            callback: Function to call with position data
        """
        with self._subscription_lock:
            self._subscription_callbacks["position"].append(SubscriptionCallback(callback, "position"))
        self._ensure_subscription_thread()

    def add_velocity_callback(self, callback: Callable[[Velocity], None]) -> None:
        """
        Add a callback for velocity updates.

        Args:
            callback: Function to call with velocity data
        """
        with self._subscription_lock:
            self._subscription_callbacks["velocity"].append(SubscriptionCallback(callback, "velocity"))
        self._ensure_subscription_thread()

    def add_attitude_callback(self, callback: Callable[[Attitude], None]) -> None:
        """
        Add a callback for attitude updates.

        Args:
            callback: Function to call with attitude data
        """
        with self._subscription_lock:
            self._subscription_callbacks["attitude"].append(SubscriptionCallback(callback, "attitude"))
        self._ensure_subscription_thread()

    def add_status_text_callback(self, callback: Callable[[str], None]) -> None:
        """
        Add a callback for status text updates.

        Args:
            callback: Function to call with status text data
        """
        with self._subscription_lock:
            self._subscription_callbacks["status_text"].append(SubscriptionCallback(callback, "status_text"))
        self._ensure_subscription_thread()

    def add_battery_status_callback(self, callback: Callable[[BatteryStatus], None]) -> None:
        """
        Add a callback for battery status updates.

        Args:
            callback: Function to call with battery status data
        """
        with self._subscription_lock:
            self._subscription_callbacks["battery_status"].append(SubscriptionCallback(callback, "battery_status"))
        self._ensure_subscription_thread()

    def remove_position_callback(self, callback: Callable[[Position], None]) -> None:
        """Remove a position callback."""
        with self._subscription_lock:
            self._subscription_callbacks["position"] = [
                cb for cb in self._subscription_callbacks["position"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def remove_velocity_callback(self, callback: Callable[[Velocity], None]) -> None:
        """Remove a velocity callback."""
        with self._subscription_lock:
            self._subscription_callbacks["velocity"] = [
                cb for cb in self._subscription_callbacks["velocity"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def remove_attitude_callback(self, callback: Callable[[Attitude], None]) -> None:
        """Remove an attitude callback."""
        with self._subscription_lock:
            self._subscription_callbacks["attitude"] = [
                cb for cb in self._subscription_callbacks["attitude"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def remove_status_text_callback(self, callback: Callable[[str], None]) -> None:
        """Remove a status text callback."""
        with self._subscription_lock:
            self._subscription_callbacks["status_text"] = [
                cb for cb in self._subscription_callbacks["status_text"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def remove_battery_status_callback(self, callback: Callable[[BatteryStatus], None]) -> None:
        """Remove a battery status callback."""
        with self._subscription_lock:
            self._subscription_callbacks["battery_status"] = [
                cb for cb in self._subscription_callbacks["battery_status"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def _add_callback(self, callback: Callable, data_type: str) -> None:
        """
        Add a callback for subscription data.

        Args:
            callback: Function to call with data
            data_type: Type of data for the callback
        """
        with self._subscription_lock:
            self._subscription_callbacks[data_type].append(SubscriptionCallback(callback, data_type))
        self._ensure_subscription_thread()

    def add_angular_velocity_callback(self, callback: Callable[[AngularVelocity], None]) -> None:
        """Add a callback for angular velocity updates."""
        self._add_callback(callback, "angular_velocity")

    def remove_angular_velocity_callback(self, callback: Callable[[AngularVelocity], None]) -> None:
        """Remove an angular velocity callback."""
        with self._subscription_lock:
            self._subscription_callbacks["angular_velocity"] = [
                cb for cb in self._subscription_callbacks["angular_velocity"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def add_acceleration_callback(self, callback: Callable[[Acceleration], None]) -> None:
        """Add a callback for acceleration updates."""
        self._add_callback(callback, "acceleration")

    def remove_acceleration_callback(self, callback: Callable[[Acceleration], None]) -> None:
        """Remove an acceleration callback."""
        with self._subscription_lock:
            self._subscription_callbacks["acceleration"] = [
                cb for cb in self._subscription_callbacks["acceleration"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def add_lidar_range_callback(self, callback: Callable[[LidarRange], None]) -> None:
        """Add a callback for lidar range updates."""
        self._add_callback(callback, "lidar_range")

    def remove_lidar_range_callback(self, callback: Callable[[LidarRange], None]) -> None:
        """Remove a lidar range callback."""
        with self._subscription_lock:
            self._subscription_callbacks["lidar_range"] = [
                cb for cb in self._subscription_callbacks["lidar_range"] if cb.callback != callback
            ]
        self._check_and_stop_subscription_thread()

    def _ensure_subscription_thread(self) -> None:
        """Ensure the subscription thread is running."""
        if not self._subscription_running:
            self._start_subscription_thread()

    def _check_and_stop_subscription_thread(self) -> None:
        """Check if subscription thread should be stopped (no active callbacks)."""
        with self._subscription_lock:
            has_callbacks = any(len(callbacks) > 0 for callbacks in self._subscription_callbacks.values())

        if not has_callbacks and self._subscription_running:
            logger.debug("No active callbacks, stopping subscription thread")
            self._stop_subscription_thread()

    def _start_subscription_thread(self) -> None:
        """Start the subscription thread."""
        if self._subscription_running:
            return

        self._subscription_running = True
        self._subscription_thread = threading.Thread(target=self._subscription_thread_worker, daemon=True)
        self._subscription_thread.start()
        logger.info("Subscription thread started")

    def _stop_subscription_thread(self) -> None:
        """Stop the subscription thread."""
        # First, try to cancel tasks and disconnect the async client on its loop
        self._subscription_running = False
        loop = self._subscription_loop
        if loop is not None:
            try:
                # Cancel running subscription tasks quickly
                def _cancel_tasks(tasks: List[asyncio.Task]):
                    for t in tasks:
                        try:
                            if not t.done():
                                t.cancel()
                        except Exception:
                            pass

                loop.call_soon_threadsafe(_cancel_tasks, list(self._subscription_tasks))

                # Disconnect async client to close streams immediately
                if self._async_client is not None:
                    fut = asyncio.run_coroutine_threadsafe(self._async_client.disconnect(), loop)
                    try:
                        fut.result(timeout=2.0)
                    except Exception:
                        pass
            except Exception:
                pass
        if self._subscription_thread and self._subscription_thread.is_alive():
            self._subscription_thread.join(timeout=5.0)  # wait for worker to exit cleanly
            logger.info("Subscription thread stopped")

    def _subscription_thread_worker(self) -> None:
        """Worker thread for handling subscriptions."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Expose loop so stopper can signal cancellation
            self._subscription_loop = loop

            # Run the async subscription worker
            loop.run_until_complete(self._async_subscription_worker())

        except Exception as e:
            logger.error(f"Subscription thread error: {e}")
        finally:
            try:
                loop.close()
            except Exception:
                pass
            # Cleanup loop reference after close
            self._subscription_loop = None

    async def _async_subscription_worker(self) -> None:
        """Async worker for handling subscriptions."""
        async_client = None
        tasks: List[asyncio.Task] = []
        try:
            # Create async client for subscriptions
            async_client = AsyncDroneClient(self.server_address)
            await async_client.connect()
            # Expose client so stopper can disconnect quickly
            self._async_client = async_client

            # Start subscription tasks
            if self._subscription_callbacks["position"]:
                tasks.append(asyncio.create_task(self._monitor_position(async_client)))

            if self._subscription_callbacks["velocity"]:
                tasks.append(asyncio.create_task(self._monitor_velocity(async_client)))

            if self._subscription_callbacks["attitude"]:
                tasks.append(asyncio.create_task(self._monitor_attitude(async_client)))

            if self._subscription_callbacks["status_text"]:
                tasks.append(asyncio.create_task(self._monitor_status_text(async_client)))

            if self._subscription_callbacks["battery_status"]:
                tasks.append(asyncio.create_task(self._monitor_battery_status(async_client)))

            if self._subscription_callbacks["angular_velocity"]:
                tasks.append(asyncio.create_task(self._monitor_angular_velocity(async_client)))

            if self._subscription_callbacks["acceleration"]:
                tasks.append(asyncio.create_task(self._monitor_acceleration(async_client)))

            if self._subscription_callbacks["lidar_range"]:
                tasks.append(asyncio.create_task(self._monitor_lidar_range(async_client)))

            # Run all subscription tasks
            if tasks:
                # Store tasks for external cancellation
                self._subscription_tasks = tasks
                await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Async subscription worker error: {e}")
        finally:
            # Cancel any remaining tasks first
            for task in tasks:
                if not task.done():
                    task.cancel()

            # Wait for tasks to complete cancellation
            if tasks:
                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    logger.debug(f"Task cancellation error: {e}")

            # Disconnect the async client
            if async_client:
                try:
                    await async_client.disconnect()
                except Exception as e:
                    logger.debug(f"Async client disconnect error: {e}")
            # Clear references
            self._async_client = None
            self._subscription_tasks = []

    async def _monitor_position(self, async_client) -> None:
        """Monitor position updates."""
        try:
            async for position in async_client.subscribe_position():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["position"].copy()

                for callback in callbacks:
                    callback(position)
        except Exception as e:
            logger.error(f"Position monitoring error: {e}")

    async def _monitor_velocity(self, async_client) -> None:
        """Monitor velocity updates."""
        try:
            async for velocity in async_client.subscribe_velocity():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["velocity"].copy()

                for callback in callbacks:
                    callback(velocity)
        except Exception as e:
            logger.error(f"Velocity monitoring error: {e}")

    async def _monitor_attitude(self, async_client) -> None:
        """Monitor attitude updates."""
        try:
            async for attitude in async_client.subscribe_attitude():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["attitude"].copy()

                for callback in callbacks:
                    callback(attitude)
        except Exception as e:
            logger.error(f"Attitude monitoring error: {e}")

    async def _monitor_status_text(self, async_client) -> None:
        """Monitor status text updates."""
        try:
            async for status_text in async_client.subscribe_status_text():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["status_text"].copy()

                for callback in callbacks:
                    callback(status_text)
        except Exception as e:
            logger.error(f"Status text monitoring error: {e}")

    async def _monitor_battery_status(self, async_client) -> None:
        """Monitor battery status updates."""
        try:
            async for battery in async_client.subscribe_battery_status():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["battery_status"].copy()

                for callback in callbacks:
                    callback(battery)
        except Exception as e:
            logger.error(f"Battery status monitoring error: {e}")

    async def _monitor_angular_velocity(self, async_client) -> None:
        """Monitor angular velocity updates."""
        try:
            async for angular_velocity in async_client.subscribe_angular_velocity():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["angular_velocity"].copy()

                for callback in callbacks:
                    callback(angular_velocity)
        except asyncio.CancelledError:
            logger.debug("Angular velocity monitoring cancelled")
        except Exception as e:
            logger.error(f"Angular velocity monitoring error: {e}")

    async def _monitor_acceleration(self, async_client) -> None:
        """Monitor acceleration updates."""
        try:
            async for acceleration in async_client.subscribe_acceleration():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["acceleration"].copy()

                for callback in callbacks:
                    callback(acceleration)
        except asyncio.CancelledError:
            logger.debug("Acceleration monitoring cancelled")
        except Exception as e:
            logger.error(f"Acceleration monitoring error: {e}")

    async def _monitor_lidar_range(self, async_client) -> None:
        """Monitor lidar range updates."""
        try:
            async for lidar_range in async_client.subscribe_lidar_range():
                if not self._subscription_running:
                    break

                with self._subscription_lock:
                    callbacks = self._subscription_callbacks["lidar_range"].copy()

                for callback in callbacks:
                    callback(lidar_range)
        except asyncio.CancelledError:
            logger.debug("Lidar range monitoring cancelled")
        except Exception as e:
            logger.error(f"Lidar range monitoring error: {e}")

    # Convenience methods
    def wait_for_connection(self, timeout: float = 30.0) -> None:
        """
        Wait for drone to be connected.

        Args:
            timeout: Maximum time to wait in seconds

        Raises:
            ConnectionError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_status()
                if status.connected:
                    logger.info("Drone connected")
                    return
            except Exception:
                pass
            time.sleep(1.0)

        raise ConnectionError(f"Drone not connected within {timeout}s")

    def wait_for_arm(self, timeout: float = 30.0) -> None:
        """
        Wait for drone to be armed.

        Args:
            timeout: Maximum time to wait in seconds

        Raises:
            CommandError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_status()
                if status.armed:
                    logger.info("Drone armed")
                    return
            except Exception:
                pass
            time.sleep(1.0)

        raise CommandError(f"Drone not armed within {timeout}s")

    def wait_for_disarm(self, timeout: float = 30.0) -> None:
        """
        Wait for drone to be disarmed.

        Args:
            timeout: Maximum time to wait in seconds

        Raises:
            CommandError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_status()
                if not status.armed:
                    logger.info("Drone disarmed")
                    return
            except Exception:
                pass
            time.sleep(1.0)

        raise CommandError(f"Drone not disarmed within {timeout}s")

    # Context manager support
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Import the async client for internal use
try:
    from .drone_client import DroneClient as AsyncDroneClient
except ImportError:
    # Fallback for when async client is not available
    AsyncDroneClient = None  # type: ignore


# Convenience functions for common operations
def create_sync_drone_client(server_address: str = "localhost:50051") -> SyncDroneClient:
    """
    Create and connect a synchronous drone client.

    Args:
        server_address: Address of the drone server

    Returns:
        SyncDroneClient: Connected synchronous drone client
    """
    client = SyncDroneClient(server_address)
    client.connect()
    return client


def basic_flight_sequence(client: SyncDroneClient, altitude: float = 1.0) -> None:
    """
    Execute a basic flight sequence: arm, takeoff, land, disarm.

    Args:
        client: Connected synchronous drone client
        altitude: Takeoff altitude in meters
    """
    try:
        logger.info("Starting basic flight sequence")

        # Wait for connection
        client.wait_for_connection()

        # Arm
        client.arm()
        client.wait_for_arm()

        # Takeoff
        client.takeoff(altitude)
        logger.info(f"Takeoff to {altitude}m completed")

        # Hover for a bit
        time.sleep(5.0)

        # Land
        client.land()
        logger.info("Landing completed")

        # Disarm
        client.disarm()
        client.wait_for_disarm()

        logger.info("Basic flight sequence completed successfully")

    except Exception as e:
        logger.error(f"Flight sequence failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    def main():
        logging.basicConfig(level=logging.INFO)

        # Example callback functions
        def position_callback(response):
            pos = response.position
            print(f"Position: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")

        def status_callback(response):
            print(f"Status: {response.status_text}")

        try:
            with SyncDroneClient() as client:
                # Add callbacks for real-time updates
                client.add_position_callback(position_callback)
                client.add_status_text_callback(status_callback)

                # Get status
                status = client.get_status()
                logger.info(f"Drone status: {status.message}")

                # Get health
                health = client.get_health()
                logger.info(f"Drone health: {health.message}")

                # Wait a bit to see some subscription data
                time.sleep(10.0)

        except Exception as e:
            logger.error(f"Example failed: {e}")

    main()
