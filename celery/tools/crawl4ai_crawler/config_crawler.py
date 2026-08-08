import os
import tempfile

os.environ["CRAWL4AI_BASE_DIR"] = os.path.join(tempfile.gettempdir(), ".crawl4ai")
os.environ["CRAWL4AI_BASE_DIRECTORY"] = os.path.join(tempfile.gettempdir(), ".crawl4ai")
if not os.access(os.path.expanduser("~"), os.W_OK):
    os.environ["HOME"] = tempfile.gettempdir()

from pydantic import BaseModel
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from app.utils.embeddings import get_gemini_api_key


class JobLinkSchema(BaseModel):
    url: str


class JobSchema(BaseModel):
    title: str
    company_name: str
    description: str
    location: str
    salary: str
    requirements: list[str]
    nice_to_have: list[str]
    benefits: list[str]
    skills: list[str]
    apply_url: str


URLS = [
    "https://fptjobs.com/tuyen-dung?tukhoa=&nganhnghe=4&khuvuc=",
]

BROWSER_CONFIG = BrowserConfig(
    headless=True,
    enable_stealth=True,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
)

LLM_CONFIG = LLMConfig(
    provider="gemini/gemini-2.5-flash", api_token=get_gemini_api_key()
)

LIST_RUN_CONFIG = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    magic=True,
    page_timeout=80000,
    extraction_strategy=LLMExtractionStrategy(
        llm_config=LLM_CONFIG,
        schema=JobLinkSchema.model_json_schema(),
        instruction="Extract the URLs of the individual job detail pages. Return a list of objects containing the url.",
    ),
)

DETAIL_RUN_CONFIG = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    magic=True,
    page_timeout=45000,
    wait_until="commit",
    extraction_strategy=LLMExtractionStrategy(
        llm_config=LLM_CONFIG,
        schema=JobSchema.model_json_schema(),
        instruction="Extract all detailed information about this specific job posting",
    ),
)

MAX_JOBS_TO_CRAWL = 3
