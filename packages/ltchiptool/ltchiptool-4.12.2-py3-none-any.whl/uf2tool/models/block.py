# Copyright (c) Kuba Szczodrzyński 2022-05-27.

from math import ceil
from typing import Dict

from ltchiptool import Family
from ltchiptool.util.intbin import align_up, intto8, inttole24, inttole32, letoint

from .enums import Tag
from .flags import Flags


class Block:
    flags: Flags

    address: int = 0
    length: int = 0

    block_seq: int = 0
    block_count: int = 0

    file_size: int = 0
    family: Family

    data: bytes = None
    md5_data: bytes = None
    tags: Dict[Tag, bytes] = None
    padding: bytes = None

    def __init__(self, family: Family = None) -> None:
        self.flags = Flags()
        self.family = family
        self.tags = {}
        self.flags.has_family_id = not not self.family

    def encode(self) -> bytes:
        self.flags.has_tags = not not self.tags
        self.length = self.data and len(self.data) or 0
        # UF2 magic 1 and 2
        data = b"\x55\x46\x32\x0a\x57\x51\x5d\x9e"
        # encode integer variables
        data += inttole32(self.flags.encode())
        data += inttole32(self.address)
        data += inttole32(self.length)
        data += inttole32(self.block_seq)
        data += inttole32(self.block_count)
        if self.flags.file_container:
            data += inttole32(self.file_size)
        elif self.flags.has_family_id:
            data += inttole32(self.family.id)
        else:
            data += b"\x00\x00\x00\x00"
        if not self.data:
            self.data = b""
        # append tags
        tags = b""
        if self.flags.has_tags and self.tags:
            for k, v in self.tags.items():
                tag_size = 4 + len(v)
                tags += intto8(tag_size)
                tags += inttole24(k.value)
                tags += v
                tag_size %= 4
                if tag_size:
                    tags += b"\x00" * (4 - tag_size)
        # append block data with padding
        data += self.data
        data += tags + b"\x00\x00\x00\x00"
        if self.padding:
            if len(self.padding) > 512 - 4 - len(data):
                raise ValueError("Padding too long")
            data += self.padding
        data += b"\x00" * (512 - 4 - len(data))
        data += b"\x30\x6f\xb1\x0a"  # magic 3
        return data

    def decode(self, data: bytes):
        # check block size
        if len(data) != 512:
            raise ValueError(f"Invalid block size ({len(data)})")
        # check Magic 1
        if letoint(data[0:4]) != 0x0A324655:
            raise ValueError(f"Invalid Magic 1 ({data[0:4]})")
        # check Magic 2
        if letoint(data[4:8]) != 0x9E5D5157:
            raise ValueError(f"Invalid Magic 2 ({data[4:8]})")
        # check Magic 3
        if letoint(data[508:512]) != 0x0AB16F30:
            raise ValueError(f"Invalid Magic 3 ({data[508:512]})")

        self.flags.decode(letoint(data[8:12]))
        self.address = letoint(data[12:16])
        self.length = letoint(data[16:20])
        self.block_seq = letoint(data[20:24])
        self.block_count = letoint(data[24:28])
        if self.flags.file_container:
            self.file_size = letoint(data[28:32])
        if self.flags.has_family_id:
            self.family = Family.get(id=letoint(data[28:32]))

        if self.flags.has_md5:
            self.md5_data = data[484:508]  # last 24 bytes of data[]

        # decode tags
        self.tags = {}
        if self.flags.has_tags:
            tags = data[32 + self.length : -4]
            i = 0
            while i < len(tags):
                length = tags[i]
                if not length:
                    tags = tags[i + 4 :]
                    break
                tag_type = letoint(tags[i + 1 : i + 4])
                tag_data = tags[i + 4 : i + length]
                self.tags[Tag(tag_type)] = tag_data
                i += length
                i = int(ceil(i / 4) * 4)
            self.padding = tags

        self.data = data[32 : 32 + self.length]

    @staticmethod
    def get_tags_length(tags: Dict[Tag, bytes]) -> int:
        if not tags:
            return 0
        out = 0
        # add tag headers
        out += 4 * len(tags)
        # add all tag lengths, padded to 4 bytes
        out += sum(align_up(l, 4) for l in map(len, tags.values()))
        # add final 0x00 tag
        out += 4
        return out

    def __str__(self) -> str:
        flags = self.flags
        address = hex(self.address)
        length = hex(self.length)
        block_seq = self.block_seq
        block_count = self.block_count
        file_size = self.file_size
        family = self.family.short_name
        tags = [(k.name, v) for k, v in self.tags.items()]
        return f"Block[{block_seq}/{block_count}](flags={flags}, address={address}, length={length}, file_size={file_size}, family={family}, tags={tags})"
