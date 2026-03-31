import { Metadata } from "next"
import Link from "next/link"
import { ArrowLeft, FileText, UserCheck, CreditCard, Scale, AlertCircle, Mail } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export const metadata: Metadata = {
  title: "Terms of Service | VeritasAd",
  description: "Terms of Service for VeritasAd - AI-powered advertising detection system",
}

export default function TermsPage() {
  const lastUpdated = "March 31, 2026"

  return (
    <SiteShell>
      <div className="container mx-auto max-w-3xl px-4 py-12">
        <div className="mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight">Terms of Service</h1>
          <p className="mt-2 text-muted-foreground">Last updated: {lastUpdated}</p>
        </div>

        <div className="space-y-6">
          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">1. Acceptance of Terms</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  By accessing and using VeritasAd (&quot;the Service&quot;), you accept and agree to be bound by the terms and provisions of this agreement. If you do not agree to abide by these terms, please do not use this Service. VeritasAd provides AI-powered advertising detection and compliance analysis for video and social media content.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Scale className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">2. Description of Service</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  VeritasAd is an AI-powered advertising detection system that analyzes video content, social media posts, and other digital media to identify potential advertising, sponsored content, brand integrations, and disclosure compliance. The Service includes video analysis, brand detection, audio transcription, visual logo recognition, and compliance reporting.
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
                <h2 className="text-xl font-semibold">3. User Accounts</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  To use the Service, you must create an account. You agree to:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Provide accurate and complete registration information
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Maintain the security of your account credentials
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Promptly update any changes to your information
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Accept responsibility for all activities under your account
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <AlertCircle className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">4. Acceptable Use</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  You agree not to use the Service to:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Upload or analyze content that infringes on intellectual property rights
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Attempt to gain unauthorized access to the Service or its infrastructure
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Interfere with or disrupt the Service or servers connected to the Service
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Use the Service for any illegal purpose or in violation of any laws
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Submit false or misleading information or content
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">5. Intellectual Property</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  The Service, including all content, features, and functionality, is owned by VeritasAd and is protected by copyright, trademark, and other intellectual property laws. You may not reproduce, distribute, modify, or create derivative works from any part of the Service without our prior written consent. Content you submit remains your property, but you grant us a license to process it for analysis purposes.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <CreditCard className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">6. Payment and Subscriptions</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Some features of the Service require a paid subscription. By subscribing, you agree to pay all fees and charges associated with your subscription plan. All payments are non-refundable unless otherwise specified in your plan terms. We reserve the right to change pricing with 30 days&apos; notice.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Scale className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">7. Limitation of Liability</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTY OF ANY KIND. VERITASAD DOES NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, SECURE, OR ERROR-FREE. IN NO EVENT SHALL VERITASAD BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF OR IN CONNECTION WITH THE USE OF THE SERVICE.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <AlertCircle className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">8. Termination</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  We reserve the right to terminate or suspend your account at any time for any violation of these Terms or for any other reason at our sole discretion. Upon termination, your right to use the Service will immediately cease.
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
                <h2 className="text-xl font-semibold">9. Contact Information</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  If you have any questions about these Terms, please contact us at{" "}
                  <a href="mailto:legal@veritasad.ai" className="text-primary hover:underline">
                    legal@veritasad.ai
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
