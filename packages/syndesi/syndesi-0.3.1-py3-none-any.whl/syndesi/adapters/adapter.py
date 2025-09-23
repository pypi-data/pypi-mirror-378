# File : adapters.py
# Author : Sébastien Deriaz
# License : GPL
#
# Adapters provide a common abstraction for the media layers (physical + data link + network)
# The following classes are provided, which all are derived from the main Adapter class
#   - IP
#   - Serial
#   - VISA
#
# Note that technically VISA is not part of the media layer, only USB is.
# This is a limitation as it is to this day not possible to communicate "raw"
# with a device through USB yet
#
# An adapter is meant to work with bytes objects but it can accept strings.
# Strings will automatically be converted to bytes using utf-8 encoding

import logging
import queue
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Literal, Optional, Tuple, Union, overload
import uuid
import weakref
from abc import ABC, abstractmethod
from multiprocessing.connection import Client

from syndesi.tools.types import DEFAULT, DefaultType, NumberLike, is_number

from ..tools.backend_api import BACKEND_PORT, Action, BackendResponse, _default_host, is_event
from ..tools.log_settings import LoggerAlias
from .backend.adapter_backend import AdapterDisconnected, AdapterReadInit, AdapterReadPayload, AdapterSignal
from .stop_condition import StopCondition, TimeoutStopCondition
from .timeout import Timeout, TimeoutAction, any_to_timeout

DEFAULT_STOP_CONDITION = TimeoutStopCondition(continuation=0.1)

DEFAULT_TIMEOUT = 5

SHUTDOWN_DELAY = 2

# Maximum time to let the backend start
START_TIMEOUT = 2

#from enum import Enum, auto

from ..tools.backend_api import raise_if_error
from .backend.descriptors import Descriptor


# class CallbackEvent(Enum):
#     DATA_READY = auto()
#     ADAPTER_DISCONNECTED = auto()


def is_backend_running(address : Optional[str] = None, port : Optional[int] = None) -> bool:

    try:
        conn = Client((
            _default_host if address is None else address,
            BACKEND_PORT if port is None else port
            ))
    except ConnectionRefusedError:
        return False
    else:
        conn.close()
        return True


def start_backend(port : Optional[int] = None) -> None:
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "syndesi.adapters.backend.backend",
            "-s",
            str(SHUTDOWN_DELAY),
            "-q",
            "-p",
            str(BACKEND_PORT if port is None else port)
        ]
    )


