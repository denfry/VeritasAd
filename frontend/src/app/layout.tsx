import type { Metadata } from "next"
import { Manrope, Space_Grotesk } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { PremiumBackdrop } from "@/components/PremiumBackdrop"

const bodyFont = Manrope({
  subsets: ["latin"],
  variable: "--font-body",
})

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
})

export const metadata: Metadata = {
  title: {
    default: "VeritasAd | Ad Intelligence Command Center",
    template: "%s | VeritasAd",
  },
  description:
    "AI advertising detection for video and social content with self-hosted MVP support, live analysis progress, and premium compliance reporting.",
  keywords: ["advertising detection", "AI", "video analysis", "sponsored content", "disclosure"],
  authors: [{ name: "VeritasAd" }],
  openGraph: {
    type: "website",
    locale: "en_US",
  },
  icons: {
    icon: '/favicon.svg',
    apple: '/apple-icon.png',
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
        <Providers>
          <PremiumBackdrop />
          <div className="relative z-10">{children}</div>
        </Providers>
      </body>
    </html>
  )
}
