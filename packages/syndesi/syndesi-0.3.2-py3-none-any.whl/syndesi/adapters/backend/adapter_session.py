# File : backendclient.py
# Author : Sébastien Deriaz
# License : GPL
#
# The backend client manages the link between clients (frontend) and the adapter (backend)
# It is instanctiated by the backend and has a thread to manage incoming data from clients
# as well as read incoming data from the adapter backend

import logging
import threading
import time
from enum import Enum
from multiprocessing.connection import Pipe, wait
from typing import Any, Tuple

from syndesi.adapters.backend.stop_condition_backend import StopConditionBackend
from syndesi.tools.types import NumberLike

from ...tools.backend_api import Action, frontend_send
from ...tools.log_settings import LoggerAlias
from .adapter_backend import (
    AdapterBackend,
    AdapterDisconnected,
    AdapterReadInit,
    AdapterReadPayload,
    Selectable,
)
from .backend_tools import NamedConnection
from .descriptors import (
    Descriptor,
    IPDescriptor,
    SerialPortDescriptor,
    VisaDescriptor,
    adapter_descriptor_by_string,
)
from .ip_backend import IPBackend
from .serialport_backend import SerialPortBackend
#from .stop_condition_backend import stop_condition_from_list
from .visa_backend import VisaBackend



class TimeoutEvent(Enum):
    MONITORING = 0
    ADAPTER = 1
    CONNECTIONS = 2

class TimeoutManager:
    def __init__(self, monitoring_delay : float) -> None:
        self._monitoring_delay = monitoring_delay
        self._timeouts : list[Tuple[TimeoutEvent, float]] = []
        self._monitoring_timestamp = time.time()

    def get_next_timeout(self) -> Tuple[TimeoutEvent, float]:
        t = time.time()
        # Sort the list
        self._timeouts.sort(key = lambda x : x[1], reverse=True)
        # Check if the first element of the list is first or if it's the monitoring timeout
        if len(self._timeouts) > 0 and self._timeouts[0][1] < self._monitoring_timestamp:
            # A timeout is first
            event, timestamp = self._timeouts.pop(0)
            delta = max(0, timestamp - t)
            return event, delta
        else:
            # Monitoring is first
            self._set_next_monitoring_delay()
            delta = max(0, self._monitoring_timestamp - t)
            return TimeoutEvent.MONITORING, delta
        
    def _set_next_monitoring_delay(self):
        t = time.time()
        self._monitoring_timestamp = t + self._monitoring_delay

    def add_timeout_absolute(self, event : TimeoutEvent, timestamp : float):
        self._timeouts.append((event, timestamp))

    def add_timeout_relative(self, event : TimeoutEvent, delay : float):
        self.add_timeout_absolute(event, time.time() + delay)

    def has_event(self, event : TimeoutEvent) -> bool:
        for _event, _ in self._timeouts:
            if _event == event:
                return True
        return False


def get_adapter(descriptor: Descriptor) -> AdapterBackend:
    # The adapter doesn't exist, create it
    if isinstance(
        descriptor, SerialPortDescriptor
    ):  # Add mandatory timeout and stop_condition here ?
        return SerialPortBackend(descriptor=descriptor)
    elif isinstance(descriptor, IPDescriptor):
        return IPBackend(descriptor=descriptor)
    elif isinstance(descriptor, VisaDescriptor):
        return VisaBackend(descriptor=descriptor)
    else:
        raise ValueError(f"Unsupported descriptor : {descriptor}")


