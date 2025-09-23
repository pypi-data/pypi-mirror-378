#!/usr/bin/env python3
"""
Comprehensive Drone Client Wrapper

This client provides a high-level interface to the PMini drone server,
similar to mavsdk-python. It handles connection management, error handling,
and provides convenient methods for drone control.
"""

import asyncio
import logging
import time
from typing import AsyncIterator, Optional

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


class DroneClient:
    """
    High-level client for controlling PMini drone via gRPC server.

    This client provides a convenient interface similar to mavsdk-python
    for controlling the drone, with proper error handling and connection management.
    """

    def __init__(self, server_address: str = "localhost:50051"):
        """
        Initialize the drone client.

        Args:
            server_address: Address of the drone server (host:port)
        """
        self.server_address = server_address
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[DroneServiceStub] = None
        self._connected = False
        self._connection_timeout = 10.0

    async def connect(self, timeout: float = 10.0) -> None:
        """
        Connect to the drone server.

        Args:
            timeout: Connection timeout in seconds

        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to drone server at {self.server_address}")
            self.channel = grpc.aio.insecure_channel(self.server_address)
            self.stub = DroneServiceStub(self.channel)

            # Test connection by calling status
            await asyncio.wait_for(self._test_connection(), timeout=timeout)
            self._connected = True
            logger.info("Successfully connected to drone server")

        except asyncio.TimeoutError:
            raise ConnectionError(f"Connection timeout after {timeout}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the drone server."""
        if self.channel:
            await self.channel.close()
            self._connected = False
            logger.info("Disconnected from drone server")

    async def _test_connection(self) -> None:
        """Test the connection by calling status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            status = await self.stub.Status(drone_pb2.StatusRequest())
            if not status.connected:
                raise ConnectionError("Drone not connected")
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")

    @property
    def connected(self) -> bool:
        """Check if connected to the server."""
        return self._connected

    async def _execute_command(self, command_name: str, request, timeout: float = 10.0):
        """
        Execute a command and handle the response.

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
            # Map request types based on proto classes
            method_map = {
                drone_pb2.TakeoffRequest: self.stub.Takeoff,
                drone_pb2.LandRequest: self.stub.Land,
                drone_pb2.ArmRequest: self.stub.Arm,
                drone_pb2.DisarmRequest: self.stub.Disarm,
                drone_pb2.SetModeRequest: self.stub.SetMode,
                drone_pb2.GoToRequest: self.stub.GoTo,
                drone_pb2.MoveVelocityRequest: self.stub.MoveVelocity,
                drone_pb2.EmergencyStopRequest: self.stub.EmergencyStop,
                drone_pb2.RebootRequest: self.stub.Reboot,
                drone_pb2.SetVelocityRequest: self.stub.SetVelocity,
            }

            method = method_map.get(type(request))
            if not method:
                raise CommandError(f"Unknown request type: {type(request)}")

            response = await asyncio.wait_for(method(request), timeout=timeout)

            if not response.success:
                raise CommandError(f"{command_name} failed: {response.message}")

            logger.debug(f"{command_name} completed successfully")
            return response

        except asyncio.TimeoutError:
            raise CommandError(f"{command_name} timed out after {timeout}s")
        except grpc.RpcError as e:
            raise CommandError(f"{command_name} gRPC error: {e}")
        except Exception as e:
            raise CommandError(f"{command_name} failed: {e}")

    # Basic flight commands
    async def arm(self, timeout: float = 10.0):
        """Arm the drone."""
        request = drone_pb2.ArmRequest(timeout=timeout)
        return await self._execute_command("Arm", request, timeout)

    async def disarm(self, timeout: float = 10.0):
        """Disarm the drone."""
        request = drone_pb2.DisarmRequest(timeout=timeout)
        return await self._execute_command("Disarm", request, timeout)

    async def takeoff(self, altitude: float = 1.0, timeout: float = 30.0):
        """
        Takeoff to specified altitude.

        Args:
            altitude: Takeoff altitude in meters
            timeout: Command timeout in seconds
        """
        request = drone_pb2.TakeoffRequest(altitude=altitude, timeout=timeout)
        return await self._execute_command("Takeoff", request, timeout)

    async def land(self, timeout: float = 30.0):
        """Land the drone."""
        request = drone_pb2.LandRequest(timeout=timeout)
        return await self._execute_command("Land", request, timeout)

    async def set_mode(self, mode: FlightMode, timeout: float = 10.0):
        """
        Set flight mode.

        Args:
            mode: Flight mode to set
            timeout: Command timeout in seconds
        """
        # Convert to proto enum value by getting the proto enum with the numeric value
        proto_mode_value = mode.to_proto_value()
        # Convert integer to proto enum value
        proto_mode = ProtoFlightMode.ValueType(proto_mode_value)
        request = drone_pb2.SetModeRequest(mode=proto_mode, timeout=timeout)
        return await self._execute_command("SetMode", request, timeout)

    # Movement commands
    async def go_to(self, x: float, y: float, z: float, yaw: Optional[float] = None, frame: int = 0, timeout: float = 30.0):
        """
        Go to a specific position.

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
        return await self._execute_command("GoTo", request, timeout)

    async def move_velocity(
        self, v_x: float, v_y: float, v_z: float, yaw_rate: Optional[float] = None, frame: int = 0, timeout: float = 10.0
    ):
        """
        Move with specified velocity.

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
        return await self._execute_command("MoveVelocity", request, timeout)

    # Emergency commands
    async def emergency_stop(self, timeout: float = 5.0):
        """Execute emergency stop."""
        request = drone_pb2.EmergencyStopRequest(timeout=timeout)
        return await self._execute_command("EmergencyStop", request, timeout)

    async def reboot(self, timeout: float = 10.0):
        """Reboot the drone."""
        request = drone_pb2.RebootRequest(timeout=timeout)
        return await self._execute_command("Reboot", request, timeout)

    # Status and health
    async def get_status(self):
        """Get current drone status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            return await self.stub.Status(drone_pb2.StatusRequest())
        except Exception as e:
            raise CommandError(f"Failed to get status: {e}")

    async def get_health(self):
        """Get drone health information."""
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            return await self.stub.GetHealth(drone_pb2.GetHealthRequest())
        except Exception as e:
            raise CommandError(f"Failed to get health: {e}")

    # Unary getters for latest values
    async def get_position(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            resp = await self.stub.GetPosition(drone_pb2.GetPositionRequest())
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

    async def get_velocity(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            resp = await self.stub.GetVelocity(drone_pb2.GetVelocityRequest())
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

    async def get_attitude(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            resp = await self.stub.GetAttitude(drone_pb2.GetAttitudeRequest())
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

    async def get_angular_velocity(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            resp = await self.stub.GetAngularVelocity(drone_pb2.GetAngularVelocityRequest())
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

    async def get_acceleration(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            resp = await self.stub.GetAcceleration(drone_pb2.GetAccelerationRequest())
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

    async def get_lidar_range(self, component: Optional[str] = None):
        if not self.stub:
            raise ConnectionError("Not connected to server")
        try:
            resp = await self.stub.GetLidarRange(drone_pb2.GetLidarRangeRequest())
            # Reuse domain message conversion
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

    # Streaming methods
    async def subscribe_position(self, rate_hz: float = 10.0) -> AsyncIterator[Position]:
        """
        Subscribe to position updates.

        Args:
            rate_hz: Requested update rate in Hz

        Yields:
            PositionResponse: Position updates
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribePositionRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribePosition(request):
                yield Position.from_proto(response.position)
        except Exception as e:
            raise CommandError(f"Position subscription failed: {e}")

    async def subscribe_velocity(self, rate_hz: float = 10.0) -> AsyncIterator[Velocity]:
        """
        Subscribe to velocity updates.

        Args:
            rate_hz: Requested update rate in Hz

        Yields:
            VelocityResponse: Velocity updates
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeVelocityRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeVelocity(request):
                yield Velocity.from_proto(response.velocity)
        except Exception as e:
            raise CommandError(f"Velocity subscription failed: {e}")

    async def subscribe_attitude(self, rate_hz: float = 10.0) -> AsyncIterator[Attitude]:
        """
        Subscribe to attitude updates.

        Args:
            rate_hz: Requested update rate in Hz

        Yields:
            AttitudeResponse: Attitude updates
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeAttitudeRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeAttitude(request):
                yield Attitude.from_proto(response.attitude)
        except Exception as e:
            raise CommandError(f"Attitude subscription failed: {e}")

    async def subscribe_status_text(self) -> AsyncIterator[str]:
        """
        Subscribe to status text messages.

        Yields:
            StatusTextResponse: Status text messages
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeStatusTextRequest()
            async for response in self.stub.SubscribeStatusText(request):
                yield response.status_text
        except Exception as e:
            raise CommandError(f"Status text subscription failed: {e}")

    async def subscribe_battery_status(self, rate_hz: float = 2.0) -> AsyncIterator[BatteryStatus]:
        """
        Subscribe to battery status updates.

        Args:
            rate_hz: Update rate in Hz (default: 2.0)

        Yields:
            BatteryStatusResponse: Battery status messages
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeBatteryStatusRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeBatteryStatus(request):
                yield BatteryStatus.from_proto(response.battery_status)
        except Exception as e:
            raise CommandError(f"Battery status subscription failed: {e}")

    async def subscribe_angular_velocity(self, rate_hz: float = 10.0) -> AsyncIterator[AngularVelocity]:
        """
        Subscribe to angular velocity updates.

        Args:
            rate_hz: Update rate in Hz (default: 10.0)

        Yields:
            AngularVelocity: Angular velocity data
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeAngularVelocityRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeAngularVelocity(request):
                yield AngularVelocity.from_proto(response.angular_velocity)
        except Exception as e:
            raise CommandError(f"Angular velocity subscription failed: {e}")

    async def subscribe_acceleration(self, rate_hz: float = 10.0) -> AsyncIterator[Acceleration]:
        """
        Subscribe to acceleration updates.

        Args:
            rate_hz: Update rate in Hz (default: 10.0)

        Yields:
            Acceleration: Acceleration data
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeAccelerationRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeAcceleration(request):
                yield Acceleration.from_proto(response.acceleration)
        except Exception as e:
            raise CommandError(f"Acceleration subscription failed: {e}")

    async def subscribe_lidar_range(self, rate_hz: float = 10.0) -> AsyncIterator[LidarRange]:
        """
        Subscribe to lidar range updates.

        Args:
            rate_hz: Update rate in Hz (default: 10.0)

        Yields:
            LidarRange: Lidar range data
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")

        try:
            request = drone_pb2.SubscribeLidarRangeRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeLidarRange(request):
                yield LidarRange.from_proto(response.lidar_range)
        except Exception as e:
            raise CommandError(f"Lidar range subscription failed: {e}")

    # Convenience methods
    async def wait_for_connection(self, timeout: float = 30.0) -> None:
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
                status = await self.get_status()
                if status.connected:
                    logger.info("Drone connected")
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)

        raise ConnectionError(f"Drone not connected within {timeout}s")

    async def wait_for_arm(self, timeout: float = 30.0) -> None:
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
                status = await self.get_status()
                if status.armed:
                    logger.info("Drone armed")
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)

        raise CommandError(f"Drone not armed within {timeout}s")

    async def wait_for_disarm(self, timeout: float = 30.0) -> None:
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
                status = await self.get_status()
                if not status.armed:
                    logger.info("Drone disarmed")
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)

        raise CommandError(f"Drone not disarmed within {timeout}s")

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience functions for common operations
async def create_drone_client(server_address: str = "localhost:50051") -> DroneClient:
    """
    Create and connect a drone client.

    Args:
        server_address: Address of the drone server

    Returns:
        DroneClient: Connected drone client
    """
    client = DroneClient(server_address)
    await client.connect()
    return client


async def basic_flight_sequence(client: DroneClient, altitude: float = 1.0) -> None:
    """
    Execute a basic flight sequence: arm, takeoff, land, disarm.

    Args:
        client: Connected drone client
        altitude: Takeoff altitude in meters
    """
    try:
        logger.info("Starting basic flight sequence")

        # Wait for connection
        await client.wait_for_connection()

        # Arm
        await client.arm()
        await client.wait_for_arm()

        # Takeoff
        await client.takeoff(altitude)
        logger.info(f"Takeoff to {altitude}m completed")

        # Hover for a bit
        await asyncio.sleep(5.0)

        # Land
        await client.land()
        logger.info("Landing completed")

        # Disarm
        await client.disarm()
        await client.wait_for_disarm()

        logger.info("Basic flight sequence completed successfully")

    except Exception as e:
        logger.error(f"Flight sequence failed: {e}")
        raise


async def monitor_drone_state(client: DroneClient, duration: float = 30.0) -> None:
    """
    Monitor drone state for a specified duration.

    Args:
        client: Connected drone client
        duration: Monitoring duration in seconds
    """
    try:
        logger.info(f"Monitoring drone state for {duration}s")

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(_monitor_position(client)),
            asyncio.create_task(_monitor_velocity(client)),
            asyncio.create_task(_monitor_attitude(client)),
            asyncio.create_task(_monitor_status_text(client)),
        ]

        # Wait for duration
        await asyncio.sleep(duration)

        # Cancel monitoring tasks
        for task in tasks:
            task.cancel()

        logger.info("Drone state monitoring completed")

    except Exception as e:
        logger.error(f"State monitoring failed: {e}")
        raise


async def _monitor_position(client: DroneClient) -> None:
    """Monitor position updates."""
    try:
        async for pos in client.subscribe_position():
            logger.info(f"Position: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
    except asyncio.CancelledError:
        pass


async def _monitor_velocity(client: DroneClient) -> None:
    """Monitor velocity updates."""
    try:
        async for vel in client.subscribe_velocity():
            logger.info(f"Velocity: ({vel.v_x:.2f}, {vel.v_y:.2f}, {vel.v_z:.2f}) m/s")
    except asyncio.CancelledError:
        pass


async def _monitor_attitude(client: DroneClient) -> None:
    """Monitor attitude updates."""
    try:
        async for att in client.subscribe_attitude():
            logger.info(f"Attitude: roll={att.roll_rad:.2f}, pitch={att.pitch_rad:.2f}, yaw={att.yaw_rad:.2f}")
    except asyncio.CancelledError:
        pass


async def _monitor_status_text(client: DroneClient) -> None:
    """Monitor status text messages."""
    try:
        async for status_text in client.subscribe_status_text():
            logger.info(f"Status: {status_text}")
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    # Example usage
    async def main():
        logging.basicConfig(level=logging.INFO)

        try:
            async with DroneClient() as client:
                # Get status
                status = await client.get_status()
                logger.info(f"Drone status: {status.message}")

                # Get health
                health = await client.get_health()
                logger.info(f"Drone health: {health.message}")

                # Monitor state for 10 seconds
                await monitor_drone_state(client, 10.0)

        except Exception as e:
            logger.error(f"Example failed: {e}")

    asyncio.run(main())
