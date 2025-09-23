import argparse
import logging
import time
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FuturesTimeoutError
from importlib import metadata
from typing import Optional

import pymavlink.dialects.v20.ardupilotmega as mavcmd

from .common import (
    Acceleration,
    AngularVelocity,
    Attitude,
    BatteryStatus,
    FlightMode,
    Frame,
    LidarRange,
    MAVResult,
    Position,
    Velocity,
    Yaw,
)
from .high_level_commander import HighLevelCommander
from .low_level_commander import LowLevelCommander
from .mavlink_client import Config, MavlinkClient, TimeoutException


class Health:
    def __init__(self) -> None:
        self.is_data_pos = False
        self.is_data_lidar = False
        self.is_data_optical_flow = False
        self.is_calibration_accel = False
        self.is_calibration_gyro = False
        # Extended flags
        self.is_heartbeat = False
        self.is_data_attitude = False
        self.is_data_battery = False
        self.is_data_state = False

    def is_health(self) -> bool:
        return (
            self.is_data_pos
            and self.is_data_lidar
            and self.is_data_optical_flow
            and self.is_calibration_accel
            and self.is_calibration_gyro
        )


class Pmini:
    MAX_TAKEOFF_HEIGHT = 1.5
    POSITION_NORM_THRESHOLD = 0.5

    def __init__(self, config=Config()) -> None:
        self.__mavlink_client = MavlinkClient(config)
        self.__health = Health()

        # Data freshness timeouts (seconds) per message/group
        # You can adjust at runtime with set_data_timeout()
        self._data_timeouts: dict[str, float] = {
            "HEARTBEAT": 1.2,
            "GLOBAL_POSITION_INT": 1.5,
            "LOCAL_POSITION_NED": 0.6,
            "ATTITUDE": 1.0,
            "ATTITUDE_QUATERNION": 1.0,
            "OPTICAL_FLOW": 1.5,
            "EXTENDED_SYS_STATE": 1.0,
            "BATTERY_STATUS": 2.0,
            "STATUSTEXT": 5.0,
        }

        # Battery percentage calculation state
        self._voltage_readings: list[float] = []
        self._max_voltage_readings = 10  # Keep last 10 readings for averaging
        self._last_battery_percentage = 100.0  # Track last percentage to ensure it only decreases

        try:
            self.__mavlink_client.connect()
        except TimeoutException as e:
            logging.exception(f"Could not connect: {e}")
            logging.critical("MAVLink connection failed, system will exit")
            raise SystemExit(1)

        self.__mavlink_client.daemon = True
        self.__mavlink_client.start()
        self.__is_stream = False

        # Wait when mavlink_client is connected
        while not self.__mavlink_client.is_connected():
            time.sleep(0.1)

        self.high_level_commander = HighLevelCommander(self.__mavlink_client)
        self.low_level_commander = LowLevelCommander(self.__mavlink_client)

    def health(self) -> bool:
        return True
        # return self.__health.is_health()

    # --- Data freshness helpers ---
    def set_data_timeout(self, name: str, seconds: float) -> None:
        self._data_timeouts[name] = seconds

    def get_data_timeout(self, name: str) -> float:
        return self._data_timeouts.get(name, 2.0)

    def get_last_receive_times(self) -> dict[str, float]:
        return self.__mavlink_client.get_last_receive_times()

    def is_message_fresh(self, name: str) -> bool:
        last = self.__mavlink_client.get_last_receive_time(name)
        if last <= 0.0:
            return False
        return (time.time() - last) <= self.get_data_timeout(name)

    def refresh_health_flags(self) -> None:
        # Heartbeat
        self.__health.is_heartbeat = self.is_message_fresh("HEARTBEAT")
        # Position: accept either LOCAL or GLOBAL
        self.__health.is_data_pos = self.is_message_fresh("LOCAL_POSITION_NED") or self.is_message_fresh("GLOBAL_POSITION_INT")
        # Attitude (either form)
        self.__health.is_data_attitude = self.is_message_fresh("ATTITUDE") or self.is_message_fresh("ATTITUDE_QUATERNION")
        # Optical flow
        self.__health.is_data_optical_flow = self.is_message_fresh("OPTICAL_FLOW")
        # Landed state
        self.__health.is_data_state = self.is_message_fresh("EXTENDED_SYS_STATE")
        # Battery
        self.__health.is_data_battery = self.is_message_fresh("BATTERY_STATUS")

    def get_health_flags(self) -> Health:
        self.refresh_health_flags()
        return self.__health

    def enable_stream(self):
        logging.debug("Enable camera stream")
        self.__is_stream = True

    def disable_stream(self):
        logging.debug("Disable camera stream")
        self.__is_stream = True

    def get_image(self):
        if self.__is_stream:
            logging.debug("Get one frame")
        else:
            logging.warning("Stream is unavailable")

    def get_position(self) -> Position:
        """Get current position in NED coordinates.

        Returns
        -------
        Position
            Current position with x (north), y (east), z (down) in meters
        """
        return self.__mavlink_client.current_location

    def get_attitude(self) -> Attitude:
        """Get current attitude.

        Returns
        -------
        Attitude
            Current attitude with roll, pitch, yaw in radians
        """
        return self.__mavlink_client.attitude

    def get_velocity(self) -> Velocity:
        """Get current velocity in NED coordinates.

        Returns
        -------
        Velocity
            Current velocity with v_x (north), v_y (east), v_z (down) in m/s
        """
        return self.__mavlink_client.current_velocity

    def get_of(self):
        return self.__mavlink_client.optical_flow

    def get_battery_status(self) -> BatteryStatus:
        """Get current battery status with calculated percentage.

        Returns:
            BatteryStatus: Current battery status with percentage calculated from voltage
        """
        raw_battery = self.__mavlink_client.battery_status

        # Calculate percentage based on voltage since drone sensor is out of order (always reports 99%)
        calculated_percentage = self._calculate_battery_percentage(raw_battery.voltage_battery)

        # Create new BatteryStatus with calculated percentage
        return BatteryStatus(
            voltage_battery=raw_battery.voltage_battery,
            current_battery=raw_battery.current_battery,
            battery_remaining=calculated_percentage,
            voltage_cell_1=raw_battery.voltage_cell_1,
            voltage_cell_2=raw_battery.voltage_cell_2,
            voltage_cell_3=raw_battery.voltage_cell_3,
            voltage_cell_4=raw_battery.voltage_cell_4,
            voltage_cell_5=raw_battery.voltage_cell_5,
            voltage_cell_6=raw_battery.voltage_cell_6,
            battery_id=raw_battery.battery_id,
            current_consumed=raw_battery.current_consumed,
            energy_consumed=raw_battery.energy_consumed,
            temperature=raw_battery.temperature,
        )

    def get_angular_velocity(self) -> AngularVelocity:
        """Get current angular velocity.

        Returns:
            AngularVelocity: Current angular velocity with roll, pitch, yaw rates in rad/s
        """
        return self.__mavlink_client.angular_velocity

    def get_acceleration(self) -> Acceleration:
        """Get current acceleration.

        Returns:
            Acceleration: Current acceleration in X, Y, Z axes in m/s²
        """
        return self.__mavlink_client.acceleration

    def get_lidar_range(self) -> LidarRange:
        """Get current lidar range data.

        Returns:
            LidarRange: Current lidar range with distance, quality, and sensor ID
        """
        return self.__mavlink_client.lidar_range

    @property
    def armed(self) -> bool:
        return self.__mavlink_client.armed

    def _calculate_battery_percentage(self, voltage: float, max_voltage: float = 8.4, min_voltage: float = 6.4) -> int:
        """Calculate battery percentage based on voltage with load compensation for single-cell drones.

        Args:
            voltage: Current battery voltage in volts
            max_voltage: Maximum voltage for 100% charge (default: 8.4V)
            min_voltage: Minimum voltage for 0% charge (default: 6.4V)

        Returns:
            Battery percentage (0-100)
        """
        if voltage <= 0.0:
            return 0

        # Add current reading to the list
        self._voltage_readings.append(voltage)

        # Keep only the last N readings
        if len(self._voltage_readings) > self._max_voltage_readings:
            self._voltage_readings.pop(0)

        # Calculate average voltage to handle temporary load drops
        avg_voltage = sum(self._voltage_readings) / len(self._voltage_readings)

        # Calculate percentage based on voltage range
        # Linear interpolation between min and max voltages
        voltage_range = max_voltage - min_voltage
        voltage_above_min = avg_voltage - min_voltage

        # Calculate percentage (0-100)
        calculated_percentage = max(0.0, min(100.0, (voltage_above_min / voltage_range) * 100.0))

        # Ensure percentage only decreases (never increases) to avoid false recovery
        # Only update if the new percentage is lower than the last recorded percentage
        if calculated_percentage < self._last_battery_percentage:
            self._last_battery_percentage = calculated_percentage

        return int(self._last_battery_percentage)

    def reset_battery_percentage_tracking(self):
        """Reset battery percentage tracking to 100%.

        Call this method when a new battery is installed or when you want to
        reset the percentage tracking to start fresh.
        """
        self._last_battery_percentage = 100.0
        self._voltage_readings.clear()
        logging.info("Battery percentage tracking reset to 100%")

    def send_msg(self, msg):
        self.__mavlink_client.send_msg(msg)

    def arm(self, timeout: float = 2.0, retries: int = 5, retry_delay: float = 0.1) -> MAVResult:
        """
        Arms the drone. If the current flight mode is not armable, switches to GUIDED mode first.
        Returns:
            MAVResult: The result of the arm command.
        """
        if self.__mavlink_client.state.is_flight():
            logging.error("Drone is in flight")
            return MAVResult.FAILED

        future: Future[MAVResult] = Future()

        def call_arm():
            self.high_level_commander.arm(None)
            self.high_level_commander.arm(lambda result: future.set_result(result if result is not None else MAVResult.FAILED))

        if self.__mavlink_client.flight_mode != FlightMode.GUIDED:
            logging.warning(f"Current mode is not armable[{self.__mavlink_client.flight_mode}]")
            logging.warning("Switching to GUIDED mode")
            if self.change_mode(FlightMode.GUIDED).is_failed():
                logging.error("Failed to change mode to GUIDED")
                return MAVResult.FAILED
            call_arm()
        else:
            logging.debug(f"Arming drone in mode {self.__mavlink_client.flight_mode}")
            call_arm()

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending arm attempt #{attempt+1} (no callback registration)")
            self.high_level_commander.arm(None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.error("Arm command timed out")
            return MAVResult.FAILED

    def takeoff(self, height_m: float = 0.5, check_height: bool = True) -> MAVResult:
        """
        Takeoff the drone.
        Args:
            height_m: The height to takeoff to.
            check_height: If True, check if the height is too high.
        Returns:
            MAVResult: The result of the takeoff command.
        """
        if check_height:
            if height_m >= self.MAX_TAKEOFF_HEIGHT:
                logging.error("Takeoff height is too high")
                return MAVResult.FAILED

        future: Future[MAVResult] = Future()

        if self.arm().is_failed():
            logging.error("Arm failed")
            return MAVResult.FAILED

        self.high_level_commander.takeoff(height_m, None)
        self.high_level_commander.takeoff(
            height_m, lambda result: future.set_result(result if result is not None else MAVResult.FAILED)
        )

        try:
            result = future.result(timeout=4.0)
            logging.debug(f"Takeoff at {height_m} meters: {result}")
            logging.debug(f"Initial position: {self.__mavlink_client.current_location}")
            return result
        except FuturesTimeoutError:
            logging.error("Takeoff command timed out")
            return MAVResult.FAILED

    def go_to(self, x: float, y: float, z: float, yaw: Yaw = Yaw(value=0), frame: Frame = Frame.BODY):
        """
        Go to a position.
        Args:
            x: The x coordinate of the position.
            y: The y coordinate of the position.
            z: The z coordinate of the position.
            yaw: The yaw angle of the position.
            frame: The frame of the position.
        """

        self.high_level_commander.go_to(x, y, z, yaw, frame)

    def set_speed(
        self,
        vx: float,
        vy: float,
        vz: float,
        yaw: Yaw = Yaw(value=0.0),
        duration_seconds: Optional[float] = None,
        frame: Frame = Frame.BODY,
    ):
        """
        Set the drone's velocity for a specified duration. This method blocks until the duration is complete.

        Args:
            vx: Velocity in x direction (m/s)
            vy: Velocity in y direction (m/s)
            vz: Velocity in z direction (m/s)
            yaw: Yaw rate in radians per second (default: Yaw(value=0.0))
            duration_seconds: Duration to maintain speed in seconds. If None,
                raises ValueError (duration must be specified)
            frame: Coordinate frame (default: Frame.BODY)
        """
        if duration_seconds is None:
            raise ValueError("duration_seconds must be specified for set_speed method")

        logging.info(f"Setting speed: vx={vx}, vy={vy}, vz={vz}, yaw_rate={yaw.value} rad/s, " f"duration={duration_seconds}s")

        start_time = time.time()

        try:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= duration_seconds:
                    logging.info(f"Speed duration of {duration_seconds}s completed")
                    break

                # Send velocity command
                self.low_level_commander.set_velocity(vx, vy, vz, yaw, frame)

                # Wait before sending next command (typically 50ms for 20Hz)
                time.sleep(0.05)

        except Exception as e:
            logging.exception(f"Error in set_speed: {e}")
            raise
        finally:
            # Send zero velocity to stop the drone (with retries for safety)
            stop_yaw = Yaw(value=0.0)
            max_retries = 5
            retry_delay = 0.05

            for attempt in range(max_retries):
                try:
                    self.low_level_commander.set_velocity(0.0, 0.0, 0.0, stop_yaw, frame)
                    if attempt == 0:
                        logging.info("Speed control completed - sent zero velocity")
                    else:
                        logging.info(f"Speed control completed - sent zero velocity (retry {attempt + 1})")
                    time.sleep(retry_delay)  # Small delay between retries
                except Exception as e:
                    logging.warning(f"Error sending stop velocity (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        logging.error("Failed to send stop velocity after all retries")

    def land(self, timeout: float = 2.0, retries: int = 5, retry_delay: float = 0.1) -> MAVResult:
        """
        Land the drone.
        """
        future: Future[MAVResult] = Future()

        self.high_level_commander.land(None)
        self.high_level_commander.land(lambda result: future.set_result(result if result is not None else MAVResult.FAILED))

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending land attempt #{attempt+1} (no callback registration)")
            self.high_level_commander.land(None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.error("Takeoff command timed out")
            return MAVResult.FAILED

    def add_sys_status_callback(self, callback):
        def on_result(result: Optional[MAVResult]):
            if result is None or result.is_failed():
                logging.warning("Set EXTENDED_SYS_STATE interval failed or rejected")
            else:
                self.__mavlink_client.add_pmini_state_callback(callback)

        self.__mavlink_client.set_message_interval(
            mavcmd.MAVLINK_MSG_ID_EXTENDED_SYS_STATE,
            int(1_000_000 / 2),
            callback=on_result,
        )

    def change_mode(self, mode: FlightMode, timeout: float = 2.0, retries: int = 5, retry_delay: float = 0.1):
        future: Future[MAVResult] = Future()

        self.high_level_commander.change_mode(mode)

        def on_result(result: Optional[MAVResult]):
            if result is None or result.is_failed():
                logging.error(f"Change mode failed or rejected: {result}")
                return MAVResult.FAILED
            else:
                future.set_result(result)

        self.high_level_commander.change_mode(mode, on_result)

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending change mode attempt #{attempt+1} (no callback registration)")
            self.high_level_commander.change_mode(mode, None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.exception("Change mode command timed out")
            return MAVResult.FAILED

    def wait_arm(self, timeout=None):
        """
        Block until motors are armed.
        """
        self.__mavlink_client.wait_arm(timeout)

    def disarm(self):
        self.__mavlink_client.disarm()

    def reboot(self):
        self.__mavlink_client.reboot_drone()

    def wait_disarm(self):
        self.__mavlink_client.wait_disarm()

    def add_position_callback(self, callback):
        self.__mavlink_client.add_position_callback(callback)

    def add_velocity_callback(self, callback):
        self.__mavlink_client.add_velocity_callback(callback)

    def add_attitude_callback(self, callback):
        self.__mavlink_client.add_attitude_callback(callback)

    def add_of_callback(self, callback):
        self.__mavlink_client.add_of_callback(callback)

    def add_status_text_callback(self, callback):
        self.__mavlink_client.add_status_text_callback(callback)

    def add_attitude_quat_callback(self, callback):
        self.__mavlink_client.add_attitude_quat_callback(callback)

    def add_flight_mode_callback(self, callback):
        self.__mavlink_client.add_flight_mode_callback(callback)

    def add_pmini_state_callback(self, callback):
        self.__mavlink_client.add_pmini_state_callback(callback)

    def add_battery_status_callback(self, callback):
        """Add a callback for battery status updates.

        The callback will receive a BatteryStatus object with calculated percentage.
        """

        def battery_callback(raw_battery: BatteryStatus):
            # Calculate percentage based on voltage since drone sensor is out of order (always reports 99%)
            calculated_percentage = self._calculate_battery_percentage(raw_battery.voltage_battery)

            # Create new BatteryStatus with calculated percentage
            battery_with_calculated_percentage = BatteryStatus(
                voltage_battery=raw_battery.voltage_battery,
                current_battery=raw_battery.current_battery,
                battery_remaining=calculated_percentage,
                voltage_cell_1=raw_battery.voltage_cell_1,
                voltage_cell_2=raw_battery.voltage_cell_2,
                voltage_cell_3=raw_battery.voltage_cell_3,
                voltage_cell_4=raw_battery.voltage_cell_4,
                voltage_cell_5=raw_battery.voltage_cell_5,
                voltage_cell_6=raw_battery.voltage_cell_6,
                battery_id=raw_battery.battery_id,
                current_consumed=raw_battery.current_consumed,
                energy_consumed=raw_battery.energy_consumed,
                temperature=raw_battery.temperature,
            )

            # Call the user's callback with the calculated battery status
            callback(battery_with_calculated_percentage)

        self.__mavlink_client.add_battery_status_callback(battery_callback)

    def emergency_stop(self, timeout: float = 10.0, retries: int = 10, retry_delay: float = 0.5) -> MAVResult:
        """Execute emergency stop - immediately force disarms the drone.

        This is a safety-critical function that should be used in emergency situations.
        It sends a force disarm command with magic code 21196, which will immediately
        stop all motors, causing the drone to fall.

        Args:
            timeout: Timeout for the command in seconds (default: 10.0)
            retries: Number of retry attempts (default: 10)
            retry_delay: Delay between retries in seconds (default: 0.5)

        Returns:
            MAVResult: The result of the emergency stop command.

        WARNING: This will cause the drone to fall immediately. Use only in
        genuine emergency situations where the drone must be stopped instantly.
        This command cannot be cancelled once initiated.
        """
        logging.critical("EMERGENCY STOP called from Pmini class - Force disarming drone")

        future: Future[MAVResult] = Future()

        def call_emergency_stop():
            self.low_level_commander.emergency_stop(None)
            self.low_level_commander.emergency_stop(
                lambda result: future.set_result(result if result is not None else MAVResult.FAILED)
            )

        call_emergency_stop()

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending emergency stop attempt #{attempt+1} (no callback registration)")
            self.low_level_commander.emergency_stop(None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.error("Emergency stop command timed out")
            return MAVResult.FAILED


def get_package_version(package_name):
    try:
        version = metadata.version(package_name)
        return version
    except metadata.PackageNotFoundError:
        return None


def arg_parse():
    parser = argparse.ArgumentParser(description="SDK logging level.")
    parser.add_argument(
        "--log", type=str, default="INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    args = parser.parse_args()

    # Convert the logging level from string to the corresponding logging constant
    return getattr(logging, args.log.upper(), logging.INFO)


def get_pmini(config=Config()) -> Optional[Pmini]:
    FORMAT = "[%(asctime)s] %(levelname)s: %(name)s: %(funcName)s: %(message)s"
    logging.basicConfig(filename="out.log", format=FORMAT, level=arg_parse())

    package_name = "pmini"
    version = get_package_version(package_name)
    if version:
        framed_message = (
            f"\n"
            f"***************************\n"
            f"* Version of {package_name}: {version} *\n"
            f"***************************\n"
        )
        logging.info(framed_message)
    else:
        logging.warning(f"Failed to get the version for the {package_name} package")

    try:
        pmini = Pmini(config)
    except Exception as e:
        logging.error(f"Failed to initialize Pmini: {e}")
        return None

    return pmini


def main():
    FORMAT = "[%(asctime)s] %(levelname)s: %(name)s: %(funcName)s: %(message)s"
    logging.basicConfig(filename="out.log", format=FORMAT, level=arg_parse())

    try:
        pmini = Pmini()
    except Exception as e:
        logging.error(f"Failed to initialize Pmini: {e}")
        return

    if pmini.health():
        logging.info("Pmini ok")
    else:
        logging.error("Pmini not ok")

    pmini.high_level_commander.takeoff()

    # Image
    pmini.get_image()

    pmini.enable_stream()
    pmini.get_image()
    # End image

    pmini.high_level_commander.go_to(0, 1, 0, Yaw(value=45))
    pmini.high_level_commander.forward(1)
    pmini.high_level_commander.backward(1)
    pmini.high_level_commander.up(1)
    pmini.high_level_commander.down(1)

    pmini.high_level_commander.land()
    pmini.low_level_commander.emergency_stop()


if __name__ == "__main__":
    main()
