# File : delimited.py
# Author : Sébastien Deriaz
# License : GPL

from typing import Callable, Optional, Tuple, Union

from syndesi.tools.types import DEFAULT, DefaultType
from ..adapters.adapter import Adapter
from ..adapters.backend.adapter_backend import AdapterReadPayload, AdapterSignal
from ..adapters.stop_condition import Termination
from ..adapters.timeout import Timeout
from .protocol import Protocol


class Delimited(Protocol):
    def __init__(
        self,
        adapter: Adapter,
        termination : str ="\n",
        format_response : bool =True,
        encoding: str = "utf-8",
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        event_callback : Optional[Callable[[AdapterSignal], None]]=None,
        receive_termination : Optional[str] =None
    ) -> None:
        """
        Protocol with delimiter, like LF, CR, etc... LF is used by default

        No presentation or application layers

        Parameters
        ----------
        adapter : Adapter
        termination : bytes
            Command termination, '\\n' by default
        format_response : bool
            Apply formatting to the response (i.e removing the termination), True by default
        encoding : str or None
            If None, delimited will not encode/decode
        timeout : Timeout
            None by default (default timeout)
        receive_termination : bytes
            Termination when receiving only, optional
            if not set, the value of termination is used
        """
        if not isinstance(termination, str) or isinstance(termination, bytes):
            raise ValueError(
                f"end argument must be of type str or bytes, not {type(termination)}"
            )
        if receive_termination is None:
            self._receive_termination = termination
        else:
            self._receive_termination = receive_termination
        self._termination = termination
        self._encoding = encoding
        self._response_formatting = format_response

        adapter.set_stop_condition(
            stop_condition=Termination(sequence=self._receive_termination)
        )
        super().__init__(adapter, timeout=timeout, event_callback=event_callback)

        # TODO : Disable encoding/decoding when encoding==None

    def __str__(self) -> str:
        if self._receive_termination == self._termination:
            return f"Delimited({self._adapter},{repr(self._termination)})"
        else:
            return f"Delimited({self._adapter},{repr(self._termination)}/{repr(self._receive_termination)})"

    def __repr__(self) -> str:
        return self.__str__()

    def _to_bytes(self, command : Union[str, bytes]) -> bytes:
        if isinstance(command, str):
            return command.encode("ASCII")
        elif isinstance(command, bytes):
            return command
        else:
            raise ValueError(f"Invalid command type : {type(command)}")

    def _from_bytes(self, payload : bytes) -> str:
        assert isinstance(payload, bytes)
        return payload.decode("ASCII") # TODO : encoding ?

    def _format_command(self, command: str) -> str:
        return command + self._termination

    def _format_response(self, response: str) -> str:
        if response.endswith(self._receive_termination):
            response = response[: -len(self._receive_termination)]
        return response

    def _on_data_ready_event(self, data: AdapterReadPayload) -> None:
        # TODO : Call the callback here ?
        #output = self._format_read(data.data(), decode=True)
        #return output
        pass

    def write(self, command: str) -> None:
        command = self._format_command(command)
        self._adapter.write(self._to_bytes(command))

    def query(
        self,
        data: str,
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        decode: bool = True,
        full_output: bool = False,
    ) -> Union[str, Tuple[str, AdapterSignal]]:
        """
        Writes then reads from the device and return the result

        Parameters
        ----------
        data : str
            Data to send to the device
        timeout : Timeout
            Custom timeout for this query (optional)
        decode : bool
            Decode incoming data, True by default
        full_output : bool
            return metrics on read operation (False by default)
        """
        self._adapter.flushRead()
        self.write(data)
        return self.read(timeout=timeout, decode=decode, full_output=full_output)

    def read(
        self,
        timeout: Union[Timeout, None, DefaultType] = DEFAULT,
        decode: bool = True,
        full_output: bool = False
    ) -> Union[str, Tuple[str, AdapterSignal]]:
        """
        Reads command and formats it as a str

        Parameters
        ----------
        timeout : Timeout
        decode : bool
            Decode incoming data, True by default
        full_output : bool
            If True, Return data and read information in a additionnal BackendReadOutput class
            If False, Return data only
        """

        # Send up to the termination
        data, signal = self._adapter.read(timeout=timeout, full_output=True)

        data_out = self._format_read(data, decode=decode)

        if full_output:
            return data_out, signal
        else:
            return data_out

    def _format_read(self, data : bytes, decode : bool) -> Union[str, bytes]:
        if decode:
            try:
                data_string = data.decode(self._encoding)
            except UnicodeDecodeError as e:
                raise ValueError(f"Failed to decode {data} to {self._encoding} ({e})")
            else:
                if not self._response_formatting:
                    # Add the termination back in since it was removed by the adapter
                    data_string += self._receive_termination

            return data_string
    
        else:
            # Return the raw data
            if self._response_formatting:
                return data
            else:
                return data + self._receive_termination.encode(self._encoding)