import { Metadata } from "next"
import Link from "next/link"
import { ArrowLeft, Cookie, Settings, Globe, Table, Mail } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export const metadata: Metadata = {
  title: "Cookie Policy | VeritasAd",
  description: "Cookie Policy for VeritasAd - Information about cookies used on our platform",
}

export default function CookiesPage() {
  const lastUpdated = "March 31, 2026"

  return (
    <SiteShell>
      <div className="container mx-auto max-w-3xl px-4 py-12">
        <div className="mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight">Cookie Policy</h1>
          <p className="mt-2 text-muted-foreground">Last updated: {lastUpdated}</p>
        </div>

        <div className="space-y-6">
          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Cookie className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">1. What Are Cookies</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Cookies are small text files stored on your device when you visit websites. They help remember your preferences, maintain your session, and improve your browsing experience. VeritasAd uses cookies to ensure our advertising detection platform functions properly and to understand how you interact with our service.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Settings className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">2. Types of Cookies We Use</h2>
                
                <h3 className="mt-4 text-base font-semibold">Essential Cookies</h3>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Required for the website to function. They enable basic features like page navigation, authentication, and access to secure areas of the platform. The website cannot function properly without these cookies.
                </p>

                <h3 className="mt-6 text-base font-semibold">Analytics Cookies</h3>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Help us understand how visitors interact with our platform by collecting and reporting information anonymously. This data helps us improve our service, optimize analysis workflows, and enhance user experience.
                </p>

                <h3 className="mt-6 text-base font-semibold">Marketing Cookies</h3>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Used to track visitors across websites. The intention is to display ads that are relevant and engaging for the individual user, thereby more valuable for publishers and third-party advertisers.
                </p>

                <h3 className="mt-6 text-base font-semibold">Functional Cookies</h3>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Enable enhanced functionality and personalization, such as remembering your preferences, language settings, and dashboard configurations.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Settings className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">3. Managing Your Cookie Preferences</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  When you first visit our website, you will see a cookie consent banner allowing you to:
                </p>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Accept All</strong> - Enable all cookie categories</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Reject All</strong> - Enable only essential cookies</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    <span><strong>Customize</strong> - Choose which categories you want to enable</span>
                  </li>
                </ul>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">
                  You can change your preferences at any time by clicking the Cookie Settings button in the bottom corner of the screen or through your account settings.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Globe className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">4. Third-Party Cookies</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Some cookies are placed by third-party services that appear on our pages. We do not control these cookies. You can manage these through your browser settings or by visiting the third-party websites directly. Third-party services may include analytics providers, payment processors, and social media integrations.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Table className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">5. Cookie List</h2>
                <div className="mt-4 overflow-x-auto rounded-xl border border-border/60">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border/60 bg-muted/30">
                        <th className="px-4 py-3 text-left font-semibold">Name</th>
                        <th className="px-4 py-3 text-left font-semibold">Type</th>
                        <th className="px-4 py-3 text-left font-semibold">Purpose</th>
                      </tr>
                    </thead>
                    <tbody className="text-muted-foreground">
                      <tr className="border-b border-border/40">
                        <td className="px-4 py-3 font-mono text-xs">session_id</td>
                        <td className="px-4 py-3">Essential</td>
                        <td className="px-4 py-3">User session management</td>
                      </tr>
                      <tr className="border-b border-border/40">
                        <td className="px-4 py-3 font-mono text-xs">auth_token</td>
                        <td className="px-4 py-3">Essential</td>
                        <td className="px-4 py-3">Authentication and authorization</td>
                      </tr>
                      <tr className="border-b border-border/40">
                        <td className="px-4 py-3 font-mono text-xs">preferences</td>
                        <td className="px-4 py-3">Functional</td>
                        <td className="px-4 py-3">User preferences and settings</td>
                      </tr>
                      <tr className="border-b border-border/40">
                        <td className="px-4 py-3 font-mono text-xs">analytics_id</td>
                        <td className="px-4 py-3">Analytics</td>
                        <td className="px-4 py-3">Usage analytics and reporting</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-mono text-xs">marketing_track</td>
                        <td className="px-4 py-3">Marketing</td>
                        <td className="px-4 py-3">Ad campaign tracking</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Mail className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">6. Contact Us</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  If you have questions about our Cookie Policy, please contact us at{" "}
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
