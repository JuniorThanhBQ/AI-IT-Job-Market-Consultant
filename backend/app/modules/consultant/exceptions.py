class ConsultantError(Exception):
    pass


class InvalidConsultantInputError(ConsultantError):
    pass


class ConsultantHistoryNotFoundError(ConsultantError):
    pass
