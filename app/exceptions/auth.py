class AuthException(Exception):
    pass


class EmailAlreadyRegistered(AuthException):
    pass


class UsernameAlreadyTaken(AuthException):
    pass


class InvalidCredentials(AuthException):
    pass