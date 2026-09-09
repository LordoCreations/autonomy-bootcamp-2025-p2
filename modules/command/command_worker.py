"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib
import queue

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    controller: worker_controller.WorkerController,
    input_queue: queue_proxy_wrapper.QueueProxyWrapper,
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
) -> None:
    """
    Worker process.

    connection: mavlink connection to send and recieve commands
    target: target position to maintain
    controller: worker controller to signal worker
    input_queue: input data queue to recieve telemetry data
    output_queue: output data queue to send results to main thread
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
    # Instantiate class object (command.Command)
    res, command_obj = command.Command.create(connection, target, local_logger)
    if not res:
        local_logger.error("Failed to create Command")
        return

    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()

        try:
            telemetry_data = input_queue.queue.get(timeout=0.1)
        except queue.Empty:
            continue

        if telemetry_data is None:
            local_logger.warning("Failed to get telemetry data")
            continue

        res, out = command_obj.run(telemetry_data)
        if not res:
            local_logger.warning("Failed to run command")
            continue

        if out is not None:
            output_queue.queue.put(out)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
