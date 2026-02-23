"use client"

import { useState } from "react"
import { Copy, RefreshCw, AlertTriangle, Key } from "lucide-react"
import { motion } from "framer-motion"

export default function ApiSettingsPage() {
  const [copied, setCopied] = useState(false)
  const apiKey = "vk_live_8f3d9c2e1b4a7...9x5z" // Mock key

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">API Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your API keys and access tokens for programmatic access.
        </p>
      </div>

      <div className="grid gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Key className="h-4 w-4 text-primary" />
              Active API Key
            </h2>
            <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
              Created: Feb 23, 2026
            </div>
          </div>
          
          <div className="flex gap-2 mb-4">
            <div className="relative flex-1">
              <input
                type="text"
                readOnly
                value={apiKey}
                className="input-field font-mono pr-12 bg-muted/30"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-muted-foreground text-xs">
                HIDDEN
              </div>
            </div>
            <button 
              onClick={copyToClipboard}
              className="btn btn-outline min-w-[100px]"
            >
              {copied ? "Copied!" : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copy
                </>
              )}
            </button>
          </div>

          <div className="flex items-center gap-2 text-sm text-amber-500/80 bg-amber-500/10 p-3 rounded-lg border border-amber-500/20">
            <AlertTriangle className="h-4 w-4" />
            <p>Your secret key is only shown once. Keep it safe.</p>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">Usage Quotas</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Monthly Requests</span>
                <span className="font-mono">8,542 / 10,000</span>
              </div>
              <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                <div className="bg-primary h-full w-[85%] rounded-full" />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Video Processing Hours</span>
                <span className="font-mono">42.5 / 100</span>
              </div>
              <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full w-[42%] rounded-full" />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
           <button className="btn btn-outline text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/20">
             Revoke all keys
           </button>
        </div>
      </div>
    </div>
  )
}
