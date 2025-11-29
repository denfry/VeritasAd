import Link from "next/link"
import { ArrowRight, Shield, Zap, BarChart3 } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/10 via-background to-secondary/10 py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
              AI-Powered
              <br />
              <span className="bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent">
                Advertising Detection
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Detect hidden advertising in videos using neural networks.
              Analyze content for brand mentions, logos, and disclosure markers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/analyze"
                className="inline-flex items-center justify-center px-8 py-4 bg-primary text-primary-foreground rounded-lg font-semibold hover:opacity-90 transition-opacity"
              >
                Start Analysis
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="/docs"
                className="inline-flex items-center justify-center px-8 py-4 border border-border rounded-lg font-semibold hover:bg-accent transition-colors"
              >
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Powerful Features
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Shield className="h-8 w-8" />}
              title="Accurate Detection"
              description="Multi-modal analysis combining visual, audio, and text signals for precise advertising detection."
            />
            <FeatureCard
              icon={<Zap className="h-8 w-8" />}
              title="Real-time Progress"
              description="Track analysis progress in real-time with Server-Sent Events. Know exactly what's happening."
            />
            <FeatureCard
              icon={<BarChart3 className="h-8 w-8" />}
              title="Detailed Reports"
              description="Get comprehensive PDF reports with timestamps, brand mentions, and confidence scores."
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-4">
        <div className="container mx-auto max-w-6xl text-center text-muted-foreground">
          <p>© 2025 VeritasAd. Built with Next.js 15 and FastAPI.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="p-6 border border-border rounded-lg hover:shadow-lg transition-shadow">
      <div className="text-primary mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  )
}
