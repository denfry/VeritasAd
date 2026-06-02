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
import { useLanguage } from "@/contexts/language-context"

import { motion } from "framer-motion"

// Numeric data only (no text)
const PLAN_PRICES: Record<string, { priceRub: number; originalPriceRub?: number; popular: boolean; iconKey: string }> = {
  free:       { priceRub: 0,     popular: false, iconKey: "zap" },
  starter:    { priceRub: 2900,  popular: false, iconKey: "users" },
  pro:        { priceRub: 7900,  originalPriceRub: 15000, popular: true,  iconKey: "trending" },
  business:   { priceRub: 19900, popular: false, iconKey: "building" },
  enterprise: { priceRub: 49900, popular: false, iconKey: "zap" },
}

const CREDIT_PACKAGES_BASE = [
  { key: "micro",    credits: 100,  priceRub: 1500,  validityDays: 30,  highlight: false, savingsPct: undefined as string | undefined },
  { key: "standard", credits: 500,  priceRub: 5000,  validityDays: 60,  highlight: true,  savingsPct: "33%" },
  { key: "pro",      credits: 1500, priceRub: 12000, validityDays: 90,  highlight: false, savingsPct: "47%" },
  { key: "business", credits: 8000, priceRub: 40000, validityDays: 180, highlight: false, savingsPct: "67%" },
]

const PLAN_ICONS: Record<string, React.ReactNode> = {
  zap:      <Zap className="h-5 w-5" />,
  users:    <Users className="h-5 w-5" />,
  trending: <TrendingUp className="h-5 w-5" />,
  building: <Building className="h-5 w-5" />,
}

export default function PricingPage() {
  const router = useRouter()
  const { user } = useAuth()
  const { t } = useLanguage()
  const p = t.pricing
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null)
  const { selectedCurrency, setSelectedCurrency, formatPrice } = useCurrency()

  async function handleSubscriptionUpgrade(plan: string) {
    if (!user) {
      toast.error(p.signInFirst)
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
      toast.error(p.unablePayment)
    }
  }

  async function handleCreditPackagePurchase(packageType: string) {
    if (!user) {
      toast.error(p.signInFirst)
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
      toast.error(p.unablePayment)
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
              <p className="eyebrow">{p.eyebrow}</p>
              <h1 className="mt-2 text-4xl font-semibold tracking-tight">
                {p.title}
              </h1>
              <p className="mt-2 text-muted-foreground max-w-lg text-sm leading-6">
                {p.description}
              </p>
            </div>
            <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-2xl border border-border/50">
              <span className="eyebrow ml-2">{p.currency}</span>
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
            <h2 className="text-xl font-semibold tracking-tight">{p.monthlyTitle}</h2>
            <p className="text-sm text-muted-foreground mt-1">
              {p.monthlyDesc}
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {(Object.keys(PLAN_PRICES) as Array<keyof typeof PLAN_PRICES>).map((planKey) => {
              const prices = PLAN_PRICES[planKey]
              const planText = p.plans[planKey as keyof typeof p.plans]
              const isPaidPlan = planKey !== "free"
              return (
                <ThreeCardEffect
                  key={planKey}
                  glowColor={prices.popular ? "hsl(var(--primary))" : "hsl(var(--muted))"}
                  intensity={10}
                >
                  <div
                    className={`surface p-5 flex flex-col relative h-full transition-all duration-200 ${
                      prices.popular
                        ? "ring-2 ring-primary/60 border-primary/30"
                        : "border-border/50"
                    }`}
                  >
                    {prices.popular && (
                      <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-[10px] font-semibold uppercase tracking-[0.2em] px-3 py-1 rounded-full shadow-md">
                        {p.mostPopular}
                      </span>
                    )}

                    <div className="mb-5">
                      <div className="flex items-center gap-2.5 mb-3">
                        <div className="p-1.5 rounded-lg bg-primary/8 text-primary border border-primary/15">
                          {PLAN_ICONS[prices.iconKey]}
                        </div>
                        <h3 className="font-semibold">{planText.name}</h3>
                      </div>
                      <div className="flex items-baseline gap-2 flex-wrap">
                        <PricePerMonth amount={prices.priceRub} className="text-2xl font-bold" />
                        {prices.originalPriceRub && (
                          <Price
                            amount={prices.originalPriceRub}
                            className="text-sm text-muted-foreground line-through opacity-50"
                          />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-2 leading-5">{planText.description}</p>
                    </div>

                    <ul className="space-y-2.5 text-sm flex-1 mb-6">
                      {planText.features.map((feature, idx) => (
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
                        prices.popular ? "btn-primary shadow-primary" : "btn-outline"
                      }`}
                    >
                      {planText.cta}
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
              <h2 className="text-xl font-semibold tracking-tight">{p.payAsYouGo}</h2>
              <p className="text-sm text-muted-foreground mt-1">
                {p.payAsYouGoDesc}
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              {CREDIT_PACKAGES_BASE.map((pkg) => {
                const pricePerAnalysis = formatPrice(pkg.priceRub / pkg.credits)
                const pkgText = p.creditPackages[pkg.key as keyof typeof p.creditPackages]

                return (
                  <ThreeCardEffect
                    key={pkg.key}
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
                        <h3 className="font-semibold text-lg">{pkgText.name}</h3>
                        <div className="mt-2 flex items-baseline gap-2">
                          <Price amount={pkg.priceRub} className="text-3xl font-bold" />
                        </div>
                        <p className="text-xs text-primary font-medium mt-1 uppercase tracking-[0.18em]">
                          {pricePerAnalysis} {p.perAnalysis}
                        </p>
                        <p className="text-xs text-muted-foreground mt-3 leading-5">{pkgText.description}</p>
                      </div>

                      <div className="space-y-2.5 flex-1 border-t border-border/50 pt-4 mb-6">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">{p.analysesIncluded}</span>
                          <span className="text-sm font-bold">{pkg.credits.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">{p.validFor}</span>
                          <span className="text-sm font-bold">{pkg.validityDays} {p.days}</span>
                        </div>
                        {pkg.savingsPct && (
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-muted-foreground">{p.youSave}</span>
                            <span className="text-sm font-bold text-emerald-500">{pkg.savingsPct}</span>
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => handleCreditPackagePurchase(pkg.key)}
                        disabled={selectedPackage === pkg.key}
                        className={`btn w-full py-2.5 rounded-full text-xs font-semibold uppercase tracking-[0.18em] transition-all ${
                          pkg.highlight ? "btn-primary shadow-primary" : "btn-outline"
                        }`}
                      >
                        {selectedPackage === pkg.key
                          ? p.processing
                          : `${p.buyCredits} ${pkg.credits.toLocaleString()} ${p.credits}`}
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
