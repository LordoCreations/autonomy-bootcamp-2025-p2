"""
Heartbeat sending logic.
"""

from pymavlink import mavutil
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[True, HeartbeatSender] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """
        # Create a HeartbeatSender object
        if connection is None:
            local_logger.error("Cannot Create HeartbeatSender: no connection provided")
            return False, None
        return True, HeartbeatSender(cls.__private_key, connection, local_logger)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatSender.__private_key, "Use create() method"

        self.connection = connection
        self.logger = local_logger

    def run(
        self,
    ) -> bool:
        """
        Attempt to send a heartbeat message.
        """
        # Send a heartbeat message

        try:
            self.connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0
            )
            self.logger.info("Heartbeat sent successfully")
        except (OSError, TypeError, AttributeError) as e:
            self.logger.error(f"Failed to send heartbeat: {e}")
            return False
        return True


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
