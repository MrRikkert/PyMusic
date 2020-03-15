import pytest
from pylast import WSError

from app.exceptions import LastFmError
from app.utils import lastfm


# @pytest.mark.lastfm
def test_get_scrobbles():
    scrobbles = lastfm.get_scrobbles("MrRikkerts", limit=10, time_to="1584285600")
    assert scrobbles is not None
    assert len(scrobbles) == 10
    assert scrobbles[0].track.title == "Dispossession / Piano Ver."


def test_get_scrobbles_no_username():
    with pytest.raises(TypeError):
        lastfm.get_scrobbles(limit=1)


def test_get_scrobbles_empty_username():
    with pytest.raises(ValueError):
        lastfm.get_scrobbles(username="", limit=1)


def test_get_scrobbles_non_exisiting_user():
    with pytest.raises(WSError):
        with pytest.raises(LastFmError):
            lastfm.get_scrobbles(username="fgdfgsdgdgfdgfgf3t345gfd", limit=1)
