import { MetadataRoute } from "next"

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || "https://veritasad.ai"

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/api/", "/account", "/admin", "/dashboard", "/history", "/payment/", "/auth/"],
      },
      {
        userAgent: "GPTBot",
        disallow: "/",
      },
    ],
    sitemap: `${BASE_URL}/sitemap.xml`,
    host: BASE_URL,
  }
}
