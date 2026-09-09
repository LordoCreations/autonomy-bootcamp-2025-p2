"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[True, HeartbeatReceiver] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        # Create a HeartbeatReceiver object

        if connection is None:
            local_logger.error("Cannot Create HeartbeatReceiver: no connection provided")
            return False, None
        return True, HeartbeatReceiver(cls.__private_key, connection, local_logger)

    def __init__(
        self, key: object, connection: mavutil.mavfile, local_logger: logger.Logger
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.logger = local_logger

        self.missed_heartbeats = 0
        self.connected = False

    def run(
        self,
    ) -> bool:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        try:
            msg = self.connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1.0)
        except (OSError, TypeError, AttributeError) as e:
            self.logger.error(f"Error recieving heartbeasts: {e}")
            return False

        if msg is not None:
            self.logger.info("Heartbeat received successfully")
            self.missed_heartbeats = 0
            self.connected = True
        else:
            self.missed_heartbeats += 1
            self.logger.warning(
                f"Missed heartbeat; Currently missed {self.missed_heartbeats} heartbeats consecutively"
            )

            if self.missed_heartbeats >= 5:
                self.connected = False
                self.logger.warning("Marked as Disconnected due to consecutive missed heartbeats")

        return True


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
