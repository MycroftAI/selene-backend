"""Define custom exceptions used in Selene APIs and scripts"""


class NotModifiedException(Exception):
    """Raise this exception when a request contains an etag found in cache.

    The Flask blueprint will catch this exception and return a HTTP 304 code.
    """
    pass
