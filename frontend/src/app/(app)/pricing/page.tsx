"use client"

import { Check, Zap, TrendingUp, Building, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/contexts/auth-context"
import { createSubscription, purchaseCreditPackage } from "@/lib/api-client"
import { CurrencySelector } from "@/components/CurrencySelector"
import { useCurrency, Price, PricePerMonth, SavingsBadge } from "@/contexts/currency-context"
import { ThreeCardEffect } from "@/components/three/ThreeCardEffect"

import { motion } from "framer-motion"

// Base prices in RUB
const SUBSCRIPTION_PLANS = {
  free: {
    name: "Free",
    priceRub: 0,
    description: "For testing and getting started.",
    features: [
      "30 analyses / month",
      "Basic LLM tier",
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
      "Starter LLM tier",
      "PDF reports",
      "Email support",
      "Priority processing",
      "API access",
    ],
    cta: "Get Starter",
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
      "Pro LLM tier",
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
      "Business LLM tier",
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
      "Enterprise LLM tier",
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

const CREDIT_PACKAGES = [
  {
    name: "Micro",
    credits: 100,
    priceRub: 1500,
    validityDays: 30,
    description: "For occasional analysis needs.",
    highlight: false,
  },
  {
    name: "Standard",
    credits: 500,
    priceRub: 5000,
    validityDays: 60,
    description: "Best value for regular usage.",
    highlight: true,
    savingsPct: "33%",
  },
  {
    name: "Pro",
    credits: 1500,
    priceRub: 12000,
    validityDays: 90,
    description: "For high-volume analysis.",
    highlight: false,
    savingsPct: "47%",
  },
  {
    name: "Business",
    credits: 8000,
    priceRub: 40000,
    validityDays: 180,
    description: "Maximum savings for large teams.",
    highlight: false,
    savingsPct: "67%",
  },
]

export default function PricingPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null)

  const { selectedCurrency, setSelectedCurrency, formatPrice } = useCurrency()

  async function handleSubscriptionUpgrade(plan: string) {
    if (!user) {
      toast.error("Please sign in first")
      router.push("/auth/login")
      return
    }
    try {
      const payment = await createSubscription({
        plan: plan as "starter" | "pro" | "business" | "enterprise",
        returnUrl: `${typeof window !== "undefined" ? window.location.origin : ""}/payment/success`,
      })
      window.location.href = payment.checkout_url
    } catch {
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
        returnUrl: `${typeof window !== "undefined" ? window.location.origin : ""}/payment/success`,
      })
      window.location.href = payment.checkout_url
    } catch {
      toast.error("Unable to create payment. Please try again.")
      setSelectedPackage(null)
    }
  }

  return (
    <>
        {/* Header */}
        <section className="container mx-auto max-w-6xl px-4 pt-12 pb-8">
          <motion.div
            className="flex flex-col md:flex-row md:items-end md:justify-between gap-6"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div>
              <p className="eyebrow">Pricing</p>
              <h1 className="mt-2 text-4xl font-semibold tracking-tight">
                Simple, transparent pricing
              </h1>
              <p className="mt-2 text-muted-foreground max-w-lg text-sm leading-6">
                Choose a monthly subscription or buy credits on demand. No hidden fees.
              </p>
            </div>
            <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-2xl border border-border/50">
              <span className="eyebrow ml-2">Currency:</span>
              <CurrencySelector
                selectedCurrency={selectedCurrency}
                onCurrencyChange={setSelectedCurrency}
              />
            </div>
          </motion.div>
        </section>

        {/* Subscription Plans */}
        <section className="container mx-auto max-w-6xl px-4 py-6">
          <div className="mb-8 text-center">
            <h2 className="text-xl font-semibold tracking-tight">Monthly subscriptions</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Renews monthly. Cancel anytime.
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {Object.entries(SUBSCRIPTION_PLANS).map(([planKey, plan]) => {
              const isPaidPlan = planKey !== "free"
              return (
                <ThreeCardEffect
                  key={plan.name}
                  glowColor={plan.popular ? "hsl(var(--primary))" : "hsl(var(--muted))"}
                  intensity={10}
                >
                  <div
                    className={`surface p-5 flex flex-col relative h-full transition-all duration-200 ${
                      plan.popular
                        ? "ring-2 ring-primary/60 border-primary/30"
                        : "border-border/50"
                    }`}
                  >
                    {plan.popular && (
                      <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-[10px] font-semibold uppercase tracking-[0.2em] px-3 py-1 rounded-full shadow-md">
                        Most popular
                      </span>
                    )}

                    <div className="mb-5">
                      <div className="flex items-center gap-2.5 mb-3">
                        <div className="p-1.5 rounded-lg bg-primary/8 text-primary border border-primary/15">
                          {plan.icon}
                        </div>
                        <h3 className="font-semibold">{plan.name}</h3>
                      </div>
                      <div className="flex items-baseline gap-2 flex-wrap">
                        <PricePerMonth amount={plan.priceRub} className="text-2xl font-bold" />
                        {"originalPriceRub" in plan && plan.originalPriceRub && (
                          <Price
                            amount={plan.originalPriceRub}
                            className="text-sm text-muted-foreground line-through opacity-50"
                          />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-2 leading-5">{plan.description}</p>
                    </div>

                    <ul className="space-y-2.5 text-sm flex-1 mb-6">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Check className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                          <span className="text-xs text-muted-foreground">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    <button
                      onClick={() => {
                        if (!isPaidPlan) {
                          router.push(user ? "/dashboard" : "/auth/register")
                          return
                        }
                        handleSubscriptionUpgrade(planKey)
                      }}
                      className={`btn w-full py-2.5 rounded-full text-xs font-semibold uppercase tracking-[0.18em] transition-all ${
                        plan.popular ? "btn-primary shadow-primary" : "btn-outline"
                      }`}
                    >
                      {plan.cta}
                    </button>
                  </div>
                </ThreeCardEffect>
              )
            })}
          </div>
        </section>

        {/* Pay-as-you-go */}
        <section className="container mx-auto max-w-6xl px-4 py-10 pb-16">
          <div className="rounded-[2rem] border border-border/50 bg-muted/20 p-8 md:p-10">
            <div className="mb-8 text-center">
              <h2 className="text-xl font-semibold tracking-tight">Pay as you go</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Buy credits once and use them whenever. No subscription required.
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              {CREDIT_PACKAGES.map((pkg) => {
                const pricePerAnalysis = formatPrice(pkg.priceRub / pkg.credits)
                const pkgKey = pkg.name.toLowerCase()

                return (
                  <ThreeCardEffect
                    key={pkg.name}
                    glowColor={pkg.highlight ? "hsl(var(--primary))" : "hsl(var(--muted))"}
                    intensity={8}
                  >
                    <div
                      className={`surface p-6 flex flex-col relative h-full bg-background transition-all duration-200 ${
                        pkg.highlight ? "border-primary/30 ring-1 ring-primary/10" : "border-border/50"
                      }`}
                    >
                      {pkg.highlight && (
                        <SavingsBadge
                          originalPrice={pkg.priceRub / (1 - (parseFloat(pkg.savingsPct ?? "0") / 100))}
                          salePrice={pkg.priceRub}
                          className="absolute -top-3 right-5"
                        />
                      )}

                      <div className="mb-5">
                        <h3 className="font-semibold text-lg">{pkg.name}</h3>
                        <div className="mt-2 flex items-baseline gap-2">
                          <Price amount={pkg.priceRub} className="text-3xl font-bold" />
                        </div>
                        <p className="text-xs text-primary font-medium mt-1 uppercase tracking-[0.18em]">
                          {pricePerAnalysis} / analysis
                        </p>
                        <p className="text-xs text-muted-foreground mt-3 leading-5">{pkg.description}</p>
                      </div>

                      <div className="space-y-2.5 flex-1 border-t border-border/50 pt-4 mb-6">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">Analyses included</span>
                          <span className="text-sm font-bold">{pkg.credits.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">Valid for</span>
                          <span className="text-sm font-bold">{pkg.validityDays} days</span>
                        </div>
                        {pkg.savingsPct && (
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-muted-foreground">You save</span>
                            <span className="text-sm font-bold text-emerald-500">{pkg.savingsPct}</span>
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => handleCreditPackagePurchase(pkgKey)}
                        disabled={selectedPackage === pkgKey}
                        className={`btn w-full py-2.5 rounded-full text-xs font-semibold uppercase tracking-[0.18em] transition-all ${
                          pkg.highlight ? "btn-primary shadow-primary" : "btn-outline"
                        }`}
                      >
                        {selectedPackage === pkgKey
                          ? "Processing..."
                          : `Buy ${pkg.credits.toLocaleString()} credits`}
                      </button>
                    </div>
                  </ThreeCardEffect>
                )
              })}
            </div>
          </div>
        </section>
    </>
  )
}
