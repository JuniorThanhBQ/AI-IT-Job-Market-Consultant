class UserError(Exception):
    pass


class UserAlreadyExistsError(UserError):
    pass


class InvalidCredentialsError(UserError):
    pass


class InactiveUserError(UserError):
    pass


class IncorrectPasswordError(UserError):
    pass


class PasswordMismatchError(UserError):
    pass


class SamePasswordError(UserError):
    pass


class InvalidVerificationTokenError(UserError):
    pass


class InvalidVerificationStatus(UserError):
    pass


class UserAlreadyVerifiedError(UserError):
    pass


class UserNotFoundError(UserError):
    pass


class InvalidConfirmPassword(UserError):
    pass
