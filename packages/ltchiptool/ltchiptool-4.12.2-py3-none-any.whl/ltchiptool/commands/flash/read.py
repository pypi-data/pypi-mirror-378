#  Copyright (c) Kuba Szczodrzyński 2022-12-23.

from time import time
from typing import IO

import click
from click import File

from ltchiptool import Family, SocInterface
from ltchiptool.models import FamilyParamType
from ltchiptool.util.cli import AutoIntParamType, DevicePortParamType
from ltchiptool.util.flash import FlashConnection, FlashMemoryType
from ltchiptool.util.logging import graph
from ltchiptool.util.misc import sizeof
from ltchiptool.util.streams import ClickProgressCallback

from ._utils import flash_link_interactive


@click.command(short_help="Read flash contents")
@click.argument("family", type=FamilyParamType())
@click.argument("file", type=File("wb"))
@click.option(
    "-d",
    "--device",
    help="Target device port (default: auto detect)",
    type=DevicePortParamType(),
    default=(),
)
@click.option(
    "-b",
    "--baudrate",
    help="UART baud rate (default: auto choose)",
    type=int,
)
@click.option(
    "-s",
    "--start",
    "offset",
    help="Starting address to read from (default: 0)",
    type=AutoIntParamType(),
)
@click.option(
    "-l",
    "--length",
    help="Length to read, in bytes (default: entire flash)",
    type=AutoIntParamType(),
)
@click.option(
    "-t",
    "--timeout",
    help="Chip connection timeout in seconds (default: 20.0)",
    type=float,
    default=None,
)
@click.option(
    "-c/-C",
    "--check/--no-check",
    help="Check hash/CRC of the read data (default: True)",
    default=True,
)
@click.option(
    "-R",
    "--rom",
    "memory",
    flag_value=FlashMemoryType.ROM,
    type=FlashMemoryType,
    help="Read from ROM instead of Flash (default: False)",
)
@click.option(
    "-E",
    "--efuse",
    "memory",
    flag_value=FlashMemoryType.EFUSE,
    type=FlashMemoryType,
    help="Read from eFuse instead of Flash (default: False)",
)
def cli(
    family: Family,
    file: IO[bytes],
    device: str,
    baudrate: int,
    offset: int,
    length: int,
    timeout: float,
    check: bool,
    memory: FlashMemoryType,
):
    """
    Read flash contents to a file.

    By default, read the entire flash chip, starting at offset 0x0.

    When not specified (-d), the first UART port is used. The baud rate (-b)
    is chosen automatically, depending on the chip capabilities.

    \b
    Arguments:
      FAMILY    Chip family name/code
      FILE      Output file name
    """
    time_start = time()
    soc = SocInterface.get(family)
    soc.flash_set_connection(FlashConnection(device, baudrate))
    flash_link_interactive(soc, timeout)

    memory = memory or FlashMemoryType.FLASH
    max_length = soc.flash_get_size(memory)

    offset = offset or 0
    length = length or (max_length - offset)

    if offset + length > max_length:
        raise ValueError(
            f"Reading length {sizeof(length)} @ 0x{offset:X} is more than "
            f"chip capacity ({sizeof(max_length)})",
        )

    graph(0, f"Reading {memory.value} ({sizeof(length)}) to '{file.name}'")

    with ClickProgressCallback(length) as callback:
        for chunk in soc.flash_read_raw(
            offset=offset,
            length=length,
            verify=check,
            memory=memory,
            callback=callback,
        ):
            file.write(chunk)

    duration = time() - time_start
    graph(1, f"Finished in {duration:.3f} s")
