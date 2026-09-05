def build_company_vector_context(
    *,
    name: str,
    slogan: str | None = None,
    company_type: str | None = None,
    industry: str | None = None,
    size: str | None = None,
    country: str | None = None,
    location: str | None = None,
    description: str | None = None,
    working_days: str | None = None,
    overtime_policy: str | None = None,
) -> str:
    parts: list[str] = []
    if name:
        parts.append(f"Company Name: {name}.")
    if slogan:
        parts.append(f"Slogan: {slogan}.")
    if company_type:
        parts.append(f"Type: {company_type}.")
    if industry:
        parts.append(f"Industry: {industry}.")
    if size:
        parts.append(f"Size: {size}.")
    if country:
        parts.append(f"Country: {country}.")
    if location:
        parts.append(f"Location: {location}.")
    if working_days:
        parts.append(f"Working Days: {working_days}.")
    if overtime_policy:
        parts.append(f"Overtime Policy: {overtime_policy}.")
    if description:
        parts.append(f"Description: {description}.")
    return " ".join(parts)
