# File : backend_logger.py
# Author : Sébastien Deriaz
# License : GPL
#
# This class starts a thread to grab log records from the backend and emit them here
# in their respective loggers

import logging
import threading
from multiprocessing.connection import Client
from time import sleep

from syndesi.tools.errors import BackendCommunicationError

from .backend_api import BACKEND_PORT, Action, _default_host, backend_request


class BackendLogger(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)

    def run(self) -> None:
        conn = None
        loggers: dict[str, logging.Logger] = {}
        while True:
            if conn is None:
                try:
                    conn = Client((_default_host, BACKEND_PORT))
                except ConnectionRefusedError:
                    conn = None
                    sleep(0.1)
                    continue
                
                try:
                    backend_request(conn, Action.SET_ROLE_LOGGER)
                except BackendCommunicationError:
                    conn.close()
                    conn = None
                    sleep(0.1)
                    continue

            else:
                try:
                    record: logging.LogRecord = conn.recv()
                except (EOFError, OSError, Exception):
                    sleep(0.1)
                    conn.close()
                    conn = None
                else:
                    logger_name = record.name
                    if logger_name not in loggers:
                        loggers[logger_name] = logging.getLogger(logger_name)
                    loggers[logger_name].handle(record)
