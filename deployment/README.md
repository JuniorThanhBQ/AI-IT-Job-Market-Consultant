# AI-IT-JOB-MARKET-CONSULTANT
AI IT Job Market Consultant (AIJMC), also known as an IT Job Market personalization system. This system solves three aspects of today's IT job market problems. The first aspect is providing a Job Consultant System amid today's low trend. The second aspect is solving the lack of an efficient way for IT job seekers to find suitable jobs. The final aspect is proving the theory of multi-agent applications for solving Job Consultant problems.          

## I. Project Description
### 1. Main goal
The overall objective of this project is to develop an IT Job Market Consultant System based on a multi-agent architecture. This system is capable of collecting, processing, and analyzing recruitment data from multiple sources. The fundamental theory of this project is based on the AI agent research by [T. M. Nguyen and colleagues](https://arxiv.org/pdf/2511.14767). At the same time, the system can provide career counseling and suggest suitable job opportunities for users based on theories from the survey by [Q. Peng](https://arxiv.org/abs/2502.10050) and the research by [Q. Wang and colleagues](https://arxiv.org/abs/2508.13423).

### 2. Project Aim
With a 10-week implementation period, the specific objectives include:
1. Objective 1: Collect and analyze business requirements related to the IT Job Market Consultant System using literature review and user story techniques. The result is the System Requirements Specification (SRS) by the end of Week 2.
2. Objective 2: A comprehensive overview of theories and technologies related to AI agents, multi-agent architectures, large language models, and AI techniques such as RAG and semantic search. The result is Chapter 2 Theoretical Foundations in the graduate report, which is to be completed by the end of Week 3.
3. Objective 3: Design and build a multi-agent system with all three main agents, including the IT job market analysis agent, the personalization agent, and the recommendation agent. The project must be completed by the end of Week 7.
4. Objective 4: Develop a web app platform with three main features: job search, a consultation chatbot, and a dashboard for analyzing individual skills. The project is scheduled for completion by the end of Week 8.
5. Objective 5: Deploy the platform to a VPS to conduct acceptance testing and document the results to finalize the report during weeks 9–10.

## II. Technologies
The project uses a modern stack for the backend, frontend, AI services, and data collection.

| Core structure | Technology | Version / Stack | Reason for use |
| :--- | :--- | :--- | :--- |
| **Backend API** | FastAPI | FastAPI 0.139+ | Provides a fast, modern, and asynchronous API layer for job search, CV analysis, and chatbot services with low latency and clean request handling. |
| **Backend models** | SQLModel + Pydantic | SQLModel 0.0.22+, Pydantic 2.13+ | Supports strongly typed data models, validation, and easy integration with the database for reliable backend development. |
| **Database** | PostgreSQL + pgvector | PostgreSQL + pgvector 0.5+ | Stores structured job data and vector embeddings together, which is useful for semantic search, recommendation, and RAG workflows. |
| **Authentication** | JWT + pwdlib | PyJWT 2.10+, pwdlib 0.3+ | Secures user login, password management, and access control with modern authentication practices. |
| **AI Agents** | Google GenAI SDK | Google GenAI 2.14+| Enables LLM orchestration, embedding generation, and retrieval-based AI features for intelligent job |
| **Data collection** | Crawl4AI + Crawlee + Playwright | Crawl4AI 0.9+, Crawlee 1.8+, Playwright 1.62+ | Allows the system to collect job information from websites, including dynamic pages that require browser rendering. |
| **Background jobs** | Celery + Redis | Celery 5.4+, Redis 5.0+ | Handles asynchronous crawlers, scheduled tasks, and background processing without blocking the main application. |
| **Frontend** | Next.js + React | Next.js 16.2+, React 19.2+ | Builds a responsive and interactive web interface for job discovery, dashboards, and user experience. |
| **UI styling** | Tailwind CSS + shadcn/ui | Tailwind 4.3+, shadcn 4.16+ | Speeds up UI development with reusable components and a modern, consistent design system. |
| **DevOps / deployment** | Docker Compose | Docker-based | Simplifies local development, service orchestration, and deployment setup for the whole platform. |
| **Testing / quality** | pytest + Vitest + Playwright + Ruff | pytest 9.1+, Vitest 4.1+, Playwright 1.62+, Ruff 0.15+ | Supports automated testing, code quality checks, and reliable maintenance across the project. |

## III. Source code and development
Link: [AI-IT-Job-Market-Consultant](https://github.com/JuniorThanhBQ/AI-IT-Job-Market-Consultant)

Note: AI-IT-Job-Market-Consultant will be set to public after 15/09/2026. For early access, please send an email to 2351050164thanh@ou.edu.vn or thanh.vantrung2005@gmail.com

Production status: Local ngrok → VPS deployment after acceptance testing.

## IV. How to use the platform
To use the platform, you only need to accept the Terms of Service and create an account. The following features are currently available:

1. Vietnamese and English: Switch between Vietnamese and English. However, the platform currently supports Vietnamese as its main language.
2. Information Pages: Access static pages such as the AIJMC introduction and FAQ.
3. Open Job Search: Find currently available IT job opportunities.
4. Semantic Job Search: Find jobs based on the meaning of your search, not only exact keywords.
5. Consultation Chatbot: Ask questions and get advice about IT jobs and the job market.

The CV and personalization features are currently unavailable and are planned to be reopened in a future version.


## V. Legal terms and policies
1. Academic and non-commercial purpose: AIJMC is a scientific research and graduation thesis project at Ho Chi Minh City Open University. It is operated for academic and personal research purposes and does not provide paid job application services or sell collected data.
2. Data collection: AIJMC collects publicly available job and company information from recruitment platforms such as ITviec, VietnamWorks, TopDev, and ITJobs. The system does not bypass authentication, security controls, or access restrictions and aims to respect applicable technical rules such as robots.txt.
3. Content ownership: Job descriptions, company information, images, logos, trademarks, and other third-party content remain the property of their respective owners. AIJMC does not claim ownership of such content.
4. Original sources: AIJMC does not provide direct job application services. Where available, job information includes a link to the original posting so users can access the original recruitment platform.
User data and privacy: AIJMC does not require sensitive identity information for normal use and does not intend to maintain long-term candidate CV profiles. Any personal data processing, if applicable, is handled in accordance with applicable Vietnamese data protection laws.
5. Accuracy and liability: Job information is collected automatically from third-party sources and may be incomplete, outdated, or inaccurate. AIJMC is provided on an “as is” basis and does not guarantee the accuracy or availability of third-party information or external links.
6. Takedown requests: If a data owner or recruitment platform believes that its content should not be displayed by AIJMC, please contact the project team. The team will review the request and may remove the relevant data, block the source, or stop the related collection process.
7. Support: 2351050164thanh@ou.edu.vn or thanh.vantrung2005@gmail.com


## VI. Important Notes
1. Do not use sensitive information such as your ID card number, bank account details, home address, or other private information.
2. Only provide information related to your job search and avoid sharing unnecessary personal information.
Please accept the Terms of Service before using the platform.
3. AIJMC never requires users to make any payment. If you see a payment request or a suspicious redirect link, please do not continue and report it to 2351050164thanh@ou.edu.vn. Unexpected requests for payment or personal information can be signs of fraud.
4. Your search text may be sent to Google GenAI servers for processing. Please only enter non-sensitive information when using the platform. Do not enter passwords, financial information, identity numbers, or other private information.
5. Warning: Do not attempt to simulate the production .env to run it locally. Doing so may expose sensitive credentials and pose security risks to your local machine
