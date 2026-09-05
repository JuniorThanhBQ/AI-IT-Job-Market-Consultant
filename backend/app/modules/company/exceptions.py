class CompanyError(Exception):
    pass


class CompanyNotFoundError(CompanyError):
    pass


class CompanyAlreadyExistsError(CompanyError):
    pass


class SuperuserRequiredError(CompanyError):
    pass
