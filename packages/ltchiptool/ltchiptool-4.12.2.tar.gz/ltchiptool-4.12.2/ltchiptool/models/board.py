# Copyright (c) Kuba Szczodrzyński 2022-07-29.

import json
from glob import glob
from os.path import basename, isfile, join
from typing import List, Optional, Tuple, Union

import click

from ltchiptool.util.dict import RecursiveDict, merge_dicts
from ltchiptool.util.fileio import readjson
from ltchiptool.util.lvm import LVM
from ltchiptool.util.toolchain import Toolchain

from .family import Family


class Board(RecursiveDict):
    _toolchain: Optional[Toolchain] = None

    def __init__(self, board: Union[str, dict]):
        super().__init__(Board.get_data(board))

    @staticmethod
    def get_data(board: Union[str, dict]) -> dict:
        if not isinstance(board, dict):
            if isfile(board):
                board = readjson(board)
                if not board:
                    raise FileNotFoundError(f"Board not found: {board}")
            else:
                source = board
                board = LVM.get().load_json(f"boards/{board}.json")
                board["source"] = source
        if "_base" in board:
            base = board["_base"]
            if not isinstance(base, list):
                base = [base]
            result = {}
            for base_name in base:
                board_base = LVM.get().load_json(f"boards/_base/{base_name}.json")
                merge_dicts(result, board_base)
            merge_dicts(result, board)
            board = result
        return board

    @classmethod
    def get_list(cls) -> List[str]:
        boards_glob = join(LVM.path(), "boards", "*.json")
        return [basename(file)[:-5] for file in glob(boards_glob)]

    def json(self) -> str:
        return json.dumps(self, indent=4)

    @property
    def name(self) -> str:
        return self["build.variant"]

    @property
    def title(self) -> str:
        return self["name"]

    @property
    def symbol(self) -> str:
        return self["symbol"]

    @property
    def vendor(self) -> str:
        return self["vendor"]

    @property
    def family(self) -> Family:
        return Family.get(short_name=self["build.family"])

    @property
    def toolchain(self):
        if not self._toolchain:
            self._toolchain = Toolchain(self["build.prefix"])
        return self._toolchain

    @property
    def is_generic(self) -> bool:
        return self.name.startswith("generic")

    @property
    def generic_name(self) -> Optional[str]:
        if self.is_generic:
            return self.name[8:]
        return None

    def region(self, name: str) -> Tuple[int, int, int]:
        region = self[f"flash.{name}"]
        if not region:
            raise ValueError(
                f"The flash region '{name}' does not exist for board '{self.name}'."
            )
        (start, length) = region.split("+")
        start = int(start, 0)
        length = int(length, 0)
        return start, length, start + length


class BoardParamType(click.ParamType):
    name = "board"

    def convert(self, value, param, ctx) -> Board:
        try:
            return Board(value)
        except FileNotFoundError:
            self.fail(f"Board {value} does not exist", param, ctx)
