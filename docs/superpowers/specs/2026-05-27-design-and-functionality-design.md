# Design & Functionality Pass (Sub-Project C) — Design Spec

**Date:** 2026-05-27
**Sub-project:** C (final of A → B → C)
**Status:** Draft for implementation

## Context

Frontend stack: Next.js 15, React 19, Tailwind 4, framer-motion, three.js, recharts, lucide, sonner, TanStack Query, Supabase SSR. Pages already present: `analyze`, `dashboard`, `history`, `account`, `admin`, `pricing`, `payment`, `auth`, `docs`, `legal/*`. Solid foundation; missing is consistency, polish, and a few UX gaps in core flows.

This spec is the **least bounded** of A/B/C. To stay shippable, it is scoped as a **polish + targeted-feature pass**, not a redesign. A full visual overhaul requires a designer and is explicitly out of scope here.

## Goal

Raise the perceived quality and usability of the core user flows (analyze → result → history) without changing brand identity, then close the most-visible functional gaps that hurt day-to-day use.

## Non-Goals

- Visual rebrand or new design language.
- New revenue features, billing surfaces, or admin tooling.
- Mobile-app surfaces.
- Replacing component libraries (Tailwind / framer-motion / three.js stay).
- Backend changes beyond what A already delivers.

## Success Criteria (Definition of Done)

1. **Consistency pass:** every page in `(app)/*` uses a shared `PageHeader`, `PageSection`, and `EmptyState` set. No ad-hoc heading/spacing decisions remain in those pages.
2. **Analyze flow:** while a job runs, the user sees stage (downloading / analyzing audio / detecting brands / scoring), live progress %, current retry attempt (from A), and clear error UI with the `hint_action` mapped to an actionable button (e.g. "Re-upload cookies", "Try again").
3. **Result view:** detected brands, evidence timestamps, transcript excerpts, disclosure markers, and the final verdict each render in a dedicated section with copy-to-clipboard. PDF/HTML export buttons surface clearly.
4. **History:** server-side filters (date range, verdict, source platform), retry-failed action, and shareable per-analysis link work.
5. **Dashboard:** at-a-glance counters (total analyses, ad-rate, top brands) populate from existing endpoints; empty state when no data.
6. **Accessibility:** every interactive element keyboard-reachable; focus rings visible in both themes; aria-labels on icon-only buttons; color contrast ≥ WCAG AA on default theme.
7. **Performance:** three.js background lazy-loaded; LCP on `/` ≤ 2.5s on a mid-tier laptop; JS bundle on first load ≤ 200 KB gzip excluding three.js.
8. **i18n completeness:** no untranslated strings on the localized routes; missing-key reporter in dev console.

## Scope (Concrete deliverables)

### 1. Design tokens & primitives

- Audit `globals.css` and `tailwind.config`. Codify: spacing scale (4-based), radii (`sm/md/lg/xl`), shadow scale, typographic scale (text-xs → text-4xl), semantic colors (`--bg-surface`, `--bg-elevated`, `--fg-primary`, `--fg-muted`, `--accent`, `--danger`, `--warning`, `--success`).
- Replace inline `style={{...}}` colors and one-off hex values in pages/components with semantic tokens.
- Add `tailwind.config` aliases for the tokens so utility classes (`bg-surface`, `text-muted`) work everywhere.

### 2. Shared layout primitives

New components under `src/components/layout/`:

- `PageHeader.tsx` — title, optional subtitle, breadcrumb slot, action slot (right-aligned buttons).
- `PageSection.tsx` — section title, description, content slot. Consistent padding and divider rules.
- `EmptyState.tsx` — icon + title + description + optional CTA. Used by `history`, `dashboard`, search results.
- `LoadingState.tsx` — wraps `Skeleton` patterns for cards, tables, and detail views.

Migrate all `(app)/*` pages to use these. No page should set its own outer container/spacing.

### 3. Analyze flow upgrade

- Stage timeline component (`AnalyzeStages.tsx`) showing 5 stages: Queue → Download → Audio → Visual → Score. Active stage highlighted, completed stages checked, failed stage marked red.
- Progress event from backend (A) populates `stage` and `attempt`. Frontend reads these; falls back to old `progress` percent if absent.
- Error UI: `AnalyzeError.tsx` reads `hint_action` from the failed job and renders a primary action button:
  - `provide_cookies` → "Update cookies file" → opens a doc modal.
  - `install_ffmpeg` → "Install ffmpeg" → external link.
  - `retry_later` → "Retry now" → re-submits.
  - `unsupported_url` → "Use a different URL".
  - `unknown` → generic retry + report-bug link.