class AdapterSession(threading.Thread):
    MONITORING_DELAY = 0.5
    daemon = True
    _shutdown_counter_top: int | None
    _shutdown_counter: int | None

    def __init__(self, adapter_descriptor: str, shutdown_delay: NumberLike | None):
        super().__init__(daemon=True)
        self._logger = logging.getLogger(LoggerAlias.ADAPTER_BACKEND.value)
        self._logger.setLevel("DEBUG")
        self._role = None

        # self._stop_flag = False
        self._connections_lock = threading.Lock()
        # self._connection_condition = threading.Condition(self._connections_lock)

        descriptor = adapter_descriptor_by_string(adapter_descriptor)

        self._adapter: AdapterBackend = get_adapter(descriptor)

        self.connections: list[NamedConnection] = []
        # self.connection_names : Dict[NamedConnection] = {}

        # self._new_connection_r, self._new_connection_w = os.pipe()
        # os.pipe does not work on Windows
        self._new_connection_r, self._new_connection_w = Pipe()

        self._shutdown_delay = shutdown_delay
        if self._shutdown_delay is not None:
            self._shutdown_counter_top = int(
                round(self._shutdown_delay / self.MONITORING_DELAY)
            )
            self._shutdown_counter = self._shutdown_counter_top
        else:
            self._shutdown_counter_top = None
            self._shutdown_counter = None

        #self._timeout_events: list[tuple[TimeoutEvent, float]] = []

        self._timeout_manager = TimeoutManager(self.MONITORING_DELAY)


    def add_connection(self, conn: NamedConnection) -> None:
        with self._connections_lock:
            self.connections.append(conn)
            # os.write(self._new_connection_w, b"\x00")
            self._new_connection_w.send(b"\x00")
            self._logger.info(f"New client : {conn.remote()}")

    def _remove_connection(self, conn: NamedConnection) -> None:
        with self._connections_lock:
            if conn in self.connections:
                conn.conn.close()
                # self.connection_names.pop(id(conn), None)
                self.connections.remove(conn)

    # def _pop_next_timeout_event(self) -> tuple[TimeoutEvent | None, float | None]:
    #     if len(self._timeout_events) > 0:
    #         self._timeout_events.sort(key=lambda x: x[1], reverse=True)
    #         return self._timeout_events.pop(0)
    #     else:
    #         return None, None

    # def _has_timeout_event(self, event: TimeoutEvent) -> bool:
    #     for event, _ in self._timeout_events:
    #         if event == event:
    #             return True
    #     return False

    # def _add_timeout_event(self, event: TimeoutEvent, timestamp: float) -> None:
    #     self._timeout_events.append((event, timestamp))

        # key_timeouts = [
        #     (TimeoutEvent.MONITORING, self._timeout_events[TimeoutEvent.MONITORING]),
        #     (TimeoutEvent.ADAPTER, self._timeout_events[TimeoutEvent.ADAPTER]),
        # ] + list(self._timeout_events[TimeoutEvent.CONNECTIONS].items())

        # key, timeout = None, None
        # for k, t in key_timeouts:
        #     if t is not Ellipsis:
        #         if isinstance(t, float) or isinstance(t, int):
        #             if timeout is None or t < timeout:
        #                 timeout = t
        #                 key = k

        # return key, timeout

    def send(self, conn: NamedConnection, action: Action, *args: Any) -> None:
        if not frontend_send(conn.conn, action, *args):
            self._logger.warning(f"Failed to send to {conn.remote()}")
            self._remove_connection(conn)

    def send_to_all(self, action: Action, *args: Any) -> None:
        for conn in self.connections:
            frontend_send(conn.conn, action, *args)

    def enumerate_connections(self) -> list[str]:
        return [x.remote_address() for x in self.connections]

    def is_adapter_opened(self) -> bool:
        return self._adapter.is_opened()

    def run(self) -> None:

        while True:
            try:
                stop = self.loop()
                if stop:
                    break
            except Exception as e:
                tb = e.__traceback__
                if tb is None:
                    error_message = ""
                else:
                    while tb.tb_next is not None:
                        tb = tb.tb_next
                    _type = type(e)
                    extra_arguments = (str(e),)
                    line_no = tb.tb_lineno
                    frame = tb.tb_frame
                    filename = frame.f_code.co_filename
                    error_message = (
                        f"{_type} : {extra_arguments} {filename}:{line_no}"
                    )


                self._logger.critical(
                    f"Error in {self._adapter.descriptor} session loop : {error_message}"
                )
                try:
                    for conn in self.connections:
                        frontend_send(conn.conn, Action.ERROR_GENERIC, str(e))
                except Exception:
                    break
        self._logger.info(f"Exit {self._adapter.descriptor} session loop")

    def loop(self) -> bool:
        # This is the main loop of the session
        # It listens for the following events :
        # - New client
        #   -> asynchronous from backend
        # - Event on a current client connection
        #   -> listen to conn
        # - Adapter event
        #   -> listen to socket/fd
        # The wait has a timeout set by the adapter, it corresponds to the current continuation/total timeout

        # Create a list of what is awaited
        wait_list: list[Selectable] = [
            conn.conn for conn in self.connections
        ]
        adapter_fd = self._adapter.selectable()
        if adapter_fd is not None and adapter_fd.fileno() >= 0:
            wait_list.append(adapter_fd)

        next_adapter_timeout = self._adapter.get_next_timeout()
        if (
            not self._timeout_manager.has_event(TimeoutEvent.ADAPTER)
            and next_adapter_timeout is not None
        ):
            self._timeout_manager.add_timeout_absolute(TimeoutEvent.ADAPTER, next_adapter_timeout)

        wait_list.append(self._new_connection_r)
        
        # event, timeout_timestamp = self._pop_next_timeout_event()
        # if timeout_timestamp is None:
        #     timeout = None
        # else:
        #     timeout = timeout_timestamp - time.time()
        

