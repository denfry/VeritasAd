# Future Growth Plan

## When to Split Modules

- sustained high change rate with frequent merge conflicts
- domain logic complexity blocks team parallelism

## When to Extract Services

- independent scaling and reliability requirements
- hard isolation required for security/compliance reasons

## Config Growth Strategy

- central schema for settings
- environment-specific overlays
- deprecate config keys with clear migration windows

## Data Access Evolution

- repository abstractions per domain
- read model optimization for analytics-heavy endpoints

## High-Load Isolation

- separate queues and worker pools per workload type
- cache and precompute for repetitive expensive operations

## Extension APIs

- define stable ingestion plugin contracts
- version extension interfaces before external adoption
