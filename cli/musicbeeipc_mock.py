from shared.exceptions import PlatformException


class Mock:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, attr):
        def func(*args, **kwargs):
            raise PlatformException

        return func
