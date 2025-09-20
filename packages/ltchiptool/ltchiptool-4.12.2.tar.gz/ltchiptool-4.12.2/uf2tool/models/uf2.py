# Copyright (c) Kuba Szczodrzyński 2022-05-27.

from hashlib import md5
from logging import info
from typing import IO, Dict, List

from ltchiptool import Family
from ltchiptool.util.intbin import align_down, align_up, intto8, inttole16, inttole32

from .block import Block
from .enums import Tag


class UF2:
    f: IO[bytes]
    seq: int = 0

    family: Family = None
    tags: Dict[Tag, bytes]
    data: List[Block]

    md5: md5

    def __init__(self, f: IO[bytes]) -> None:
        self.f = f
        self.tags = {}
        self.data = []
        self.md5 = md5()

    def store(
        self,
        address: int,
        data: bytes,
        tags: Dict[Tag, bytes] = None,
        block_size: int = 256,
    ):
        if len(data) <= block_size:
            block = Block(self.family)
            block.tags = tags
            block.address = address
            block.data = data
            block.length = len(data)
            self.data.append(block)
            return
        for offs in range(0, len(data), block_size):
            block = Block(self.family)
            block.tags = tags
            data_part = data[offs : offs + block_size]
            block.address = address + offs
            block.data = data_part
            block.length = len(data_part)
            self.data.append(block)
            tags = None

    def put_str(self, tag: Tag, value: str):
        self.tags[tag] = value.encode("utf-8")

    def put_int32le(self, tag: Tag, value: int):
        self.tags[tag] = inttole32(value)

    def put_int16le(self, tag: Tag, value: int):
        self.tags[tag] = inttole16(value)

    def put_int8(self, tag: Tag, value: int):
        self.tags[tag] = intto8(value)

    def read(self, block_tags: bool = True, count: int = 0):
        while True:
            data = self.f.read(512)
            if len(data) not in [0, 512]:
                raise ValueError(f"Block size invalid ({len(data)})")
            if not len(data):
                break
            block = Block()
            block.decode(data)
            self.md5.update(data)

            if self.family and self.family != block.family:
                raise ValueError(f"Mismatched family ({self.family} != {block.family})")
            self.family = block.family

            if block.block_seq != self.seq:
                raise ValueError(
                    f"Mismatched sequence number ({self.seq} != {block.block_seq})"
                )
            self.seq += 1

            if block_tags or not block.length:
                self.tags.update(block.tags)
            self.data.append(block)

            if count and self.seq >= count:
                break

    def dump(self):
        info(f"Family: {self.family.short_name} / {self.family.description}")
        info(f"Tags:")
        for k, v in self.tags.items():
            if "\\x" not in str(v):
                v = v.decode()
            else:
                v = v.hex()
            info(f" - {k.name}: {v}")
        info(f"Block count: {len(self.data)}")
        info(f"Total binary size: {sum(bl.length for bl in self.data)}")

    @property
    def block_count(self) -> int:
        cnt = len(self.data)
        if self.tags:
            cnt += 1
        return cnt

    def write_header(self):
        comment = "Hi! Please visit https://docs.libretiny.eu/ to read specifications of this file format."
        bl = Block(self.family)
        bl.flags.has_tags = True
        bl.flags.not_main_flash = True
        bl.block_seq = 0
        bl.block_count = self.block_count
        bl.tags = self.tags

        data = bl.encode()
        # add comment in the unused space
        tags_len = align_up(Block.get_tags_length(bl.tags), 16)
        comment_len = len(comment)
        if 476 - 16 >= tags_len + comment_len:
            space = 476 - 16 - tags_len
            start = (space - comment_len) // 2
            start = align_down(start, 16)
            padding1 = b"\x00" * start
            padding2 = b"\x00" * (476 - tags_len - comment_len - start)
            data = (
                data[0 : 32 + tags_len]
                + padding1
                + comment.encode()
                + padding2
                + data[-4:]
            )

        self.f.write(data)

    def write(self):
        if self.tags and self.seq == 0:
            self.write_header()
            self.seq += 1

        for bl in self.data:
            bl.block_count = self.block_count
            bl.block_seq = self.seq
            self.f.write(bl.encode())
            self.seq += 1
