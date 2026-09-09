"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import worker_controller
from . import heartbeat_sender
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_sender_worker(
    connection: mavutil.mavfile,
    controller: worker_controller.WorkerController,
) -> None:
    """
    Worker process.

    connection: mavlink connection to send heartbeats
    controller: worker controller to check for pause/exit requests
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_sender.HeartbeatSender)
    res, sender = heartbeat_sender.HeartbeatSender.create(connection, local_logger)

    if not res:
        local_logger.error("Failed to create HeartbeatSender")
        return

    local_logger.info("HeartbeatSender created successfully")

    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()

        if not sender.run():
            local_logger.warning("Heartbeat failed to send")

        time.sleep(1)

    local_logger.info("Exiting Heartbeat Sender worker gracefully")


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
