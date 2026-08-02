from typing import Any

PROMPT_TEMPLATES: dict[str, str] = {
    "cv_screening": (
        "You are an expert technical recruiter. Analyze the following candidate CV and match it "
        "against the target job description. Identify core strengths, key gaps, and a compatibility score.\n\n"
        "Job Description:\n{job_description}\n\n"
        "Candidate CV:\n{candidate_cv}\n\n"
        "Format the output using clear markdown sections."
    ),
    "market_analysis": (
        "You are an IT job market consultant. Analyze the provided dataset/trends for {market_region}. "
        "Highlight high-demand skills, salary bands, and future demand forecasts.\n\n"
        "Data context:\n{market_data}\n\n"
        "Return a professional consulting brief."
    ),
}


def get_prompt_template(name: str, **kwargs: Any) -> str:
    template = PROMPT_TEMPLATES.get(name)
    if not template:
        raise ValueError(f"Prompt template '{name}' not found.")
    return template.format(**kwargs)
