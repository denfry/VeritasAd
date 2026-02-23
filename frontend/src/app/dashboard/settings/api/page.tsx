"use client"

import { useState } from "react"
import { Copy, RefreshCw, AlertTriangle, Key, Loader2, Check } from "lucide-react"
import { motion } from "framer-motion"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"

export default function ApiSettingsPage() {
  const { user, loading } = useAuth()
  const [copied, setCopied] = useState(false)
  const [showKey, setShowKey] = useState(false)

  const copyToClipboard = () => {
    if (!user?.api_key) return
    navigator.clipboard.writeText(user.api_key)
    setCopied(true)
    toast.success("API key copied to clipboard")
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">API Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your API keys and access tokens for programmatic access to VeritasAd.
        </p>
      </div>

      <div className="grid gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Key className="h-4 w-4 text-primary" />
              Your API Key
            </h2>
            <div className="text-[10px] uppercase font-bold text-muted-foreground bg-muted px-2 py-1 rounded">
              {user?.plan} PLAN
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-2 mb-4">
            <div className="relative flex-1">
              <input
                type={showKey ? "text" : "password"}
                readOnly
                value={user?.api_key || "No API key generated"}
                className="input-field font-mono pr-20 bg-muted/30"
              />
              <button 
                onClick={() => setShowKey(!showKey)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-primary text-xs font-semibold hover:underline"
              >
                {showKey ? "HIDE" : "SHOW"}
              </button>
            </div>
            <button 
              onClick={copyToClipboard}
              disabled={!user?.api_key}
              className="btn btn-outline min-w-[120px]"
            >
              {copied ? (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copy Key
                </>
              )}
            </button>
          </div>

          <div className="flex items-start gap-3 text-sm text-amber-600 bg-amber-500/5 p-4 rounded-lg border border-amber-500/10">
            <AlertTriangle className="h-5 w-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Security Warning</p>
              <p className="opacity-90">
                Your API key grants full access to your account's analysis credits. 
                Never share it in client-side code, public repositories, or with unauthorized persons.
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            Usage & Quotas
          </h2>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">Daily Analysis Limit</span>
                <span className="font-mono text-muted-foreground">
                  <span className="text-foreground font-bold">{user?.daily_used || 0}</span> / {user?.daily_limit || 0}
                </span>
              </div>
              <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-primary h-full transition-all duration-500" 
                  style={{ width: `${Math.min(100, ((user?.daily_used || 0) / (user?.daily_limit || 1)) * 100)}%` }}
                />
              </div>
              <p className="text-[10px] text-muted-foreground mt-2 uppercase tracking-wider">
                Resets every 24 hours at 00:00 UTC
              </p>
            </div>
            
            <div className="pt-4 border-t border-dashed">
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">Total Lifetime Analyses</span>
                <span className="font-mono font-bold">{user?.total_analyses || 0}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                You have processed {user?.total_analyses} videos since joining the platform.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-muted/20 rounded-xl border border-dashed">
          <div className="text-sm text-muted-foreground">
             Need a higher limit or custom integration assistance?
          </div>
          <Link href="/pricing" className="btn btn-primary btn-sm">
             View Enterprise Plans
          </Link>
        </div>
      </div>
    </div>
  )
}

import Link from "next/link"
