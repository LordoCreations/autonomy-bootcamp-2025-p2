"""
Decision-making logic.
"""

import math

import numpy as np
from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> "tuple[bool, Command | None]":
        """
        Falliable create (instantiation) method to create a Command object.
        """
        try:
            return True, Command(cls.__private_key, connection, target, local_logger)
        except (OSError, TypeError, AttributeError) as e:
            local_logger.error(f"Unexpected Error when creating Command object: {e}")
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.target = target
        self.logger = local_logger

        self.vel_sum = np.array([0.0, 0.0, 0.0])
        self.samples = 0

    def run(
        self,
        telemetry_data: telemetry.Telemetry,
    ) -> "tuple[bool, str | None]":
        """
        Make a decision based on received telemetry data.
        """

        if telemetry_data is None:
            self.logger.error("Did not recieve telemetry data")
            return False, None

        # Log average velocity for this trip so far
        if (
            telemetry_data.x_velocity is None
            or telemetry_data.y_velocity is None
            or telemetry_data.z_velocity is None
        ):
            self.logger.error("Telemetry data missing velocity information")
            return False, None

        self.vel_sum += np.array(
            [telemetry_data.x_velocity, telemetry_data.y_velocity, telemetry_data.z_velocity]
        )

        self.samples += 1
        avg_vel = self.vel_sum / self.samples
        self.logger.info(f"Average velocity so far: {avg_vel}")

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"

        delta_height = self.target.z - telemetry_data.z
        if abs(delta_height) > 0.5:
            self.connection.mav.command_long_send(
                1,
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                self.target.z,
            )
            out = f"CHANGE ALTITUDE: {delta_height}"
            self.logger.info(out)
            return True, out

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system

        target_yaw = math.atan2(self.target.y - telemetry_data.y, self.target.x - telemetry_data.x)

        delta_yaw = math.degrees(target_yaw - telemetry_data.yaw)
        while delta_yaw > 180:
            delta_yaw -= 360
        while delta_yaw < -180:
            delta_yaw += 360

        if abs(delta_yaw) > 5:
            self.connection.mav.command_long_send(
                1,
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                0,
                delta_yaw,
                5,
                0,
                1,
                0,
                0,
                0,
            )
            out = f"CHANGE YAW: {delta_yaw}"
            self.logger.info(out)
            return True, out

        return True, None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
