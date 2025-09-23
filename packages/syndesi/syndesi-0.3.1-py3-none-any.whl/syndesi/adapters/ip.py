# File : ip.py
# Author : Sébastien Deriaz
# License : GPL
#
# IP adapter, communicates with TCP or UDP


from typing import Callable, Optional, Union

from syndesi.adapters.backend.adapter_backend import AdapterSignal
from syndesi.tools.types import DEFAULT, NumberLike, DefaultType
from .adapter import Adapter
from .backend.descriptors import IPDescriptor
from .stop_condition import StopCondition
from .timeout import Timeout

# TODO : Server ? create an adapter from a socket ?

# TODO : Manage opening and closing, modes ? open at instance or at write/read ? close after read ? error if already opened before / strict mode ?


class IP(Adapter):
    def __init__(
        self,
        address: str,
        port: Optional[int] = None,
        transport: Union[str, IPDescriptor.Protocol] = IPDescriptor.Protocol.TCP.value,
        timeout: Union[Timeout, NumberLike, None, DefaultType] = DEFAULT,
        stop_condition: Union[StopCondition, None, DefaultType] = DEFAULT,
        alias: str = "",
        encoding: str = "utf-8",
        event_callback : Optional[Callable[[AdapterSignal], None]]=None,
        auto_open : bool = True,
        backend_address : Optional[str] = None,
        backend_port : Optional[int] = None
    ):
        """
        IP adapter

        Parameters
        ----------
        address : str
            IP description
        port : int
            IP port
        transport : str
            'TCP' or 'UDP'
        timeout : Timeout | float
            Specify communication timeout
        stop_condition : StopCondition
            Specify a read stop condition (None by default)
        auto_open : bool
            Automatically open the adapter
        socket : socket.socket
            Specify a custom socket, this is reserved for server application

        """
        super().__init__(
            descriptor=IPDescriptor(
                address=address,
                port=port,
                transport=IPDescriptor.Protocol(transport),
            ),
            alias=alias,
            timeout=timeout,
            stop_condition=stop_condition,
            encoding=encoding,
            event_callback=event_callback,
            auto_open=auto_open,
            backend_address=backend_address,
            backend_port=backend_port
        )
        self.descriptor : IPDescriptor

        self._logger.info(f"Setting up {self.descriptor.transport.value} IP adapter")

        self.set_default_timeout(self._default_timeout())

    def _default_timeout(self) -> Timeout:
        return Timeout(response=5, action="error")

    def set_default_port(self, port : int) -> None:
        """
        Sets IP port if no port has been set yet.

        This way, the user can leave the port empty
        and the driver/protocol can specify it later

        Parameters
        ----------
        port : int
        """
        if self.descriptor.port is None:
            self.descriptor.port = port
