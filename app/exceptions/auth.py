from app.exceptions.base import AppException


class EmailAlreadyRegistered(AppException):
    status_code = 400
    detail = "Email already registered"


class UsernameAlreadyTaken(AppException):
    status_code = 400
    detail = "Username already taken"


class InvalidCredentials(AppException):
    status_code = 401
    detail = "Invalid credentials"


class InvalidTokenError(AppException):
    status_code = 401
    detail = "Invalid token"


class UserNotFoundError(AppException):
    status_code = 401
    detail = "User not found"