### 4. Result view sectioning

`AnalyzeResult.tsx` decomposes into:

- `ResultVerdictHeader` — top: verdict (Ad / Mention / No-ad / etc.), confidence, model version footnote.
- `ResultEvidence` — tabs: Visual brands · Audio transcript · Disclosure markers · Detected links/CTAs. Each tab has copy-to-clipboard on entries.
- `ResultActions` — Download report (PDF) · Share link · Open in history.
- Existing `VideoTimeline` integrated into `ResultEvidence > Visual` with brand pills clickable to jump.

### 5. History page upgrade

- Filter bar: date range, verdict (multi), platform (multi), search by URL/title.
- Row actions: View · Re-run · Copy link · Delete.
- Server-side query parameters; existing endpoint extension is minimal (or filter client-side first if endpoint changes are out of scope — document tradeoff).
- Empty state with CTA "Run your first analysis".

### 6. Dashboard

- Three counter cards (uses existing `StatCard`): total analyses (period selector 7d/30d/90d), ad-rate %, distinct brands detected.
- One chart (recharts) — verdicts over time (stacked).
- Top-10 brands list with deep-link to History filtered by brand.
- Empty state when no data.

### 7. Accessibility audit

- Add `next lint` rule + a `jsx-a11y` config update; fix all warnings in `(app)/*` and `components/*`.
- Manual pass with keyboard only — every link, button, dialog, menu reachable; modal traps focus; escape closes.
- Focus ring tokens applied to all interactive primitives.
- Run `pa11y` (or Lighthouse a11y) against the five core routes; capture baseline and post-fix scores.

### 8. Performance

- Lazy-load `BackgroundWeb` / `InteractiveSpiderweb` (dynamic import + `loading`).
- Verify framer-motion features tree-shaken; move heavy 3D pages to `dynamic` boundaries.
- Run `@next/bundle-analyzer` baseline + post; commit a short note in `docs/decision-log.md`.
- Defer telemetry / analytics scripts (`afterInteractive`).

### 9. i18n completeness

- Sweep `(app)/*` and shared components for raw string literals; route through the existing i18n surface.
- Add a dev-only missing-key reporter that warns once per session per missing key.
- Verify the 4 most-used languages (RU, EN, plus 2 picked by traffic) render with no truncation in the header, footer, and analyze flow.

## Architecture / File map

```
frontend/src/
  components/
    layout/PageHeader.tsx
    layout/PageSection.tsx
    layout/EmptyState.tsx
    layout/LoadingState.tsx
    analyze/AnalyzeStages.tsx
    analyze/AnalyzeError.tsx
    analyze/AnalyzeResult.tsx              (refactor existing)
    result/ResultVerdictHeader.tsx
    result/ResultEvidence.tsx
    result/ResultActions.tsx
    history/HistoryFilters.tsx
    history/HistoryTable.tsx               (refactor existing)
    dashboard/DashboardCounters.tsx
    dashboard/VerdictsOverTimeChart.tsx
  lib/
    tokens.ts                              (semantic token names)
    i18n/missing-key-reporter.ts
  app/(app)/...                            (slim pages; mostly layout glue)
  styles/globals.css                       (token vars)
tailwind.config.ts                         (token aliases)
```

## Testing

There is no frontend test runner today (`AGENTS.md` notes this). Do not introduce one in this spec — adopting Vitest is itself a separable initiative. Instead:

- Type-check (`npm run type-check`) and `next lint` must be green.
- Manual checklist in PR description, mirroring success criteria.
- Lighthouse run on five core routes; numbers attached to PR.
- Visual regression: not in scope (would require Chromatic or Playwright snapshot infra).

## Risks

| Risk | Mitigation |
|---|---|
| Polish PR balloons into rewrite | Strict scope: only listed deliverables; no new pages or features |
| Backend contract drift (stage/attempt fields) | Frontend reads them optionally; falls back to current behavior |
| Performance budget unmet | Bundle-analyzer step gates the merge; biggest win is lazy-loading three.js |
| Accessibility audit reveals deep issues | Land low-hanging fixes; file follow-up issues for systemic ones |
| i18n sweep destabilizes copy | Diff carefully; reviewers smoke-test 2 languages |

## Out of Scope (Explicit)

- A (local env / downloads) and B (dataset) — separate specs already drafted.
- Brand / marketing rebrand.
- New paid features.
- Replacing three.js / framer-motion / Tailwind.
- Adding a JS test runner.
- Native mobile.

## Governance

- `AGENTS.md`: no API contracts broken; frontend-only changes; backward compatibility preserved (new progress fields are additive).
- Rollback: revert PR; no DB or env changes required.
