import { Metadata } from "next"
import Link from "next/link"
import { ShieldCheck } from "lucide-react"

export const metadata: Metadata = {
  title: "Privacy Policy | VeritasAd",
  description: "Privacy Policy for VeritasAd - How we collect, use, and protect your data",
}

export default function PrivacyPage() {
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
        <h1 className="text-4xl font-extrabold tracking-tight mb-4">Privacy Policy</h1>
        <p className="text-muted-foreground mb-8">Last updated: {lastUpdated}</p>

        <div className="prose prose-gray dark:prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Introduction</h2>
            <p className="text-muted-foreground">
              At VeritasAd, we take your privacy seriously. This Privacy Policy explains how we collect, 
              use, disclose, and safeguard your information when you use our AI-powered advertising detection service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Information We Collect</h2>
            <h3 className="text-xl font-semibold mb-2">Personal Information</h3>
            <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
              <li>Account information (email, name, phone number)</li>
              <li>Payment information (processed securely through third-party providers)</li>
              <li>Telegram account information (when linking)</li>
              <li>Profile preferences</li>
            </ul>
            
            <h3 className="text-xl font-semibold mb-2 mt-6">Usage Data</h3>
            <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
              <li>Video content you submit for analysis</li>
              <li>Analysis results and reports</li>
              <li>Interaction with our service</li>
              <li>Device and browser information</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. How We Use Your Information</h2>
            <p className="text-muted-foreground">We use the collected information to:</p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li>Provide and maintain our advertising detection services</li>
              <li>Process your payments and manage subscriptions</li>
              <li>Improve and personalize your experience</li>
              <li>Send you technical notices and support messages</li>
              <li>Respond to your comments and questions</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Data Storage and Security</h2>
            <p className="text-muted-foreground">
              Your data is stored on secure servers with industry-standard encryption. We implement 
              appropriate technical and organizational measures to protect your personal information 
              against unauthorized access, alteration, disclosure, or destruction.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Third-Party Services</h2>
            <p className="text-muted-foreground">
              We may share your information with third-party service providers who assist us in operating 
              our service, conducting our business, or serving our users. These parties are obligated 
              to maintain the confidentiality of your information.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Data Retention</h2>
            <p className="text-muted-foreground">
              We will retain your personal information only for as long as is necessary for the 
              purposes set out in this Privacy Policy. Analysis data may be retained for up to 12 
              months after your last interaction with the service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Your Rights</h2>
            <p className="text-muted-foreground">Under GDPR and other regulations, you have the right to:</p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li>Access your personal data</li>
              <li>Rectify inaccurate personal data</li>
              <li>Request erasure of your personal data</li>
              <li>Restrict processing of your personal data</li>
              <li>Data portability</li>
              <li>Object to processing</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Cookies</h2>
            <p className="text-muted-foreground">
              We use cookies and similar tracking technologies to track activity on our service and hold 
              certain information. For detailed information about the cookies we use, please refer to 
              our Cookie Policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">9. Children&apos;s Privacy</h2>
            <p className="text-muted-foreground">
              Our Service does not address anyone under the age of 13. We do not knowingly collect 
              personally identifiable information from anyone under the age of 13.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">10. Changes to This Policy</h2>
            <p className="text-muted-foreground">
              We may update our Privacy Policy from time to time. We will notify you of any changes 
              by posting the new Privacy Policy on this page and updating the &quot;last updated&quot; date.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">11. Contact Us</h2>
            <p className="text-muted-foreground">
              If you have any questions about this Privacy Policy, please contact us at:{" "}
              <a href="mailto:privacy@veritasad.ai" className="text-primary hover:underline">
                privacy@veritasad.ai
              </a>
            </p>
          </section>
        </div>
      </main>
    </div>
  )
}
