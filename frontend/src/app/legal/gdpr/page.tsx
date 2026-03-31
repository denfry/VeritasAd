import { Metadata } from "next"
import Link from "next/link"
import { ArrowLeft, User, FileText, Trash2, Download, Ban, Scale } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export const metadata: Metadata = {
  title: "GDPR Rights | VeritasAd",
  description: "Your rights under GDPR and how to exercise them with VeritasAd",
}

export default function GDPRPage() {
  const lastUpdated = "March 31, 2026"

  return (
    <SiteShell>
      <div className="container mx-auto max-w-3xl px-4 py-12">
        <div className="mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight">Your GDPR Rights</h1>
          <p className="mt-2 text-muted-foreground">Last updated: {lastUpdated}</p>
          <p className="mt-4 text-sm leading-7 text-muted-foreground">
            Under the General Data Protection Regulation (GDPR), you have specific rights regarding your personal data. VeritasAd is committed to respecting and facilitating these rights for all users within the European Economic Area and beyond.
          </p>
        </div>

        <div className="space-y-4">
          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <User className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Right to Access</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  You have the right to obtain confirmation as to whether or not personal data concerning you is being processed, and where that is the case, access to the personal data and specific purposes of processing. This includes information about what data we hold about you, how it is used, and who it is shared with.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Right to Rectification</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  You have the right to have inaccurate personal data rectified. You may also have incomplete personal data completed by providing a supplementary statement. This applies to all personal data we hold, including account information and analysis metadata.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Trash2 className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Right to Erasure</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Also known as the &quot;right to be forgotten,&quot; you may request the deletion of your personal data when it is no longer necessary for the purposes for which it was collected, when you withdraw consent, or when the data has been unlawfully processed.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Download className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Right to Data Portability</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  You have the right to receive your personal data in a structured, commonly used, and machine-readable format and to transmit that data to another controller. For VeritasAd, this includes your analysis history, reports, and account data in JSON or CSV format.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Ban className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Right to Object</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  You have the right to object to processing of your personal data for direct marketing purposes, or when processing is based on legitimate interests. You may also object to automated decision-making, including profiling.
                </p>
              </div>
            </div>
          </div>

          <div className="surface rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Scale className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Right to Restrict Processing</h2>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  You have the right to request that we restrict the processing of your personal data under certain circumstances, such as when you contest the accuracy of the data or when the processing is unlawful but you oppose erasure.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 space-y-6">
          <div className="surface rounded-2xl p-6">
            <h2 className="text-xl font-semibold">How to Exercise Your Rights</h2>
            <p className="mt-3 text-sm leading-7 text-muted-foreground">
              To exercise any of these rights, please contact us using one of the methods below:
            </p>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                Email:{" "}
                <a href="mailto:gdpr@veritasad.ai" className="text-primary hover:underline">
                  gdpr@veritasad.ai
                </a>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                Through your account settings (Data Export and Delete options)
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                Via our Telegram bot support channel
              </li>
            </ul>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              We will respond to your request within 30 days. For data export requests, we will provide your data in a common format (JSON or CSV). If your request is complex, we may extend this period by up to 60 days and will notify you accordingly.
            </p>
          </div>

          <div className="rounded-2xl border border-border/60 bg-muted/20 p-6">
            <h3 className="text-base font-semibold">Data Protection Officer</h3>
            <p className="mt-2 text-sm leading-7 text-muted-foreground">
              For questions about this policy or our data practices, please contact our Data Protection Officer at{" "}
              <a href="mailto:dpo@veritasad.ai" className="text-primary hover:underline">
                dpo@veritasad.ai
              </a>
            </p>
            <p className="mt-2 text-sm leading-7 text-muted-foreground">
              You also have the right to lodge a complaint with a supervisory authority in your jurisdiction if you believe your rights have been violated.
            </p>
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
