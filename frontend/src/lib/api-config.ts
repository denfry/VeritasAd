export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
  /\/+$/,
  ""
)

export const FRONTEND_AUTH_DISABLED = process.env.NEXT_PUBLIC_DISABLE_AUTH === "true"

export type ApiHealthResponse = {
  status: string
  service?: string
  version?: string
  environment?: string
  [key: string]: unknown
}

export async function fetchApiHealth(signal?: AbortSignal): Promise<ApiHealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: "GET",
    cache: "no-store",
    headers: {
      Accept: "application/json",
    },
    signal,
  })

  if (!response.ok) {
    throw new Error(`API health check failed with status ${response.status}`)
  }

  return (await response.json()) as ApiHealthResponse
}
