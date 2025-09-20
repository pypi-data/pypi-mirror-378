# Copyright (c) Kuba Szczodrzyński 2022-06-10.

import json
from io import SEEK_CUR, BytesIO
from json import JSONDecodeError
from os import makedirs
from os.path import dirname, getmtime, isfile, join
from typing import IO, List, Optional, Union


def chname(path: str, name: str) -> str:
    """Change the basename of 'path' to 'name'."""
    return join(dirname(path), name)


def chext(path: str, ext: str) -> str:
    """Change the file extension of 'path' to 'ext' (without the dot)."""
    return path.rpartition(".")[0] + "." + ext


def isnewer(what: str, than: str) -> bool:
    """Check if 'what' is newer than 'than'.

    Returns False if 'what' is not a file.

    Returns True if 'than' is not a file.
    """
    if not isfile(what):
        return False
    if not isfile(than):
        return True
    return getmtime(what) > getmtime(than)


def readbin(file: str) -> bytes:
    """Read a binary file into a bytes object."""
    with open(file, "rb") as f:
        data = f.read()
    return data


def writebin(file: str, data: Union[bytes, BytesIO]):
    """Write data into a binary file."""
    with open(file, "wb") as f:
        if isinstance(data, BytesIO):
            f.write(data.getvalue())
        else:
            f.write(data)


# same as load_json
def readjson(file: str) -> Optional[Union[dict, list]]:
    """Read a JSON file into a dict or list."""
    if not isfile(file):
        return None
    with open(file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except JSONDecodeError:
            return None


def writejson(file: str, data: Union[dict, list]):
    """Write a dict or list to a JSON file."""
    makedirs(dirname(file), exist_ok=True)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t")


def readtext(file: str) -> str:
    """Read a text file into a string."""
    with open(file, "r", encoding="utf-8") as f:
        data = f.read()
    return data


def writetext(file: str, data: Union[str, bytes, List[str]]):
    """Write data into a text file."""
    with open(file, "w", encoding="utf-8") as f:
        if isinstance(data, bytes):
            f.write(data.decode())
        elif isinstance(data, list):
            f.write("\n".join(data))
            f.write("\n")
        else:
            f.write(data)


def peek(file: IO[bytes], size: int, seek: int = 0) -> Optional[bytes]:
    try:
        if seek:
            file.seek(seek, SEEK_CUR)
        data = file.read(size)
        file.seek(-len(data) - seek, SEEK_CUR)
        if len(data) == size:
            return data
    except OSError:
        pass
    return None
