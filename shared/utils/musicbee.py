# https://gist.github.com/lempamo/6e8977065da593e372e45d4c628e7fc7
from enum import Enum
from typing import List

global library


class Tags(Enum):
    title = 65
    artist = 32
    album = 30
    album_artist = 31
    genre = 59
    vocals = 46
    series = 47
    franchise = 48
    op_ed = 49
    season = 50
    alternate = 96
    type = 97
    sort_artist = 98
    language = 99


def __decode_from_7bit(data):
    """
    Decode 7-bit encoded int from str data
    """
    result = 0
    for index, char in enumerate(data):
        # byte_value = ord(char)
        result |= (char & 0x7F) << (7 * index)
        if char & 0x80 == 0:
            break
    return result


def __read_int(bytes_):
    return int.from_bytes(bytes_, byteorder="little", signed=True)


def __read_uint(bytes_):
    return int.from_bytes(bytes_, byteorder="little")


def __read_str(file):
    len_1 = file.read(1)
    if __read_uint(len_1) > 0x7F:
        len_2 = file.read(1)
        if __read_uint(len_2) > 0x7F:
            length = __decode_from_7bit(
                [__read_uint(len_1), __read_uint(len_2), __read_uint(file.read(1))]
            )
        else:
            length = __decode_from_7bit([__read_uint(len_1), __read_uint(len_2)])
    else:
        length = __read_uint(len_1)
    if length == 0:
        return None
    return file.read(length).decode("utf-8")


def read_file(library_location: str) -> List[dict]:  # noqa
    with open(library_location, "rb") as mbl:
        count = __read_int(mbl.read(4))

        if not count & 0xFF:
            raise

        count = count >> 8
        library = {"file_count": count, "files": []}

        while True:
            media = {"file_designation": __read_uint(mbl.read(1))}
            if media["file_designation"] == 1:
                break

            if 10 > media["file_designation"] > 1:
                media["status"] = __read_uint(mbl.read(1))
                if media["status"] > 6:
                    raise

                media["unknown_1"] = __read_uint(mbl.read(1))
                media["play_count"] = __read_uint(mbl.read(2))
                media["date_last_played"] = __read_int(mbl.read(8))
                media["skip_count"] = __read_uint(mbl.read(2))
                media["file_path"] = __read_str(mbl)
                if media["file_path"] == "":
                    raise

                media["file_size"] = __read_int(mbl.read(4))
                media["sample_rate"] = __read_int(mbl.read(4))
                media["channel_mode"] = __read_uint(mbl.read(1))
                media["bitrate_type"] = __read_uint(mbl.read(1))
                media["bitrate"] = __read_int(mbl.read(2))
                media["track_length"] = __read_int(mbl.read(4))
                media["date_added"] = __read_int(mbl.read(8))
                media["date_modified"] = __read_int(mbl.read(8))

                media["artwork"] = []
                while True:
                    art = {"type": __read_uint(mbl.read(1))}
                    if art["type"] > 253:
                        break

                    art["string_1"] = __read_str(mbl)
                    art["store_mode"] = __read_uint(mbl.read(1))
                    art["string_2"] = __read_str(mbl)
                    media["artwork"].append(art)

                media["tags_type"] = __read_uint(mbl.read(1))
                while True:
                    tag_code = __read_uint(mbl.read(1))
                    if tag_code == 0:
                        break
                    if tag_code == 255:
                        c = __read_int(mbl.read(2))
                        i = 0
                        media["cue"] = []

                        while i < c:
                            cue = {}
                            cue["a"] = __read_uint(mbl.read(1))
                            cue["b"] = __read_uint(mbl.read(2))
                            cue["c"] = __read_int(mbl.read(8))
                            cue["d"] = __read_uint(mbl.read(2))
                            media["cue"].append(cue)
                            i += 1
                        break

                    # media["tags"][str(tag_code)] = read_str(mbl)
                    try:
                        media[Tags(tag_code).name] = __read_str(mbl)
                        # media[str(tag_code)] = __read_str(mbl)
                    except ValueError:
                        pass

                library["files"].append(media)
            else:
                raise
        return library["files"]
