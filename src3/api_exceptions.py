# add captcha exception
# add session expired exception

class TWException(Exception):
    """The base Exception that all other exception classes extend."""

class SessionException(TWException):
    """Indicate exception that involve expired sessions."""

