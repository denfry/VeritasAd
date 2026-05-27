---
title: VeritasAd Obsidian Vault
created: 2026-05-27
tags: [veritasad, vault]
status: active
related: ["[[Home]]", "[[VeritasAd Map]]"]
---

# VeritasAd Obsidian Vault

This vault is the project knowledge layer for VeritasAd.

Open `D:\Projects\VeritasAd\obsidian-vault` as an Obsidian vault. The repository code stays outside the vault tree, while notes link back to canonical project files in `../docs`, `../backend`, and `../frontend`.

## Tree

```text
obsidian-vault/
|-- .obsidian/                 # empty vault marker; Obsidian owns its config
|-- Home.md                    # starting dashboard
|-- README.md                  # how to use this vault
|-- 00_Maps/                   # maps of content and navigation
|   `-- VeritasAd Map.md
|-- 00_Inbox/                  # quick captures before triage
|   `-- Inbox.md
|-- 10_Projects/               # active project work
|   |-- Ad Detection Platform.md
|   `-- VeritasAd Operating System.md
|-- 20_Areas/                  # durable responsibility areas
|   |-- Architecture.md
|   |-- Backend.md
|   |-- Frontend.md
|   |-- ML And Analysis Pipeline.md
|   `-- Release And Governance.md
|-- 30_Resources/              # reference notes and indexes
|   |-- Command Reference.md
|   |-- Decision Log Index.md
|   `-- Documentation Index.md
|-- 40_Archive/                # completed or inactive notes
|   `-- Archive.md
|-- 90_Daily/2026/05/          # daily notes
|   `-- 2026-05-27.md
|-- 99_Templates/              # copyable note templates
|   |-- Daily.md
|   |-- Decision.md
|   |-- Incident.md
|   `-- Project Note.md
`-- _agent/                    # agent-managed working memory
    |-- context/Active Context.md
    |-- heartbeat/README.md
    |-- memory/Project Memory.md
    `-- runs/README.md
```

## Conventions

- Keep canonical engineering rules in the repo docs. Use vault notes as maps, indexes, decisions, and working context.
- Add new project work under `10_Projects/`.
- Add stable ownership areas under `20_Areas/`.
- Add references under `30_Resources/`.
- Append daily activity to `90_Daily/YYYY/MM/YYYY-MM-DD.md`.
- Use wikilinks for project knowledge and Markdown links for repository files.

## Related

- [[Home]]
- [[VeritasAd Map]]
- [[VeritasAd Operating System]]
