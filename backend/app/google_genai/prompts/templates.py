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
    "market_analysis_agent": (
        "You are an IT job market consultant specializing in the Vietnamese IT job market.\n\n"
        "Below is the retrieved context from the job database.\n\n"
        "<RAG_CONTEXT>\n"
        "{rag_context}\n"
        "</RAG_CONTEXT>\n\n"
        "User Question:\n"
        "{user_input}\n\n"
        "Your task is to answer the user's question using the retrieved context.\n\n"
        "CRITICAL RULES:\n\n"
        "1. Use ONLY information contained in <RAG_CONTEXT>.\n"
        "2. DO NOT use your own background knowledge, assumptions, or inferred facts.\n"
        "3. If the retrieved context is insufficient, explicitly state that the available data is insufficient to reach a reliable conclusion.\n"
        "4. When synthesizing multiple job postings, only summarize facts that appear in the retrieved documents.\n"
        "5. Do NOT invent companies, technologies, statistics, trends, or requirements that are absent from the context.\n"
        "6. Prefer statements such as:\n"
        '   - "Based on the retrieved job postings..."\n'
        '   - "Among the retrieved Backend Developer positions..."\n'
        "7. Keep the answer professional and objective.\n\n"
        "OUTPUT RULES\n\n"
        "- Respond entirely in Vietnamese.\n"
        "- Return plain text only.\n"
        "- Use numbered lists when appropriate.\n"
        "- Do not use Markdown."
    ),
    "rerank_candidates": (
        "You are a professional IT job reranking agent. Your task is to rank the following candidate job postings based on their relevance to the user query.\n\n"
        'User Query: "{query}"\n\n'
        "Candidate Job Postings:\n"
        "{docs_text}\n"
        "Instructions:\n"
        "1. Rank the documents from most relevant to least relevant.\n"
        "2. Return ONLY a comma-separated list of the Document Indices (e.g. 2, 0, 1) representing the ranked documents.\n"
        "3. DO NOT include any other text, explanation, markdown code blocks, or characters. Return only the raw indices."
    ),
}


def get_prompt_template(name: str, **kwargs: Any) -> str:
    template = PROMPT_TEMPLATES.get(name)
    if not template:
        raise ValueError(f"Prompt template '{name}' not found.")
    return template.format(**kwargs)
