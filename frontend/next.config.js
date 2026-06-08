/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  },
  async headers() {
    const isDev = process.env.NODE_ENV === "development"
    const scriptSrc = [
      "'self'",
      "'unsafe-inline'",
      "https://telegram.org",
      ...(isDev ? ["'unsafe-eval'"] : []),
    ].join(" ")
    // Allow the configured backend origin (and its ws:// variant) in connect-src
    // so changing NEXT_PUBLIC_API_URL (e.g. a non-8000 port) doesn't break CSP.
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    const apiWsUrl = apiUrl.replace(/^http/, "ws")
    const connectSrc = [
      "'self'",
      apiUrl,
      apiWsUrl,
      "http://localhost:8000",
      "ws://localhost:8000",
      "https:",
      "ws:",
      "wss:",
      "*.supabase.co",
    ].join(" ")
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src " + scriptSrc,
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: blob: https:",
              "font-src 'self'",
              "connect-src " + connectSrc,
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
              "upgrade-insecure-requests",
            ].join("; "),
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains; preload",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
        ],
      },
    ]
  },
}

// Bundle analyzer (dev only)
if (process.env.ANALYZE === "true") {
  const withBundleAnalyzer = require("@next/bundle-analyzer")({ enabled: true })
  module.exports = withBundleAnalyzer(nextConfig)
} else {
  module.exports = nextConfig
}
