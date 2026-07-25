# import asyncio
# import logging
# from urllib.parse import urljoin, urlparse
# from datetime import datetime
# from bs4 import BeautifulSoup
# from crawlee import Request
# from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

# from app.modules.job.repository import JobRepository
# from ..crawler_adapter import JobAdapter
# from .base_factory import BaseCrawlerFactory

# logger = logging.getLogger(__name__)


# class ITJobsCrawlerFactory(BaseCrawlerFactory):
#     def get_handler(self, session_factory):
#         async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
#             url = context.request.url

#             await self.apply_delay()

#             context.log.info(f"Crawling ITJobs: {url} (label: {context.request.label})")

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
#                 "/job/" in url and "/search" not in url
#             )

#             if is_detail:
#                 context.log.info(f"Extracting detail page: {url}")

#                 company_name = "Unknown Company"
#                 company_size = "Unknown"
#                 company_address = ""

#                 company_right = soup.select_one(".jp_company-right")
#                 if company_right:
#                     h1 = company_right.find("h1")
#                     company_name = h1.get_text(strip=True) if h1 else "Unknown Company"

#                     text_nodes = [
#                         t
#                         for t in company_right.children
#                         if isinstance(t, str) or (t.name != "h1" and t.name != "a")
#                     ]
#                     for node in text_nodes:
#                         node_text = (
#                             node.get_text(strip=True)
#                             if hasattr(node, "get_text")
#                             else str(node).strip()
#                         )
#                         if not node_text:
#                             continue
#                         if "Quy mô công ty" in node_text or "Quy mô" in node_text:
#                             company_size = node_text.split(":")[-1].strip()
#                         else:
#                             company_address += node_text + " "
#                     company_address = company_address.strip()

#                 title = "Unknown Title"
#                 location = "Vietnam"
#                 salary = "Negotiable"
#                 working_hours = "Full-time"
#                 seniority = "Middle"

#                 job_summary = soup.select_one(
#                     ".jp_job_post_detail_cont"
#                 ) or soup.select_one("#job-summary")
#                 if job_summary:
#                     h3 = job_summary.find("h3")
#                     if h3:
#                         title = h3.get_text(strip=True)

#                     loc_icon = job_summary.find("i", class_="fa-map-marker")
#                     if loc_icon:
#                         loc_span = loc_icon.find_parent("li") or loc_icon.find_next(
#                             "span"
#                         )
#                         if loc_span:
#                             location = loc_span.get_text(strip=True)

#                     sal_icon = job_summary.find("i", class_="fa-usd")
#                     if sal_icon:
#                         sal_span = sal_icon.find_parent("li") or sal_icon.find_next(
#                             "span"
#                         )
#                         if sal_span:
#                             salary = sal_span.get_text(strip=True)

#                     clock_icon = job_summary.find("i", class_="fa-clock-o")
#                     if clock_icon:
#                         clock_span = clock_icon.find_parent(
#                             "li"
#                         ) or clock_icon.find_next("span")
#                         if clock_span:
#                             working_hours = clock_span.get_text(strip=True)

#                     suit_icon = job_summary.find("i", class_="fa-suitcase")
#                     if suit_icon:
#                         suit_span = suit_icon.find_parent("li") or suit_icon.find_next(
#                             "span"
#                         )
#                         if suit_span:
#                             seniority = suit_span.get_text(strip=True)

#                 description = ""
#                 requirements = ""

#                 desc_sect = soup.select_one(
#                     ".job-description-section .jp_overview_wrapper"
#                 )
#                 if desc_sect:
#                     description = desc_sect.get_text(strip=True)

#                 req_sect = soup.select_one(
#                     ".job-requirement-section .jp_overview_wrapper"
#                 )
#                 if req_sect:
#                     requirements = req_sect.get_text(strip=True)

