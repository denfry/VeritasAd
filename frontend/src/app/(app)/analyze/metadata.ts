import type { Metadata } from "next"
import { seoConfig } from "@/lib/seo-config"

const page = seoConfig.en.analyze

export const metadata: Metadata = {
  title: page.title,
  description: page.description,
  keywords: page.keywords,
  robots: page.robots,
  alternates: {
    canonical: page.canonical,
  },
  openGraph: {
    title: page.ogTitle || page.title,
    description: page.ogDescription || page.description,
    url: page.canonical,
    siteName: "VeritasAd",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: page.ogTitle || page.title,
    description: page.ogDescription || page.description,
    site: "@veritasad",
    creator: "@veritasad",
  },
}
