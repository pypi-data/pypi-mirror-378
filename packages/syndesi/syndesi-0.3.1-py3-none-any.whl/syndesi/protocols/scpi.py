# File : scpi.py
# Author : Sébastien Deriaz
# License : GPL


from typing import Literal, Optional, Tuple, Union, overload

from syndesi.adapters.backend.adapter_backend import AdapterSignal
from syndesi.tools.types import DEFAULT, DefaultType
from ..adapters.adapter import Adapter
from ..adapters.ip import IP
from ..adapters.stop_condition import StopCondition, Termination
from ..adapters.timeout import Timeout, TimeoutAction
from .protocol import Protocol

class SCPI(Protocol):
    DEFAULT_PORT = 5025

    def __init__(
        self,
        adapter: Adapter,
        send_termination : str = "\n",
        receive_termination : Optional[str] = None,
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        encoding: str = "utf-8",
    ) -> None:
        """
        SDP (Syndesi Device Protocol) compatible device

        Parameters
        ----------
        adapter : Adapter
        send_termination : str
            '\n' by default
        receive_termination : str
            None by default (copy value from send_termination)
        timeout : Timeout/float/tuple
            Set device timeout
        """
        self._encoding = encoding
        # Set the default timeout

        if receive_termination is None:
            self._receive_termination = send_termination
        else:
            self._receive_termination = receive_termination
        self._send_termination = send_termination
        # Configure the adapter for stop-condition mode (timeouts will raise errors)
        if not adapter._default_stop_condition:
            raise ValueError(
                "No stop-conditions can be set for an adapter used by SCPI protocol"
            )
        adapter.set_stop_condition(
            Termination(self._receive_termination.encode(self._encoding))
        )
        

        #adapter.set_timeout(self.timeout)
        if isinstance(adapter, IP):
            adapter.set_default_port(self.DEFAULT_PORT)
        # Give the adapter to the Protocol base class
        super().__init__(adapter=adapter, timeout=timeout)

    def _default_timeout(self) -> Timeout | None:
        return Timeout(response=5, action=TimeoutAction.ERROR.value)

    def _to_bytes(self, command : str) -> bytes:
        if isinstance(command, str):
            return command.encode("ASCII")
        else:
            raise ValueError(f"Invalid command type : {type(command)}")

    def _from_bytes(self, payload: bytes) -> str:
        if isinstance(payload, bytes):
            return payload.decode("ASCII")
        else:
            raise ValueError(f"Invalid payload type : {type(payload)}")

    def _formatCommand(self, command : str) -> str:
        return command + self._send_termination

    def _unformatCommand(self, payload : str) -> str:
        return payload.replace(self._receive_termination, "")

    def _checkCommand(self, command: str) -> None:
        for c in ["\n", "\r"]:
            if c in command:
                raise ValueError(f"Invalid char {repr(c)} in command")

    def write(self, command: str) -> None:
        self._checkCommand(command)
        payload = self._to_bytes(self._formatCommand(command))
        self._adapter.write(payload)

    def write_raw(self, data: bytes, termination: bool = False) -> None:
        self._adapter.write(data + (self._send_termination.encode(self._encoding) if termination else b""))

    def query(
        self,
        command: str,
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        stop_condition: Union[StopCondition, None, DefaultType] = DEFAULT,
        full_output: bool = False,
    ) -> Union[str, Tuple[str, AdapterSignal]]:
        self._adapter.flushRead()
        self.write(command)
        output, signal = self.read(
            timeout=timeout,
            stop_condition=stop_condition,
            full_output=True,
        )

        if full_output:
            return output
        else:
            return output, signal

    @overload
    def read(
        self,
        timeout: Union[Timeout, None, DefaultType],
        stop_condition: Union[StopCondition, None, DefaultType],
        full_output: Literal[True],
    ) -> Tuple[str, AdapterSignal]: ...
    
    @overload
    def read(
        self,
        timeout: Union[Timeout, None, DefaultType],
        stop_condition: Union[StopCondition, None, DefaultType],
        full_output: Literal[False],
    ) -> str: ...

    def read(
        self,
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        stop_condition: Union[StopCondition, None, DefaultType] = DEFAULT,
        full_output: bool = False,
    ) -> Union[str, Tuple[str, AdapterSignal]]:
        raw_output, signal = self._adapter.read(
                timeout=timeout,
                stop_condition=stop_condition,
                full_output=True
            ) 
        
        output = self._unformatCommand(self._from_bytes(raw_output))

        if full_output:
            return output
        else:
            return output, signal

    @overload
    def read_raw(
        self,
        timeout : Union[Timeout, None, DefaultType],
        stop_condition : Union[StopCondition, None, DefaultType],
        full_output: Literal[False]
    ) -> bytes: ...
    @overload 
    def read_raw(
        self,
        timeout : Union[Timeout, None, DefaultType],
        stop_condition : Union[StopCondition, None, DefaultType],
        full_output: Literal[True]
    ) -> Tuple[bytes, AdapterSignal]: ...

    def read_raw(
        self,
        timeout : Union[Timeout, None, DefaultType] = DEFAULT,
        stop_condition : Union[StopCondition, None, DefaultType] = DEFAULT,
        full_output: bool = False
    ) -> Union[bytes, Tuple[bytes, AdapterSignal]]:
        """
        Return the raw bytes instead of str
        """
        output, signal = self._adapter.read(
            timeout=timeout, stop_condition=stop_condition, full_output=True
        )
        if full_output:
            return output, signal
        else:
            return output
