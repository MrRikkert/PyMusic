import pytest
from pony import orm
from pony.orm import db_session

from tests.utils import reset_db


def setup_function():
    reset_db()
