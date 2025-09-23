# backend_status.py
# 13.07.2025
# Sébastien Deriaz

import argparse
import logging
import threading
import time
from multiprocessing.connection import Client, Connection
from time import sleep

from typing import Any, Callable, Optional, Tuple, List, cast

from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from ..tools.backend_api import LOCALHOST, Action, AdapterBackendStatus, backend_request, BACKEND_PORT
from ..tools.backend_logger import BackendLogger
from ..tools.log_settings import LoggerAlias

LOGGING_COLORS = {
    logging.DEBUG: "grey66",
    logging.INFO: "green",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "bold purple",
}

logging.getLogger().setLevel(logging.CRITICAL + 1)


class LogHandler(logging.Handler):
    def __init__(self, callback : Optional[Callable[[logging.LogRecord], None]] = None) -> None:
        super().__init__()
        self.callback = callback

    def emit(self, record : logging.LogRecord) -> None:
        if self.callback is not None:
            self.callback(record)


class BackendStatus:
    DEFAULT_REFRESH_RATE = 0.5
    DEFAULT_N_CONSOLE_LINES = 20  # Number of lines in the console view
    CONNECTIONS_MIN_HEIGHT = 2

    def __init__(self, input_args : list[str]) -> None:
        self.argument_parser = argparse.ArgumentParser()
        self.argument_parser.add_argument(
            "-l",
            "--live",
            type=float,
            default=False,
            help="Live mode, update status continuously at set refresh rate",
        )
        self.argument_parser.add_argument(
            "--log-lines",
            type=int,
            default=self.DEFAULT_N_CONSOLE_LINES,
            help="Number of log lines to display",
        )
        self.argument_parser.add_argument(
            "-a",
            "--address",
            type=str,
            default=LOCALHOST,
            help="Listening address, set it to the interface that will be used by the client",
        )
        self.argument_parser.add_argument("-p", "--port", type=int, default=BACKEND_PORT)
        self.argument_parser.add_argument("--log-level", type=str, choices=list(logging._nameToLevel.keys())) # pyright: ignore[reportPrivateUsage]

        args = self.argument_parser.parse_args(input_args)

        self._n_console_lines = args.log_lines
        self.host : str = args.address
        self.port : int = args.port
        self.live_delay : Optional[float] = args.live

        self.console_lines : List[str] = []  # Buffer for last N_CONSOLE_LINES log messages
        self.console_lock = threading.Lock()  # Lock for thread safety
        self._backend_logger = BackendLogger()  # use_queue=True)
        self._backend_logger.start()
        self._start_time = time.time()
        self.conn : Optional[Connection[Any, Any]] = None

        self._log_handler = LogHandler()

    def run(self) -> None:        
        self._log_handler.callback = self._add_line_status_screen
        logging.getLogger().addHandler(self._log_handler)
        adapter_table = None
        main_table = Table(box=None, padding=(0, 1))
        main_table.add_column(justify="right")
        main_table.add_column(justify="left")
        try:
            with Live(refresh_per_second=30) as live_display:
                while True:
                    if self.conn is None:
                        try:
                            self.conn = Client((self.host, self.port))
                        except ConnectionRefusedError as e:
                            self.conn = None
                            sleep(0.5)
                        else:
                            backend_request(self.conn, Action.SET_ROLE_MONITORING)
                            # TODO : Make log level configurable
                            backend_request(self.conn, Action.SET_LOG_LEVEL, int(logging.DEBUG))

                    logger_connections = Table(
                            "", box=None, caption_justify="right"
                        )
                    
                    if self.conn is not None:
                        backend_status = "[green3]● Online"
                        adapter_table = Table(
                            "", box=None, caption_justify="right"
                        )

                        snapshot : dict[str, Tuple[bool, List[str]]] = cast(dict[str, Tuple[bool, List[str]]], backend_request(self.conn, Action.ENUMERATE_ADAPTER_CONNECTIONS)[0])
                        
                        unique_clients : set[str] = set()
                        for adapter, (status, adapter_clients) in snapshot.items():
                            unique_clients |= set(adapter_clients)

                        for client in unique_clients:
                            adapter_table.add_column(f"{client}", justify="center")

                        for adapter, (status, adapter_clients) in snapshot.items():
                            status_indicator = "[green3]●" if status else "[red3]●"
                            client_indicators : List[str] = []
                            for client in unique_clients:
                                client_indicators.append("[green3]●[/]" if client in adapter_clients else "[red3]●[/]")        
                            adapter_table.add_row(f'{adapter} {status_indicator}', *client_indicators)                    

                        logger_response : List[str] = cast(List[str], backend_request(self.conn, Action.ENUMERATE_LOGGER_CONNECTIONS)[0])

                        #status_conn = ""
                        #_, sock_address = get_conn_addresses(self.conn)
                        #status_conn = f"{sock_address[0]}:{sock_address[1]}"

                        for connection in logger_response:
                            logger_connections.add_row(connection)
                            # if connection == status_conn:
                            #     logger_connections.add_row(f"[grey50]{connection}[/]")
                            # else:
                            #     logger_connections.add_row(c_string)
                        for _ in range(
                            self.CONNECTIONS_MIN_HEIGHT - len(logger_response)
                        ):
                            logger_connections.add_row("")

                        pid_response : int = cast(int, backend_request(self.conn, Action.GET_PID)[0])
                        pid = str(pid_response)
                    else:
                        backend_status = "[red3]● Offline"
                        pid = ''

                    main_table = Table(box=None, padding=(0, 1))
                    main_table.add_column(justify="right")
                    main_table.add_column(justify="left")
                    main_table.add_row("Status :", backend_status)
                    main_table.add_row("PID :", pid)
                    main_table.add_row("Logger connections :", logger_connections)
                    main_table.add_row(
                        "Adapter connections :",
                        (adapter_table if adapter_table is not None else Text("")),
                    )

                    # Build the console panel
                    with self.console_lock:
                        console_content = "\n".join(self.console_lines) or " "
                    console_panel = Panel(
                        console_content,
                        title="Console",
                        height=self._n_console_lines + 2,  # +2 for panel borders
                        border_style="dim",
                        padding=(0, 1),
                    )

                    # Group the main table and console panel vertically
                    group = Group(main_table, console_panel)
                    live_display.update(group)

                    if self.live_delay is not None:
                        sleep(self.live_delay)
                    else:
                        break
        except KeyboardInterrupt:
            pass

    def _format_record(self, record: logging.LogRecord) -> str:
        color = LOGGING_COLORS.get(record.levelno)
        relative_time = record.created - self._start_time

        line = f"[{color}]{relative_time:7.3f} {record.levelname:<8} {record.msg}[/]"
        if record.name == LoggerAlias.BACKEND.value:
            line = f"[bold]{line}[/bold]"
        return line

    def _add_line_status_screen(self, record: logging.LogRecord) -> None:
        """
        Add a log message to the console buffer, with color formatting by log level.
        Thread-safe.
        """
        formated_text = self._format_record(record)
        with self.console_lock:
            self.console_lines.append(formated_text)
            if len(self.console_lines) > self._n_console_lines:
                self.console_lines = self.console_lines[-self._n_console_lines :]