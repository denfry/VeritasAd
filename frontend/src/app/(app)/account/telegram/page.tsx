"use client"

import { useState, useEffect, useCallback } from "react"

import { motion, AnimatePresence } from "framer-motion"
import {
  CheckCircle2,
  Link2,
  Unlink2,
  Copy,
  Send,
  Loader2,
  Shield,
  MessageCircle,
  ArrowLeft,
  Clock,
  AlertCircle,
} from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"
import {
  getTelegramLinkStatus,
  generateTelegramLinkToken,
  linkTelegramAccount,
  unlinkTelegramAccount,
  type TelegramLinkStatus,
} from "@/lib/api-client"
import { TelegramLogin } from "@/components/TelegramLogin"

const BOT_USERNAME = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || "VeritasAdBot"

export default function TelegramPage() {
  const [loading, setLoading] = useState(true)
  const [linkStatus, setLinkStatus] = useState<TelegramLinkStatus | null>(null)
  const [generating, setGenerating] = useState(false)
  const [unlinking, setUnlinking] = useState(false)
  const [linkToken, setLinkToken] = useState<string | null>(null)
  const [tokenExpiry, setTokenExpiry] = useState<number | null>(null)
  const [copied, setCopied] = useState(false)
  const [showWidget, setShowWidget] = useState(false)

  const fetchStatus = useCallback(async () => {
    try {
      const status = await getTelegramLinkStatus()
      setLinkStatus(status)
    } catch {
      toast.error("Failed to load Telegram link status")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const handleGenerateToken = async () => {
    setGenerating(true)
    try {
      const result = await generateTelegramLinkToken()
      setLinkToken(result.token)
      setTokenExpiry(result.expires_in)
      toast.success("Link token generated successfully")
    } catch {
      toast.error("Failed to generate link token")
    } finally {
      setGenerating(false)
    }
  }

  const handleCopyLink = async () => {
    if (!linkToken) return
    const botLink = `https://t.me/${BOT_USERNAME.replace("@", "")}?start=${linkToken}`
    await navigator.clipboard.writeText(botLink)
    setCopied(true)
    toast.success("Link copied to clipboard")
    setTimeout(() => setCopied(false), 2000)
  }

  const handleUnlink = async () => {
    setUnlinking(true)
    try {
      await unlinkTelegramAccount()
      setLinkStatus({ is_linked: false })
      setLinkToken(null)
      setTokenExpiry(null)
      toast.success("Telegram account unlinked")
    } catch {
      toast.error("Failed to unlink Telegram account")
    } finally {
      setUnlinking(false)
    }
  }

  const handleTelegramAuthSuccess = async (authData: {
    id: number
    first_name: string
    last_name?: string
    username?: string
    photo_url?: string
    auth_date: number
    hash: string
  }) => {
    if (!linkToken) {
      toast.error("Please generate a link token first")
      return
    }
    try {
      await linkTelegramAccount({
        telegram_id: authData.id,
        link_token: linkToken,
        username: authData.username,
      })
      toast.success("Telegram account linked successfully")
      await fetchStatus()
      setLinkToken(null)
      setTokenExpiry(null)
      setShowWidget(false)
    } catch {
      toast.error("Failed to link Telegram account")
    }
  }

  const formatExpiry = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  if (loading) {
    return (
      
        <section className="container mx-auto max-w-3xl px-4 py-12 lg:py-16">
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </section>
      
    )
  }

  return (
    
      <section className="container mx-auto max-w-3xl px-4 py-12 lg:py-16 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-3 mb-2">
            <Link href="/account" className="p-2 rounded-xl hover:bg-muted transition-colors">
              <ArrowLeft className="h-4 w-4 text-muted-foreground" />
            </Link>
            <h1 className="text-3xl font-semibold tracking-tight">Telegram Integration</h1>
          </div>
          <p className="text-muted-foreground font-medium">
            Connect your Telegram account for seamless access and notifications
          </p>
        </motion.div>

        <AnimatePresence mode="wait">
          {linkStatus?.is_linked ? (
            <motion.div
              key="linked"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              <div className="surface p-8 space-y-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-6 opacity-5">
                  <MessageCircle className="h-32 w-32" />
                </div>

                <div className="flex items-center justify-between relative z-10">
                  <div className="flex items-center gap-4">
                    <div className="h-14 w-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                      <CheckCircle2 className="h-7 w-7 text-emerald-500" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold">Telegram Connected</h2>
                      <p className="text-sm text-muted-foreground font-medium">
                        {linkStatus.telegram_username ? `@${linkStatus.telegram_username}` : "Account linked"}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleUnlink}
                    disabled={unlinking}
                    className="btn btn-outline h-11 px-5 rounded-full gap-2 text-red-500 border-red-500/20 hover:bg-red-500/10 font-semibold disabled:opacity-50"
                  >
                    {unlinking ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Unlink2 className="h-4 w-4" />
                    )}
                    Disconnect
                  </button>
                </div>

                {linkStatus.linked_at && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground pt-4 border-t border-border/50">
                    <Clock className="h-3.5 w-3.5" />
                    <span>Linked on {new Date(linkStatus.linked_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</span>
                  </div>
                )}
              </div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="surface p-8 space-y-6"
              >
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Connected Features
                </h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  {[
                    { title: "Quick Analysis", desc: "Send videos directly via Telegram bot" },
                    { title: "Notifications", desc: "Get alerts when analysis completes" },
                    { title: "Unified History", desc: "Sync analysis across web and Telegram" },
                    { title: "Telegram Login", desc: "Sign in to website using Telegram" },
                  ].map((feature, i) => (
                    <div key={i} className="p-4 rounded-2xl bg-muted/20 border border-border/50 space-y-1">
                      <p className="text-sm font-semibold">{feature.title}</p>
                      <p className="text-xs text-muted-foreground">{feature.desc}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key="unlinked"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              <div className="surface p-8 space-y-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-6 opacity-5">
                  <MessageCircle className="h-32 w-32" />
                </div>

                <div className="flex items-center gap-4 relative z-10">
                  <div className="h-14 w-14 rounded-2xl bg-muted flex items-center justify-center">
                    <Link2 className="h-7 w-7 text-muted-foreground" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold">Not Connected</h2>
                    <p className="text-sm text-muted-foreground font-medium">
                      Link your Telegram account to unlock additional features
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-border/50 space-y-4">
                  <p className="text-sm text-muted-foreground font-medium">Choose a linking method:</p>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <button
                      onClick={() => {
                        setShowWidget(true)
                        setLinkToken(null)
                      }}
                      className="p-5 rounded-2xl bg-muted/20 border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all text-left space-y-3 group"
                    >
                      <div className="h-10 w-10 rounded-xl bg-blue-500/10 flex items-center justify-center group-hover:bg-blue-500/20 transition-colors">
                        <MessageCircle className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">Telegram Login Widget</p>
                        <p className="text-xs text-muted-foreground">Quick one-click authorization</p>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        setShowWidget(false)
                        handleGenerateToken()
                      }}
                      disabled={generating}
                      className="p-5 rounded-2xl bg-muted/20 border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all text-left space-y-3 group disabled:opacity-50"
                    >
                      <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
                        {generating ? (
                          <Loader2 className="h-5 w-5 text-purple-500 animate-spin" />
                        ) : (
                          <Link2 className="h-5 w-5 text-purple-500" />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-semibold">Link Token</p>
                        <p className="text-xs text-muted-foreground">Generate a token for the bot</p>
                      </div>
                    </button>
                  </div>
                </div>
              </div>

              <AnimatePresence>
                {showWidget && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="surface p-8 space-y-4">
                      <h3 className="text-lg font-semibold">Telegram Login</h3>
                      <p className="text-sm text-muted-foreground">
                        Click the button below to authorize via Telegram
                      </p>
                      <TelegramLogin
                        botUsername={BOT_USERNAME}
                        onAuthSuccess={handleTelegramAuthSuccess}
                        onAuthError={(error) => toast.error(error.message)}
                        size="large"
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {linkToken && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="surface p-8 space-y-6">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Send className="h-5 w-5 text-primary" />
                        Link via Bot
                      </h3>

                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 rounded-2xl bg-muted/20 border border-border/50">
                          <code className="text-sm font-mono font-medium">/start {linkToken}</code>
                          <button
                            onClick={handleCopyLink}
                            className="p-2.5 rounded-xl hover:bg-muted transition-colors"
                            title="Copy link"
                          >
                            {copied ? (
                              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                            ) : (
                              <Copy className="h-4 w-4 text-muted-foreground" />
                            )}
                          </button>
                        </div>

                        {tokenExpiry && (
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Clock className="h-3.5 w-3.5" />
                            <span>Token expires in {formatExpiry(tokenExpiry)}</span>
                          </div>
                        )}

                        <a
                          href={`https://t.me/${BOT_USERNAME.replace("@", "")}?start=${linkToken}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-sm text-primary hover:underline font-medium"
                        >
                          <Send className="h-4 w-4" />
                          Open @{BOT_USERNAME.replace("@", "")} in Telegram
                        </a>
                      </div>

                      <div className="flex items-start gap-3 p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20">
                        <AlertCircle className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-muted-foreground leading-relaxed">
                          Send the <code className="text-xs font-mono">/start</code> command with your token to the bot. The bot will automatically link your account once verified.
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="surface p-8 space-y-6"
              >
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Why Connect Telegram?
                </h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  {[
                    { title: "Quick Analysis", desc: "Send videos directly via Telegram bot" },
                    { title: "Notifications", desc: "Get alerts when analysis completes" },
                    { title: "Unified History", desc: "Sync analysis across web and Telegram" },
                    { title: "Telegram Login", desc: "Sign in to website using Telegram" },
                  ].map((feature, i) => (
                    <div key={i} className="p-4 rounded-2xl bg-muted/20 border border-border/50 space-y-1">
                      <p className="text-sm font-semibold">{feature.title}</p>
                      <p className="text-xs text-muted-foreground">{feature.desc}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    
  )
}
