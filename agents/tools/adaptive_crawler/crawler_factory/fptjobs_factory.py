# import json
# import logging
# from urllib.parse import urljoin
# from bs4 import BeautifulSoup
# from crawlee import Request
# from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

# from app.modules.job.repository import JobRepository
# from ..crawler_adapter import JobAdapter
# from .base_factory import BaseCrawlerFactory

# logger = logging.getLogger(__name__)


# class FPTJobsCrawlerFactory(BaseCrawlerFactory):
#     def get_handler(self, session_factory):

#         async def _process_detail_page(
#             context: AdaptivePlaywrightCrawlingContext, soup, url: str
#         ) -> None:
#             context.log.info(f"Extracting detail page: {url}")
#             title = None
#             company_name = "FPT Telecom"
#             company_desc = ""
#             description = ""
#             requirements = ""
#             benefits = []
#             location = "Vietnam"
#             salary = "Negotiable"
#             working_hours = "FULL_TIME"
#             expired_date = None

#             json_ld_tags = soup.find_all("script", type="application/ld+json")
#             for tag in json_ld_tags:
#                 try:
#                     data = json.loads(tag.string)
#                     if data.get("@type") == "JobPosting":
#                         title = data.get("title")
#                         salary_val = data.get("baseSalary", {}).get("value", {})
#                         if isinstance(salary_val, dict):
#                             salary = salary_val.get("description", "Negotiable")

#                         loc_data = data.get("jobLocation", {})
#                         if loc_data and "address" in loc_data:
#                             location = loc_data["address"].get(
#                                 "addressLocality", "Vietnam"
#                             )

#                         expired_date = data.get("validThrough")
#                 except Exception as e:
#                     context.log.error(f"Error parsing JSON-LD: {e}")
#             header_el = soup.select_one(".top-head-detail h1")
#             if header_el:
#                 title = header_el.get_text(strip=True)

#             desc_el = soup.select_one(".content-detail-job")
#             if desc_el:
#                 description = desc_el.get_text(strip=True)

#             req_el = soup.select_one(".content-detail-job-req")
#             if req_el:
#                 requirements = req_el.get_text(strip=True)

#             benefit_els = soup.select(".benefit-job-item")
#             for b in benefit_els:
#                 benefits.append(b.get_text(strip=True))

#             loc_el = soup.select_one(".address-detail-job")
#             if loc_el:
#                 location = loc_el.get_text(strip=True)

#             sal_el = soup.select_one(".salary-detail-job")
#             if sal_el:
#                 salary = sal_el.get_text(strip=True)

#             if not title:
#                 title_meta = soup.find("meta", property="og:title")
#                 if title_meta:
#                     title = title_meta.get("content", "").strip()

#             raw_data = {
#                 "title": title or "Software Engineer",
#                 "company": company_name,
#                 "company_desc": company_desc,
#                 "url": url,
#                 "description": description,
#                 "requirements": requirements,
#                 "benefits": benefits,
#                 "location": location,
#                 "salary": salary,
#                 "working_hours": working_hours,
#                 "expired_date": expired_date,
#                 "domains": ["Telecom", "IT"],
#                 "skills": [],
#             }

#             job = JobAdapter.to_job(raw_data, "fptjobs")
#             async with session_factory() as session:
#                 repo = JobRepository(session)
#                 await repo.save(job)
#                 await session.commit()
#             context.log.info(f"Successfully saved FPT Job: {title}")

#         async def _process_list_page(
#             context: AdaptivePlaywrightCrawlingContext, soup, url: str
#         ) -> None:
#             context.log.info(f"Parsing list page for URLs: {url}")

#             job_links = soup.select(".job-list-container a.link-overlay")
#             enqueued_count = 0

#             for link in job_links:
#                 href = link.get("href")
#                 if href:
#                     detail_url = urljoin("https://fptjobs.com", href)
#                     await context.add_requests(
#                         [Request.from_url(url=detail_url, label="detail")]
#                     )
#                     enqueued_count += 1

#             context.log.info(
#                 f"Enqueued {enqueued_count} job detail pages from FPTJobs list."
#             )

#         async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
#             url = context.request.url
#             await self.apply_delay()
#             context.log.info(
#                 f"Crawling FPTJobs: {url} (label: {context.request.label})"
#             )

#             html_content = ""
#             if context._page:
#                 html_content = await context.page.content()
#             elif context.http_response:
#                 html_content = (await context.http_response.read()).decode(
#                     "utf-8", errors="ignore"
#                 )

#             if not html_content:
#                 context.log.warning(f"Empty content for URL: {url}")
#                 return

#             soup = BeautifulSoup(html_content, "html.parser")

#             is_detail = context.request.label in ["detail", "updater_detail"] or (
#                 any(char.isdigit() for char in url.split("-")[-1])
#                 and url.count("-") > 1
#             )

#             if is_detail:
#                 await _process_detail_page(context, soup, url)
#             else:
#                 await _process_list_page(context, soup, url)

#         return handler
