# File : stop_condition.py
# Author : Sébastien Deriaz
# License : GPL
#
# A stop-condition describes when a communication with a device should
# be stopped based on the data received (length, contents, termination, etc...)
# A stop-condition can also format the data if necessary (remove termination for example)

import time
from abc import abstractmethod
from enum import Enum

from syndesi.adapters.stop_condition import StopCondition, Termination, Length, TimeoutStopCondition

from ...tools.backend_api import Fragment


# class StopConditionType(Enum):
#     TERMINATION = "termination"
#     LENGTH = "length"
#     LAMBDA = "lambda"
#     TIMEOUT = "timeout"


# class StopConditionDescriptorKey(Enum):
#     TYPE = "type"
#     TERMINATION_SEQUENCE = "sequence"
#     LENGTH_N = "N"
#     TIMEOUT_CONTINUATION = "tc"
#     TIMEOUT_TOTAL = "tt"

def termination_in_data(termination: bytes, data: bytes) -> tuple[int | None, int]:
    """
    Return the position (if it exists) and length of the termination (or part of it) inside data
    """
    p = None
    L = len(termination)
    # First check if the full termination is somewhere. If that's the case, data will be split
    try:
        p = data.index(termination)
        # If found, return that
    except ValueError:
        # If not, we'll try to find if part of the sequence is at the end, in that case
        # we'll return the length of the sequence that was found
        L -= 1
        while L > 0:
            if data[-L:] == termination[:L]:
                p = len(data) - L# - 1
                break
            L -= 1

    return p, L

class StopConditionBackend:
    def __init__(self, stop_condition : StopCondition) -> None:
        self.stop_condition = stop_condition

        # Termination
        self._sequence_found_length = 0

        # Length
        self._counter = 0

        # Timeout
        self._start_time: float | None = None
        self._last_fragment: float | None = None

    def initiate_read(self) -> None:
        # Termination
        self._sequence_found_length = 0
        # Length
        self._counter = 0
        # Timeout
        self._start_time = time.time()
        self._last_fragment = self._start_time


    def evaluate(
        self, raw_fragment: Fragment) -> tuple[bool, Fragment, Fragment, float | None]:

        if isinstance(self.stop_condition, Termination):
            return self._evaluate_termination(raw_fragment)
        elif isinstance(self.stop_condition, Length):
            return self._evaluate_length(raw_fragment)
        elif isinstance(self.stop_condition, TimeoutStopCondition):
            return self._evaluate_timeout(raw_fragment)
        else:
            raise RuntimeError(f"Invalid stop condition : {self.stop_condition}")

    def flush_read(self):
        self._sequence_found_length = 0
        self._counter = 0
        self._start_time = None
        self._last_fragment = None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.stop_condition.__str__()

    def _evaluate_termination(self, raw_fragment: Fragment) -> tuple[bool, Fragment, Fragment, float | None]:
        self.stop_condition : Termination
        if raw_fragment.data is None:
            raise RuntimeError("Trying to evaluate an invalid fragment")
        
        position, length = termination_in_data(
            self.stop_condition.sequence[self._sequence_found_length :], raw_fragment.data
        )
        stop = False
        deferred = Fragment(b"", None)

        if position is None:
            # Nothing was found, keep everything
            kept = raw_fragment
        else:
            self._sequence_found_length += length

            if self._sequence_found_length == len(self.stop_condition.sequence):
                # The sequence was found entirely
                deferred = raw_fragment[position + length :]
                self._sequence_found_length = 0
                stop = True
            elif position + length == len(raw_fragment.data):
                # Part of the sequence was found at the end
                # Return what's before the sequence
                deferred = Fragment(b"", None)

            kept = raw_fragment[:position]
        
        return stop, kept, deferred, None

    def _evaluate_length(self, raw_fragment: Fragment) -> tuple[bool, Fragment, Fragment, float | None]:
        self.stop_condition : Length
        remaining_bytes = self.stop_condition.N - self._counter
        kept_fragment = raw_fragment[:remaining_bytes]
        deferred_fragment = raw_fragment[remaining_bytes:]
        self._counter += len(kept_fragment.data)
        remaining_bytes = self.stop_condition.N - self._counter
        # TODO : remaining_bytes <= 0 ? Alongside above TODO maybe
        return remaining_bytes == 0, kept_fragment, deferred_fragment, None

    def _evaluate_timeout(self, raw_fragment: Fragment) -> tuple[bool, Fragment, Fragment, float | None]:
        self.stop_condition : TimeoutStopCondition

        stop = False
        kept = raw_fragment
        deferred = Fragment(b"", None)
        next_event_timeout = None

        if raw_fragment.timestamp is None:
            raise RuntimeError("Cannot evaluate fragment with no timestamp")
        # last_fragment can be none if no data was ever received
        if self.stop_condition.continuation is not None and self._last_fragment is not None:
            continuation_timestamp = self._last_fragment + self.stop_condition.continuation
            stop |= continuation_timestamp <= raw_fragment.timestamp
            next_event_timeout = continuation_timestamp

        if self.stop_condition.total is not None:
            if self._start_time is None:
                raise RuntimeError("Invalid start time")
            total_timestamp = self._start_time + self.stop_condition.total
            stop |= total_timestamp <= raw_fragment.timestamp
            if next_event_timeout is None:
                next_event_timeout = total_timestamp
            else:
                next_event_timeout = min(next_event_timeout, total_timestamp)

        return stop, kept, deferred, next_event_timeout




    # @property
    # @abstractmethod
    # def _TYPE(self) -> StopConditionType:
    #     raise NotImplementedError

    # def __init__(self) -> None:
    #     """
    #     A condition to stop reading from a device

    #     Cannot be used on its own
    #     """
    #     self._and = None
    #     self._or = None

    #     self._eval_time = None

    # @abstractmethod
    # def initiate_read(self) -> float | None:
    #     """
    #     Initiate a read sequence.

    #     The maximum time that should be spent in the next byte read
    #     is returned

    #     Returns
    #     -------
    #     timeout : float or None
    #         None is there's no timeout
    #     """
    #     pass

    # @abstractmethod
    # def evaluate(
    #     self, raw_fragment: Fragment, timestamp: float
    # ) -> tuple[bool, Fragment, Fragment, float | None]:
    #     """
    #     Evaluate the next received byte

    #     Returns
    #     -------
    #     stop : bool
    #         False if read should continue
    #         True if read should stop
    #     kept_fragment : bytes
    #         Part of the fragment kept for future use
    #     deferred_fragment : bytes
    #         Part of the fragment that was deferred because of a stop condition
    #     """
    #     pass

    # @abstractmethod
    # def flush_read(self) -> None:
    #     """
    #     Flush input buffer and reset stop-condition
    #     """
    #     pass




