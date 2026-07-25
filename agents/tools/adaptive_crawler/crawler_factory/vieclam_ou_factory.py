# import logging
# from urllib.parse import urljoin
# from datetime import datetime
# from bs4 import BeautifulSoup
# from crawlee import Request
# from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

# from app.modules.job.repository import JobRepository
# from ..crawler_adapter import JobAdapter
# from .base_factory import BaseCrawlerFactory

# logger = logging.getLogger(__name__)


# class VieclamOUCrawlerFactory(BaseCrawlerFactory):
#     def get_handler(self, session_factory):

#         async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
#             url = context.request.url

#             await self.apply_delay()

#             context.log.info(
#                 f"Crawling VieclamOU: {url} (label: {context.request.label})"
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
#                 ".html" in url and "/viec-lam/" in url
#             )

#             if is_detail:
#                 context.log.info(f"Extracting detail page: {url}")

#                 title_com = "Unknown Title"
#                 title_elem = soup.select_one("h1.col_theme")
#                 if title_elem:
#                     title_com = title_elem.get_text(strip=True)

#                 title = title_com
#                 company_name = "Unknown Company"
#                 if " - " in title_com:
#                     parts = title_com.rsplit(" - ", 1)
#                     title = parts[0].strip()
#                     company_name = parts[1].strip()

#                 location = ""
#                 seniority = ""
#                 working_hours = "Toàn thời gian"
#                 experience = ""
#                 salary = "Thỏa Thuận"
#                 industry = ""
#                 expired_date_str = ""

#                 basic_ul = soup.select_one("ul.basic")
#                 if basic_ul:
#                     for li in basic_ul.find_all("li"):
#                         label = li.find("label")
#                         val_div = li.find("div", class_="value")
#                         if label and val_div:
#                             label_text = label.get_text(strip=True).lower()
#                             val_text = val_div.get_text(strip=True)

#                             if "nơi làm việc" in label_text:
#                                 location = val_text
#                             elif "cấp bậc" in label_text:
#                                 seniority = val_text
#                             elif "hình thức" in label_text:
#                                 working_hours = val_text
#                             elif "kinh nghiệm" in label_text:
#                                 experience = val_text
#                             elif "mức lương" in label_text:
#                                 salary = val_text
#                             elif "ngành nghề" in label_text:
#                                 industry = val_text
#                             elif "hạn chót" in label_text:
#                                 expired_date_str = val_text

#                 benefits = []
#                 benefits_ul = soup.select_one("ul.list-benefits")
#                 if benefits_ul:
#                     for li in benefits_ul.find_all("li"):
#                         b_text = li.get_text(strip=True)
#                         if b_text:
#                             benefits.append(b_text)

#                 description = ""
#                 requirements = ""
#                 headers = soup.find_all("h2", class_="col_theme")
#                 for h in headers:
#                     h_text = h.get_text(strip=True).lower()
#                     next_div = h.find_next_sibling("div", class_="content_fck")
#                     if next_div:
#                         if "mô tả công việc" in h_text:
#                             description = next_div.get_text(separator="\n", strip=True)
#                         elif "yêu cầu công việc" in h_text:
#                             requirements = next_div.get_text(separator="\n", strip=True)

#                 raw_data = {
#                     "title": title,
#                     "company": company_name,
#                     "url": url,
#                     "description": description or "No description provided",
#                     "requirements": requirements or "No requirements specified",
#                     "benefits": benefits,
#                     "location": location,
#                     "salary": salary,
#                     "working_hours": working_hours,
#                     "seniority": seniority,
#                     "experience": experience,
#                     "industry": industry,
#                     "expired_date": expired_date_str,
#                 }

#                 is_updater = context.request.label == "updater_detail"
#                 if is_updater:
#                     is_not_found = False
#                     if context.http_response and context.http_response.status_code in [
#                         404,
#                         410,
#                     ]:
#                         is_not_found = True

#                     page_text = soup.get_text().lower()
#                     is_expired_text = any(
#                         msg in page_text
#                         for msg in [
#                             "đã hết hạn",
#                             "ngừng nhận hồ sơ",
#                             "không tìm thấy",
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

#                     if not title or title.strip() == "" or not description:
#                         context.log.warning(
#                             f"New parsed data is null/empty for URL {url}. Keeping old record."
#                         )
#                         return

#                 job = JobAdapter.to_job(raw_data, "vieclam_ou")
#                 async with session_factory() as session:
#                     repo = JobRepository(session)
#                     await repo.save(job)
#                     await session.commit()
#                 context.log.info(
#                     f"Successfully saved VieclamOU Job: {title} at {company_name}"
#                 )

#             else:
#                 context.log.info(f"Parsing list page for URLs: {url}")

#                 table = soup.find("table", id="tbl_job_listing")
#                 enqueued_count = 0

#                 if table:
#                     anchors = table.select("p.name_job a")
#                     for a in anchors:
#                         href = a.get("href")
#                         if href:
#                             detail_url = urljoin("https://vieclam.ou.edu.vn", href)
#                             await context.add_requests(
#                                 [Request.from_url(url=detail_url, label="detail")]
#                             )
#                             enqueued_count += 1

#                 context.log.info(
#                     f"Enqueued {enqueued_count} job detail pages from VieclamOU list."
#                 )

#         return handler
