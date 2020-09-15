from pony import orm

db = orm.Database()


@db.on_connect(provider="sqlite")
def sqlite_case_sensitivity(db, connection):
    cursor = connection.cursor()
    cursor.execute("PRAGMA case_sensitive_like = OFF")

