# ADR-02: Three Key Architectural Characteristics of the Software

## Status
Approved

## Context
An IT job market consulting system involves three critical areas. First, the system must store and analyze diverse job posting information in unstructured or semi-structured formats, sourced from various job boards with inconsistent HTML structures. Second, users need to provide a significant amount of personal information to receive accurate consultations, which raises security and privacy requirements. Finally, an AI Agent system is capable of handling user requests with low latency.

## Decision
Identify and focus the system's development on three key architectural characteristics: security, performance, and scalability.

## Rationale
1. **Security:** Protecting users' personal profiles, resumes, and career goals is paramount to comply with data privacy regulations and build user trust.
2. **performance:** The system should follow the response time guidelines by Jakob Nielsen, with a recommended average time of 1 second and a maximum of 10 seconds.
3. **Scalability:** The system must handle increasing volumes of job market data and concurrent user queries as community adoption grows.


## Consequences
### Positive
* **Robust Data Privacy:** Emphasizing security prevents data leaks and ensures sensitive user data is stored safely.
* **Reliable Performance:** Ensuring scalability keeps response times fast and consistent even under peak traffic and heavy background data processing.

### Negative
* **Increased Development Complexity:** Implementing strict security rule and clean abstractions increases initial development effort.
* **Higher Infrastructure Costs:** Supporting a highly scalable AI Agent backend and large-scale web crawlers requires more robust and expensive hosting resources.

## Decision Date
Approved on 18/07/2026
