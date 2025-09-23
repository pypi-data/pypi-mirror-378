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

from enum import Enum
import logging
import queue
import subprocess
import sys
import threading
import time
import uuid
import weakref
from abc import ABC, abstractmethod
from collections.abc import Callable
from multiprocessing.connection import Client, Connection
from types import EllipsisType
from typing import Any, cast
import os

from .backend.backend_tools import BACKEND_REQUEST_DEFAULT_TIMEOUT
from syndesi.tools.types import NumberLike, is_number

from ..tools.backend_api import (
    BACKEND_PORT,
    Action,
    BackendResponse,
    default_host,
    is_event,
    raise_if_error,
)
from ..tools.log_settings import LoggerAlias
from .backend.adapter_backend import (
    AdapterDisconnected,
    AdapterReadInit,
    AdapterReadPayload,
    AdapterSignal,
)
from .backend.descriptors import Descriptor
from .stop_condition import StopCondition, TimeoutStopCondition
from .timeout import Timeout, TimeoutAction, any_to_timeout

DEFAULT_STOP_CONDITION = [TimeoutStopCondition(continuation=0.1)]

DEFAULT_TIMEOUT = Timeout(response=5, action='error')

SHUTDOWN_DELAY = 2

# Maximum time to let the backend start
START_TIMEOUT = 2

# from enum import Enum, auto


# class CallbackEvent(Enum):
#     DATA_READY = auto()
#     ADAPTER_DISCONNECTED = auto()

import time
import queue
from typing import TypeVar, Generic

T = TypeVar("T")

class PeekQueue(queue.Queue, Generic[T]):
    def peek(self, block: bool = True, timeout: float | None = None) -> T:
        """
        Return (without removing) the head item.

        Args:
            block: If False, raise queue.Empty immediately if empty.
            timeout: Max seconds to wait if block=True. None means wait forever.

        Raises:
            queue.Empty: if no item is available within constraints.
        """
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise queue.Empty
                return self.queue[0]  # type: ignore[attr-defined]

            end = None if timeout is None else time.monotonic() + timeout
            while not self._qsize():
                if timeout is None:
                    self.not_empty.wait()
                else:
                    remaining = end - time.monotonic()
                    if remaining <= 0:
                        raise queue.Empty
                    self.not_empty.wait(remaining)

            return self.queue[0]  # type: ignore[attr-defined]


def is_backend_running(address: str, port: int) -> bool:

    try:
        conn = Client((address, port))
    except ConnectionRefusedError:
        return False
    else:
        conn.close()
        return True

def start_backend(port: int | None = None) -> None:
    arguments = [
            sys.executable,
            "-m",
            "syndesi.adapters.backend.backend",
            "-s",
            str(SHUTDOWN_DELAY),
            "-q",
            "-p",
            str(BACKEND_PORT if port is None else port),
        ]
    
    # Always sever stdio — if you leave any of these inherited,
    # you can keep an implicit console/TTY attachment.
    stdin  = subprocess.DEVNULL
    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL

    if os.name == "posix":
        # New session == new process group, no longer the terminal's foreground PG.
        # This prevents keyboard SIGINT/SIGTSTP from the parent's TTY.
        subprocess.Popen(
            arguments,
            # cwd=None,
            # env=None,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,   # safer than preexec_fn=os.setsid in threaded parents
            close_fds=True,           # ensure we don't leak any FDs that tie us to the parent
        )

    else:
        # Windows: detach from the parent's console so keyboard Ctrl+C won't propagate.
        CREATE_NEW_PROCESS_GROUP = subprocess.CREATE_NEW_PROCESS_GROUP
        DETACHED_PROCESS = 0x00000008          # not exposed by subprocess on all Pythons
        # Optional: CREATE_NO_WINDOW (no window even for console apps)
        CREATE_NO_WINDOW = 0x08000000

        creationflags = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS | CREATE_NO_WINDOW

        subprocess.Popen(
            arguments,
            # cwd=cwd,
            # env=env,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
            close_fds=True,  # break handle inheritance (important with DETACHED_PROCESS)
        )

class ReadScope(Enum):
    NEXT = 'next'
    BUFFERED = 'buffered'

