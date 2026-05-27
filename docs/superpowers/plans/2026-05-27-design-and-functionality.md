# Design & Functionality Pass — Implementation Plan (Sub-Project C)

**Spec:** `docs/superpowers/specs/2026-05-27-design-and-functionality-design.md`
**Executor:** Codex (external)
**Goal:** Deliver the consistency pass, analyze-flow upgrade, result/history/dashboard improvements, a11y, perf, and i18n cleanup defined in the spec.

**Ground rules:**
- Frontend-only PRs; no backend changes beyond reading the additive fields A delivers (`stage`, `attempt`, `hint_action`).
- Land in 4–6 small PRs, not one mega-PR. Suggested grouping below.
- Each PR includes Lighthouse + bundle-analyzer numbers in the description.
- Conventional commits (`feat(ui): …`, `refactor(ui): …`, `chore(perf): …`).

---

## Task 1 — Design tokens

**PR 1.**

**Files:** `frontend/src/styles/globals.css`, `frontend/tailwind.config.ts`, `frontend/src/lib/tokens.ts` (new).

Define semantic CSS variables for surfaces, foregrounds, accent, danger, warning, success in both themes. Add Tailwind aliases. Replace inline hex/RGBA in `components/*` and `app/(app)/*` with token utilities. Do not introduce new colors.

**Done when:** grep for hardcoded `#` colors in `components/` and `app/(app)/` returns only token definitions; both themes still render correctly.

---

## Task 2 — Layout primitives

**PR 1 (same as Task 1) or PR 2.**

**Files (new):** `frontend/src/components/layout/{PageHeader,PageSection,EmptyState,LoadingState}.tsx`.

Build the four primitives. Public props minimal: `title`, `subtitle?`, `actions?`, `breadcrumb?` for `PageHeader`; `title`, `description?`, `children` for `PageSection`; `icon`, `title`, `description?`, `cta?` for `EmptyState`. `LoadingState` exports `<LoadingCard />`, `<LoadingTable />`, `<LoadingDetail />` variants using the existing `Skeleton`.

Migrate every page under `app/(app)/*` to use them. Pages stop owning outer container/spacing — they only compose primitives.

**Done when:** no page under `app/(app)/*` has a top-level `<div className="container ...">` block of its own; all use `PageHeader` + `PageSection`.

---

## Task 3 — Analyze stages & error UI

**PR 2.**

**Files (new):** `frontend/src/components/analyze/{AnalyzeStages,AnalyzeError}.tsx`. **Modify:** `app/(app)/analyze/page.tsx`.

`AnalyzeStages` renders 5 stages: Queue, Download, Audio, Visual, Score. Reads `stage` from progress event; falls back to mapping `progress` percent → stage if `stage` missing.

`AnalyzeError` reads `hint_action`:
- `provide_cookies` → button "Open cookies guide" linking to `/docs#cookies`.
- `install_ffmpeg` → external link to ffmpeg install docs.
- `retry_later` → "Retry now" calling existing re-submit hook.
- `unsupported_url` → "Try a different URL".
- `unknown` → "Retry" + "Report problem" (mailto / Telegram link from settings).

**Done when:** running an analysis shows live stage + attempt; mocking each failure type via dev tools shows the right action button.

---

## Task 4 — Result view refactor

**PR 3.**

**Files (new):** `frontend/src/components/result/{ResultVerdictHeader,ResultEvidence,ResultActions}.tsx`. **Modify:** existing analyze result component.

Move sub-blocks into the three new components. Tabs in `ResultEvidence`: Visual / Audio / Disclosure / Links. Each entry copyable via icon-button using `navigator.clipboard`. `ResultActions` exposes Download report, Share link (copy to clipboard), Open in history.

Existing `VideoTimeline` mounts inside `ResultEvidence > Visual`; brand pills are clickable, jumping the timeline to first timestamp.

**Done when:** the analyze success state uses only the three components; old monolithic block removed.

---

## Task 5 — History upgrade

**PR 3 (or PR 4).**

**Files (new):** `frontend/src/components/history/{HistoryFilters,HistoryTable}.tsx`. **Modify:** `app/(app)/history/page.tsx`.

Filter bar with date range, verdict multi-select, platform multi-select, URL search. Filters live in URL query params; navigating preserves them. Row actions: View, Re-run, Copy link, Delete.

If the backend list endpoint already accepts filter params, use them. If not, document the gap in `docs/decision-log.md` and filter client-side as a temporary measure; flag for follow-up.

Empty state via `EmptyState` with CTA to `/analyze`.

