# import json
# import logging
# from urllib.parse import urljoin, urlparse
# from datetime import datetime
# from bs4 import BeautifulSoup
# from crawlee import Request
# from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

# from app.modules.job.repository import JobRepository
# from app.modules.company.repository import CompanyRepository
# from app.modules.company.models import Company, CompanyBenefit
# from ..crawler_adapter import JobAdapter
# from .base_factory import BaseCrawlerFactory

# logger = logging.getLogger(__name__)


# class TopDevCrawlerFactory(BaseCrawlerFactory):
#     def get_handler(self, session_factory):

#         async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
#             url = context.request.url
#             await self.apply_delay()
#             context.log.info(f"Crawling TopDev: {url} (label: {context.request.label})")

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
#                 "/detail-jobs/" in url
#             )
#             is_company = (
#                 context.request.label == "company"
#                 or "/companies/" in url
#                 or "/nha-tuyen-dung/" in url
#             )

#             if context._page:
#                 try:
#                     context.log.info(f"Waiting for detail page to fully load: {url}")
#                     await context.page.wait_for_load_state("networkidle", timeout=15000)
#                     new_html = await context.page.content()
#                     soup = BeautifulSoup(new_html, "html.parser")
#                 except Exception as e:
#                     context.log.warning(
#                         f"Timeout/Error waiting for page load, falling back to initial HTML: {e}"
#                     )

#             if is_detail:
#                 await self._process_job_detail(context, session_factory, soup, url)
#             elif is_company:
#                 await self._process_company(context, session_factory, soup, url)
#             else:
#                 await self._process_list_page(context, soup, url)

#         return handler

#     async def _process_job_detail(self, context, session_factory, soup, url):
#         context.log.info(f"Extracting detail page: {url}")
#         title = None
#         company_name = None
#         skills = []
#         description = ""
#         requirements = ""
#         benefits = []
#         location = "Vietnam"
#         salary = "Negotiable"

#         json_ld_tags = soup.find_all("script", type="application/ld+json")
#         for tag in json_ld_tags:
#             try:
#                 data = json.loads(tag.string)
#                 if data.get("@type") == "JobPosting" or "JobPosting" in str(
#                     data.get("@type")
#                 ):
#                     title = data.get("title")
#                     company_name = data.get("hiringOrganization", {}).get("name")
#                     if data.get("skills"):
#                         if isinstance(data["skills"], str):
#                             skills = [
#                                 s.strip()
#                                 for s in data["skills"].split(",")
#                                 if s.strip()
#                             ]
#                         elif isinstance(data["skills"], list):
#                             skills = data["skills"]

#                     loc_data = data.get("jobLocation")
#                     if loc_data:
#                         if isinstance(loc_data, list) and len(loc_data) > 0:
#                             loc_data = loc_data[0]
#                         address = loc_data.get("address", {})
#                         location = address.get(
#                             "addressRegion",
#                             address.get("addressLocality", "Vietnam"),
#                         )

#                     salary_val = data.get("baseSalary", {}).get("value", {})
#                     if isinstance(salary_val, dict):
#                         salary = salary_val.get("value", "Negotiable")
#                     elif isinstance(salary_val, str):
#                         salary = salary_val

#                     raw_desc = data.get("description", "")
#                     description = (
#                         BeautifulSoup(raw_desc, "html.parser").get_text(
#                             separator="\n", strip=True
#                         )
#                         if raw_desc
#                         else ""
#                     )
#                     job_benefits = data.get("jobBenefits", "")
#                     if job_benefits:
#                         if isinstance(job_benefits, list):
#                             benefits = job_benefits
#                         else:
#                             sub_soup = BeautifulSoup(job_benefits, "html.parser")
#                             benefits = [
#                                 li.get_text(strip=True)
#                                 for li in sub_soup.find_all("li")
#                                 if li.get_text(strip=True)
#                             ]
#                     break
#             except Exception as e:
#                 logger.error(f"Error parsing JSON-LD in TopDev: {e}")

#         if not title:
#             title_elem = soup.find("h1")
#             title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"

#         employer_links = soup.find_all("a", href=lambda h: h and "/companies/" in h)
#         employer_info = None