# class TerminationBackend(StopConditionBackend):
#     # _TYPE = StopConditionType.TERMINATION
#     def flush_read(self) -> None:
#         self._sequence_found_length = 0

#     def __repr__(self) -> str:
#         return self.__str__()

#     def __str__(self) -> str:
#         return f"TerminationBackend({repr(self._sequence)})"


# # TODO : Add a "allow_longer" parameter ? If more than N data is received, keep it instead of raising an error ?
# class LengthBackend(StopConditionBackend):
#     # _TYPE = StopConditionType.LENGTH

    

#     def __repr__(self) -> str:
#         return self.__str__()

#     def __str__(self) -> str:
#         return f"LengthBackend({self._N})"

#     def flush_read(self) -> None:
#         self._counter = 0


# class TimeoutStopConditionBackend(StopConditionBackend):
#     # _TYPE = StopConditionType.TIMEOUT

#     def __init__(self, continuation: float | None, total: float | None) -> None:
#         """
#         Timeout stop condition, can stop on continuation (device not responding after x seconds),
#         or total (total communication time exceeds a given value)

#         Parameters
#         ----------
#         continuation : float
#         total : float
#         """
#         super().__init__()
#         self._start_time: float | None = None
#         self._last_fragment: float | None = None
#         self._continuation = continuation
#         self._total = total

#     def initiate_read(self) -> None:
#         self._start_time = time.time()
#         self._last_fragment = self._start_time

    

#     def flush_read(self) -> None:
#         self._counter = 0
#         self._start_time = None
#         self._last_fragment = None


# class Lambda(StopCondition): # TODO : maybe work on this a bit more
#     class LambdaReturn:
#         ERROR = 'error' # Discard everything and raise an error
#         VALID = 'valid' # Return everything
#         KEEP_N = 'keep_n' # Keep the first N bytes
#         CONTINUE = 'continue' # Keep reading

#     def __init__(self, _lambda : Callable) -> None:
#         super().__init__()
#         self._lambda = _lambda

#     def initiate_read(self) -> Union[float, None]:
#         return None

#     def evaluate(self, fragment: bytes) -> Tuple[bool, Union[float, None]]:
#         lambda_return, N = self._lambda(fragment)
#         match lambda_return:
#             case self.LambdaReturn.ERROR:
#                 raise RuntimeError(f"Couldn't apply Lambda condition on fragment : {fragment}")
#             case self.LambdaReturn.VALID:
#                 return True, fragment, b''
#             case self.LambdaReturn.KEEP_N:
#                 return True, fragment[:N], fragment[N:]
#             case self.LambdaReturn.CONTINUE:
#                 return False, fragment, b'' # TODO : Check this

#     def __repr__(self) -> str:
#         return self.__str__()

#     def __str__(self) -> str:
#         return f'Lambda(...)'

# def stop_conditions_to_backends(stop_conditions: list[StopCondition]) -> list["StopConditionBackend"]:
#     output = []
#     for stop_condition in stop_conditions:
#         if isinstance(stop_condition, Termination):
#             output.append(TerminationBackend(
#                 sequence=stop_condition.sequence
#             ))
#         elif isinstance(stop_condition, Length):
#             output.append(LengthBackend(
#                 N=stop_condition.N
#             ))
#         elif isinstance(stop_condition, TimeoutStopCondition):
#             output.append(TimeoutStopConditionBackend(
#                 continuation=stop_condition.continuation,
#                 total=stop_condition.total,
#             ))

#     return output