**Done when:** filters survive page reload via URL; row actions all work; empty state shows on a fresh account.

---

## Task 6 — Dashboard counters + chart

**PR 4.**

**Files (new):** `frontend/src/components/dashboard/{DashboardCounters,VerdictsOverTimeChart}.tsx`. **Modify:** `app/(app)/dashboard/page.tsx`.

Three counters using `StatCard`: total analyses, ad-rate %, distinct brands. Period selector (7d/30d/90d) in `PageHeader` action slot, drives query params.

Recharts stacked area chart of verdicts over time. Recharts already a dep; lazy-import to keep dashboard bundle slim.

Top-10 brands list, each row deep-links to `/history?brand=...`.

Empty states everywhere data may be absent.

**Done when:** dashboard renders for a new account (empty states), and for an account with data (numbers + chart).

---

## Task 7 — Accessibility pass

**PR 5.**

**Files:** `frontend/.eslintrc.*` (or `eslint.config.*`), interactive components project-wide.

Enable `eslint-plugin-jsx-a11y` recommended config (already transitively via `eslint-config-next`, but verify rules active). Fix all warnings in `components/*` and `app/(app)/*`. Add `aria-label` to icon-only buttons. Verify focus rings visible in both themes.

Manual keyboard pass through the five core routes. Capture Lighthouse a11y score before/after.

**Done when:** `next lint` clean; Lighthouse a11y ≥ 95 on the five core routes; keyboard pass log attached to PR.

---

## Task 8 — Performance pass

**PR 5 or PR 6.**

**Files:** dynamic imports across `app/page.tsx` and any route using `BackgroundWeb`/`InteractiveSpiderweb`.

- `dynamic(() => import('@/components/BackgroundWeb'), { ssr: false, loading: () => null })` for three.js components.
- Audit `framer-motion` usage — switch to `LazyMotion` + `domAnimation` where appropriate.
- Defer analytics / telemetry scripts via `next/script` strategy `afterInteractive` (verify they aren't `beforeInteractive` already).
- Run `@next/bundle-analyzer`; commit `docs/decision-log.md` entry with first-load JS size before/after.

**Done when:** LCP ≤ 2.5s on `/` on a mid-tier laptop run; first-load JS ≤ 200 KB gzip (excluding three.js chunk); bundle-analyzer report screenshot attached.

---

## Task 9 — i18n completeness

**PR 6.**

**Files:** all components and pages that ship user-visible strings; `frontend/src/lib/i18n/missing-key-reporter.ts` (new).

Sweep for raw string literals not routed through the i18n surface. Add the dev-only missing-key reporter that hooks into the existing translation function and warns once per session per missing key.

Pick the 4 most-used languages (RU, EN, plus 2 others). Smoke-test header, footer, analyze flow, result view, error states for truncation and layout breaks.

**Done when:** dev console shows no missing-key warnings on the five core routes; manual smoke of 4 languages passes.

---

## Task 10 — Docs

**Files:** `docs/decision-log.md` (append), `frontend/README.md` (modify or create).

- `decision-log.md`: scope of polish pass + Lighthouse / bundle numbers.
- `frontend/README.md`: how to use the new layout primitives, design tokens table, where to add new translations.

---

## Verification (after all PRs)

- `npm run type-check && npm run lint` clean.
- Lighthouse on `/`, `/analyze`, `/dashboard`, `/history`, `/pricing`: a11y ≥ 95, perf ≥ 85, LCP ≤ 2.5s on `/`.
- First-load JS ≤ 200 KB gzip excluding three.js.
- Manual keyboard pass through the five core routes.
- Smoke 4 languages; no missing-key warnings on core routes.
- Stage / attempt / hint_action wiring confirmed against backend from A (or feature-flagged off until A lands).

## Suggested PR Sequence

| PR | Tasks | Why grouped |
|---|---|---|
| 1 | 1, 2 | Tokens + primitives are foundation |
| 2 | 3 | Analyze flow self-contained |
| 3 | 4, 5 | Result + history share table/tab patterns |
| 4 | 6 | Dashboard independent |
| 5 | 7, 8 | Cross-cutting cleanup |
| 6 | 9, 10 | Final polish + docs |

## Dependencies

- PRs 2 (analyze stages reading `stage`/`attempt`) and any error UI consuming `hint_action` benefit from A being merged first, but can ship behind a graceful fallback before A lands.
- B has no dependency on C; can proceed in parallel.

## Out of scope

A and B (other sub-projects), brand rebrand, new business features, mobile, replacing the component stack, adding JS test runner.
