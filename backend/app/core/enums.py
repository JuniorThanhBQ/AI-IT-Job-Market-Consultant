from enum import StrEnum


class JobStatus(StrEnum):
    OPEN = "Open"
    CLOSED = "Closed"
    DRAFT = "Draft"
    EXPIRED = "Expired"


class SeniorityLevel(StrEnum):
    INTERN = "Intern"
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"
    UNKNOWN = "Unknown"


class WorkingModel(StrEnum):
    ONSITE = "Onsite"
    HYBRID = "Hybrid"
    REMOTE = "Remote"
    OTHER = "Other"


class CompanyType(StrEnum):
    PRODUCT = "Product"
    OUTSOURCING = "Outsourcing"
    CONSULTING = "Consulting"
    AGENCY = "Agency"
    NON_PROFIT = "Non-Profit"
    OTHER = "Other"


class Currency(StrEnum):
    VND = "VND"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    SGD = "SGD"
