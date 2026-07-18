# ADR-02: Three Key Architectural Characteristics of the Software

## Status
Approved

## Context
An IT job market consulting system involves three critical areas that need to be processed and stored. First, the system must store and analyze diverse job posting information with unstructured or semi-structured formats, sourced from various job boards with inconsistent HTML structures. Second, users need to provide a significant amount of personal information to receive accurate consultations, which raises strict security requirements. Finally, a multi-agent system is required to handle these processes flexibly as the AI and job market evolve over time.

## Decision
Identify and focus the system's development on three key architectural characteristics: maintainability, security, and scalability.

## Rationale
1. **Maintainability:** Since job boards frequently change their layouts, the scraping and data extraction components must be easy to modify and maintain without breaking the entire application.
2. **Security:** Protecting users' personal profiles, resumes, and career goals is paramount to comply with data privacy regulations and build user trust.
3. **Scalability:** The system must handle increasing volumes of job market data and concurrent user queries as community adoption grows.
4. **Extensibility:** A modular architecture allows easy integration of new LLM providers, analysis algorithms, or external data APIs in the future as the AI market changes.

## Consequences
### Positive
* **Robust Data Privacy:** Emphasizing security prevents data leaks and ensures sensitive user data is encrypted and stored safely.
* **Future-Proof Codebase:** Prioritizing maintainability and extensibility allows the code to easily adapt to new features and job crawler sources without major refactoring.
* **Reliable Performance:** Ensuring scalability keeps response times fast and consistent even under peak traffic and heavy background data processing.

### Negative
* **Increased Development Complexity:** Implementing strict security rules (encryption, input validation) and clean abstractions increases initial development effort.
* **Performance Overhead:** Encrypting data and validating security policies can lead to major processing latencies.
* **Higher Infrastructure Costs:** Supporting a highly scalable multi-agent backend and large-scale web crawlers requires more robust and expensive hosting resources.

## Decision Date
Approved on 18/07/2026
