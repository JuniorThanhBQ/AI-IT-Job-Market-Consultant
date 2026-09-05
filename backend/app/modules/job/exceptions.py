class JobError(Exception):
    pass


class JobNotFoundError(JobError):
    pass


class SuperuserRequiredError(JobError):
    pass


class InvalidSalaryRangeError(JobError):
    pass
