/**
 * Loading UI for analyze page - shown while segment loads.
 */
export default function AnalyzeLoading() {
  return (
    <div className="container mx-auto max-w-6xl px-4 py-12">
      <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <div className="h-10 w-48 animate-pulse rounded bg-muted" />
          <div className="h-4 w-full animate-pulse rounded bg-muted" />
          <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
          <div className="h-32 w-full animate-pulse rounded-lg bg-muted" />
        </div>
        <div className="h-64 animate-pulse rounded-lg bg-muted" />
      </div>
    </div>
  )
}
