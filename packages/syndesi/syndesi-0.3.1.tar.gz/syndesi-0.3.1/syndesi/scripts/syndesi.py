# File : syndesi.py
# Author : Sébastien Deriaz
# License : GPL

import argparse
from enum import Enum

from ..tools.log import log
from ..version import __version__
from ..cli.adapter_shell import AdapterShell, AdapterType

from enum import Enum

class SyndesiCommands(Enum):
    SERIAL = "serial"
    IP = "ip"
    MODBUS = "modbus"
    VISA = "visa"


def main():
    parser = argparse.ArgumentParser(
        prog="syndesi", description="Syndesi command line tool", epilog=""
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "command",
        choices=[x.value for x in SyndesiCommands],
        help="Command, use syndesi <command> -h for help",
    )

    args, remaining_args = parser.parse_known_args()
    command = SyndesiCommands(args.command)

    if args.verbose:
        log("DEBUG", console=True)

    if command == SyndesiCommands.SERIAL:
        AdapterShell(AdapterType.SERIAL).run(remaining_args)
    elif command == SyndesiCommands.IP:
        AdapterShell(AdapterType.IP).run(remaining_args)
    elif command == SyndesiCommands.VISA:
        AdapterShell(AdapterType.VISA).run(remaining_args)
    else:
        raise RuntimeError(f"Command '{command.value}' is not supported yet")
    
if __name__ == '__main__':
    main()