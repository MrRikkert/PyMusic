import re
from typing import List


def split_artists(artist: str) -> List[str]:
    # https://regex101.com/r/Aot9px/1
    return re.split(";|,|feat.|×|vs\.?|&", artist)


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
