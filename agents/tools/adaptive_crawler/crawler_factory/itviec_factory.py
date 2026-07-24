# import json
import logging

# from urllib.parse import urljoin, urlparse
# from datetime import datetime
# from bs4 import BeautifulSoup
# from crawlee import Request
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

# from app.modules.job.repository import JobRepository
# from app.modules.company.repository import CompanyRepository
# from app.modules.company.models import Company, CompanyBenefit
# from ..crawler_adapter import JobAdapter
from .base_factory import BaseCrawlerFactory

logger = logging.getLogger(__name__)


class ITViecCrawlerFactory(BaseCrawlerFactory):
    def get_handler(self, session_factory):

        # async def _process_detail_page(
        #     context: AdaptivePlaywrightCrawlingContext, soup, url: str
        # ) -> None:
        #     context.log.info(f"Extracting detail page: {url}")
        #     title = None
        #     company_name = None
        #     skills = []
        #     description = ""
        #     requirements = ""
        #     benefits = []
        #     location = "Vietnam"
        #     salary = "Negotiable"

        #     json_ld_tags = soup.find_all("script", type="application/ld+json")
        #     for tag in json_ld_tags:
        #         try:
        #             data = json.loads(tag.string)
        #             if data.get("@type") == "JobPosting" or "JobPosting" in str(
        #                 data.get("@type")
        #             ):
        #                 title = data.get("title")
        #                 company_name = data.get("hiringOrganization", {}).get("name")
        #                 if data.get("skills"):
        #                     if isinstance(data["skills"], str):
        #                         skills = [
        #                             s.strip()
        #                             for s in data["skills"].split(",")
        #                             if s.strip()
        #                         ]
        #                     elif isinstance(data["skills"], list):
        #                         skills = data["skills"]

        #                 loc_data = data.get("jobLocation")
        #                 if loc_data:
        #                     if isinstance(loc_data, list) and len(loc_data) > 0:
        #                         loc_data = loc_data[0]
        #                     address = loc_data.get("address", {})
        #                     location = address.get("addressLocality", "Vietnam")

        #                 salary_val = data.get("baseSalary", {}).get("value", {})
        #                 if isinstance(salary_val, dict):
        #                     salary = salary_val.get("value", "Negotiable")
        #                 elif isinstance(salary_val, str):
        #                     salary = salary_val
        #                 break
        #         except Exception as e:
        #             context.log.error(f"Error parsing JSON-LD in ITViec: {e}")

        #     if not title:
        #         title_elem = soup.find("h1")
        #         title = (
        #             title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        #         )

        #     employer_info = soup.select_one(".job-show-employer-info h3 a")
        #     if employer_info:
        #         company_name = employer_info.get_text(strip=True)
        #         company_href = employer_info.get("href")
        #         if company_href:
        #             company_url = urljoin(url, company_href)
        #             await context.add_requests(
        #                 [Request.from_url(url=company_url, label="company")]
        #             )
        #     else:
        #         if not company_name:
        #             company_name = "Unknown Company"

        #     content_section = soup.select_one(".job-content")
        #     nice_to_have = []
        #     if content_section:
        #         current_section = None
        #         for child in content_section.descendants:
        #             if child.name in ["h2", "h3"]:
        #                 header_text = child.get_text(strip=True).lower()
        #                 if (
        #                     "description" in header_text
        #                     or "about the role" in header_text
        #                     or "job summary" in header_text
        #                 ):
        #                     current_section = "desc"
        #                 elif (
        #                     "skills" in header_text
        #                     or "experience" in header_text
        #                     or "frontend" in header_text
        #                     or "backend" in header_text
        #                 ):
        #                     current_section = "req"
        #                 elif (
        #                     "preferred" in header_text
        #                     or "nice to have" in header_text
        #                     or "expectation" in header_text
        #                 ):
        #                     current_section = "nice"
        #                 elif "love working" in header_text or "benefit" in header_text:
        #                     current_section = "benefits"
        #                 else:
        #                     current_section = None
        #             elif child.name in ["p", "ul", "li"] and current_section:
        #                 if child.name in ["ul", "ol"]:
        #                     continue
        #                 text = child.get_text(strip=True)
        #                 if not text:
        #                     continue
        #                 if current_section == "desc":
        #                     description += text + "\n"
        #                 elif current_section == "req":
        #                     requirements += text + "\n"
        #                 elif current_section == "nice":
        #                     nice_to_have.append(text)
        #                 elif current_section == "benefits":
        #                     benefits.append(text)

        #     domain_div = soup.find(
        #         lambda tag: (
        #             tag.name == "div"
        #             and "Job Domain:" in tag.get_text()
        #             and not tag.find("div")
        #         )
        #     )
        #     domains = []
        #     if domain_div:
        #         sibling = domain_div.find_next_sibling("div")
        #         if sibling:
        #             domains = [
        #                 d.get_text(strip=True)
        #                 for d in sibling.select(".itag")
        #                 if d.get_text(strip=True)
        #             ]

        #     raw_data = {
        #         "title": title,
        #         "company": company_name,
        #         "url": url,
        #         "description": description or "No description provided",
        #         "requirements": requirements or "No requirements specified",
        #         "benefits": benefits,
        #         "location": location,
        #         "salary": salary,
        #         "skills": skills,
        #         "nice_to_have": nice_to_have,
        #         "domains": domains,
        #     }

        #     is_updater = context.request.label == "updater_detail"
        #     if is_updater:
        #         is_not_found = False
        #         if context.http_response and context.http_response.status_code in [
        #             404,
        #             410,
        #         ]:
        #             is_not_found = True
        #         elif context._page:
        #             current_url = context.page.url
        #             if urlparse(current_url).path != urlparse(url).path:
        #                 if (
        #                     "/it-jobs/" not in current_url
        #                     and "/detail-jobs/" not in current_url
        #                 ):
        #                     is_not_found = True

        #         page_text = soup.get_text().lower()
        #         is_expired_text = any(
        #             msg in page_text
        #             for msg in [
        #                 "ngưng nhận hồ sơ",
        #                 "hết hạn",
        #                 "job expired",
        #                 "posting expired",
        #             ]
        #         )

        #         if is_not_found or is_expired_text:
        #             context.log.info(
        #                 f"Job posting not found or expired: {url}. Marking as Closed."
        #             )
        #             async with session_factory() as session:
        #                 repo = JobRepository(session)
        #                 existing = await repo.get_by_url(url)
        #                 if existing:
        #                     existing.status = "Closed"
        #                     existing.updated_date = datetime.utcnow()
        #                     session.add(existing)
        #                     await session.commit()
        #             return

        #         if (
        #             not title
        #             or title.strip().lower() in ["unknown title", "no title", ""]
        #             or not description
        #             or description.strip().lower()
        #             in ["no description provided", "not provided", ""]
        #         ):
        #             context.log.warning(
        #                 f"New parsed data is null/empty for URL {url} due to extraction error. Keeping old record."
        #             )
        #             return

        #     job = JobAdapter.to_job(raw_data, "itviec")
        #     async with session_factory() as session:
        #         repo = JobRepository(session)
        #         await repo.save(job)
        #         await session.commit()
        #     context.log.info(
        #         f"Successfully saved ITViec Job: {title} at {company_name}"
        #     )

        # async def _process_company_page(
        #     context: AdaptivePlaywrightCrawlingContext, soup, url: str
        # ) -> None:
        #     context.log.info(f"Extracting company page: {url}")
        #     name_elem = soup.find("h1")
        #     name = name_elem.get_text(strip=True) if name_elem else ""
        #     if not name:
        #         context.log.warning(f"Company profile has no name: {url}")
        #         return

        #     industry = "Unknown"
        #     size = "Unknown"
        #     company_type = "Unknown"
        #     country = "Unknown"
        #     location = "Vietnam"
        #     working_days = None
        #     overtime_policy = None
        #     slogan = None
        #     description = ""
        #     website = ""
        #     benefits_list = []

        #     working_days_div = soup.find(
        #         "div", string=lambda s: s and "Working days" in s
        #     )
        #     if working_days_div:
        #         val_div = working_days_div.find_next_sibling(
        #             "div", class_="normal-text"
        #         )
        #         if val_div:
        #             working_days = val_div.get_text(strip=True)

        #     overtime_div = soup.find(
        #         "div", string=lambda s: s and "Overtime policy" in s
        #     )
        #     if overtime_div:
        #         val_div = overtime_div.find_next_sibling("div", class_="normal-text")
        #         if val_div:
        #             overtime_policy = val_div.get_text(strip=True)

        #     type_div = soup.find("div", string=lambda s: s and "Company type" in s)
        #     if type_div:
        #         val_div = type_div.find_next_sibling("div", class_="normal-text")
        #         if val_div:
        #             company_type = val_div.get_text(strip=True)

        #     ind_div = soup.find("div", string=lambda s: s and "Company industry" in s)
        #     if ind_div:
        #         val_div = ind_div.find_next_sibling("div")
        #         if val_div:
        #             industry = val_div.get_text(strip=True)

        #     size_div = soup.find("div", string=lambda s: s and "Company size" in s)
        #     if size_div:
        #         val_div = size_div.find_next_sibling("div", class_="normal-text")
        #         if val_div:
        #             size = val_div.get_text(strip=True)

        #     country_div = soup.find("div", string=lambda s: s and "Country" in s)
        #     if country_div:
        #         sibling = country_div.find_next_sibling("div")
        #         if sibling:
        #             span_el = sibling.find("span")
        #             if span_el:
        #                 country = span_el.get_text(strip=True)

        #     overview_hdr = soup.find(
        #         "h2", string=lambda s: s and "Company overview" in s
        #     )
        #     if overview_hdr:
        #         overview_div = overview_hdr.find_next_sibling("div", class_="paragraph")
        #         if overview_div:
        #             desc_text = overview_div.get_text(separator="\n", strip=True)
        #             lines = [
        #                 line.strip() for line in desc_text.split("\n") if line.strip()
        #             ]
        #             if lines:
        #                 slogan = lines[0]
        #                 description = "\n".join(lines[1:])

        #     website_div = soup.find("div", attrs={"data-redirect-url-url-value": True})
        #     if website_div:
        #         website = website_div.get("data-redirect-url-url-value", "")

        #     location_div = soup.find(
        #         "div",
        #         class_="location",
        #         attrs={"data-employers--location-target": "place"},
        #     )
        #     if location_div:
        #         loc_val = location_div.find("span", class_="text-break")
        #         if loc_val:
        #             location = loc_val.get_text(strip=True)

        #     benefits_hdr = soup.find(
        #         "h2", string=lambda s: s and "love working here" in s.lower()
        #     )
        #     if benefits_hdr:
        #         benefits_container = benefits_hdr.find_next("ul")
        #         if benefits_container:
        #             for li in benefits_container.find_all("li"):
        #                 txt = li.get_text(strip=True)
        #                 if txt:
        #                     benefits_list.append(CompanyBenefit(name=txt))

        #     vector_context = f"Company Name: {name}. Industry: {industry}. Size: {size}. Location: {location}. Description: {description}."
        #     company_obj = Company(
        #         name=name,
        #         industry=industry,
        #         size=size,
        #         location=location,
        #         addresses=[location],
        #         description=description,
        #         website=website,
        #         slogan=slogan,
        #         company_type=company_type,
        #         country=country,
        #         working_days=working_days,
        #         overtime_policy=overtime_policy,
        #         vector_context=vector_context,
        #         benefits=benefits_list,
        #     )

        #     async with session_factory() as session:
        #         company_repo = CompanyRepository(session)
        #         await company_repo.save(company_obj)
        #         await session.commit()
        #     context.log.info(f"Successfully saved company information for: {name}")

        # async def _process_list_page(
        #     context: AdaptivePlaywrightCrawlingContext, soup, url: str
        # ) -> None:
        #     context.log.info(f"Parsing list page for URLs: {url}")
        #     job_cards = soup.select(".job-card")
        #     enqueued_count = 0

        #     for card in job_cards:
        #         slug = card.get(
        #             "data-search--job-selection-job-slug-value"
        #         ) or card.get("data-job-slug-value")
        #         if slug:
        #             detail_url = urljoin("https://itviec.com", f"/it-jobs/{slug}")
        #             await context.add_requests(
        #                 [Request.from_url(url=detail_url, label="detail")]
        #             )
        #             enqueued_count += 1

        #     context.log.info(
        #         f"Enqueued {enqueued_count} job detail pages from ITViec list."
        #     )

        #     if enqueued_count > 0:
        #         from urllib.parse import parse_qs, urlencode, urlunparse

        #         parsed = urlparse(url)
        #         qs = parse_qs(parsed.query)
        #         current_page = 1
        #         if "page" in qs:
        #             try:
        #                 current_page = int(qs["page"][0])
        #             except ValueError:
        #                 pass

        #         if current_page < 15:
        #             qs["page"] = [str(current_page + 1)]
        #             next_url = urlunparse(
        #                 (
        #                     parsed.scheme,
        #                     parsed.netloc,
        #                     parsed.path,
        #                     parsed.params,
        #                     urlencode(qs, doseq=True),
        #                     parsed.fragment,
        #                 )
        #             )
        #             context.log.info(f"Enqueuing next ITViec list page: {next_url}")
        #             await context.add_requests(
        #                 [Request.from_url(url=next_url, label="list")]
        #             )

        async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
            url = context.request.url

            context.log.info(
                f"[TESTING] ITViec handler reached! URL: {url} (label: {context.request.label})"
            )
            logger.info(
                f"[TESTING] ITViec handler executed on Celery worker for URL: {url}"
            )

            # await self.apply_delay()

            # context.log.info(f"Crawling ITViec: {url} (label: {context.request.label})")

            # html_content = ""
            # if context._page:
            #     html_content = await context.page.content()
            # elif context.http_response:
            #     html_content = (await context.http_response.read()).decode(
            #         "utf-8", errors="ignore"
            #     )

            # if not html_content:
            #     context.log.warning(f"Empty content for URL: {url}")
            #     return

            # soup = BeautifulSoup(html_content, "html.parser")
            # is_detail = context.request.label in ["detail", "updater_detail"] or (
            #     "/it-jobs/" in url
            #     and any(char.isdigit() for char in url.split("/")[-1])
            # )
            # is_company = (
            #     context.request.label == "company"
            #     or "/companies/" in url
            #     or "/nha-tuyen-dung/" in url
            # )

            # if is_detail:
            #     await _process_detail_page(context, soup, url)
            # elif is_company:
            #     await _process_company_page(context, soup, url)
            # else:
            #     await _process_list_page(context, soup, url)

        return handler
