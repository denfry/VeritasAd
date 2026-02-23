"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { getCurrentUserProfile, getUserCredits, getCreditHistory } from "@/lib/api-client"
import type { UserProfile } from "@/types/api"
import type { UserCreditsResponse, CreditTransactionItem } from "@/lib/api-client"
import { toast } from "sonner"
import { Loader2, LogOut, User, Key, BarChart3, Zap, Calendar, History } from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"
import { useCurrency, Price } from "@/contexts/currency-context"

export default function AccountPage() {
  const router = useRouter()
  const { user, signOut, loading: authLoading } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [credits, setCredits] = useState<UserCreditsResponse | null>(null)
  const [creditHistory, setCreditHistory] = useState<CreditTransactionItem[]>([])
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  
  // Get currency context for global currency conversion
  const { formatPrice } = useCurrency()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
      return
    }

    if (user) {
      loadProfile()
      loadCredits()
    }
  }, [user, authLoading, router])

  const loadProfile = async () => {
    try {
      const data = await getCurrentUserProfile()
      setProfile(data)
      setErrorMessage(null)
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error("Session expired. Please sign in again.")
        try {
          await signOut()
        } catch (signOutError) {
          console.warn("Failed to sign out after session expiry:", signOutError)
        }
        router.push("/auth/login")
        setErrorMessage("Session expired. Please sign in again.")
      } else {
        toast.error("Failed to load profile")
        setErrorMessage("Failed to load profile. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  const loadCredits = async () => {
    try {
      const [creditsData, historyData] = await Promise.all([
        getUserCredits(),
        getCreditHistory({ limit: 10 }),
      ])
      setCredits(creditsData)
      setCreditHistory(historyData.transactions)
    } catch (error) {
      console.warn("Failed to load credits:", error)
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      toast.success("Signed out successfully")
      router.push("/")
    } catch (error: any) {
      toast.error("Failed to sign out")
    }
  }

  const getUsagePercentage = () => {
    if (!profile) return 0
    return Math.min((profile.daily_used / profile.daily_limit) * 100, 100)
  }

  const getPlanColor = (plan: string) => {
    const colors: Record<string, string> = {
      free: "bg-gray-500",
      starter: "bg-blue-500",
      pro: "bg-purple-500",
      business: "bg-orange-500",
      enterprise: "bg-red-500",
    }
    return colors[plan.toLowerCase()] || "bg-gray-500"
  }

  if (authLoading || loading) {
    return (
      <SiteShell>
        <section className="container mx-auto max-w-4xl px-4 section">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </section>
      </SiteShell>
    )
  }

  if (!profile) {
    return (
      <SiteShell>
        <section className="container mx-auto max-w-4xl px-4 section">
          <div className="card p-6 space-y-4 text-center">
            <h1 className="text-xl font-semibold">Account unavailable</h1>
            <p className="text-sm text-muted-foreground">
              {errorMessage ?? "Unable to load account details right now."}
            </p>
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => {
                  setLoading(true)
                  loadProfile()
                }}
                className="btn btn-primary"
              >
                Retry
              </button>
              <button onClick={() => router.push("/")} className="btn btn-outline">
                Go home
              </button>
            </div>
          </div>
        </section>
      </SiteShell>
    )
  }

  return (
    <SiteShell>
      <section className="container mx-auto max-w-4xl px-4 section space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold">Account</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Manage your profile, subscription, and credits
            </p>
          </div>
          <button onClick={handleSignOut} className="btn btn-outline gap-2">
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>

        {/* Main Stats */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {/* Plan */}
          <div className="card card-hover p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="text-primary">
                <User className="h-5 w-5" />
              </div>
              <span className={`badge ${getPlanColor(profile.plan)} text-white text-xs`}>
                {profile.plan.toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">Subscription</p>
            <p className="mt-1 text-2xl font-semibold capitalize">{profile.plan}</p>
          </div>

          {/* Daily Usage */}
          <div className="card card-hover p-5">
            <div className="text-primary mb-3">
              <BarChart3 className="h-5 w-5" />
            </div>
            <p className="text-sm text-muted-foreground">Daily usage</p>
            <p className="mt-1 text-2xl font-semibold">
              {profile.daily_used} / {profile.daily_limit}
            </p>
            <div className="mt-3 h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  getUsagePercentage() >= 90 ? "bg-red-500" :
                  getUsagePercentage() >= 70 ? "bg-yellow-500" : "bg-green-500"
                }`}
                style={{ width: `${getUsagePercentage()}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {getUsagePercentage().toFixed(0)}% used
            </p>
          </div>

          {/* Credits Balance */}
          <div className="card card-hover p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="text-primary">
                <Zap className="h-5 w-5" />
              </div>
              {credits && credits.credits > 0 && (
                <span className="badge bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 text-xs">
                  Active
                </span>
              )}
            </div>
            <p className="text-sm text-muted-foreground">Credits balance</p>
            <p className="mt-1 text-2xl font-semibold">
              {credits?.credits ?? 0}
            </p>
            {credits?.expires_at && (
              <p className="mt-1 text-xs text-muted-foreground">
                Expires: {format(new Date(credits.expires_at), "MMM d, yyyy")}
              </p>
            )}
          </div>

          {/* Total Analyses */}
          <div className="card card-hover p-5">
            <div className="text-primary mb-3">
              <Key className="h-4 w-4" />
            </div>
            <p className="text-sm text-muted-foreground">Total analyses</p>
            <p className="mt-1 text-2xl font-semibold">{profile.total_analyses}</p>
          </div>
        </div>

        {/* Credits & Usage Details */}
        {credits && (credits.total_purchased > 0 || credits.credits > 0) && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Credits Overview
            </h2>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Available</p>
                <p className="text-2xl font-semibold">{credits.credits}</p>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Total purchased</p>
                <p className="text-2xl font-semibold">{credits.total_purchased}</p>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Total used</p>
                <p className="text-2xl font-semibold">{credits.total_used}</p>
              </div>
            </div>
            {credits.expires_at && (
              <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>Credits expire on {format(new Date(credits.expires_at), "MMMM d, yyyy")}</span>
              </div>
            )}
            <div className="mt-6 flex gap-3">
              <Link href="/pricing" className="btn btn-primary">
                Buy more credits
              </Link>
              <Link href="/pricing#pay-as-you-go" className="btn btn-outline">
                View packages
              </Link>
            </div>
          </div>
        )}

        {/* Credit History */}
        {creditHistory.length > 0 && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <History className="h-5 w-5" />
              Recent Credit Transactions
            </h2>
            <div className="space-y-3">
              {creditHistory.map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${
                      tx.transaction_type === "purchase" ? "bg-green-500/10 text-green-600" :
                      tx.transaction_type === "usage" ? "bg-blue-500/10 text-blue-600" :
                      "bg-gray-500/10 text-gray-600"
                    }`}>
                      {tx.transaction_type === "purchase" ? "+" :
                       tx.transaction_type === "usage" ? "−" : "•"}
                    </div>
                    <div>
                      <p className="font-medium capitalize">{tx.transaction_type}</p>
                      {tx.description && (
                        <p className="text-xs text-muted-foreground">{tx.description}</p>
                      )}
                      {tx.package_type && (
                        <p className="text-xs text-muted-foreground capitalize">
                          Package: {tx.package_type}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${
                      tx.credits > 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {tx.credits > 0 ? "+" : ""}{tx.credits}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Balance: {tx.balance_after}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {format(new Date(tx.created_at), "MMM d, HH:mm")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Profile Information */}
        <div className="card p-6 space-y-6">
          <h2 className="text-xl font-semibold">Profile information</h2>

          <div className="grid gap-4">
            <div>
              <label className="text-sm text-muted-foreground">Email</label>
              <p className="mt-1 font-medium">{profile.email || "Not set"}</p>
            </div>

            <div>
              <label className="text-sm text-muted-foreground">Role</label>
              <p className="mt-1 font-medium capitalize">{profile.role}</p>
            </div>

            <div>
              <label className="text-sm text-muted-foreground">Account status</label>
              <p className="mt-1 font-medium">
                {profile.is_active ? "Active" : "Inactive"}
              </p>
            </div>

            {profile.api_key && (
              <div>
                <label className="text-sm text-muted-foreground">API Key (legacy)</label>
                <p className="mt-1 font-mono text-xs bg-muted px-3 py-2 rounded">
                  {profile.api_key}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Admin Access */}
        {profile.role === "admin" && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Admin access</h2>
            <p className="text-sm text-muted-foreground mb-4">
              You have admin privileges. Access the admin dashboard to manage users and view
              analytics.
            </p>
            <Link href="/admin" className="btn btn-primary">
              Go to admin dashboard
            </Link>
          </div>
        )}

        {/* Upgrade Plan */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Need more analyses?</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Upgrade your plan for higher daily limits and priority support.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/pricing" className="btn btn-primary">
              View pricing plans
            </Link>
            <Link href="/pricing#pay-as-you-go" className="btn btn-outline">
              Buy credits
            </Link>
          </div>
          <div className="mt-4 p-4 bg-muted/50 rounded-lg">
            <p className="text-sm font-medium mb-2">Popular plans:</p>
            <div className="flex flex-wrap gap-4 text-sm">
              <span>
                <strong>Starter:</strong> <Price amount={2900} /> / month
              </span>
              <span>
                <strong>Pro:</strong> <Price amount={7900} /> / month
              </span>
              <span>
                <strong>Business:</strong> <Price amount={19900} /> / month
              </span>
            </div>
          </div>
        </div>
      </section>
    </SiteShell>
  )
}
