from app.utils.clean import split_artists, clean_album
from tests.utils import reset_db


def setup_function():
    reset_db()


def test_split_artist():
    assert len(split_artists("Matsuoka Yoshitsugu, Kayano Ai")) == 2
    assert len(split_artists("Matsuoka Yoshitsugu")) == 1
    assert len(split_artists("Personative feat. MC NOREAJ")) == 2
    assert len(split_artists("Benjamin & mpi, Laco")) == 3
    assert len(split_artists("庭師D vs T.Ihashi")) == 2
    assert len(split_artists("Maozon vs. Primal Beast")) == 2


def test_clean_album():
    assert (
        clean_album("Tengen Toppa Gurren Lagann Original Soundtrack - CD01")
        == "Tengen Toppa Gurren Lagann Original Soundtrack"
    )
    assert (
        clean_album("OURPATH: Diverse Style The Best 2000-2005 disc 3")
        == "OURPATH: Diverse Style The Best 2000-2005"
    )
    assert (
        clean_album("FINAL FANTASY XII Original Soundtrack [Disc 3]")
        == "FINAL FANTASY XII Original Soundtrack"
    )
    assert (
        clean_album("FINAL FANTASY XII Original Soundtrack - [Disc 3]")
        == "FINAL FANTASY XII Original Soundtrack"
    )
    assert (
        clean_album("Ryu ga Gotoku OF THE END Original Soundtrack Vol.2")
        == "Ryu ga Gotoku OF THE END Original Soundtrack Vol.2"
    )
    assert (
        clean_album("DATE A LIVE: Ars Install Animate Gentei Set Tokuten Drama CD")
        == "DATE A LIVE: Ars Install Animate Gentei Set Tokuten Drama CD"
    )
    assert (
        clean_album("Super Eurobeat Vol. 221 - Extended Version")
        == "Super Eurobeat Vol. 221 - Extended Version"
    )
    assert clean_album("Super Eurobeat Vol. 92") == "Super Eurobeat Vol. 92"
