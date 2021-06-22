from mixer.backend.pony import Mixer
from mixer.factory import GenFactory
from mixer.main import faker
from pony import orm

from app.db.base import db


class MyFactory(GenFactory):
    fakers = {
        ("name", str): lambda: faker.name().lower().replace(".", ""),
        ("title", str): lambda: faker.title().lower(),
    }


mixer = Mixer(factory=MyFactory)


def reset_db():
    """Resets db by dropping all columns with data and regenerating the schema.
    Note!
    ---
    Does not reset auto_increment keys!
    """
    try:
        db.bind(provider="sqlite", filename=":memory:")
        # db.bind(provider="sqlite", filename="test.sqlite", create_db=True)
    except orm.core.BindingError:
        # Logging not needed
        pass
    else:
        db.generate_mapping(check_tables=False)

    db.drop_all_tables(with_all_data=True)
    db.create_tables()
