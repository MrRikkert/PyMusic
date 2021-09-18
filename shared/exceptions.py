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


class PlatformException(Exception):
    """Raise when a function is unsupported on the platform

    ## examples:
    - Windows package on Linux/macOS
    """