#asd
# Probably an infinite wait here that blocks the monitoring
        event, timeout = self._timeout_manager.get_next_timeout()
        ready = wait(wait_list, timeout=timeout)  # type: ignore

        if len(ready) == 0:
            # Timeout event
            if event == TimeoutEvent.MONITORING:
                stop = self._monitor()
                if stop:
                    return True
            elif event == TimeoutEvent.ADAPTER:
                signal = self._adapter.on_timeout_event()
                if signal is not None:
                    # The signal can be none if it has been disabled in the meantime
                    self._logger.debug(f"Adapter signal (timeout) : {signal}")
                    if isinstance(signal, AdapterReadPayload):
                        self.send_to_all(Action.ADAPTER_EVENT_DATA_READY, signal)
                    elif isinstance(signal, AdapterReadInit):
                        self.send_to_all(Action.ADAPTER_EVENT_READ_INIT, signal)
        # Main adapter loop
        if self._new_connection_r in ready:
            # New connection event
            # os.read(self._new_connection_r, 1)
            self._new_connection_r.recv()
        # Adapter event
        if self._adapter.selectable() in ready:
            for signal in self._adapter.on_socket_ready():
                self._logger.debug(f"Adapter signal (selectable) : {signal}")
                if isinstance(signal, AdapterDisconnected):
                    # TODO : Maybe use Action.EVENT only and the signal specifies which one it is
                    self.send_to_all(Action.ADAPTER_EVENT_DISCONNECTED, signal)
                elif isinstance(signal, AdapterReadInit):
                    self.send_to_all(Action.ADAPTER_EVENT_READ_INIT, signal)
                elif isinstance(signal, AdapterReadPayload):
                    self.send_to_all(Action.ADAPTER_EVENT_DATA_READY, signal)

        for conn in self.connections:
            if conn.conn in ready:
                # Manage a command received from the user
                self.manage_conn(conn)
        return False

    def _monitor(self) -> bool:
        stop = False
        if self._shutdown_counter is not None:
            with self._connections_lock:
                if len(self.connections) == 0:
                    if self._shutdown_counter == 0:
                        # Shutdown
                        self._logger.info(
                            f"No clients on adapter {self._adapter.descriptor} for {self._shutdown_delay}s, closing"
                        )
                        self._adapter.close()
                        stop = True
                    else:
                        self._shutdown_counter -= 1
                else:
                    self._shutdown_counter = self._shutdown_counter_top

        return stop

    def manage_conn(self, conn: NamedConnection) -> None:
        extra_arguments: tuple[Any, ...]
        remove_after_response = False
        if not conn.conn.poll():
            # No data, connection is closed
            self._logger.warning(f"Client {conn.remote()} closed unexpectedly")
            self._remove_connection(conn)
            return
        try:
            request = conn.conn.recv()
            request_timestamp = time.time()
        except (EOFError, ConnectionResetError) as e:
            # Probably a ping or an error
            self._logger.warning(
                f"Failed to read from client {conn.remote()} ({e}), closing connection "
            )
            self._remove_connection(conn)
        else:
            if not (isinstance(request, tuple) and len(request) >= 1):
                response_action = Action.ERROR_INVALID_REQUEST
                extra_arguments = ("",)
            else:
                action: Action
                action = Action(request[0])
                response_action = Action.ERROR_GENERIC
                extra_arguments = ("Unknown error in session",)
                try:
                    match action:
                        case Action.OPEN:
                            self._adapter.set_stop_conditions(
                                [StopConditionBackend(sc) for sc in request[1]]
                            )
                            if self._adapter.open():
                                # Success !
                                response_action = Action.OPEN
                            else:
                                response_action = Action.ERROR_FAILED_TO_OPEN
                            extra_arguments = ("",)
                        case Action.FORCE_CLOSE:
                            self._adapter.close()
                            remove_after_response = True
                            response_action, extra_arguments = Action.FORCE_CLOSE, ()
                        case Action.WRITE:
                            data = request[1]
                            if self._adapter.is_opened():
                                if self._adapter.write(data):
                                    # Success
                                    response_action, extra_arguments = Action.WRITE, ()
                                else:
                                    response_action, extra_arguments = (
                                        Action.ERROR_ADAPTER_DISCONNECTED,
                                        ("",),
                                    )
                                    # TODO : Maybe close here ? not sure
                            else:
                                response_action, extra_arguments = (
                                    Action.ERROR_ADAPTER_NOT_OPENED,
                                    ("Open adapter before writing",),
                                )
                                self._logger.error("Could not write, adapter is closed")
                        case Action.PING:
                            response_action, extra_arguments = Action.PING, ()
                        case Action.SET_STOP_CONDITION:
                            stop_conditions = stop_conditions_to_backends(request[1])
                            self._adapter.set_stop_conditions(stop_conditions)
                            response_action, extra_arguments = (
                                Action.SET_STOP_CONDITION,
                                (),
                            )
                        case Action.FLUSHREAD:
                            self._adapter.flush_read()
                            response_action, extra_arguments = Action.FLUSHREAD, ()
                        # case Action.START_READ:
                        #     response_time = float(request[1])
                        #     uuid = request[2]
                        #     self._adapter.start_read(response_time, uuid)
                        #     response_action, extra_arguments = Action.START_READ, ()
                        case Action.GET_BACKEND_TIME:
                            response_action = Action.GET_BACKEND_TIME
                            extra_arguments = (request_timestamp, )
                        case Action.CLOSE:
                            # Close this connection
                            remove_after_response = True
                            response_action, extra_arguments = Action.CLOSE, ()
                        case _:
                            response_action, extra_arguments = (
                                Action.ERROR_UNKNOWN_ACTION,
                                (f"{action}",),
                            )
                except Exception as e:
                    tb = e.__traceback__
                    if tb is None:
                        error_message = ""
                    else:
                        while tb.tb_next is not None:
                            tb = tb.tb_next
                        _type = type(e)
                        extra_arguments = (str(e),)
                        line_no = tb.tb_lineno
                        frame = tb.tb_frame
                        filename = frame.f_code.co_filename
                        error_message = (
                            f"{_type} : {extra_arguments} {filename}:{line_no}"
                        )

                    response_action, extra_arguments = (
                        Action.ERROR_GENERIC,
                        (error_message,),
                    )

            frontend_send(conn.conn, response_action, *extra_arguments)
            if remove_after_response:
                self._logger.info(f"Closing client {conn.remote()} connection")
                self._remove_connection(conn)
