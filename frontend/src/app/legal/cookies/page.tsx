import { Metadata } from "next"
import Link from "next/link"
import { ShieldCheck } from "lucide-react"

export const metadata: Metadata = {
  title: "Cookie Policy | VeritasAd",
  description: "Cookie Policy for VeritasAd - Information about cookies used on our platform",
}

export default function CookiesPage() {
  const lastUpdated = "March 17, 2026"

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
        <h1 className="text-4xl font-extrabold tracking-tight mb-4">Cookie Policy</h1>
        <p className="text-muted-foreground mb-8">Last updated: {lastUpdated}</p>

        <div className="prose prose-gray dark:prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. What Are Cookies</h2>
            <p className="text-muted-foreground">
              Cookies are small text files stored on your device when you visit websites. They help 
              remember your preferences and improve your browsing experience.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Types of Cookies We Use</h2>
            
            <h3 className="text-xl font-semibold mb-2 mt-6">Essential Cookies</h3>
            <p className="text-muted-foreground">
              Required for the website to function. They enable basic features like page navigation 
              and access to secure areas. The website cannot function without these cookies.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-6">Analytics Cookies</h3>
            <p className="text-muted-foreground">
              Help us understand how visitors interact with our website by collecting and reporting 
              information anonymously. This helps us improve our service.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-6">Marketing Cookies</h3>
            <p className="text-muted-foreground">
              Used to track visitors across websites. The intention is to display ads that are 
              relevant and engaging for the individual user.
            </p>

            <h3 className="text-xl font-semibold mb-2 mt-6">Functional Cookies</h3>
            <p className="text-muted-foreground">
              Enable enhanced functionality and personalization, such as remembering your preferences 
              and settings.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Managing Your Cookie Preferences</h2>
            <p className="text-muted-foreground">
              When you first visit our website, you will see a cookie consent banner allowing you to:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2 text-muted-foreground">
              <li><strong>Accept All</strong> - Enable all cookie categories</li>
              <li><strong>Reject All</strong> - Enable only essential cookies</li>
              <li><strong>Customize</strong> - Choose which categories you want to enable</li>
            </ul>
            <p className="text-muted-foreground mt-4">
              You can change your preferences at any time by clicking the Cookie Settings button 
              in the bottom corner of the screen.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Third-Party Cookies</h2>
            <p className="text-muted-foreground">
              Some cookies are placed by third-party services that appear on our pages. We do not 
              control these cookies. You can manage these through your browser settings or by 
              visiting the third-party websites directly.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Cookie List</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 pr-4 font-semibold">Name</th>
                    <th className="text-left py-3 pr-4 font-semibold">Type</th>
                    <th className="text-left py-3 font-semibold">Purpose</th>
                  </tr>
                </thead>
                <tbody className="text-muted-foreground">
                  <tr className="border-b">
                    <td className="py-3 pr-4">session_id</td>
                    <td className="py-3 pr-4">Essential</td>
                    <td className="py-3">User session management</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">auth_token</td>
                    <td className="py-3 pr-4">Essential</td>
                    <td className="py-3">Authentication</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">preferences</td>
                    <td className="py-3 pr-4">Functional</td>
                    <td className="py-3">User preferences</td>
                  </tr>
                  <tr>
                    <td className="py-3 pr-4">analytics_id</td>
                    <td className="py-3 pr-4">Analytics</td>
                    <td className="py-3">Usage analytics</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Contact Us</h2>
            <p className="text-muted-foreground">
              If you have questions about our Cookie Policy, please contact us at:{" "}
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
