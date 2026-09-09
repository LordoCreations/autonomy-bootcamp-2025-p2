"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import heartbeat_receiver
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_receiver_worker(
    connection: mavutil.mavfile,
    controller: worker_controller.WorkerController,
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
) -> None:
    """
    Worker process.

    connection: mavlink connection to recieve heartbeats from
    controller: worker controller to check for pause/exit requests
    output_queue: output data queue to send connection states to
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
    # Instantiate class object (heartbeat_receiver.HeartbeatReceiver)
    res, receiver = heartbeat_receiver.HeartbeatReceiver.create(connection, local_logger)

    if not res:
        local_logger.error("Failed to create HeartbeatReceiver")
        return

    local_logger.info("HeartbeatReceiver created successfully")

    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()

        if not receiver.run():
            local_logger.error("Failed to receive heartbeat")
            continue

        output_queue.queue.put("Connected" if receiver.connected else "Disconnected")

    local_logger.info("Exiting Heartbeat Receiver worker gracefully")


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
