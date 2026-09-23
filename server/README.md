# Local AIJMC Server with Ngrok
This section is dedicated to the method of deploying AIJMC locally using Ngrok. I will provide instructions for local installation and execution in the near future (likely by September 30, 2026). Please carefully read the information below to fully understand the guidelines and risks associated with running AIJMC locally.  

## I. How to use the platform
To use the platform, you only need to accept the Terms of Service and create an account. The following features are currently available:

1. Vietnamese and English: Switch between Vietnamese and English. However, the platform currently supports Vietnamese as its main language.
2. Information Pages: Access static pages such as the AIJMC introduction and FAQ.
3. Open Job Search: Find currently available IT job opportunities.
4. Semantic Job Search: Find jobs based on the meaning of your search, not only exact keywords.
5. Consultation Chatbot: Ask questions and get advice about IT jobs and the job market.

The CV and personalization features are currently unavailable and are planned to be reopened in a future version.

## II. Legal terms and policies
1. Academic and non-commercial purpose: AIJMC is a scientific research and graduation thesis project at Ho Chi Minh City Open University. It is operated for academic and personal research purposes and does not provide paid job application services or sell collected data.
2. Data collection: AIJMC collects publicly available job and company information from recruitment platforms such as ITviec, VietnamWorks, TopDev, and ITJobs. The system does not bypass authentication, security controls, or access restrictions and aims to respect applicable technical rules such as robots.txt.
3. Content ownership: Job descriptions, company information, images, logos, trademarks, and other third-party content remain the property of their respective owners. AIJMC does not claim ownership of such content.
4. Original sources: AIJMC does not provide direct job application services. Where available, job information includes a link to the original posting so users can access the original recruitment platform.
User data and privacy: AIJMC does not require sensitive identity information for normal use and does not intend to maintain long-term candidate CV profiles. Any personal data processing, if applicable, is handled in accordance with applicable Vietnamese data protection laws.
5. Accuracy and liability: Job information is collected automatically from third-party sources and may be incomplete, outdated, or inaccurate. AIJMC is provided on an “as is” basis and does not guarantee the accuracy or availability of third-party information or external links.
6. Takedown requests: If a data owner or recruitment platform believes that its content should not be displayed by AIJMC, please contact the project team. The team will review the request and may remove the relevant data, block the source, or stop the related collection process.
7. Support: 2351050164thanh@ou.edu.vn or thanh.vantrung2005@gmail.com.

## III. Important Notes
1. Do not use sensitive information such as your ID card number, bank account details, home address, or other private information.
2. Only provide information related to your job search and avoid sharing unnecessary personal information.
Please accept the Terms of Service before using the platform.
3. AIJMC never requires users to make any payment. If you see a payment request or a suspicious redirect link, please do not continue and report it to 2351050164thanh@ou.edu.vn. Unexpected requests for payment or personal information can be signs of fraud.
4. Your search text may be sent to Google GenAI servers for processing. Please only enter non-sensitive information when using the platform. Do not enter passwords, financial information, identity numbers, or other private information.

## IV. Grafana k6
> [!NOTE]
> You can run endurance_test, load_test, spike_test, stress_test by running: "k6 run k6_testing/<file_name>".
> Caution: You need to configure .env correctly before running.
