import { Metadata } from "next"
import Link from "next/link"
import { ShieldCheck } from "lucide-react"

export const metadata: Metadata = {
  title: "Terms of Service | VeritasAd",
  description: "Terms of Service for VeritasAd - AI-powered advertising detection system",
}

export default function TermsPage() {
  const lastUpdated = "March 17, 2026"

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <span>VeritasAd</span>
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto max-w-3xl px-4 py-12">
        <h1 className="text-4xl font-extrabold tracking-tight mb-4">Terms of Service</h1>
        <p className="text-muted-foreground mb-8">Last updated: {lastUpdated}</p>

        <div className="prose prose-gray dark:prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Acceptance of Terms</h2>
            <p className="text-muted-foreground">
              By accessing and using VeritasAd (&quot;the Service&quot;), you accept and agree to be bound 
              by the terms and provision of this agreement. If you do not agree to abide by these 
              terms, please do not use this Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Description of Service</h2>
            <p className="text-muted-foreground">
              VeritasAd is an AI-powered advertising detection system that analyzes video content 
              to identify potential advertising, sponsored content, and brand integrations. The Service 
              includes video analysis, brand detection, and compliance reporting.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. User Accounts</h2>
            <p className="text-muted-foreground">
              To use the Service, you must create an account. You agree to:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li>Provide accurate and complete registration information</li>
              <li>Maintain the security of your account credentials</li>
              <li>Promptly update any changes to your information</li>
              <li>Accept responsibility for all activities under your account</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Acceptable Use</h2>
            <p className="text-muted-foreground">
              You agree not to use the Service to:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li>Upload or analyze content that infringes on intellectual property rights</li>
              <li>Attempt to gain unauthorized access to the Service</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Use the Service for any illegal purpose</li>
              <li>Submit false or misleading information</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Intellectual Property</h2>
            <p className="text-muted-foreground">
              The Service, including all content, features, and functionality, is owned by VeritasAd 
              and is protected by copyright, trademark, and other intellectual property laws. You may not 
              reproduce, distribute, modify, or create derivative works from any part of the Service 
              without our prior written consent.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Payment and Subscriptions</h2>
            <p className="text-muted-foreground">
              Some features of the Service require a paid subscription. By subscribing, you agree to 
              pay all fees and charges associated with your subscription. All payments are non-refundable 
              unless otherwise specified.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Limitation of Liability</h2>
            <p className="text-muted-foreground">
              THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTY OF ANY KIND. VERITASAD DOES NOT 
              WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED OR ERROR-FREE. IN NO EVENT SHALL VERITASAD 
              BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Termination</h2>
            <p className="text-muted-foreground">
              We reserve the right to terminate or suspend your account at any time for any violation 
              of these Terms or for any other reason at our sole discretion.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">9. Changes to Terms</h2>
            <p className="text-muted-foreground">
              We may modify these Terms at any time. Your continued use of the Service after any 
              modifications indicates your acceptance of the modified Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">10. Contact Information</h2>
            <p className="text-muted-foreground">
              If you have any questions about these Terms, please contact us at: 
              <a href="mailto:legal@veritasad.ai" className="text-primary hover:underline"> legal@veritasad.ai</a>
            </p>
          </section>
        </div>
      </main>
    </div>
  )
}
