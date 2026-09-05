# ADR-09: Decision on Firebase Spark Tier Integration, CV Attachment Uploads, and Lifecycle Operations

## Status
Proposed

## Context
The platform requires consultees to upload Curriculum Vitae (CV) documents to enable automated profile extraction, scoring, and consultant matching. When a CV file is uploaded, the system needs to host the document securely.

## Decision
Using Firebase Storage to upload CV files with PATCH and DELETE endpoints. The decision consists of three part are firebase spark tier integration, environment and core configuration, and multi-layered PDF file validation (extension, size, MIME, and magic bytes).

## Rationale
1. The Firebase Spark tier provides 5 GB storage and 1 GB/day transfer with zero billing requirement.
2. Google Cloud Storage signed URLs require token-creation permissions and a billing account on GCP. Native Firebase download tokens provide permanent, resilient access on Spark without billing.
3. Validating file size, extension, MIME type, and magic bytes protects backend workers and client browsers from malicious payloads masquerading as PDF files.

## Consequences
### Positive
* Leverages the free Firebase Spark tier for document hosting.
* Malicious and oversized files are rejected at the application boundary prior to cloud upload.
* Allow scoring user ability based on Curriculum Vitae

### Negative
* Storage is capped at 5 GB and 1 GB/day bandwidth. Scaling beyond these thresholds will necessitate upgrading to the Blaze (pay-as-you-go) plan. Also, increase reliance on third-party services.
* Handling multipart uploads directly in the API process introduces modest latency during large file transfers compared to direct client-to-bucket uploads.

## Decision Date
Waiting for approval until 20/09/2026
