class ConsulteeProfileError(Exception):
    pass


class ProfileNotFoundError(ConsulteeProfileError):
    pass


class CVNotFoundError(ConsulteeProfileError):
    pass


class ProjectNotFoundError(ConsulteeProfileError):
    pass


class ProjectLimitExceededError(ConsulteeProfileError):
    pass


class InvalidProjectDateRangeError(ConsulteeProfileError):
    pass
