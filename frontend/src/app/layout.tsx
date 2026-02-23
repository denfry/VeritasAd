import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { BackgroundWeb } from "@/components/BackgroundWeb"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: {
    default: "VeritasAd - AI Advertising Detection",
    template: "%s | VeritasAd",
  },
  description:
    "Neural network-based advertising detection in video content. Analyze videos and social posts for sponsored content disclosure.",
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
      <body className={`${inter.className} antialiased`}>
        <Providers>
          <BackgroundWeb />
          <div className="relative z-10">{children}</div>
        </Providers>
      </body>
    </html>
  )
}