class Adapter(ABC):
    def __init__(
        self,
        descriptor: Descriptor,
        alias: str = "",
        stop_conditions: StopCondition | EllipsisType | list = ...,
        timeout: Timeout | EllipsisType | NumberLike | None = ...,
        encoding: str = "utf-8",
        event_callback: Callable[[AdapterSignal], None] | None = None,
        auto_open: bool = True,
        backend_address: str | None = None,
        backend_port: int | None = None,
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
        self._event_queue: PeekQueue[BackendResponse] = PeekQueue()
        self.event_callback: Callable[[AdapterSignal], None] | None = event_callback
        self.backend_connection: Connection | None = None
        self._backend_connection_lock = threading.Lock()
        self._make_backend_request_queue: queue.Queue[BackendResponse] = queue.Queue()
        self._make_backend_request_flag = threading.Event()
        self.opened = False
        self._alias = alias
        self._read_buffer = []

        if backend_address is None:
            self._backend_address = default_host
        else:
            self._backend_address = backend_address
        if backend_port is None:
            self._backend_port = BACKEND_PORT
        else:
            self._backend_port = backend_port

        # There a two possibilities here
        # A) The descriptor is fully initialized
        #    -> The adapter can be connected directly
        # B) The descriptor is not fully initialized
        #    -> Wait for the protocol to set defaults and then connect the adapter

        assert isinstance(
            descriptor, Descriptor
        ), "descriptor must be a Descriptor class"
        self.descriptor = descriptor
        self.auto_open = auto_open

        # Set the stop-condition
        self._stop_conditions: list[StopCondition | None]
        if stop_conditions is ...:
            self._default_stop_condition = True
            self._stop_conditions = DEFAULT_STOP_CONDITION
        else:
            self._default_stop_condition = False
            if isinstance(stop_conditions, StopCondition):
                self._stop_conditions = [stop_conditions]
            elif isinstance(stop_conditions, list):
                self._stop_conditions = stop_conditions
            else:
                raise ValueError('Invalid stop_conditions')

        # Set the timeout
        self.is_default_timeout = False
        self._timeout: Timeout | None
        if timeout is Ellipsis:
            # Not set
            self.is_default_timeout = True
            self._timeout = DEFAULT_TIMEOUT
        elif isinstance(timeout, Timeout):
            self._timeout = timeout
        elif is_number(timeout):
            self._timeout = Timeout(timeout, action=TimeoutAction.ERROR)
        elif timeout is None:
            self._timeout = timeout

        # Buffer for data that has been pulled from the queue but
        # not used because of termination or length stop condition
        self._previous_buffer = b""

        if self.descriptor.is_initialized():
            self.connect()

        weakref.finalize(self, self._cleanup)
        self._init_ok = True

        # We can auto-open only if auto_open is enabled and if
        # connection with the backend has been made (descriptor initialized)
        if self.auto_open and self.backend_connection is not None:
            self.open()

    def connect(self) -> None:
        if self.backend_connection is not None:
            # No need to connect, everything has been done already
            return
        if not self.descriptor.is_initialized():
            raise RuntimeError("Descriptor wasn't initialized fully")

        if is_backend_running(self._backend_address, self._backend_port):
            self._logger.info("Backend already running")
        else:
            self._logger.info("Starting backend...")
            start_backend(self._backend_port)
            start = time.time()
            while time.time() < (start + START_TIMEOUT):
                if is_backend_running(self._backend_address, self._backend_port):
                    self._logger.info("Backend started")
                    break
                time.sleep(0.1)
            else:
                # Backend could not start
                self._logger.error("Could not start backend")

        # Create the client to communicate with the backend
        try:
            self.backend_connection = Client((default_host, BACKEND_PORT))
        except ConnectionRefusedError as err:
            raise RuntimeError("Failed to connect to backend") from err
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

        if self.auto_open:
            self.open()

    def _make_backend_request(self, action: Action, *args: Any) -> BackendResponse:
        """
        Send a request to the backend and return the arguments
        """

        with self._backend_connection_lock:
            if self.backend_connection is not None:
                self.backend_connection.send((action.value, *args))

        self._make_backend_request_flag.set()
        try:
            response = self._make_backend_request_queue.get(
                timeout=BACKEND_REQUEST_DEFAULT_TIMEOUT
            )
        except queue.Empty as err:
            raise RuntimeError(
                f"Failed to receive response from backend to {action}"
            ) from err

        assert (
            isinstance(response, tuple) and len(response) > 0
        ), f"Invalid response received from backend : {response}"
        raise_if_error(response)

        return response[1:]

    def read_thread(
        self,
        event_queue: queue.Queue[BackendResponse],
        request_queue: queue.Queue[BackendResponse],
    ) -> None:
        while True:
            try:
                if self.backend_connection is None:
                    raise RuntimeError("Backend connection wasn't initialized")
                response: tuple[Any, ...] = self.backend_connection.recv()
            except (EOFError, TypeError, OSError):
                event_queue.put((Action.ERROR_BACKEND_DISCONNECTED,))
                request_queue.put((Action.ERROR_BACKEND_DISCONNECTED,))
                break
            else:
                if not isinstance(response, tuple):
                    raise RuntimeError(f"Invalid response from backend : {response}")
                action = Action(response[0])

                if is_event(action):
                    if len(response) <= 1:
                        raise RuntimeError(f"Invalid event response : {response}")
                    if self.event_callback is not None:
                        signal: AdapterSignal = response[1]
                        self.event_callback(signal)
                    event_queue.put(response)
                else:
                    request_queue.put(response)

    @abstractmethod
    def _default_timeout(self) -> Timeout:
        pass

    def set_timeout(self, timeout: Timeout | None) -> None:
        """
        Overwrite timeout

        Parameters
        ----------
        timeout : Timeout
        """
        self._timeout = timeout

    def set_default_timeout(self, default_timeout: Timeout | None) -> None:
        """
        Set the default timeout for this adapter. If a previous timeout has been set, it will be fused

        Parameters
        ----------
        default_timeout : Timeout or tuple or float
        """
        if self.is_default_timeout:
            self._logger.debug(f"Setting default timeout to {default_timeout}")
            self._timeout = default_timeout

    def set_stop_conditions(self, stop_conditions: StopCondition | None | list) -> None:
        """
        Overwrite the stop-condition

        Parameters
        ----------
        stop_condition : StopCondition
        """
        if isinstance(stop_conditions, list):
            self._stop_conditions = stop_conditions
        elif isinstance(stop_conditions, StopCondition):
            self._stop_conditions = [stop_conditions]
        elif stop_conditions is None:
            self._stop_conditions = []

        # if self._stop_conditions is None:
        #     payload = None
        # else:
        #     payload = self._stop_conditions.compose_json()
        self._make_backend_request(Action.SET_STOP_CONDITION, self._stop_conditions)

    def set_default_stop_condition(self, stop_condition: StopCondition) -> None:
        """
        Set the default stop condition for this adapter.

        Parameters
        ----------
        stop_condition : StopCondition
        """
        if self._default_stop_condition:
            self.set_stop_conditions(stop_condition)

    def flushRead(self) -> None:
        """
        Flush the input buffer
        """
        self._make_backend_request(
            Action.FLUSHREAD,
        )
        while True:
            try:
                self._event_queue.get(block=False)
            except queue.Empty:
                break
            

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
        self._make_backend_request(Action.OPEN, self._stop_conditions)
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
            if self.backend_connection is not None:
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

    def read_detailed(
        self,
        timeout: Timeout | EllipsisType | None = ...,
        stop_condition: StopCondition | EllipsisType | None = ...,
        scope : str = ReadScope.BUFFERED.value,
    ) -> tuple[bytes, AdapterReadPayload | None]:
        """
        Read data from the device

        Parameters
        ----------
        timeout : tuple, Timeout
            Temporary timeout
        stop_condition : StopCondition
            Temporary stop condition
        scope : str
            Return previous data ('buffered') or only future data ('next')
        Returns
        -------
        data : bytes
        signal : AdapterReadPayload
        """
        _scope = ReadScope(scope)
        # Okay idea : Remove the start read and instead ask for the time of the backend.
        # Then we read whatever payload comes from the backend and compare that to the time
        # If it doesn't match our criteria, we trash it
        # When waiting for the backend payload, we wait +0.5s so make sure we received everything
        # This 0.5s could be changed if we're local or not by the way


        # First, ask for the backend time, this is the official start of the read 
        backend_read_start_time = cast(NumberLike, self._make_backend_request(Action.GET_BACKEND_TIME)[0])

        # If not timeout is specified, use the default one
        if timeout is ...:
            read_timeout = self._timeout
        else:
            read_timeout = any_to_timeout(timeout)

        if read_timeout is not None:
            if not read_timeout.is_initialized():
                raise RuntimeError("Timeout needs to be initialized")

        # Calculate last_valid_timestamp, the limit at which a payload is not accepted anymore
        # Calculate the queue timeout (time for a response + small delay)
        #last_valid_timestamp = None
        queue_timeout_timestamp = None
        if read_timeout is not None:
            response_delay = read_timeout.response()
        else:
            response_delay = None

        if response_delay is not None:
            #last_valid_timestamp = backend_read_start_time + response_delay
            queue_timeout_timestamp = time.time() + response_delay + BACKEND_REQUEST_DEFAULT_TIMEOUT

        output_signal : AdapterReadPayload | None

        # Ready to read payloads
        while True:
            if queue_timeout_timestamp is None:
                queue_timeout = None
            else:
                queue_timeout = queue_timeout_timestamp - time.time()
                if queue_timeout < 0:
                    queue_timeout = 0

            try:
                response = self._event_queue.peek(block=True, timeout=queue_timeout)
                signal = response[1]

                if isinstance(signal, AdapterReadPayload):
                    if response_delay is not None and signal.response_timestamp - backend_read_start_time > response_delay:
                        # This signal happened after the max response time, act as if a timeout occured
                        # and do not pop it out of the queue
                        # TODO : Make _timeout always Timeout, never None ?
                        output_signal = None
                        break

                    if _scope == ReadScope.NEXT and signal.response_timestamp < backend_read_start_time:
                        # The payload happened before the read start
                        self._event_queue.get()
                        continue

                    if response_delay is not None:
                        if signal.response_timestamp - backend_read_start_time > response_delay:
                            self._event_queue.get()
                            output_signal = None
                            break
                    
                    # Other wise the payload is valid
                    self._event_queue.get()
                    output_signal = signal
                    break

                elif isinstance(signal, AdapterDisconnected):
                    self._event_queue.get()
                    raise RuntimeError("Adapter disconnected")

            except queue.Empty:
                output_signal = None
                break    



        if output_signal is None:
            # TODO : Make _timeout always Timeout, never None ?
            if read_timeout.action == TimeoutAction.RETURN:
                data = b""
                output_signal = None
            elif read_timeout.action == TimeoutAction.ERROR:
                raise TimeoutError(
                    f"No response received from device within {read_timeout.response()} seconds"
                )
        else:
            data = output_signal.data()
            output_signal.response_delay = output_signal.response_timestamp - backend_read_start_time

        
        return data, output_signal

    def read(
        self,
        timeout: Timeout | EllipsisType | None = ...,
        stop_condition: StopCondition | EllipsisType | None = ...,
    ) -> bytes:
        return self.read_detailed(timeout=timeout, stop_condition=stop_condition)[0]

    def _cleanup(self) -> None:
        if self._init_ok and self.opened:
            self.close()

    def query_detailed(
        self,
        data: bytes | str,
        timeout: Timeout | EllipsisType | None = ...,
        stop_condition: StopCondition | EllipsisType | None = ...,
    ) -> tuple[bytes, AdapterReadPayload | None]:
        """
        Shortcut function that combines
        - flush_read
        - write
        - read
        """
        self.flushRead()
        self.write(data)
        return self.read_detailed(timeout=timeout, stop_condition=stop_condition)

    def query(
        self,
        data: bytes | str,
        timeout: Timeout | EllipsisType | None = ...,
        stop_condition: StopCondition | EllipsisType | None = ...,
    ) -> bytes:
        return self.query_detailed(
            data=data, timeout=timeout, stop_condition=stop_condition
        )[0]

    def set_event_callback(self, callback: Callable[[AdapterSignal], None]) -> None:
        self.event_callback = callback

    def __str__(self) -> str:
        return str(self.descriptor)

    def __repr__(self) -> str:
        return self.__str__()
