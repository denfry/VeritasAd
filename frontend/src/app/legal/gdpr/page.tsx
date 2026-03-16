import { Metadata } from "next"
import Link from "next/link"
import { ShieldCheck, User, Mail, Download, Trash2, FileText } from "lucide-react"

export const metadata: Metadata = {
  title: "GDPR Rights | VeritasAd",
  description: "Your rights under GDPR and how to exercise them",
}

export default function GDPRPage() {
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
        <h1 className="text-4xl font-extrabold tracking-tight mb-4">Your GDPR Rights</h1>
        <p className="text-muted-foreground mb-8">
          Under the General Data Protection Regulation (GDPR), you have specific rights regarding your personal data.
        </p>

        <div className="space-y-6">
          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-2">Right to Access</h2>
                <p className="text-muted-foreground">
                  You have the right to obtain confirmation as to whether or not personal data concerning you is being processed, 
                  and where that is the case, access to the personal data and specific purposes of processing.
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-2">Right to Rectification</h2>
                <p className="text-muted-foreground">
                  You have the right to have inaccurate personal data rectified. You may also have incomplete personal data completed.
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Trash2 className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-2">Right to Erasure</h2>
                <p className="text-muted-foreground">
                  Also known as &quot;right to be forgotten,&quot; you may request the deletion of your personal data when 
                  it is no longer necessary for the purposes for which it was collected.
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <Download className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-2">Right to Data Portability</h2>
                <p className="text-muted-foreground">
                  You have the right to receive your personal data in a structured, commonly used, and machine-readable format 
                  and to transmit that data to another controller.
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-3">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-2">Right to Object</h2>
                <p className="text-muted-foreground">
                  You have the right to object to processing of your personal data for direct marketing purposes, 
                  or when processing is based on legitimate interests.
                </p>
              </div>
            </div>
          </div>
        </div>

        <section className="mt-12">
          <h2 className="text-2xl font-bold mb-6">How to Exercise Your Rights</h2>
          <p className="text-muted-foreground mb-4">
            To exercise any of these rights, please contact us using one of the methods below:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
            <li>Email: <a href="mailto:gdpr@veritasad.ai" className="text-primary hover:underline">gdpr@veritasad.ai</a></li>
            <li>Through your account settings</li>
            <li>Via our Telegram bot</li>
          </ul>
          <p className="text-muted-foreground mt-6">
            We will respond to your request within 30 days. For data export requests, we will provide your data in a common format (JSON or CSV).
          </p>
        </section>

        <section className="mt-12 p-6 bg-muted/30 rounded-xl">
          <h3 className="font-semibold mb-2">Data Protection Officer</h3>
          <p className="text-sm text-muted-foreground">
            For questions about this policy or our data practices, please contact our Data Protection Officer at{" "}
            <a href="mailto:dpo@veritasad.ai" className="text-primary hover:underline">dpo@veritasad.ai</a>
          </p>
        </section>
      </main>
    </div>
  )
}
