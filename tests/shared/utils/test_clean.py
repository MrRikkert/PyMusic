from shared.utils.clean import (
    clean_album,
    clean_artist,
    reverse_artist,
    romanise_text,
    split_artists,
    get_character_voice,
)
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


def test_clean_artist():
    assert clean_artist("Nishikino Maki (CV. Pile)") == "Nishikino Maki"
    assert clean_artist("Cocoa [CV. Ayane Sakura]") == "Cocoa"
    assert clean_artist("BNSI [中西哲一]") == "BNSI"


def test_clean_artist_return_character_voice():
    artist, cv = clean_artist("Nishikino Maki (CV. Pile)", return_character_voice=True)
    assert artist == "Nishikino Maki"
    assert cv == "Pile"

    artist, cv = clean_artist("Cocoa [CV. Ayane Sakura]", return_character_voice=True)
    assert artist == "Cocoa"
    assert cv == "Ayane Sakura"


def test_get_character_voice():
    assert get_character_voice("Nishikino Maki (CV. Pile)") == "Pile"
    assert get_character_voice("Cocoa [CV. Ayane Sakura]") == "Ayane Sakura"


def test_reverse_artist():
    assert reverse_artist("Keiichi Okabe") == "Okabe Keiichi"
    assert reverse_artist("first second third") is None
    assert reverse_artist("first") is None


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


def test_romanise_text():
    assert romanise_text("岡部啓一") == "okabe keiichi"
    assert romanise_text("John Doe") == "John Doe"
