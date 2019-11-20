import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.logic import tag as tag_logic
from app.db.models import TagDb
from tests.utils import reset_db
from app.exceptions import IntegrityError


def setup_function():
    reset_db()


@db_session
def test_get_tag_existing():
    db_tag = mixer.blend(TagDb)
    tag = tag_logic.get_tag(tag_type=db_tag.tag_type, value=db_tag.value)
    assert tag is not None
    assert tag.tag_type == db_tag.tag_type
    assert tag.value == db_tag.value


@db_session
def test_get_tag_non_existing():
    tag = tag_logic.get_tag(tag_type="hallo", value="test")
    assert tag is None


@db_session
def test_tag_exists_existing():
    tag = mixer.blend(TagDb)
    exists = tag_logic.tag_exists(tag_type=tag.tag_type, value=tag.value)
    assert exists


@db_session
def test_tag_exists_non_existing():
    exists = tag_logic.tag_exists(tag_type="type", value="value")
    assert not exists


@db_session
def test_add_tag():
    tag_logic.add_tag(tag_type="type", value="value")
    assert orm.count(a for a in TagDb) == 1


@db_session
def test_add_tag_existing():
    db_tag = mixer.blend(TagDb)
    with pytest.raises(IntegrityError):
        tag_logic.add_tag(tag_type=db_tag.tag_type, value=db_tag.value)


@db_session
def test_add_tag_existing_with_return_existing():
    db_tag = mixer.blend(TagDb)
    tag = tag_logic.add_tag(
        tag_type=db_tag.tag_type, value=db_tag.value, return_existing=True
    )
    assert orm.count(a for a in TagDb) == 1
    assert tag is not None
    assert db_tag.tag_type == tag.tag_type
    assert db_tag.value == tag.value
