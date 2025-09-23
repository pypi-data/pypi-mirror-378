# File : adapter_shell.py
# Author : Sébastien Deriaz
# License : GPL


from argparse import ArgumentParser
from enum import Enum

from syndesi.adapters.backend.adapter_backend import AdapterDisconnected, AdapterReadPayload, AdapterSignal

from .. import IP, Delimited, Raw, SerialPort, Visa
from ..adapters.timeout import Timeout
from .shell import Shell
from typing import List, Union

HISTORY_FILE_NAME = "syndesi"


class Format(Enum):
    TEXT = "text"
    HEX = "hex"

class AdapterType(Enum):
    IP = "ip"
    SERIAL = "serial"
    VISA = "visa"

class SpecialLineEnding(Enum):
    CR = "cr"
    LF = "lf"
    CRLF = "crlf"


LINE_ENDING_CHARS = {
    SpecialLineEnding.CR: "\r",
    SpecialLineEnding.LF: "\n",
    SpecialLineEnding.CRLF: "\r\n"
}

def hex2array(raw: str):
    s = raw.replace(" ", "")
    if len(s) % 2 != 0:
        s = "0" + s
    try:
        array = bytes([int(s[2 * i : 2 * (i + 1)], 16) for i in range(len(s) // 2)])
    except ValueError:
        raise ValueError(f"Cannot parse hex string : {raw}")
    return array


def array2hex(array: bytes):
    return " ".join([f"{x:02X}" for x in array])

def parse_end_argument(arg : Union[str, None]):
    if arg is None:
        return None
    # Return a special line end char if it corresponds
    for s, t in LINE_ENDING_CHARS.items():
        if arg == s.value:
            return t
    # Otherwise parse "\\n" -> "\n"
    return arg.replace('\\n', '\n').replace('\\r', '\r')

class AdapterShell:
    def __init__(self, kind: str) -> None:
        self.shell = None
        self._parser = ArgumentParser()
        self._parser.add_argument(
            "-t",
            "--timeout",
            nargs="+",
            type=float,
            required=False,
            default=[2],
            help="Adapter timeout (response)",
        )
        self._parser.add_argument(
            "-e",
            "--end",
            required=False,
            default=SpecialLineEnding.LF.value,
            help="Termination, cr, lf, crlf, none or a custom string. Only used with text format. Custom receive end can be set with --receive-end",
        )
        self._parser.add_argument(
            '--receive-end',
            required=False,
            default=None,
            help="Reception termination, same as --end but for reception only. If not set, the value of --end will be used"
        )
        self._parser.add_argument(
            "-f",
            "--format",
            default=Format.TEXT,
            help="Format, text or hex",
            choices=[x.value for x in Format],
        )
        self._parser.add_argument(
            "--backend-address",
            default=None,
            help="Address of the backend server"
        )
        self._parser.add_argument(
            "--backend-port",
            default=None,
            help="Port of the backend server"
        )


        self._kind = AdapterType(kind)
        if self._kind == AdapterType.IP:
            self._parser.add_argument("-a", "--address", type=str, required=True)
            self._parser.add_argument("-p", "--port", type=int, required=True)
            self._parser.add_argument(
                "--protocol", choices=["TCP", "UDP"], default="TCP"
            )
        elif self._kind == AdapterType.SERIAL:
            self._parser.add_argument("-p", "--port", type=str, required=True)
            self._parser.add_argument("-b", "--baudrate", type=int, required=True)
            self._parser.add_argument(
                "--rtscts", action="store_true", default=False, help="Enable RTS/CTS"
            )
        elif self._kind == AdapterType.VISA:
            self._parser.add_argument("descriptor", type=str)
        else:
            raise ValueError("Unsupported Kind")

    def run(self, remaining_args : List[str]):
        args = self._parser.parse_args(remaining_args)
        timeout = Timeout(args.timeout)

        # Create the adapter
        if self._kind == AdapterType.IP:
            self.adapter = IP(
                address=args.address,
                port=args.port,
                transport=args.protocol,
                timeout=timeout,
                backend_address=args.backend_address,
                backend_port=args.backend_port
            )
        elif self._kind == AdapterType.SERIAL:
            self.adapter = SerialPort(
                port=args.port,
                baudrate=args.baudrate,
                timeout=timeout,
                rts_cts=args.rtscts,
                backend_address=args.backend_address,
                backend_port=args.backend_port
            )
        elif self._kind == AdapterType.VISA:
            self.adapter = Visa(
                descriptor=args.descriptor,
                timeout=timeout,
                backend_address=args.backend_address,
                backend_port=args.backend_port)

        self.adapter.set_default_timeout(Timeout(action="return"))
        # Add the protocol
        _format = Format(args.format)
        if _format == Format.HEX:
            self._protocol = Raw(self.adapter, event_callback=self.event)
        elif _format == Format.TEXT:
            send_end = parse_end_argument(args.end)
            receive_end = parse_end_argument(args.receive_end)

            self._protocol = Delimited(
                self.adapter, termination=send_end, event_callback=self.event, receive_termination=receive_end
            )

        # Create the shell
        self.shell = Shell(
            on_command=self.on_command,
            history_file_name=HISTORY_FILE_NAME,
            commands=[],
        )

        try:
            self.adapter.open()
        except Exception: # TODO : Change this to a suitable exception
            self.shell.print(f'Failed to open adapter {self.adapter.descriptor}', style=Shell.Style.ERROR)
            self.adapter.close() # TODO : Maybe force here ?
        else:
            self.shell.print(
                f"Opened adapter {self.adapter.descriptor}", style=Shell.Style.NOTE
            )
            self.shell.run()

    def on_command(self, command: str):
        self._protocol.write(command)

    def event(self, signal: AdapterSignal, *args):
        if self.shell is not None:
            if isinstance(signal, AdapterDisconnected):
                def f(answer: str):
                    if answer.lower() == "y":
                        try:
                            self._protocol._adapter.open()
                        except Exception:  # TODO : Change this
                            self.shell.print(
                                "Failed to open adapter", style=Shell.Style.WARNING
                            )
                        else:
                            self.shell.print("Adapter opened", style=Shell.Style.NOTE)
                    self.shell.reprompt()

                answer = self.shell.ask("Adapter disconnected, reconnect ? (y/n): ", f)
            elif isinstance(signal, AdapterReadPayload):
                data = signal.data()
                # TODO : Catch data from delimited with formatting
                self.shell.print(data.decode('ASCII'))