#                 skills = []
#                 skills_wrapper = soup.select_one(".jp_job_post_keyword_wrapper")
#                 if skills_wrapper:
#                     anchors = skills_wrapper.find_all("a")
#                     for a in anchors:
#                         tag = a.get_text(strip=True).rstrip(",")
#                         if tag and tag not in skills:
#                             skills.append(tag)

#                 raw_data = {
#                     "title": title,
#                     "company": company_name,
#                     "company_size": company_size,
#                     "company_address": company_address,
#                     "url": url,
#                     "description": description or "No description provided",
#                     "requirements": requirements or "No requirements specified",
#                     "benefits": [],
#                     "location": location,
#                     "salary": salary,
#                     "working_hours": working_hours,
#                     "seniority": seniority,
#                     "skills": skills,
#                 }

#                 is_updater = context.request.label == "updater_detail"
#                 if is_updater:
#                     is_not_found = False
#                     if context.http_response and context.http_response.status_code in [
#                         404,
#                         410,
#                     ]:
#                         is_not_found = True
#                     elif context._page:
#                         current_url = context.page.url
#                         if urlparse(current_url).path != urlparse(url).path:
#                             if "/job/" not in current_url:
#                                 is_not_found = True

#                     page_text = soup.get_text().lower()
#                     is_expired_text = any(
#                         msg in page_text
#                         for msg in [
#                             "ngưng nhận hồ sơ",
#                             "hết hạn",
#                             "job expired",
#                             "posting expired",
#                         ]
#                     )

#                     if is_not_found or is_expired_text:
#                         context.log.info(
#                             f"Job posting not found or expired: {url}. Marking as Closed."
#                         )
#                         async with session_factory() as session:
#                             repo = JobRepository(session)
#                             existing = await repo.get_by_url(url)
#                             if existing:
#                                 existing.status = "Closed"
#                                 existing.updated_date = datetime.utcnow()
#                                 session.add(existing)
#                                 await session.commit()
#                         return

#                     if (
#                         not title
#                         or title.strip().lower() in ["unknown title", "no title", ""]
#                         or not description
#                         or description.strip().lower()
#                         in ["no description provided", "not provided", ""]
#                     ):
#                         context.log.warning(
#                             f"New parsed data is null/empty for URL {url} due to extraction error. Keeping old record."
#                         )
#                         return

#                 job = JobAdapter.to_job(raw_data, "itjobs")
#                 async with session_factory() as session:
#                     repo = JobRepository(session)
#                     await repo.save(job)
#                     await session.commit()
#                 context.log.info(
#                     f"Successfully saved ITJobs Job: {title} at {company_name}"
#                 )

#             else:
#                 context.log.info(f"Parsing list page for URLs: {url}")

#                 if context._page:
#                     show_more_selector = "#btnShowMoreJob"
#                     for i in range(10):
#                         try:
#                             button = await context.page.query_selector(
#                                 show_more_selector
#                             )
#                             if button and await button.is_visible():
#                                 context.log.info(
#                                     f"Clicking 'XEM THÊM' button (iteration {i + 1})"
#                                 )
#                                 await button.click()
#                                 await asyncio.sleep(2.0)
#                             else:
#                                 break
#                         except Exception as e:
#                             context.log.warning(
#                                 f"Failed to click show more button: {e}"
#                             )
#                             break
#                     html_content = await context.page.content()
#                     soup = BeautifulSoup(html_content, "html.parser")

#                 anchors = soup.select("a.jp_job_post_link, a.top-jobs__item")
#                 enqueued_count = 0

#                 for a in anchors:
#                     href = a.get("href")
#                     if href and "/job/" in href:
#                         detail_url = urljoin("https://itjobs.com.vn", href)
#                         await context.add_requests(
#                             [Request.from_url(url=detail_url, label="detail")]
#                         )
#                         enqueued_count += 1

#                 context.log.info(
#                     f"Enqueued {enqueued_count} job detail pages from ITJobs list."
#                 )

#         return handler
