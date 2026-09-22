# ADR-03: Codebase Organization by Feature with Layered Architecture

## Status
Approved

## Context
This decision starts from the context that backend and frontend structures can follow a standard layered approach from routers -> views -> services -> repositories -> models. However, organizing code solely by technical layer introduces significant risks as the project grows. A single directory can quickly increase to dozens of files, making it extremely difficult to identify which files belong to which business feature.

## Decision
Standardize codebase development by structuring both frontend and backend directories by business feature and applying the layered architecture inside each feature folder. This ensures consistency and flexibility in code organization.

## Rationale
1. **Encapsulation of Features:** Keeping all components of a feature in a single folder makes it easier to locate, modify, or delete a feature without scanning multiple global directories.
2. **Improved Maintainability:** Developers can work on a specific business domain inside a single, self-contained directory, which reduces cognitive load.
3. **Prevention of Cluttered Directories:** Structuring by feature prevents technical layers from becoming cluttered with unrelated code files.
4. **Better Scalability for Personal Development:** As a single developer on a tight schedule, finding files quickly based on the business capability you are editing is faster than navigating a purely layered structure.

## Consequences
### Positive
* **High Cohesion:** Code files that change together are stored together, increasing code cohesion and modularity.
* **Simplified Navigation:** Project directories match the business domain, making the codebase intuitive to navigate.
* **Easier Testing:** Mocking and writing unit tests for a specific feature is simpler because all dependencies are grouped in the same module.

### Negative
* **Redundant Utilities:** Features might implement similar utility functions, potentially leading to duplication if not properly extracted into a shared/common module.
* **Upfront Planning Overhead:** Setting up features with their own sub-layers requires more planning upfront than just dropping files into global layers.

## Decision Date
Approved on 18/07/2026
