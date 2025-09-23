# File : visa.py
# Author : Sébastien Deriaz
# License : GPL
#
# VISA adatper, uses a VISA backend like pyvisa-py or NI to communicate with instruments

from typing import Callable, Optional, Union
from syndesi.adapters.backend.adapter_backend import AdapterSignal
from syndesi.adapters.stop_condition import StopCondition
from syndesi.tools.types import DEFAULT, DefaultType
from .adapter import Adapter
from .backend.descriptors import VisaDescriptor
from .timeout import Timeout


class Visa(Adapter):
    def __init__(
        self,
        descriptor : str,
        alias : str = "",
        stop_condition : Union[StopCondition, None, DefaultType] = DEFAULT,
        timeout : Union[None, float, Timeout, DefaultType] = DEFAULT,
        encoding : str = "utf-8",
        event_callback : Optional[Callable[[AdapterSignal], None]] = None,
    ) -> None:
        super().__init__(
            VisaDescriptor.from_string(descriptor),
            alias,
            stop_condition,
            timeout,
            encoding,
            event_callback,
        )

        self._logger.info("Setting up VISA IP adapter")

    def _default_timeout(self) -> Timeout:
        return Timeout(response=5, action="error")
