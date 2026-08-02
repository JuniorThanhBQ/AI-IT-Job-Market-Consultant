from enum import StrEnum


class CountryEnum(StrEnum):
    VIETNAM = "Vietnam"
    INDIA = "India"
    CHINA = "China"
    JAPAN = "Japan"
    SOUTH_KOREA = "South Korea"
    SINGAPORE = "Singapore"
    TAIWAN = "Taiwan"
    UNITED_STATES = "United States"
    CANADA = "Canada"
    UNITED_KINGDOM = "United Kingdom"
    GERMANY = "Germany"
    NETHERLANDS = "Netherlands"
    SWEDEN = "Sweden"
    FRANCE = "France"
    IRELAND = "Ireland"
    POLAND = "Poland"
    AUSTRALIA = "Australia"
    NEW_ZEALAND = "New Zealand"


class JobStatus(StrEnum):
    OPEN = "Open"
    CLOSED = "Closed"
    DRAFT = "Draft"
    EXPIRED = "Expired"


class SeniorityLevel(StrEnum):
    INTERN = "Intern"
    FRESHER = "Fresher"
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


class ConsultantMode(StrEnum):
    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    PERSONAL_STANDARD_EVALUATION = "PERSONAL_STANDARD_EVALUATION"
    JOB_RECOMMEND = "JOB_RECOMMEND"
    DEEP_ANALYSIS_EVALUATION = "DEEP_ANALYSIS_EVALUATION"


class CrawlWebsite(StrEnum):
    ITVIEC = "ITViec"
    TOPDEV = "TopDev"
    ITJOBS = "ITJobs"
    VIETNAMWORKS = "VietnamWorks"
    FPTJOBS = "FPTJobs"
