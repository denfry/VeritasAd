/**
 * Loading UI for history page.
 */
export default function HistoryLoading() {
  return (
    <div className="container mx-auto max-w-6xl px-4 py-12">
      <div className="h-10 w-48 animate-pulse rounded bg-muted mb-8" />
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-20 animate-pulse rounded-lg bg-muted"
          />
        ))}
      </div>
    </div>
  )
}
