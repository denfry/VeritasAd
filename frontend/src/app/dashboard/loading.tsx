/**
 * Loading UI for dashboard page.
 */
export default function DashboardLoading() {
  return (
    <div className="container mx-auto max-w-6xl px-4 py-12">
      <div className="h-10 w-64 animate-pulse rounded bg-muted mb-8" />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-lg bg-muted"
          />
        ))}
      </div>
    </div>
  )
}
