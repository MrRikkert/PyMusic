from pony import orm

from app.db.base import db


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
        pass
    else:
        db.generate_mapping(check_tables=False)

    db.drop_all_tables(with_all_data=True)
    db.create_tables()
