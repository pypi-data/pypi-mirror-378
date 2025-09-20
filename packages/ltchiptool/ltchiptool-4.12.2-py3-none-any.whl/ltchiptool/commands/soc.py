#  Copyright (c) Kuba Szczodrzyński 2022-10-5.

import click

from ltchiptool.util.cli import get_multi_command_class

COMMANDS = {
    "bkpackager": "ltchiptool/soc/bk72xx/bkpackager.py",
    "rtltool": "ltchiptool/soc/ambz/util/rtltool.py",
    "ambztool": "ltchiptool/soc/ambz/util/ambztool.py",
    "ambz2tool": "ltchiptool/soc/ambz2/util/ambz2tool.py",
    "ln882htool": "ltchiptool/soc/ln882h/util/ln882htool.py",
}


@click.command(
    cls=get_multi_command_class(COMMANDS),
    help="Run SoC-specific tools",
)
def cli():
    pass
