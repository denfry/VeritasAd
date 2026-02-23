Scaling notes

- Add horizontal Celery workers for heavy video workloads
- Introduce read replicas for PostgreSQL when QPS grows
- Migrate large files to S3-compatible storage
- Consider Kubernetes for auto-scaling when traffic exceeds 1000 RPS
