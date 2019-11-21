class IntegrityError(Exception):
    """Raise when an integrity check fails

    ## examples:
    - Object already exists
    - Contraint failed
    """
