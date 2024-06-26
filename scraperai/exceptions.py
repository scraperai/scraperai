
class NotFoundError(Exception):
    """Raises when could find an answer"""


class NoCodeFoundError(Exception):
    """
    Raised when no code is found in the response.

    Args:
        Exception (Exception): NoCodeFoundError
    """
