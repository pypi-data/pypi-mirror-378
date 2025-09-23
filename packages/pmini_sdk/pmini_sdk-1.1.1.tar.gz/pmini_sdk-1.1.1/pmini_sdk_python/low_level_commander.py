import logging

import pymavlink.dialects.v20.ardupilotmega as mavcmd

from .common import Frame, Yaw

logger = logging.getLogger(__name__)


class LowLevelCommander:
    def __init__(self, mavlink_client=None):
        self.__mavlink_client = mavlink_client

    def emergency_stop(self, callback=None):
        """Execute emergency stop by force disarming the drone immediately.

        This method performs an emergency stop by sending a force disarm command
        with the magic code 21196. This will immediately stop all motors,
        causing the drone to fall. This is the proper emergency stop procedure
        for in-flight emergencies.

        Args:
            callback: Optional callback function to receive the result

        WARNING: This will cause the drone to fall immediately. Use only in
        genuine emergency situations where the drone must be stopped instantly.
        """
        logger.critical("EMERGENCY STOP INITIATED - Force disarming drone immediately")

        # Check if drone is already disarmed
        if not self.__mavlink_client.armed:
            logger.critical("Emergency stop: Drone already disarmed")
            if callback:
                from .common import MAVResult

                callback(MAVResult.ACCEPTED)
            return

        # Send emergency stop command with ACK tracking
        emergency_msg = self.__mavlink_client.command_packager.package_emergency_stop()
        self.__mavlink_client.send_msg_with_ack(emergency_msg, callback)
        logger.critical("Emergency stop: Force disarm command sent")

    def set_velocity(self, x: float, y: float, z: float, yaw: Yaw, frame: Frame = Frame.BODY):
        logger.info(f"package and send: vel = ({x}, {y}, {z}) yaw = {yaw.value}[rad] in {frame}")
        type_mask = (
            mavcmd.POSITION_TARGET_TYPEMASK_X_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_Y_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_Z_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AX_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AY_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AZ_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_FORCE_SET
            | mavcmd.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
        )

        self.__mavlink_client.send_msg(self.__mavlink_client.command_packager.package_velocity(x, y, z, type_mask, yaw))

    def set_angle(self, r: float, p: float, y: float, yaw: float, frame: Frame = Frame.BODY):
        logger.debug(f"Send angle: vel = ({r}, {p}, {y}) yaw = {yaw}[deg] in {frame}")