#         for link in employer_links:
#             name_span = link.find(
#                 "span",
#                 class_=lambda c: c and "text-brand-500" in c and "font-semibold" in c,
#             )
#             if name_span:
#                 employer_info = link
#                 if not company_name:
#                     company_name = name_span.get_text(strip=True)
#                 break

#         if employer_info:
#             company_href = employer_info.get("href")
#             if company_href:
#                 company_url = urljoin(url, company_href)
#                 await context.add_requests(
#                     [Request.from_url(url=company_url, label="company")]
#                 )
#         else:
#             if not company_name:
#                 company_name = "Unknown Company"

#         if not description:
#             desc_div = soup.select_one(".job-description") or soup.select_one(
#                 ".description"
#             )
#             description = (
#                 desc_div.get_text(strip=True) if desc_div else "No description provided"
#             )

#         nice_to_have = []
#         skills_header = soup.find(
#             lambda tag: (
#                 tag.name in ["span", "h1", "h2", "h3", "h4", "div"]
#                 and tag.get_text()
#                 and "skills & qualifications" in tag.get_text().lower()
#             )
#         )
#         container = None
#         if skills_header:
#             container = skills_header.find_next("div", class_="prose-ul")
#         if not container:
#             container = soup.find("div", class_="prose-ul")

#         if container:
#             current_list = "req"
#             for element in container.children:
#                 if element.name in ["p", "div", "h1", "h2", "h3", "h4"]:
#                     if "nice to have" in element.get_text().lower():
#                         current_list = "nice"
#                 elif element.name in ["ul", "ol"]:
#                     for li in element.find_all("li"):
#                         txt = li.get_text(strip=True)
#                         if txt:
#                             if current_list == "req":
#                                 requirements += txt + "\n"
#                             else:
#                                 nice_to_have.append(txt)

#         raw_data = {
#             "title": title,
#             "company": company_name,
#             "url": url,
#             "description": description,
#             "requirements": requirements or "No requirements specified",
#             "nice_to_have": nice_to_have,
#             "benefits": benefits,
#             "location": location,
#             "salary": salary,
#             "skills": skills,
#         }

#         is_updater = context.request.label == "updater_detail"
#         if is_updater:
#             is_not_found = False
#             if context.http_response and context.http_response.status_code in [
#                 404,
#                 410,
#             ]:
#                 is_not_found = True
#             elif context._page:
#                 current_url = context.page.url
#                 if urlparse(current_url).path != urlparse(url).path:
#                     if (
#                         "/it-jobs/" not in current_url
#                         and "/detail-jobs/" not in current_url
#                     ):
#                         is_not_found = True

#             page_text = soup.get_text().lower()
#             is_expired_text = any(
#                 msg in page_text
#                 for msg in [
#                     "ngưng nhận hồ sơ",
#                     "hết hạn",
#                     "job expired",
#                     "posting expired",
#                 ]
#             )

#             if is_not_found or is_expired_text:
#                 context.log.info(
#                     f"Job posting not found or expired: {url}. Marking as Closed."
#                 )
#                 async with session_factory() as session:
#                     repo = JobRepository(session)
#                     existing = await repo.get_by_url(url)
#                     if existing:
#                         existing.status = "Closed"
#                         existing.updated_date = datetime.utcnow()
#                         session.add(existing)
#                         await session.commit()
#                 return

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

#         job = JobAdapter.to_job(raw_data, "topdev")
#         async with session_factory() as session:
#             repo = JobRepository(session)
#             await repo.save(job)
#             await session.commit()
#         context.log.info(f"Successfully saved TopDev Job: {title} at {company_name}")

#     async def _process_company(self, context, session_factory, soup, url):
#         context.log.info(f"Extracting company page: {url}")
#         name_elem = soup.find(
#             "span", class_=lambda c: c and "text-brand-500" in c and "text-xl" in c
#         )
#         name = name_elem.get_text(strip=True) if name_elem else ""

#         if not name:
#             context.log.warning(f"Company profile has no name: {url}")
#             return

#         industry = "Unknown"
#         size = "Unknown"
#         company_type = None
#         country = "Unknown"
#         location = "Vietnam"
#         working_days = None
#         overtime_policy = None
#         slogan = None
#         description = ""
#         website = ""
#         benefits_list = []

#         loc_spans = soup.find_all("span", class_="flex text-sm text-text-400")
#         for span in loc_spans:
#             if span.find("svg"):
#                 location = span.get_text(strip=True)
#                 break

