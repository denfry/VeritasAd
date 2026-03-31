import { Metadata } from "next"
import Link from "next/link"
import { ArrowLeft, AlertTriangle, FileText, Info, ExternalLink, UserCheck, Mail } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export const metadata: Metadata = {
  title: "Disclaimer | VeritasAd",
  description: "Disclaimer and limitations of liability for VeritasAd service",
}

export default function DisclaimerPage() {
  const lastUpdated = "March 31, 2026"

  return (
    <SiteShell>
      <div className="container mx-auto max-w-3xl px-4 py-12">
        <div className="mb-10">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-amber-500/10 p-2">
              <AlertTriangle className="h-6 w-6 text-amber-500" />
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight">Disclaimer</h1>
          </div>
          <p className="mt-2 text-muted-foreground">Last updated: {lastUpdated}</p>
        </div>

        <div className="space-y-6">
          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Info className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">1. General Information</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  The information provided by VeritasAd (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) on this website and through our service is for general informational and educational purposes only. All information on our platform is provided in good faith, however we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">2. Accuracy of Information</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  While we strive to keep the information accurate and up-to-date, we make no warranties, express or implied, about the completeness, accuracy, reliability, suitability, or availability of the information, products, services, or related graphics contained on the website. Any reliance you place on such information is strictly at your own risk.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <AlertTriangle className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">3. Analysis Results Disclaimer</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  VeritasAd uses artificial intelligence and machine learning algorithms to analyze video content and social media posts for potential advertising indicators. The results provided are:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Not legal advice</strong> - Our analysis does not constitute legal, financial, or regulatory advice</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Not guaranteed</strong> - We do not guarantee 100% accuracy in detecting advertising, brand mentions, or disclosure compliance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Subject to limitations</strong> - AI models may miss subtle, novel, or context-dependent advertising techniques</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Context-dependent</strong> - Results may vary based on video quality, platform, content type, and language</span>
                  </li>
                </ul>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">
                  Users should independently verify analysis results before making any legal, financial, or business decisions based on them.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <AlertTriangle className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">4. Limitation of Liability</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  In no event shall VeritasAd be liable for any loss or damage, including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of or in connection with the use of this service. This includes but is not limited to decisions made based on analysis results, compliance actions taken, or business impacts resulting from the use of our platform.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <ExternalLink className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">5. External Links</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Our service may contain links to external websites that are not provided or maintained by us. We do not guarantee the accuracy, relevance, timeliness, or completeness of any information on these external sites. The inclusion of any links does not necessarily imply a recommendation or endorse the views expressed within them.
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
                <h2 className="text-xl font-semibold">6. User Responsibility</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Users of VeritasAd are responsible for:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Verifying analysis results through additional means when required
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Complying with applicable laws and regulations in their jurisdiction
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Obtaining appropriate legal or professional advice when needed
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Using the service in accordance with our Terms of Service
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    Ensuring they have the right to upload and analyze submitted content
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Mail className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">7. Contact Us</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  If you have any questions about this Disclaimer, please contact us at{" "}
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
