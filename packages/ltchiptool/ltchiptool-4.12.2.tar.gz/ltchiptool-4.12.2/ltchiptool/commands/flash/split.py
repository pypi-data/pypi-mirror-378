# Copyright (c) Kuba Szczodrzyński 2022-08-06.

from binascii import crc32
from logging import error, info
from os import makedirs
from os.path import basename, dirname, join
from typing import IO

import click

from ltchiptool import Board
from ltchiptool.models import BoardParamType
from ltchiptool.util.crc16 import CRC16


@click.command()
@click.argument("board", type=BoardParamType())
@click.argument("input", type=click.File("rb"))
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False),
    default=None,
    help="Output directory (default <input name>.split/)",
)
@click.option(
    "-t/-T",
    "--trim/--no-trim",
    default=True,
    help="Trim output binaries (default)",
)
@click.option(
    "-c/-C",
    "--checksum/--no-checksum",
    default=True,
    help="Append checksum to file names (default)",
)
def cli(board: Board, input: IO[bytes], output: str, trim: bool, checksum: bool):
    """
    Split raw dump file based on board partitions.

    \b
    Arguments:
      BOARD    Name of the board of this dump
      INPUT    Raw input file
    """
    if not board["flash"]:
        raise ValueError("Flash layout not defined")
    if not output:
        output = join(dirname(input.name), basename(input.name) + ".split")
    makedirs(output, exist_ok=True)
    dump = input.read()

    for name in board["flash"].keys():
        (start, length, end) = board.region(name)
        if end > len(dump):
            error(f"Partition '{name}' is out of bounds!")
            error(f" - Dump size: {hex(len(dump))}")
            error(f" - Partition start: {hex(start)}")
            error(f" - Partition length: {hex(length)}")
            error(f" - Partition end: {hex(end)}")
            raise ValueError("Partition out of bounds")

        part = dump[start:end]
        offset = start.to_bytes(length=3, byteorder="big").hex().upper()
        filename = f"{offset}_{name}.bin"

        if trim:
            part = part.rstrip(b"\xff")
        if checksum:
            if length > 0x10000:  # 64 KiB
                cs = crc32(part)
                cs = cs.to_bytes(length=4, byteorder="big")
            else:
                cs = CRC16.ARC.calc(part)
                cs = cs.to_bytes(length=2, byteorder="big")
            filename = f"{offset}_{name}_{cs.hex().upper()}.bin"
        info(f"Writing {filename}")
        with open(join(output, filename), "wb") as f:
            f.write(part)
