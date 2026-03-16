import { Metadata } from "next"
import Link from "next/link"
import { ShieldCheck, AlertTriangle } from "lucide-react"

export const metadata: Metadata = {
  title: "Disclaimer | VeritasAd",
  description: "Disclaimer and limitations of liability for VeritasAd service",
}

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <span>VeritasAd</span>
          </Link>
        </div>
      </header>

      <main className="container mx-auto max-w-3xl px-4 py-12">
        <div className="flex items-center gap-3 mb-8">
          <div className="rounded-full bg-amber-500/10 p-2">
            <AlertTriangle className="h-6 w-6 text-amber-500" />
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">Disclaimer</h1>
        </div>

        <div className="prose prose-gray dark:prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. General Information</h2>
            <p className="text-muted-foreground">
              The information provided by VeritasAd (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) on this website and through 
              our service is for general informational and educational purposes only. All information on our 
              platform is provided in good faith, however we make no representation or warranty of any kind, 
              express or implied.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Accuracy of Information</h2>
            <p className="text-muted-foreground">
              While we strive to keep the information accurate and up-to-date, we make no warranties, 
              express or implied, about the completeness, accuracy, reliability, suitability, or availability 
              of the information, products, services, or related graphics contained on the website. Any 
              reliance you place on such information is strictly at your own risk.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Analysis Results Disclaimer</h2>
            <p className="text-muted-foreground">
              VeritasAd uses artificial intelligence and machine learning algorithms to analyze video 
              content for potential advertising indicators. The results provided are:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li><strong>Not legal advice</strong> - Our analysis does not constitute legal, financial, or regulatory advice</li>
              <li><strong>Not guaranteed</strong> - We do not guarantee 100% accuracy in detecting advertising</li>
              <li><strong>Subject to limitations</strong> - AI models may miss subtle or novel advertising techniques</li>
              <li><strong>Context-dependent</strong> - Results may vary based on video quality, platform, and content type</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Limitation of Liability</h2>
            <p className="text-muted-foreground">
              In no event shall VeritasAd be liable for any loss or damage, including without limitation, 
              indirect or consequential loss or damage, or any loss or damage whatsoever arising from 
              loss of data or profits arising out of or in connection with the use of this service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. External Links</h2>
            <p className="text-muted-foreground">
              Our service may contain links to external websites that are not provided or maintained by 
              us. We do not guarantee the accuracy, relevance, timeliness, or completeness of any 
              information on these external sites.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. User Responsibility</h2>
            <p className="text-muted-foreground">
              Users of VeritasAd are responsible for:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li>Verifying analysis results through additional means when required</li>
              <li>Complying with applicable laws and regulations in their jurisdiction</li>
              <li>Obtaining appropriate legal or professional advice when needed</li>
              <li>Using the service in accordance with our Terms of Service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Changes to This Disclaimer</h2>
            <p className="text-muted-foreground">
              We may update this disclaimer from time to time. Any changes will be posted on this page 
              and will take effect immediately upon posting.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Contact Us</h2>
            <p className="text-muted-foreground">
              If you have any questions about this Disclaimer, please contact us at:{" "}
              <a href="mailto:legal@veritasad.ai" className="text-primary hover:underline">
                legal@veritasad.ai
              </a>
            </p>
          </section>
        </div>
      </main>
    </div>
  )
}
