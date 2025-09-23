# File : serialport.py
# Author : Sébastien Deriaz
# License : GPL

from typing import Callable, Union, Optional
from syndesi.adapters.backend.adapter_backend import AdapterSignal
from syndesi.tools.types import DEFAULT, NumberLike, DefaultType
from .adapter import Adapter
from .backend.descriptors import SerialPortDescriptor
from .stop_condition import StopCondition
from .timeout import Timeout


class SerialPort(Adapter):
    def __init__(
        self,
        port: str,
        baudrate: Optional[int] = None,
        timeout: Union[Timeout, NumberLike, None, DefaultType] = DEFAULT,
        stop_condition: Union[StopCondition, None, DefaultType] = DEFAULT,
        alias: str = "",
        rts_cts: bool = False,  # rts_cts experimental
        event_callback : Optional[Callable[[AdapterSignal], None]] = None,
    ) -> None:
        """
        Serial communication adapter

        Parameters
        ----------
        port : str
            Serial port (COMx or ttyACMx)
        """
        descriptor = SerialPortDescriptor(port, baudrate)
        super().__init__(
            descriptor=descriptor,
            timeout=timeout,
            stop_condition=stop_condition,
            alias=alias,
            event_callback=event_callback,
        )
        self.descriptor : SerialPortDescriptor

        self._logger.info(
            f"Setting up SerialPort adapter {self.descriptor}, timeout={timeout} and stop_condition={stop_condition}"
        )
        # self._port = None

        self.open()

        self._rts_cts = rts_cts

    def _default_timeout(self) -> Timeout:
        return Timeout(response=2, action="error")

    def set_baudrate(self, baudrate: int) -> None:
        """
        Set baudrate

        Parameters
        ----------
        baudrate : int
        """
        if self.descriptor.set_default_baudrate(baudrate):
            self.close()
            self.open()

    def open(self) -> None:
        if self.descriptor.baudrate is None:
            raise ValueError("Baudrate must be set, please use set_baudrate")
        super().open()

    def close(self, force : bool = False) -> None:
        super().close(force)
        self._logger.info("Adapter closed !")
