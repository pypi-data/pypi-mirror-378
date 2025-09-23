# File : stop_condition.py
# Author : Sébastien Deriaz
# License : GPL

import json
from abc import abstractmethod
from typing import Optional, Type

from .backend.stop_condition_backend import JsonKey, StopConditionType


class StopCondition:
    def __init__(self) -> None:
        """
        A condition to stop reading from a device

        Cannot be used on its own
        """

    @abstractmethod
    def compose_json(self) -> str:
        raise NotImplementedError


class Termination(StopCondition):
    def __init__(self, sequence: bytes | str) -> None:
        """
        Stop reading once the desired sequence is detected

        Parameters
        ----------
        sequence : bytes
        """
        self._sequence: bytes
        if isinstance(sequence, str):
            self._sequence = sequence.encode("utf-8")
        elif isinstance(sequence, bytes):
            self._sequence = sequence
        else:
            raise ValueError(f"Invalid termination sequence type : {type(sequence)}")

    def compose_json(self) -> str:
        data = {
            JsonKey.TYPE.value: StopConditionType.TERMINATION.value,
            JsonKey.TERMINATION_SEQUENCE.value: self._sequence.decode("utf-8"),
        }
        return json.dumps(data)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Termination({repr(self._sequence)})"


class Length(StopCondition):
    def __init__(self, N: int) -> None:
        """
        Stop condition when the desired number of bytes is reached or passed

        Parameters
        ----------
        N : int
            Number of bytes
        """
        self._N = N

    def compose_json(self) -> str:
        data = {
            JsonKey.TYPE.value: StopConditionType.LENGTH.value,
            JsonKey.LENGTH_N.value: self._N,
        }
        return json.dumps(data)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Length({self._N})"


class TimeoutStopCondition(StopCondition):
    def __init__(
        self, continuation: float | None = None, total: float | None = None
    ) -> None:
        super().__init__()
        self.continuation = continuation
        self.total = total

    def compose_json(self) -> str:
        data = {
            JsonKey.TYPE.value: StopConditionType.TIMEOUT.value,
            JsonKey.TIMEOUT_CONTINUATION.value: self.continuation,
            JsonKey.TIMEOUT_TOTAL.value: self.total,
        }
        return json.dumps(data)

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return super().__str__()
