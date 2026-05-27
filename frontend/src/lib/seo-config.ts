export type SeoPageConfig = {
  title: string
  description: string
  keywords: string[]
  ogTitle?: string
  ogDescription?: string
  canonical: string
  robots?: {
    index: boolean
    follow: boolean
  }
}

type SeoLocaleConfig = Record<string, SeoPageConfig>

type SeoConfig = {
  en: SeoLocaleConfig
  ru: SeoLocaleConfig
}

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || "https://veritasad.ai"

const indexed = { index: true, follow: true }
const noindexed = { index: false, follow: false }

const en: SeoLocaleConfig = {
  home: {
    title: "VeritasAd | Ad Intelligence Command Center",
    description:
      "Detect ads in video and social content with AI, track compliance signals, and generate evidence-ready reports from a single command center.",
    keywords: ["ad intelligence", "advertising detection", "video compliance", "brand safety", "social media analysis"],
    ogTitle: "VeritasAd | Ad Intelligence Command Center",
    ogDescription: "AI ad detection and compliance intelligence for video and social content.",
    canonical: `${BASE_URL}/`,
    robots: indexed,
  },
  analyze: {
    title: "Analyze Content | VeritasAd",
    description:
      "Analyze videos and social posts for advertising signals, disclosures, and brand mentions with real-time progress and explainable confidence scoring.",
    keywords: ["content analysis", "ad detection", "sponsored content", "video AI", "brand mentions"],
    ogTitle: "Analyze Content | VeritasAd",
    ogDescription: "Detect ads in video and social posts with explainable AI verdicts.",
    canonical: `${BASE_URL}/analyze`,
    robots: indexed,
  },
  pricing: {
    title: "Pricing | VeritasAd",
    description:
      "Explore transparent VeritasAd plans for teams and enterprises, including subscriptions and pay-as-you-go credits for ad compliance analysis.",
    keywords: ["veritasad pricing", "ad compliance pricing", "analysis credits", "saas plans", "ai pricing"],
    ogTitle: "Pricing | VeritasAd",
    ogDescription: "Simple, transparent plans for ad intelligence and compliance teams.",
    canonical: `${BASE_URL}/pricing`,
    robots: indexed,
  },
  docs: {
    title: "Docs | VeritasAd",
    description:
      "Read VeritasAd documentation for self-hosted setup, API connectivity, and deployment guidance for reliable ad intelligence workflows.",
    keywords: ["veritasad docs", "self-hosted setup", "api integration", "deployment guide", "compliance platform"],
    ogTitle: "Docs | VeritasAd",
    ogDescription: "Self-hosted setup guide and integration docs for VeritasAd.",
    canonical: `${BASE_URL}/docs`,
    robots: indexed,
  },
  login: {
    title: "Sign In | VeritasAd",
    description: "Sign in to VeritasAd to access your ad intelligence dashboard, analysis history, and compliance reporting workspace.",
    keywords: ["veritasad login", "sign in", "ad intelligence dashboard", "account access", "compliance platform"],
    ogTitle: "Sign In | VeritasAd",
    ogDescription: "Access your VeritasAd workspace and analysis tools.",
    canonical: `${BASE_URL}/auth/login`,
    robots: noindexed,
  },
  register: {
    title: "Sign Up | VeritasAd",
    description: "Create your VeritasAd account to analyze video and social content for advertising signals and compliance risks.",
    keywords: ["veritasad sign up", "create account", "ad analysis", "compliance onboarding", "ai detection"],
    ogTitle: "Sign Up | VeritasAd",
    ogDescription: "Create your VeritasAd account and start analyzing content.",
    canonical: `${BASE_URL}/auth/register`,
    robots: noindexed,
  },
  dashboard: {
    title: "Dashboard | VeritasAd",
    description: "Manage analysis operations, monitor confidence trends, and track compliance outcomes from the VeritasAd dashboard.",
    keywords: ["veritasad dashboard", "analysis operations", "compliance metrics", "workflow management", "team analytics"],
    ogTitle: "Dashboard | VeritasAd",
    ogDescription: "Your operational hub for ad intelligence workflows.",
    canonical: `${BASE_URL}/dashboard`,
    robots: noindexed,
  },
  history: {
    title: "History | VeritasAd",
    description: "Review completed analyses, verdict timelines, and historical compliance evidence across your VeritasAd projects.",
    keywords: ["analysis history", "verdict timeline", "compliance archive", "report history", "evidence records"],
    ogTitle: "History | VeritasAd",
    ogDescription: "Track previous analyses and compliance outcomes.",
    canonical: `${BASE_URL}/history`,
    robots: noindexed,
  },
  account: {
    title: "Account | VeritasAd",
    description: "Update profile settings, billing preferences, and security options for your VeritasAd account.",
    keywords: ["account settings", "billing", "security", "profile", "veritasad account"],
    ogTitle: "Account | VeritasAd",
    ogDescription: "Manage profile, security, and billing settings.",
    canonical: `${BASE_URL}/account`,
    robots: noindexed,
  },
  admin: {
    title: "Admin | VeritasAd",
    description: "Admin controls for managing platform configuration, user access, and operational safeguards in VeritasAd.",
    keywords: ["admin panel", "platform management", "access control", "operations", "veritasad admin"],
    ogTitle: "Admin | VeritasAd",
    ogDescription: "Administrative controls for the VeritasAd platform.",
    canonical: `${BASE_URL}/admin`,
    robots: noindexed,
  },
  privacy: {
    title: "Privacy Policy | VeritasAd",
    description: "Read the VeritasAd Privacy Policy to understand how we collect, process, and protect data used in ad intelligence workflows.",
    keywords: ["privacy policy", "data protection", "gdpr", "user data", "compliance"],
    ogTitle: "Privacy Policy | VeritasAd",
    ogDescription: "How VeritasAd collects, uses, and protects your data.",
    canonical: `${BASE_URL}/legal/privacy`,
    robots: indexed,
  },
  terms: {
    title: "Terms of Service | VeritasAd",
    description: "Review VeritasAd Terms of Service covering platform usage, subscriptions, account responsibilities, and legal limitations.",
    keywords: ["terms of service", "legal terms", "subscription terms", "platform usage", "veritasad"],
    ogTitle: "Terms of Service | VeritasAd",
    ogDescription: "Service terms and legal conditions for using VeritasAd.",
    canonical: `${BASE_URL}/legal/terms`,
    robots: indexed,
  },
  cookies: {
    title: "Cookie Policy | VeritasAd",
    description: "Learn how VeritasAd uses essential, analytics, and functional cookies, and how you can manage your cookie preferences.",
    keywords: ["cookie policy", "tracking technologies", "privacy controls", "analytics cookies", "consent"],
    ogTitle: "Cookie Policy | VeritasAd",
    ogDescription: "Details on cookie usage and preference management.",
    canonical: `${BASE_URL}/legal/cookies`,
    robots: indexed,
  },
  gdpr: {
    title: "GDPR | VeritasAd",
    description: "Understand your GDPR rights with VeritasAd, including access, portability, erasure, and procedures for submitting requests.",
    keywords: ["gdpr rights", "data subject rights", "data portability", "erasure", "privacy rights"],
    ogTitle: "GDPR | VeritasAd",
    ogDescription: "Your data rights and GDPR request process at VeritasAd.",
    canonical: `${BASE_URL}/legal/gdpr`,
    robots: indexed,
  },
  disclaimer: {
    title: "Disclaimer | VeritasAd",
    description: "Read the VeritasAd disclaimer about AI analysis limitations, liability boundaries, and responsible use of compliance insights.",
    keywords: ["disclaimer", "liability", "ai limitations", "legal notice", "compliance guidance"],
    ogTitle: "Disclaimer | VeritasAd",
    ogDescription: "Important limitations and responsibility terms for VeritasAd.",
    canonical: `${BASE_URL}/legal/disclaimer`,
    robots: indexed,
  },
}

export const seoConfig: SeoConfig = {
  en,
  ru: en,
}
