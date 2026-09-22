# ADR-01: Client-Server Architecture with Layered

## Status
Approved

## Context
This decision is set in the context of building an IT job market consulting system with moderate to high expected community demand. On the other hand, the development team consists of only a single developer who has prior experience with Client-Server architecture and layered design. Furthermore, the project has a timeline of only 10 weeks to develop.

## Decision
Use a Client-Server architecture for the overall software system with APIs organized according to REST principles. Additionally, backend will follow a Layered Architecture.

## Rationale
1. The developer has prior experience with Client-Server and Layered architectures which minimizes the learning curve and speeds up development within the 10-week timeline.
2. The Client-Server architecture allows the frontend and backend to be developed independently, reducing development dependencies.
3. The Layered Architecture separates responsibilities clearly and makes the source code easier to organize by feature modules.
4. The Client-Server architecture is flexible for deployment because it is supported by many cloud platforms.
5. It is more suitable for a personal project than a Microservices architecture.

## Consequences
### Positive
* Better separation between the frontend and backend.
* Easier to maintain, extend, and modify business logic.
* Supports independent deployment of the frontend and backend.

### Negative
* Network communication introduces latency because the system is distributed.
* The backend may suffer from common layered architecture issues such as the **Sinkhole Anti-Pattern**, **God Objects**, and limited availability if deployed as a single server.

## Decision Date
Approved on 18/07/2026
