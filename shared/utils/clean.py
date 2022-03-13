import re
from typing import List, Tuple, Union

import pykakasi

kks = pykakasi.kakasi()


def split_artists(artist: str) -> List[str]:
    # https://regex101.com/r/Aot9px/1
    artists = re.split(r";|,|feat.|×|vs\.?|&", artist)
    # Due to Musicbee problems, an artist is sometimes an empty/whitespace string
    # This removes these artists
    return [a for a in artists if a.strip()]


def romanise_text(text: str) -> str:
    is_japanese = re.search(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]",
        text,
    )
    if is_japanese:
        result = [result["hepburn"] for result in kks.convert(text)]
        return " ".join(result).strip()
    return text


def clean_artist(
    artist: str, romanise: bool = True, return_character_voice=False
) -> Union[str, Tuple[str, str]]:
    # https://regex101.com/r/qrmQEh/1

    # Remove everything between brackets
    _artist = re.sub(
        r"[\(\[](?:(?:c\.?v\.?)?(?:v\.?o\.?)?(?:)?[.:：])?(.*)[\)\]]",
        "",
        artist,
        flags=re.IGNORECASE,
    ).strip()
    if romanise:
        _artist = romanise_text(_artist)
    if return_character_voice:
        return _artist, get_character_voice(artist, romanise=romanise)
    return _artist


def get_character_voice(artist: str, romanise: bool = True) -> str:
    # https://regex101.com/r/qrmQEh/1
    cv = re.search(
        r"[\(\[](?:(?:c\.?v\.?)?(?:v\.?o\.?)?(?:)?[.:：])?(.*)[\)\]]",
        artist,
        flags=re.IGNORECASE,
    )
    if cv:
        cv = cv.group(1).strip()
        if romanise:
            cv = romanise_text(cv)
    return cv


def reverse_artist(artist: str) -> str:
    names = artist.split(" ")
    if not len(names) == 2:
        return None

    return " ".join(reversed(names)).strip()


def clean_album(album: str) -> str:
    # https://regex101.com/r/hjgeTD/4
    return re.sub(
        r"""
        (
            (-\s*)?             # match optional leading '-'
            [
                \(\[]           # match opening of '(' or '['
                (disc|cd|disk)  # match words like disk and cd
                .*              # match any character after the word and before the closing
                [\)\]
            ]                   # match closing of '(' or '['
        )$ |
        (
            (-\s)?              # match optional leading '-'
            (cd|disk|disc)      # match words like disk and cd
            .*                 # match any character after the word
            \d{1,}              # match any digit
        )
        """,
        "",
        album,
        flags=re.VERBOSE | re.IGNORECASE,
    ).strip()
