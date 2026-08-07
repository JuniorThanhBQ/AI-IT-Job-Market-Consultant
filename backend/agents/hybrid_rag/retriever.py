from typing import Any


def build_rag_context(top_documents: list[Any]) -> str:
    rag_context = ""
    for idx, doc in enumerate(top_documents, start=1):
        if len(doc) == 3:
            job, company, distance = doc
        else:
            job, company = doc
            distance = None

        rag_context += f"--- Document {idx} ---\n"
        if distance is not None:
            rag_context += f"  Match Distance (Cosine Similarity): {distance:.6f}\n"

        rag_context += "Company Details:\n"
        rag_context += f"  Name: {company.name}\n"
        rag_context += f"  Industry: {company.industry}\n"
        if company.size:
            rag_context += f"  Size: {company.size}\n"
        if company.location:
            rag_context += f"  Location: {company.location}\n"
        if company.website:
            rag_context += f"  Website: {company.website}\n"
        if company.company_type:
            company_type_val = getattr(
                company.company_type, "value", str(company.company_type)
            )
            rag_context += f"  Type: {company_type_val}\n"
        if company.addresses:
            rag_context += f"  Addresses: {', '.join(company.addresses)}\n"
        if company.working_days:
            rag_context += f"  Working Days: {company.working_days}\n"
        if company.overtime_policy:
            rag_context += f"  Overtime Policy: {company.overtime_policy}\n"

        rag_context += "Job Details:\n"
        rag_context += f"  Title: {job.title}\n"
        seniority_val = getattr(job.seniority, "value", str(job.seniority))
        rag_context += f"  Seniority: {seniority_val}\n"

        currency_val = getattr(job.currency, "value", str(job.currency))
        rag_context += f"  Salary: {job.min_salary} - {job.max_salary} {currency_val}\n"
        rag_context += f"  Working Hours: {job.working_hours}\n"

        working_model_val = getattr(job.working_model, "value", str(job.working_model))
        rag_context += f"  Working Model: {working_model_val}\n"

        if job.responsibilities:
            rag_context += "  Responsibilities:\n"
            for resp in job.responsibilities[:5]:
                rag_context += f"    - {resp}\n"
        if job.required_qualifications:
            rag_context += "  Required Qualifications:\n"
            for req in job.required_qualifications[:5]:
                rag_context += f"    - {req}\n"
        if job.nice_to_have:
            rag_context += "  Nice to Have:\n"
            for nth in job.nice_to_have[:10]:
                rag_context += f"    - {nth}\n"
        if job.domains:
            rag_context += f"  Domains: {', '.join(job.domains)}\n"
        if job.skills:
            skill_names = [skill.name for skill in job.skills]
            rag_context += f"  Skills: {', '.join(skill_names)}\n"
        rag_context += f"  URL: {job.url}\n\n"
    return rag_context
