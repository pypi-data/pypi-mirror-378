# File : raw.py
# Author : Sébastien Deriaz
# License : GPL

from typing import Tuple, Union

from syndesi.adapters.backend.adapter_backend import AdapterSignal
from syndesi.adapters.stop_condition import StopCondition
from syndesi.tools.types import DEFAULT, DefaultType
from ..adapters.timeout import Timeout
from ..adapters.adapter import Adapter
from .protocol import Protocol

# Raw protocols provide the user with the binary data directly,
# without converting it to string first


class Raw(Protocol):
    def __init__(self,
                 adapter: Adapter,
                 timeout: Union[Timeout, None, DefaultType] = DEFAULT) -> None:
        """
        Raw device, no presentation and application layers

        Parameters
        ----------
        adapter : IAdapter
        """
        super().__init__(adapter, timeout)

    def write(self, data: bytes) -> None:
        self._adapter.write(data)

    def query(
        self,
        data: bytes,
        timeout : Union[Timeout, None, DefaultType] = DEFAULT,
        stop_condition : Union[StopCondition, None, DefaultType] = DEFAULT,
        full_output: bool = False,
    ) -> Union[bytes, Tuple[bytes, AdapterSignal]]:
        self._adapter.flushRead()
        self.write(data)
        return self.read(
            timeout=timeout,
            stop_condition=stop_condition,
            full_output=full_output,
        )

    def read(
        self,
        timeout : Union[Timeout, None, DefaultType] = DEFAULT,
        stop_condition : Union[StopCondition, None, DefaultType] = DEFAULT,
        full_output: bool = False
    ) -> Union[bytes, Tuple[bytes, AdapterSignal]]:
        output, signal = self._adapter.read(
            timeout=timeout, stop_condition=stop_condition, full_output=True
        )
        if full_output:
            return output, signal
        else:
            return output

    def __str__(self) -> str:
        return f"Raw({self._adapter})"
