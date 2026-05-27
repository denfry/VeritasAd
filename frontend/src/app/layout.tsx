import type { Metadata } from "next"
import { Manrope, Space_Grotesk } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { PremiumBackdrop } from "@/components/PremiumBackdrop"
import { JsonLd } from "@/components/seo/JsonLd"

const bodyFont = Manrope({
  subsets: ["latin"],
  variable: "--font-body",
})

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
})

const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "https://veritasad.ai"

export const metadata: Metadata = {
  metadataBase: new URL(baseUrl),
  title: {
    default: "VeritasAd | Ad Intelligence Command Center",
    template: "%s | VeritasAd",
  },
  description:
    "AI advertising detection for video and social content with self-hosted MVP support, live analysis progress, and premium compliance reporting.",
  keywords: ["advertising detection", "AI", "video analysis", "sponsored content", "disclosure"],
  authors: [{ name: "VeritasAd", url: "https://veritasad.ai" }],
  creator: "VeritasAd",
  publisher: "VeritasAd",
  category: "technology",
  classification: "Business Software",
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "VeritasAd",
    images: [
      {
        url: "/opengraph-image",
        width: 1200,
        height: 630,
        alt: "VeritasAd - Ad Intelligence Command Center",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "@veritasad",
    creator: "@veritasad",
  },
  verification: {},
  other: {
    "msapplication-TileColor": "#06b6d4",
  },
}

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "VeritasAd",
  url: "https://veritasad.ai",
  logo: "https://veritasad.ai/favicon.svg",
}

const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "VeritasAd",
  url: "https://veritasad.ai",
  potentialAction: {
    "@type": "SearchAction",
    target: "https://veritasad.ai/docs?query={search_term_string}",
    "query-input": "required name=search_term_string",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${bodyFont.variable} ${displayFont.variable} relative antialiased`}>
        <JsonLd data={[organizationSchema, websiteSchema]} />
        <Providers>
          <PremiumBackdrop />
          <div className="relative z-10">{children}</div>
        </Providers>
      </body>
    </html>
  )
}
