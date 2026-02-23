import Link from "next/link"

/**
 * Global 404 page - served for unmatched routes.
 */
export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <h1 className="text-4xl font-bold">404</h1>
      <h2 className="text-xl font-semibold">Page not found</h2>
      <p className="max-w-md text-center text-muted-foreground">
        The page you are looking for does not exist or has been moved.
      </p>
      <Link
        href="/"
        className="rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:opacity-90"
      >
        Go to homepage
      </Link>
    </div>
  )
}
