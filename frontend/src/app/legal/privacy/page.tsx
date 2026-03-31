import { Metadata } from "next"
import Link from "next/link"
import { ArrowLeft, Shield, Database, Eye, Lock, Share2, Clock, UserCheck, Cookie, Mail } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export const metadata: Metadata = {
  title: "Privacy Policy | VeritasAd",
  description: "Privacy Policy for VeritasAd - How we collect, use, and protect your data",
}

export default function PrivacyPage() {
  const lastUpdated = "March 31, 2026"

  return (
    <SiteShell>
      <div className="container mx-auto max-w-3xl px-4 py-12">
        <div className="mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight">Privacy Policy</h1>
          <p className="mt-2 text-muted-foreground">Last updated: {lastUpdated}</p>
        </div>

        <div className="space-y-6">
          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">1. Introduction</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  At VeritasAd, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered advertising detection service. By using our Service, you consent to the practices described in this policy.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Database className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">2. Information We Collect</h2>
                <h3 className="mt-4 text-base font-semibold">Personal Information</h3>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Account information (email address, name, phone number)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Payment information (processed securely through third-party providers)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Telegram account information (when linking your account)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Profile preferences and settings
                  </li>
                </ul>
                <h3 className="mt-6 text-base font-semibold">Usage Data</h3>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Video content and social media posts you submit for analysis
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Analysis results, reports, and detection data
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Interaction patterns with our service
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Device, browser, and IP address information
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Eye className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">3. How We Use Your Information</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  We use the collected information to:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Provide and maintain our advertising detection services
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Process your payments and manage subscriptions
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Improve and personalize your experience
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Send you technical notices and support messages
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Respond to your comments and questions
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Comply with legal obligations and enforce our terms
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Lock className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">4. Data Storage and Security</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Your data is stored on secure servers with industry-standard encryption. We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. Video content submitted for analysis is processed securely and deleted after the analysis period unless you choose to retain it.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Share2 className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">5. Third-Party Services</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  We may share your information with third-party service providers who assist us in operating our service, conducting our business, or serving our users. These include payment processors, cloud hosting providers, and analytics services. These parties are obligated to maintain the confidentiality of your information and are prohibited from using it for any other purpose.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Clock className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">6. Data Retention</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  We will retain your personal information only for as long as is necessary for the purposes set out in this Privacy Policy. Analysis data may be retained for up to 12 months after your last interaction with the service. You may request deletion of your data at any time through your account settings or by contacting us.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <UserCheck className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">7. Your Rights</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Under GDPR and other applicable regulations, you have the right to:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Access your personal data
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Rectify inaccurate personal data
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Request erasure of your personal data
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Restrict processing of your personal data
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Data portability
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Object to processing
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Cookie className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">8. Cookies</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  We use cookies and similar tracking technologies to track activity on our service and hold certain information. For detailed information about the cookies we use, please refer to our{" "}
                  <Link href="/legal/cookies" className="text-primary hover:underline">
                    Cookie Policy
                  </Link>
                  .
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Mail className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">9. Contact Us</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  If you have any questions about this Privacy Policy, please contact us at{" "}
                  <a href="mailto:privacy@veritasad.ai" className="text-primary hover:underline">
                    privacy@veritasad.ai
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12">
          <Link href="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Back to home
          </Link>
        </div>
      </div>
    </SiteShell>
  )
}
