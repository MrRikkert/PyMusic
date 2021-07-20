class IntegrityError(Exception):
    """Raise when an integrity check fails

    ## examples:
    - Object already exists
    - Contraint failed
    """


class LastFmError(Exception):
    """Raise when LastFM raises an error

    ## examples:
    - user not found
    """
