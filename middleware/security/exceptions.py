class AuthenticationError(Exception):
    pass


class InvalidTokenError(AuthenticationError):
    pass


class MissingTokenError(AuthenticationError):
    pass