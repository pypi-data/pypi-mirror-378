# File : visa.py
# Author : Sébastien Deriaz
# License : GPL
#
# The VISA backend communicates with using pyvisa


import queue
import socket
import threading
import time
from typing import List, Optional
from typing_extensions import Self  # 3.10/3.9

from pyvisa import ResourceManager, VisaIOError
from pyvisa.errors import InvalidSession
from pyvisa.resources import Resource

from ...tools.backend_api import AdapterBackendStatus, Fragment
from .adapter_backend import AdapterBackend, AdapterDisconnected, AdapterSignal, HasFileno, Selectable
from .descriptors import VisaDescriptor


class VisaBackend(AdapterBackend):
    def __init__(self, descriptor: VisaDescriptor):
        """
        USB VISA stack adapter

        Parameters
        ----------
        resource : str
            resource address string
        """
        super().__init__(
            descriptor=descriptor,
        )
        self.descriptor : VisaDescriptor

        self._rm = ResourceManager()
        self._inst: Optional[Resource] = None

        # We need a socket pair because VISA doesn't expose a selectable fileno/socket
        # So we create a thread to read data and push that to the socket
        self._notify_recv, self._notify_send = socket.socketpair()
        self._notify_recv.setblocking(False)
        self._notify_send.setblocking(False)

        self._stop_lock = threading.Lock()
        self.stop = False

        self._fragment_lock = threading.Lock()
        self._fragment = Fragment(b"", None)
        self._event_queue : queue.Queue[AdapterSignal] = queue.Queue()

        # self._logger.info(f'Setting up VISA adapter {}')

    @classmethod
    def list_devices(cls: type[Self]) -> list[str]:
        """
        Returns a list of available VISA devices
        """
        # To list available devices only and not previously connected ones,
        # each device will be opened and added to the list only if that succeeded
        rm = ResourceManager()

        available_resources : List[str] = []
        for device in rm.list_resources():
            try:
                d = rm.open_resource(device)
                d.close()
                available_resources.append(device)
            except VisaIOError:
                pass

        return available_resources

    def flush_read(self) -> bool:
        super().flush_read()
        while not self._event_queue.empty():
            self._event_queue.get()

        return True

    def open(self) -> bool:
        output = False
        if self._inst is None:
            try:
                self._inst = self._rm.open_resource(self.descriptor.descriptor)
            except:
                pass
        
        if self._status == AdapterBackendStatus.DISCONNECTED:
            self._inst.write_termination = "" # type: ignore
            self._inst.read_termination = None  # type: ignore

            self._inst_lock = threading.Lock()
            self._status = AdapterBackendStatus.CONNECTED
        if self._thread is None:
            self._thread = threading.Thread(
                target=self._internal_thread,
                args=(self._inst, self._event_queue),
                daemon=True,
            )
            self._thread.start()
            output = True

        return output

    def close(self) -> bool:
        super().close()
        with self._inst_lock:
            if self._inst is not None:
                self._inst.close()
        self._status = AdapterBackendStatus.DISCONNECTED
        with self._stop_lock:
            self.stop = True
        return True

    def write(self, data: bytes) -> bool:
        super().write(data)
        with self._inst_lock:
            if self._inst is not None:
                # TODO : Do error catching here
                self._inst.write_raw(data) # type: ignore
        return True

    def _socket_read(self) -> Fragment:
        self._notify_recv.recv(1)
        if not self._event_queue.empty():
            event = self._event_queue.get()
            if isinstance(event, AdapterDisconnected):
                return Fragment(b"", None)

        with self._fragment_lock:
            output = self._fragment
            self._fragment = Fragment(b"", None)
            return output

    def _internal_thread(self, inst: Resource, event_queue: queue.Queue[AdapterSignal]) -> None:
        timeout = 2000
        while True:
            payload = bytes()
            with self._fragment_lock:
                self._fragment = Fragment(b"", None)
            try:
                inst.timeout = timeout
            except InvalidSession:
                pass
            try:
                while True:
                    # Read up to an error
                    payload += inst.read_bytes(1) # type: ignore
                    inst.timeout = 0
            except VisaIOError:
                # Timeout
                if payload:
                    with self._fragment_lock:
                        if self._fragment.timestamp is None:
                            self._fragment.timestamp = time.time()
                            #if self._fragment.data is not None:
                            self._fragment.data += payload
                            
                    # Tell the session that there's data (write to a virtual socket)
                    self._notify_send.send(b"1")
            except (TypeError, InvalidSession, BrokenPipeError):
                event_queue.put(AdapterDisconnected())
                self._notify_send.send(b"1")
            with self._stop_lock:
                if self.stop:
                    break

    def selectable(self) -> Optional[HasFileno]:
        return self._notify_recv

    def is_opened(self) -> bool:
        if self._inst is None:
            return False
        else:
            return self._status == AdapterBackendStatus.CONNECTED