#         def find_label_span(keyword):
#             return soup.find(
#                 lambda tag: (
#                     tag.name == "span"
#                     and tag.get_text(strip=True)
#                     and keyword in tag.get_text(strip=True).lower()
#                 )
#             )

#         country_lbl = find_label_span("country")
#         if country_lbl and country_lbl.parent:
#             val_span = country_lbl.parent.find(
#                 "span",
#                 class_=lambda c: c and "font-semibold" in c and "text-text-700" in c,
#             )
#             if val_span:
#                 country = val_span.get_text(strip=True)

#         industry_lbl = find_label_span("industry")
#         if industry_lbl and industry_lbl.parent:
#             val_spans = industry_lbl.parent.find_all(
#                 "span",
#                 class_=lambda c: c and "font-semibold" in c and "text-text-700" in c,
#             )
#             industry = ", ".join([s.get_text(strip=True) for s in val_spans])

#         size_lbl = find_label_span("size")
#         if size_lbl and size_lbl.parent:
#             val_span = size_lbl.parent.find(
#                 "span",
#                 class_=lambda c: c and "font-semibold" in c and "text-text-700" in c,
#             )
#             if val_span:
#                 size = val_span.get_text(strip=True)

#         overview_lbl = find_label_span("company overview")
#         if overview_lbl and overview_lbl.parent:
#             desc_div = overview_lbl.parent.find("div", class_="text-gray-700")
#             if desc_div:
#                 description = desc_div.get_text(separator="\n", strip=True)

#         benefits_lbl = find_label_span("benefits")
#         if benefits_lbl and benefits_lbl.parent:
#             ul_elem = benefits_lbl.parent.find("ul")
#             if ul_elem:
#                 for li in ul_elem.find_all("li"):
#                     txt = li.get_text(strip=True)
#                     if txt:
#                         benefits_list.append(CompanyBenefit(name=txt))

#         website_span = soup.find("span", string=lambda s: s and "Company Website" in s)
#         if website_span:
#             website_link = website_span.find_parent("a")
#             if website_link:
#                 website = website_link.get("href", "")

#         vector_context = f"Company Name: {name}. Industry: {industry}. Size: {size}. Location: {location}. Description: {description}."
#         company_obj = Company(
#             name=name,
#             industry=industry,
#             size=size,
#             location=location,
#             addresses=[location],
#             description=description,
#             website=website,
#             slogan=slogan,
#             company_type=company_type,
#             country=country,
#             working_days=working_days,
#             overtime_policy=overtime_policy,
#             vector_context=vector_context,
#             benefits=benefits_list,
#         )
#         async with session_factory() as session:
#             company_repo = CompanyRepository(session)
#             await company_repo.save(company_obj)
#             await session.commit()
#         context.log.info(f"Successfully saved company information for: {name}")

#     async def _process_list_page(self, context, soup, url):
#         context.log.info(f"Parsing list page for URLs: {url}")
#         links = soup.select('a[href*="/detail-jobs/"]')
#         enqueued_count = 0

#         for link in links:
#             href = link.get("href")
#             if href:
#                 detail_url = urljoin("https://topdev.vn", href)
#                 await context.add_requests(
#                     [Request.from_url(url=detail_url, label="detail")]
#                 )
#                 enqueued_count += 1

#         context.log.info(
#             f"Enqueued {enqueued_count} job detail pages from TopDev list."
#         )

#         if enqueued_count > 0:
#             from urllib.parse import parse_qs, urlencode, urlunparse

#             parsed = urlparse(url)
#             qs = parse_qs(parsed.query)
#             current_page = 1
#             if "page" in qs:
#                 try:
#                     current_page = int(qs["page"][0])
#                 except ValueError:
#                     pass

#             if current_page < 15:
#                 qs["page"] = [str(current_page + 1)]
#                 next_url = urlunparse(
#                     (
#                         parsed.scheme,
#                         parsed.netloc,
#                         parsed.path,
#                         parsed.params,
#                         urlencode(qs, doseq=True),
#                         parsed.fragment,
#                     )
#                 )
#                 context.log.info(f"Enqueuing next TopDev list page: {next_url}")
#                 await context.add_requests(
#                     [Request.from_url(url=next_url, label="list")]
#                 )
