"use client"

import { Check, Zap, TrendingUp, Building, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { createSubscription, purchaseCreditPackage } from "@/lib/api-client"
import { CurrencySelector } from "@/components/CurrencySelector"
import { useCurrency, Price, PricePerMonth, SavingsBadge } from "@/contexts/currency-context"

// ==================== SUBSCRIPTION PLANS (Base prices in RUB) ====================

const SUBSCRIPTION_PLANS_RUB = {
  free: {
    name: "Free",
    priceRub: 0,
    description: "For testing and experimentation.",
    features: [
      "30 analyses / month",
      "Basic reporting",
      "Community support",
      "Standard processing speed",
    ],
    cta: "Start free",
    popular: false,
    icon: <Zap className="h-5 w-5" />,
  },
  starter: {
    name: "Starter",
    priceRub: 2900,
    description: "For freelancers and light usage.",
    features: [
      "300 analyses / month",
      "PDF reports",
      "Email support",
      "Priority processing",
      "API access",
    ],
    cta: "Start Starter",
    popular: false,
    icon: <Users className="h-5 w-5" />,
  },
  pro: {
    name: "Pro",
    priceRub: 7900,
    originalPriceRub: 15000,
    description: "For small business and marketing teams.",
    features: [
      "1 500 analyses / month",
      "Advanced PDF reports",
      "Priority support",
      "Fast processing",
      "API access",
      "Brand detection",
    ],
    cta: "Upgrade to Pro",
    popular: true,
    icon: <TrendingUp className="h-5 w-5" />,
  },
  business: {
    name: "Business",
    priceRub: 19900,
    description: "For agencies and growing companies.",
    features: [
      "5 000 analyses / month",
      "White-label reports",
      "Dedicated support",
      "Fastest processing",
      "Full API access",
      "Custom integrations",
      "Team management",
    ],
    cta: "Go Business",
    popular: false,
    icon: <Building className="h-5 w-5" />,
  },
  enterprise: {
    name: "Enterprise",
    priceRub: 49900,
    description: "For corporations and custom deployments.",
    features: [
      "20 000 analyses / month",
      "Custom reporting",
      "24/7 dedicated support",
      "SLA guarantee",
      "On-premise option",
      "Custom models",
      "Training & onboarding",
    ],
    cta: "Contact Sales",
    popular: false,
    icon: <Zap className="h-5 w-5" />,
  },
}

// ==================== PAY-AS-YOU-GO PACKAGES (Base prices in RUB) ====================

const CREDIT_PACKAGES_RUB = [
  {
    name: "Micro",
    credits: 100,
    priceRub: 1500,
    validity: 30,
    description: "For occasional analysis needs.",
    highlight: false,
  },
  {
    name: "Standard",
    credits: 500,
    priceRub: 5000,
    validity: 60,
    description: "Best value for regular usage.",
    highlight: true,
    savings: "33%",
  },
  {
    name: "Pro",
    credits: 1500,
    priceRub: 12000,
    validity: 90,
    description: "For high-volume analysis.",
    highlight: false,
    savings: "47%",
  },
  {
    name: "Business",
    credits: 8000,
    priceRub: 40000,
    validity: 180,
    description: "Maximum savings for teams.",
    highlight: false,
    savings: "67%",
  },
]

export default function PricingPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null)
  
  // Currency context - globally available
  const {
    selectedCurrency,
    setSelectedCurrency,
    formatPrice,
  } = useCurrency()

  async function handleSubscriptionUpgrade(plan: string) {
    if (!user) {
      toast.error("Please sign in first")
      router.push("/auth/login")
      return
    }
    try {
      const payment = await createSubscription({
        plan: plan as "starter" | "pro" | "business" | "enterprise",
        returnUrl: `${window.location.origin}/payment/success`,
      })
      window.location.href = payment.checkout_url
    } catch (error) {
      toast.error("Unable to create payment. Please try again.")
    }
  }

  async function handleCreditPackagePurchase(packageType: string) {
    if (!user) {
      toast.error("Please sign in first")
      router.push("/auth/login")
      return
    }
    setSelectedPackage(packageType)
    try {
      const payment = await purchaseCreditPackage({
        package: packageType as "micro" | "standard" | "pro" | "business",
        returnUrl: `${window.location.origin}/payment/success`,
      })
      window.location.href = payment.checkout_url
    } catch (error) {
      toast.error("Unable to create payment. Please try again.")
      setSelectedPackage(null)
    }
  }

  return (
    <SiteShell>
      {/* Header with Currency Selector */}
      <section className="container mx-auto max-w-6xl px-4 section space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="text-center md:text-left">
            <p className="text-sm text-muted-foreground">Pricing</p>
            <h1 className="text-4xl font-semibold">Flexible plans for every need</h1>
            <p className="text-muted-foreground max-w-2xl mt-2">
              Choose a subscription plan or buy credits as you go. Both options give you access to
              the same powerful AI detection features.
            </p>
          </div>
          <div className="flex items-center justify-center md:justify-end gap-3">
            <span className="text-sm text-muted-foreground">Currency:</span>
            <CurrencySelector
              selectedCurrency={selectedCurrency}
              onCurrencyChange={setSelectedCurrency}
            />
          </div>
        </div>
      </section>

      {/* Subscription Plans */}
      <section className="container mx-auto max-w-6xl px-4 section">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold mb-2">Subscription Plans</h2>
          <p className="text-muted-foreground">
            Monthly subscription with daily analysis limits. Cancel anytime.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {Object.values(SUBSCRIPTION_PLANS_RUB).map((plan) => {
            return (
              <div
                key={plan.name}
                className={`card p-5 flex flex-col relative ${
                  plan.popular ? "ring-2 ring-primary border-primary/20" : ""
                }`}
              >
                {plan.popular && (
                  <span className="badge badge-primary absolute -top-3 left-1/2 -translate-x-1/2">
                    Most popular
                  </span>
                )}
                
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-primary">{plan.icon}</span>
                    <h3 className="text-lg font-semibold">{plan.name}</h3>
                  </div>
                  <div className="flex items-baseline gap-2 flex-wrap">
                    <PricePerMonth amount={plan.priceRub} className="text-3xl font-semibold" />
                    {'originalPriceRub' in plan && plan.originalPriceRub && (
                      <Price amount={plan.originalPriceRub} className="text-sm text-muted-foreground line-through" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{plan.description}</p>
                </div>

                <ul className="space-y-2 text-sm text-muted-foreground flex-1">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleSubscriptionUpgrade(plan.name.toLowerCase())}
                  className={`btn mt-6 w-full ${
                    plan.popular ? "btn-primary" : "btn-outline"
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            )
          })}
        </div>
      </section>

      {/* Pay-as-you-go Section */}
      <section className="container mx-auto max-w-6xl px-4 section bg-muted/30 rounded-2xl p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold mb-2">Pay-as-you-go Credits</h2>
          <p className="text-muted-foreground">
            Buy credits once, use them anytime. No subscription required. Credits expire after the validity period.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {CREDIT_PACKAGES_RUB.map((pkg) => {
            const pricePerAnalysis = formatPrice(pkg.priceRub / pkg.credits)
            
            return (
              <div
                key={pkg.name}
                className={`card p-6 flex flex-col relative ${
                  pkg.highlight ? "ring-2 ring-primary border-primary/20 bg-primary/5" : ""
                }`}
              >
                {pkg.highlight && (
                  <SavingsBadge originalPrice={pkg.priceRub * (1 / 0.67)} salePrice={pkg.priceRub} className="absolute -top-3 right-3" />
                )}

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-semibold">{pkg.name}</h3>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <Price amount={pkg.priceRub} className="text-4xl font-semibold" />
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {pricePerAnalysis} / analysis
                  </p>
                  <p className="text-sm text-muted-foreground mt-3">{pkg.description}</p>
                </div>

                <div className="space-y-2 text-sm flex-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Credits:</span>
                    <span className="font-medium">{pkg.credits}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Validity:</span>
                    <span className="font-medium">{pkg.validity} days</span>
                  </div>
                </div>

                <button
                  onClick={() => handleCreditPackagePurchase(pkg.name.toLowerCase())}
                  disabled={selectedPackage === pkg.name.toLowerCase()}
                  className={`btn mt-6 w-full ${
                    pkg.highlight ? "btn-primary" : "btn-outline"
                  }`}
                >
                  {selectedPackage === pkg.name.toLowerCase() ? "Processing..." : `Buy ${pkg.credits} credits`}
                </button>
              </div>
            )
          })}
        </div>
      </section>

      {/* Comparison Table */}
      <section className="container mx-auto max-w-6xl px-4 section">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold mb-2">Compare plans</h2>
          <p className="text-muted-foreground">
            See which plan is right for you
          </p>
        </div>

        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-4 font-medium">Feature</th>
                  <th className="text-center p-4 font-medium">Free</th>
                  <th className="text-center p-4 font-medium">Starter</th>
                  <th className="text-center p-4 font-medium bg-primary/5">Pro</th>
                  <th className="text-center p-4 font-medium">Business</th>
                  <th className="text-center p-4 font-medium">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-4 text-muted-foreground">Analyses / month</td>
                  <td className="text-center p-4">30</td>
                  <td className="text-center p-4">300</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">1 500</td>
                  <td className="text-center p-4">5 000</td>
                  <td className="text-center p-4">20 000</td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 text-muted-foreground">PDF reports</td>
                  <td className="text-center p-4">—</td>
                  <td className="text-center p-4">✓</td>
                  <td className="text-center p-4 bg-primary/5">✓</td>
                  <td className="text-center p-4">✓</td>
                  <td className="text-center p-4">✓</td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 text-muted-foreground">API access</td>
                  <td className="text-center p-4">—</td>
                  <td className="text-center p-4">✓</td>
                  <td className="text-center p-4 bg-primary/5">✓</td>
                  <td className="text-center p-4">✓</td>
                  <td className="text-center p-4">✓</td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 text-muted-foreground">Support</td>
                  <td className="text-center p-4">Community</td>
                  <td className="text-center p-4">Email</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">Priority</td>
                  <td className="text-center p-4">Dedicated</td>
                  <td className="text-center p-4">24/7</td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 text-muted-foreground">Processing speed</td>
                  <td className="text-center p-4">Standard</td>
                  <td className="text-center p-4">Priority</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">Fast</td>
                  <td className="text-center p-4">Fastest</td>
                  <td className="text-center p-4">Custom</td>
                </tr>
                <tr>
                  <td className="p-4 text-muted-foreground">Price</td>
                  <td className="text-center p-4 font-semibold"><Price amount={0} /></td>
                  <td className="text-center p-4 font-semibold"><Price amount={2900} /></td>
                  <td className="text-center p-4 font-semibold bg-primary/5"><Price amount={7900} /></td>
                  <td className="text-center p-4 font-semibold"><Price amount={19900} /></td>
                  <td className="text-center p-4 font-semibold"><Price amount={49900} /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="container mx-auto max-w-4xl px-4 section">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold mb-2">Frequently asked questions</h2>
        </div>

        <div className="space-y-4">
          <FAQItem
            question="What happens if I exceed my daily limit?"
            answer="You can purchase pay-as-you-go credits to continue analyzing videos. Credits are automatically used when you exceed your subscription limit."
          />
          <FAQItem
            question="Do credits expire?"
            answer="Yes, credits have a validity period based on the package: Micro (30 days), Standard (60 days), Pro (90 days), Business (180 days). Unused credits expire after this period."
          />
          <FAQItem
            question="Can I switch between plans?"
            answer="Yes, you can upgrade or downgrade your subscription at any time. Changes take effect immediately for upgrades and at the next billing cycle for downgrades."
          />
          <FAQItem
            question="What payment methods do you accept?"
            answer="We accept all major Russian bank cards through YooKassa, as well as SBP (Система быстрых платежей)."
          />
          <FAQItem
            question="Is there a refund policy?"
            answer="Yes, we offer a 14-day money-back guarantee for subscription plans. If you're not satisfied, contact support within 14 days for a full refund."
          />
          <FAQItem
            question="Why are prices shown in my local currency?"
            answer="We automatically convert prices from RUB to your selected currency using real-time exchange rates. Your actual charge will be in RUB at the current rate."
          />
        </div>
      </section>
    </SiteShell>
  )
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="card p-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left"
      >
        <span className="font-medium">{question}</span>
        <span className="text-muted-foreground">{isOpen ? "−" : "+"}</span>
      </button>
      {isOpen && (
        <p className="mt-3 text-sm text-muted-foreground">{answer}</p>
      )}
    </div>
  )
}
