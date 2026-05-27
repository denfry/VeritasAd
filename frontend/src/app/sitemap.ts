import { MetadataRoute } from "next"

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || "https://veritasad.ai"
const LAST_MODIFIED = new Date("2026-05-14")

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${BASE_URL}/`, lastModified: LAST_MODIFIED, changeFrequency: "weekly", priority: 1.0 },
    { url: `${BASE_URL}/analyze`, lastModified: LAST_MODIFIED, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/pricing`, lastModified: LAST_MODIFIED, changeFrequency: "monthly", priority: 0.8 },
    { url: `${BASE_URL}/docs`, lastModified: LAST_MODIFIED, changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE_URL}/auth/login`, lastModified: LAST_MODIFIED, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE_URL}/auth/register`, lastModified: LAST_MODIFIED, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE_URL}/legal/privacy`, lastModified: LAST_MODIFIED, changeFrequency: "yearly", priority: 0.6 },
    { url: `${BASE_URL}/legal/terms`, lastModified: LAST_MODIFIED, changeFrequency: "yearly", priority: 0.6 },
    { url: `${BASE_URL}/legal/cookies`, lastModified: LAST_MODIFIED, changeFrequency: "yearly", priority: 0.5 },
    { url: `${BASE_URL}/legal/gdpr`, lastModified: LAST_MODIFIED, changeFrequency: "yearly", priority: 0.5 },
    { url: `${BASE_URL}/legal/disclaimer`, lastModified: LAST_MODIFIED, changeFrequency: "yearly", priority: 0.5 },
  ]
}
