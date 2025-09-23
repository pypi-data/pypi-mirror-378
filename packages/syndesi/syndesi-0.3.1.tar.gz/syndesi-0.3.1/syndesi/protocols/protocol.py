# File : protocol.py
# Author : Sébastien Deriaz
# License : GPL

import logging
from abc import abstractmethod
from typing import Any, Callable, Optional, Union

from syndesi.adapters.stop_condition import StopCondition
from syndesi.tools.types import DEFAULT, DefaultType

from ..adapters.timeout import Timeout
from ..adapters.adapter import Adapter
from ..adapters.auto import auto_adapter
from ..adapters.backend.adapter_backend import AdapterReadPayload, AdapterSignal
from ..tools.log_settings import LoggerAlias


class Protocol:
    def __init__(
        self,
        adapter: Adapter,
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        event_callback : Optional[Callable[[AdapterSignal], None]] = None
    ) -> None:
        # TODO : Convert the callable from AdapterSignal to ProtocolSignal or something similar
        self._adapter = auto_adapter(adapter)

        self._event_callback = event_callback
        self._adapter.set_event_callback(self.event_callback)

        if timeout is not DEFAULT:
            self._adapter.set_default_timeout(timeout)
        self._logger = logging.getLogger(LoggerAlias.PROTOCOL.value)

        if timeout is DEFAULT:
            self._adapter.set_timeout(self._default_timeout())
        else:
            self._adapter.set_timeout(timeout)

    @abstractmethod
    def _default_timeout(self) -> Optional[Timeout]:
        pass
    def flushRead(self) -> None:
        self._adapter.flushRead()

    def event_callback(self, event: AdapterSignal) -> None:
        if self._event_callback is not None:
            self._event_callback(event)

    @abstractmethod
    def _on_data_ready_event(self, data: AdapterReadPayload) -> None:
        pass

    @abstractmethod
    def write(self, *args : Any, **kwargs : Any) -> None:
        pass
    
    @abstractmethod
    def query(self,
              *args : Any,
              **kwargs : Any
            #   timeout: Union[Timeout, DefaultType, None],
            #   stop_condition: Union[StopCondition, None, DefaultType],
            #   full_output : bool,
            ) -> Any:
        pass
    
    @abstractmethod
    def read(self, *args : Any, **kwargs : Any) -> Any:
        pass