"use client"

import { Check, Zap, TrendingUp, Building, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"
import { AppShell } from "@/components/AppShell"
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
    <AppShell>
      {/* Header with Currency Selector */}
      <section className="container mx-auto max-w-6xl px-4 py-12 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="text-center md:text-left">
            <p className="text-xs font-black uppercase tracking-widest text-primary">Deployment Tiers</p>
            <h1 className="text-4xl font-extrabold tracking-tight mt-1">Flexible Node Clustering</h1>
            <p className="text-muted-foreground max-w-2xl mt-2 font-medium">
              Choose a dedicated subscription node or utilize pay-as-you-go compute units.
            </p>
          </div>
          <div className="flex items-center justify-center md:justify-end gap-3 p-2 bg-muted rounded-2xl border border-border/50">
            <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-2">Vector:</span>
            <CurrencySelector
              selectedCurrency={selectedCurrency}
              onCurrencyChange={setSelectedCurrency}
            />
          </div>
        </div>
      </section>

      {/* Subscription Plans */}
      <section className="container mx-auto max-w-6xl px-4 py-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl font-black tracking-tight mb-2">Subscription Clusters</h2>
          <p className="text-muted-foreground font-medium">
            Monthly synchronization with automated daily analysis quotas.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {Object.values(SUBSCRIPTION_PLANS_RUB).map((plan) => {
            return (
              <div
                key={plan.name}
                className={`card p-6 flex flex-col relative transition-all hover:scale-[1.02] shadow-xl shadow-black/5 ${
                  plan.popular ? "ring-2 ring-primary border-primary/20 bg-primary/[0.02]" : "border-border/50"
                }`}
              >
                {plan.popular && (
                  <span className="bg-primary text-primary-foreground text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full absolute -top-3 left-1/2 -translate-x-1/2 shadow-lg">
                    Highest Vector
                  </span>
                )}
                
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                       {plan.icon}
                    </div>
                    <h3 className="text-lg font-bold">{plan.name}</h3>
                  </div>
                  <div className="flex items-baseline gap-2 flex-wrap">
                    <PricePerMonth amount={plan.priceRub} className="text-3xl font-black" />
                    {'originalPriceRub' in plan && plan.originalPriceRub && (
                      <Price amount={plan.originalPriceRub} className="text-sm text-muted-foreground line-through opacity-50" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-3 font-medium leading-relaxed">{plan.description}</p>
                </div>

                <ul className="space-y-3 text-sm text-muted-foreground flex-1 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                      <span className="text-xs font-bold">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleSubscriptionUpgrade(plan.name.toLowerCase())}
                  className={`btn w-full py-4 rounded-xl font-black uppercase tracking-widest text-[10px] transition-all shadow-lg ${
                    plan.popular ? "btn-primary shadow-primary/20" : "btn-outline hover:bg-muted"
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
      <section className="container mx-auto max-w-6xl px-4 py-12 mb-12">
        <div className="card p-10 bg-muted/30 border-dashed border-2 border-border/50 rounded-[2rem]">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-black tracking-tight mb-2">On-Demand Units</h2>
            <p className="text-muted-foreground font-medium">
              Burst compute capacity. No recurring authorization required.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {CREDIT_PACKAGES_RUB.map((pkg) => {
              const pricePerAnalysis = formatPrice(pkg.priceRub / pkg.credits)
              
              return (
                <div
                  key={pkg.name}
                  className={`card p-8 flex flex-col relative transition-all hover:translate-y-[-4px] bg-background shadow-2xl shadow-black/5 ${
                    pkg.highlight ? "border-primary/30 ring-1 ring-primary/10" : "border-border/50"
                  }`}
                >
                  {pkg.highlight && (
                    <SavingsBadge originalPrice={pkg.priceRub * (1 / 0.67)} salePrice={pkg.priceRub} className="absolute -top-3 right-6" />
                  )}

                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-black">{pkg.name}</h3>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <Price amount={pkg.priceRub} className="text-4xl font-black" />
                    </div>
                    <p className="text-[10px] font-black uppercase tracking-widest text-primary mt-2">
                      {pricePerAnalysis} / UNIT
                    </p>
                    <p className="text-xs text-muted-foreground mt-4 font-medium">{pkg.description}</p>
                  </div>

                  <div className="space-y-3 text-[10px] font-black uppercase tracking-widest flex-1 border-t border-border/50 pt-6 mb-8">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Compute Units:</span>
                      <span className="text-sm font-black">{pkg.credits}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">SLA Window:</span>
                      <span className="text-sm font-black">{pkg.validity} Days</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleCreditPackagePurchase(pkg.name.toLowerCase())}
                    disabled={selectedPackage === pkg.name.toLowerCase()}
                    className={`btn w-full py-4 rounded-xl font-black uppercase tracking-widest text-[10px] transition-all ${
                      pkg.highlight ? "btn-primary shadow-lg shadow-primary/20" : "btn-outline"
                    }`}
                  >
                    {selectedPackage === pkg.name.toLowerCase() ? "Processing..." : `Initialize ${pkg.credits} Units`}
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      </section>
    </AppShell>
  )
}
