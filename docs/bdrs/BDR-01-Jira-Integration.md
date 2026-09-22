# BDR-01: Integration of Jira with GitHub Projects for AIJMC Management

## Status
Pending

## Context
The project currently uses GitHub Projects for issue and project management.

## Problem
One of the most obvious problems is the inconvenience of managing a project in the long term. These issues include:
- Limitations in Agile organizational methods (GitHub Projects are generally fine with Kanban).
- The platform binding between the repository and the project (GitHub downtime, while rare, can significantly delay the entire project)
- The need to expand Jira to accommodate future project management issues arising from third parties.

## Options Considered
- Continue using GitHub Projects.
- Integrate Jira with GitHub Projects.
- Linear

## Decision
Adopt Jira as the primary project management platform and integrate it with GitHub for development workflow visibility and traceability.

## Rationale

- **Separation of concerns:** Project management and source code management will be handled by separate platforms. Jira will manage project planning and work items, while GitHub will remain responsible for source code, repositories, branches, commits, and pull requests.

- **GitHub integration:** Jira can integrate GitHub development activity, allowing branches, commits, pull requests, builds, and deployments to be associated with Jira work items. This maintains traceability between planned work and implementation without requiring project management to remain inside GitHub.

- **Long-term extensibility:** Using a dedicated project management platform provides a clearer foundation for future project management requirements, including collaboration with third parties and potentially more complex workflows.

- **Reduced platform dependency:** Moving project management out of GitHub reduces the operational dependency between project planning and the source code hosting platform. A GitHub service disruption would not prevent the team from accessing project plans, issues, and other management information.

## Consequences

- **The team's workflow must be updated.** Developers will need to use Jira for project management while continuing to use GitHub for source control and code collaboration.

- **Existing project management data must be migrated.** Relevant issues, project information, and workflow data from GitHub Projects must be reviewed and migrated to Jira where appropriate.

- **There will be an initial migration and adoption cost.** Developers must configure Jira, establish workflows, migrate existing data, update documentation, and become familiar with the new process.

- **The project will maintain two primary tools with different responsibilities.** This introduces additional workflow and integration complexity, which must be managed through clear ownership and documented processes.

## Decision Date
Pending until 25/09/2026
