from app.utils import lastfm
import pytest


@pytest.mark.lastfm
def test_get_scrobbles():
    scrobbles = lastfm.get_scrobbles("MrRikkerts")
    assert scrobbles is not None