class Adapter(ABC):
    ADDITIONNAL_RESPONSE_DELAY = 1
    BACKEND_REQUEST_DEFAULT_TIMEOUT = 1

    def __init__(
        self,
        descriptor: Descriptor,
        alias: str = "",
        stop_condition: Optional[Union[StopCondition, DefaultType]] = DEFAULT,
        timeout: Optional[Union[Timeout, DefaultType, NumberLike]] = DEFAULT,
        encoding: str = "utf-8",
        event_callback : Optional[Callable[[AdapterSignal], None]] = None,
        auto_open : bool = True,
        backend_address : Optional[str] = None,
        backend_port : Optional[int] = None
    ) -> None:
        """
        Adapter instance

        Parameters
        ----------
        alias : str
            The alias is used to identify the class in the logs
        timeout : float or Timeout instance
            Default timeout is
        stop_condition : StopCondition or None
            Default to None
        encoding : str
            Which encoding to use if str has to be encoded into bytes
        """
        self._init_ok = False
        super().__init__()
        self._logger = logging.getLogger(LoggerAlias.ADAPTER.value)
        self.encoding = encoding
        self._event_queue : queue.Queue[BackendResponse] = queue.Queue()
        self.event_callback : Optional[Callable[[AdapterSignal], None]] = event_callback
        self._backend_connection_lock = threading.Lock()
        self._make_backend_request_queue : queue.Queue[BackendResponse] = queue.Queue()
        self._make_backend_request_flag = threading.Event()
        self.opened = False

        if is_backend_running(backend_address, backend_port):
            self._logger.info("Backend already running")
        elif backend_address is not None:
            raise RuntimeError(f"Cannot connect to backend {backend_address}")
        else:
            self._logger.info("Starting backend...")
            start_backend(backend_port)
            start = time.time()
            while time.time() < (start + START_TIMEOUT):
                if is_backend_running():
                    self._logger.info("Backend started")
                    break
                time.sleep(0.1)
            else:
                # Backend could not start
                self._logger.error("Could not start backend")

        assert isinstance(
            descriptor, Descriptor
        ), "descriptor must be a Descriptor class"
        self.descriptor = descriptor

        # Open the connection with the backend
        try:
            self.backend_connection = Client((_default_host, BACKEND_PORT))
        except ConnectionRefusedError:
            raise RuntimeError("Failed to connect to backend")
        self._read_thread = threading.Thread(
            target=self.read_thread,
            args=(self._event_queue, self._make_backend_request_queue),
            daemon=True,
        )
        self._read_thread.start()

        # Identify ourselves
        self._make_backend_request(Action.SET_ROLE_ADAPTER)

        # Set the adapter
        self._make_backend_request(Action.SELECT_ADAPTER, str(self.descriptor))

        self._alias = alias

        # Set the timeout
        self.is_default_timeout = False
        self._timeout : Optional[Timeout]
        if timeout is Ellipsis:
            # Not set
            self.is_default_timeout = True
        elif isinstance(timeout, Timeout):
            self._timeout = timeout
        elif is_number(timeout):
            self._timeout = Timeout(timeout, action=TimeoutAction.ERROR)
        elif timeout is None:
            self._timeout = timeout


        # Set the stop-condition
        self._stop_condition : Optional[StopCondition]
        if stop_condition is DEFAULT:
            self._default_stop_condition = True
            self._stop_condition = DEFAULT_STOP_CONDITION
        else:
            self._default_stop_condition = False
            self._stop_condition = stop_condition

        # Buffer for data that has been pulled from the queue but
        # not used because of termination or length stop condition
        self._previous_buffer = b""

        weakref.finalize(self, self._cleanup)
        self._init_ok = True
        self.auto_open = auto_open
        if auto_open:
            self.open()

    def _make_backend_request(self, action: Action, *args : Any) -> BackendResponse:
        """
        Send a request to the backend and return the arguments
        """

        with self._backend_connection_lock:
            self.backend_connection.send((action.value, *args))

        self._make_backend_request_flag.set()
        try:
            response = self._make_backend_request_queue.get(
                timeout=self.BACKEND_REQUEST_DEFAULT_TIMEOUT
            )
        except queue.Empty:
            raise RuntimeError(f"Failed to receive response from backend to {action}")

        assert (
            isinstance(response, tuple) and len(response) > 0
        ), f"Invalid response received from backend : {response}"
        raise_if_error(response)

        return response[1:]

    def read_thread(self, event_queue: queue.Queue[BackendResponse], request_queue: queue.Queue[BackendResponse]) -> None:
        while True:
            try:
                response : Tuple[Any,...] = self.backend_connection.recv()
            except (EOFError, TypeError, OSError):
                event_queue.put((Action.ERROR_BACKEND_DISCONNECTED,))
                request_queue.put((Action.ERROR_BACKEND_DISCONNECTED,))
            else:
                if not isinstance(response, tuple):
                    raise RuntimeError(f"Invalid response from backend : {response}")
                action = Action(response[0])

                if is_event(action):
                    if self.event_callback is not None:
                        signal : AdapterSignal = response[1]
                        self.event_callback(signal)
                    event_queue.put(response)
                else:
                    request_queue.put(response)

    @abstractmethod
    def _default_timeout(self) -> Timeout:
        pass

    def set_timeout(self, timeout: Optional[Timeout]) -> None:
        """
        Overwrite timeout

        Parameters
        ----------
        timeout : Timeout
        """
        self._timeout = timeout

    def set_default_timeout(self, default_timeout: Optional[Timeout]) -> None:
        """
        Set the default timeout for this adapter. If a previous timeout has been set, it will be fused

        Parameters
        ----------
        default_timeout : Timeout or tuple or float
        """
        if self.is_default_timeout:
            self._logger.debug(f"Setting default timeout to {default_timeout}")
            self._timeout = default_timeout

    def set_stop_condition(self, stop_condition: Optional[StopCondition]) -> None:
        """
        Overwrite the stop-condition

        Parameters
        ----------
        stop_condition : StopCondition
        """
        self._stop_condition = stop_condition
        #payload : Optional[str]
        if self._stop_condition is None:
            payload = None
        else:
            payload = self._stop_condition.compose_json()
        self._make_backend_request(
            Action.SET_STOP_CONDITION, payload
        )

    def set_default_stop_condition(self, stop_condition : StopCondition) -> None:
        """
        Set the default stop condition for this adapter.

        Parameters
        ----------
        stop_condition : StopCondition
        """
        if self._default_stop_condition:
            self.set_stop_condition(stop_condition)

    def flushRead(self) -> None:
        """
        Flush the input buffer
        """
        self._make_backend_request(
            Action.FLUSHREAD,
        )

    def previous_read_buffer_empty(self) -> bool:
        """
        Check whether the previous read buffer is empty

        Returns
        -------
        empty : bool
        """
        return self._previous_buffer == b""

    def open(self) -> None:
        """
        Start communication with the device
        """
        if self._stop_condition is None:
            payload = None
        else:
            payload = self._stop_condition.compose_json()
        self._make_backend_request(
            Action.OPEN,
            payload
        )
        self._logger.info("Adapter opened")
        self.opened = True

    def close(self, force: bool = False) -> None:
        """
        Stop communication with the device
        """
        self._logger.debug("Closing adapter frontend")
        self._make_backend_request(Action.CLOSE)
        if force:
            self._logger.debug("Force closing adapter backend")
            self._make_backend_request(Action.FORCE_CLOSE)

        with self._backend_connection_lock:
            self.backend_connection.close()

        self.opened = False

    def write(self, data: bytes | str) -> None:
        """
        Send data to the device

        Parameters
        ----------
        data : bytes or str
        """

        if isinstance(data, str):
            data = data.encode(self.encoding)
        self._make_backend_request(Action.WRITE, data)
    
    @overload
    def read( #type: ignore (default arguments mess everything up)
        self,
        timeout: Union[Timeout, DefaultType, None] = DEFAULT,
        stop_condition: Union[StopCondition, DefaultType, None] = DEFAULT,
        full_output: Literal[True] = True,
    ) -> Tuple[bytes, AdapterSignal]: ...

    @overload
    def read(
        self,
        timeout: Union[Timeout, DefaultType, None] = DEFAULT,
        stop_condition: Union[StopCondition, DefaultType, None] = DEFAULT,
        full_output: Literal[False] = False,
    ) -> bytes: ...
    
    def read(
        self,
        timeout: Union[None, Timeout, DefaultType] = DEFAULT,
        stop_condition: Optional[Union[StopCondition, DefaultType]] = DEFAULT,
        full_output: bool = False,
    ) -> Union[bytes, Tuple[bytes, AdapterSignal]]:
        """
        Read data from the device

        Parameters
        ----------
        timeout : tuple, Timeout
            Temporary timeout
        stop_condition : StopCondition
            Temporary stop condition
        full_output : bool
            If True, return read information as well as data
        Returns
        -------
        data : bytes
        metrics : dict
            Only if full_output is True
        """
            
        if timeout is DEFAULT:
            read_timeout = self._timeout
        else:
            read_timeout = any_to_timeout(timeout)

        output = None

        response_received = False

        if read_timeout is None:
            queue_timeout_timestamp = None
        elif read_timeout.response is None:
            queue_timeout_timestamp = None
        else:
            if read_timeout.response is DEFAULT:
                raise RuntimeError('Timeout needs to be initialized')
            
            queue_timeout_timestamp = (
                time.time() + read_timeout.response + self.ADDITIONNAL_RESPONSE_DELAY
            )

        start_read_uuid = uuid.uuid1()
        # Send a read signal to the backend
        self._make_backend_request(
            Action.START_READ,
            read_timeout.response if read_timeout is not None else None,
            start_read_uuid
        )

        while True:
            if queue_timeout_timestamp is None or response_received:
                queue_timeout = None
            else:
                queue_timeout = queue_timeout_timestamp - time.time()
                if queue_timeout < 0:
                    queue_timeout = 0

            try:
                response = self._event_queue.get(block=True, timeout=queue_timeout)
                signal = response[1]
            except queue.Empty:
                raise RuntimeError(
                    "Failed to receive response confirmation from backend"
                )
            else:
                if isinstance(signal, AdapterReadPayload):
                    if response_received:
                        output = signal.data()
                        break
                elif isinstance(signal, AdapterReadInit):
                    #signal: AdapterReadInit = response[1]
                    # Check if it's the right read_init with the uuid, otherwise ignore it
                    if signal.uuid == start_read_uuid:
                        if signal.received_response_in_time:
                            response_received = True
                        else:
                            if self._timeout is None:
                                raise RuntimeError('Failed to receive data in time but timeout is None')
                            else:
                                if self._timeout.action == TimeoutAction.RETURN:
                                    output = b""
                                    break
                                elif self._timeout.action == TimeoutAction.ERROR:
                                    raise TimeoutError(
                                        f"No response received from device within {self._timeout.response} seconds"
                                    )
                elif isinstance(signal, AdapterDisconnected):
                    raise RuntimeError("Adapter disconnected")

        if full_output:
            return output, signal
        else:
            return output

    def _cleanup(self) -> None:
        if self._init_ok and self.opened:
            self.close()

    @overload
    def query(
        self,
        data: Union[bytes, str],
        timeout: Optional[Union[Timeout, DefaultType]] = DEFAULT,
        stop_condition: Optional[Union[StopCondition, DefaultType]] = DEFAULT,
        full_output: Literal[True] = True,
    ) -> Tuple[bytes, AdapterSignal]: ...
    @overload
    def query(
        self,
        data: Union[bytes, str],
        timeout: Optional[Union[Timeout, DefaultType]] = DEFAULT,
        stop_condition: Optional[Union[StopCondition, DefaultType]] = DEFAULT,
        full_output: Literal[False] = False,
    ) -> bytes: ...
    
    def query(
        self,
        data: Union[bytes, str],
        timeout: Optional[Union[Timeout, DefaultType]] = DEFAULT,
        stop_condition: Optional[Union[StopCondition, DefaultType]] = DEFAULT,
        full_output: bool = False,
    ) -> Union[bytes, Tuple[bytes, AdapterSignal]]:
        """
        Shortcut function that combines
        - flush_read
        - write
        - read
        """
        self.flushRead()
        self.write(data)
        output, signal = self.read(
            timeout=timeout, stop_condition=stop_condition, full_output=True
        )

        if full_output:
            return output, signal
        else:
            return output

    def set_event_callback(self, callback : Callable[[AdapterSignal], None]) -> None:
        self.event_callback = callback

    def __str__(self) -> str:
        return str(self.descriptor)

    def __repr__(self) -> str:
        return self.__str__()
