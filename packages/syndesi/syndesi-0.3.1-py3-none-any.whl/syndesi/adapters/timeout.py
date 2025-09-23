# File : timeout.py
# Author : Sébastien Deriaz
# License : GPL

from enum import Enum
from typing import Any, Optional, Protocol, TypeGuard, Union

from ..tools.backend_api import Action

from ..tools.types import DEFAULT, NumberLike, DefaultType, is_number

# from .backend.timeout import TimeoutAction, JsonKey


class TimeoutAction(Enum):
    ERROR = "error"
    RETURN = "return"

class IsInitialized(Protocol):
    response: Optional[NumberLike]

class Timeout:
    DEFAULT_ACTION = TimeoutAction.ERROR
    def __init__(self, response : Union[NumberLike, None, DefaultType] = DEFAULT, action : Union[str, DefaultType, TimeoutAction] = DEFAULT) -> None:
        """
        This class holds timeout information

        Parameters
        ----------
        response : float
            Time before the device responds
        action : str
            Action performed when a timeout occurs. 'error' -> raise an error, 'return' -> return b''
        """
        super().__init__()

        self._is_default_response = response is DEFAULT
        self._is_default_action = action is DEFAULT

        self.action : Union[DefaultType, TimeoutAction]
        if action is DEFAULT:
            self.action = self.DEFAULT_ACTION
            self.action = DEFAULT
        else:
            self.action = TimeoutAction(action)
             
        self.response : Optional[Union[DefaultType, NumberLike]] = response

    def __str__(self) -> str:
        if self.response is DEFAULT:
            r = "..."
        else:
            r = f"{self.response:.3f}"
        if self.action is DEFAULT:
            a = "..."
        else:
            a = f"{self.action}"
        return f"Timeout({r}:{a})"

    def __repr__(self) -> str:
        return self.__str__()

    def set_default(self, default_timeout: "Timeout") -> None:
        if self._is_default_response:
            self.response = default_timeout.response
        if self._is_default_action:
            self.action = default_timeout.action

def any_to_timeout(value : Any) -> Timeout:
    if value is None:
        return Timeout(response=None)
    elif is_number(value):
        return Timeout(response=float(value))
    elif isinstance(value, Timeout):
        return value
    else:
        raise ValueError(f"Could not convert {value} to Timeout")
    
class TimeoutException(Exception):
    def __init__(self, value: NumberLike, limit: NumberLike) -> None:
        super().__init__()
        self._value = value
        self._limit = limit

    def __str__(self) -> str:
        try:
            value_string = f"{self._value * 1e3:.3f}ms"
        except (ValueError, TypeError):
            value_string = "not received"

        try:
            limit_string = f"{self._limit * 1e3:.3f}ms"
        except (ValueError, TypeError):
            limit_string = "not received"

        return f"{value_string} / {limit_string}"

    def __repr__(self) -> str:
        return self.__str__()
