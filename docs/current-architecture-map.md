# Current Architecture Map

## Product Purpose

VeritasAd detects advertising/compliance signals in video and social content and provides explainable evidence outputs for teams and partners.

## Core Business Capabilities

- video/url intake
- asynchronous analysis pipeline
- multimodal evidence scoring
- report generation and export
- user accounts, plans, credits, billing
- admin analytics and audit tooling

## Critical User Journeys

1. User submits URL/file for analysis.
2. Backend creates task and streams progress.
3. Pipeline computes verdict, confidence, and evidence markers.
4. User reviews results and exports PDF report.
5. Paid users manage plans/credits and API usage.

## Performance-Sensitive Flows

- video download and preprocessing
- logo detection and audio transcription
- queue throughput and worker backpressure
- progress stream responsiveness

## Security-Sensitive Operations

- auth token handling and API key lifecycle
- webhook signature/IP verification
- upload handling and URL/source validation
- admin and audit endpoints

## Deployment and Runtime

- FastAPI backend + Celery workers + Redis + PostgreSQL
- Next.js frontend (self-hosted path supported)
- containerized deployment options in `docker-compose*` and `infra/`

## Testing Maturity

- backend: unit/integration tests present
- frontend: no dedicated automated test suite configured
- contract-level API-client regression coverage needs strengthening
