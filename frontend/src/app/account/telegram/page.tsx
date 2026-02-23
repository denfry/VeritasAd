"use client"

import { useState, useEffect } from "react"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"
import { Loader2, Link, Unlink, Copy, Check, Send } from "lucide-react"
import {
  getTelegramLinkStatus,
  generateTelegramLinkToken,
  unlinkTelegramAccount,
  type TelegramLinkStatus,
} from "@/lib/api-client"
import { Button } from "@/components/ui/Button"

export default function TelegramAccountPage() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [linkStatus, setLinkStatus] = useState<TelegramLinkStatus | null>(null)
  const [generating, setGenerating] = useState(false)
  const [unlinking, setUnlinking] = useState(false)
  const [linkToken, setLinkToken] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const BOT_USERNAME = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || "VeritasAdBot"

  // Fetch link status on mount
  useEffect(() => {
    async function fetchStatus() {
      try {
        const status = await getTelegramLinkStatus()
        setLinkStatus(status)
      } catch (error) {
        toast.error("Failed to load link status")
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  // Generate link token
  const handleGenerateToken = async () => {
    setGenerating(true)
    try {
      const result = await generateTelegramLinkToken()
      setLinkToken(result.token)
      toast.success("Token generated! Open the bot and send /start {token}")
    } catch (error) {
      toast.error("Failed to generate token")
    } finally {
      setGenerating(false)
    }
  }

  // Copy link to clipboard
  const handleCopyLink = async () => {
    if (!linkToken) return

    const botLink = `https://t.me/${BOT_USERNAME.replace("@", "")}?start=${linkToken}`
    await navigator.clipboard.writeText(botLink)
    setCopied(true)
    toast.success("Link copied to clipboard")

    setTimeout(() => setCopied(false), 2000)
  }

  // Unlink account
  const handleUnlink = async () => {
    if (!confirm("Are you sure you want to unlink your Telegram account?")) return

    setUnlinking(true)
    try {
      await unlinkTelegramAccount()
      setLinkStatus({ is_linked: false })
      setLinkToken(null)
      toast.success("Telegram account unlinked")
    } catch (error) {
      toast.error("Failed to unlink account")
    } finally {
      setUnlinking(false)
    }
  }

  if (loading) {
    return (
      <SiteShell>
        <div className="container mx-auto max-w-2xl px-4 py-8">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        </div>
      </SiteShell>
    )
  }

  return (
    <SiteShell>
      <section className="container mx-auto max-w-2xl px-4 py-8 space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-semibold">Telegram Linking</h1>
          <p className="text-muted-foreground">
            Link your account with Telegram for easy access via the bot
          </p>
        </div>

        {/* Status Card */}
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {linkStatus?.is_linked ? (
                <div className="h-10 w-10 rounded-full bg-green-500/15 flex items-center justify-center">
                  <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
              ) : (
                <div className="h-10 w-10 rounded-full bg-gray-500/15 flex items-center justify-center">
                  <Link className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </div>
              )}
              <div>
                <h3 className="font-medium">
                  {linkStatus?.is_linked ? "Telegram linked" : "Telegram not linked"}
                </h3>
                {linkStatus?.is_linked && linkStatus.telegram_username && (
                  <p className="text-sm text-muted-foreground">
                    @{linkStatus.telegram_username}
                  </p>
                )}
              </div>
            </div>

            {linkStatus?.is_linked && (
              <Button
                variant="outline"
                onClick={handleUnlink}
                disabled={unlinking}
                className="gap-2"
              >
                {unlinking ? <Loader2 className="h-4 w-4 animate-spin" /> : <Unlink className="h-4 w-4" />}
                Unlink
              </Button>
            )}
          </div>

          {linkStatus?.is_linked && linkStatus.linked_at && (
            <div className="text-sm text-muted-foreground pt-4 border-t">
              Linked on {new Date(linkStatus.linked_at).toLocaleDateString("en-US")}
            </div>
          )}
        </div>

        {/* Link Instructions */}
        {!linkStatus?.is_linked && (
          <div className="card p-6 space-y-4">
            <h3 className="font-medium">How to link Telegram:</h3>

            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-primary/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-medium">1</span>
                </div>
                <p className="text-muted-foreground">
                  Open the Telegram bot{" "}
                  <a
                    href={`https://t.me/${BOT_USERNAME.replace("@", "")}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline inline-flex items-center gap-1"
                  >
                    @{BOT_USERNAME.replace("@", "")}
                    <Send className="h-3 w-3" />
                  </a>
                </p>
              </div>

              <div className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-primary/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-medium">2</span>
                </div>
                <div className="space-y-2 flex-1">
                  <p className="text-muted-foreground">
                    Click the button to generate a link token:
                  </p>
                  <Button
                    onClick={handleGenerateToken}
                    disabled={generating}
                    className="w-full gap-2"
                  >
                    {generating ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Generating token...
                      </>
                    ) : (
                      <>
                        <Link className="h-4 w-4" />
                        Generate link token
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {linkToken && (
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-primary/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium">3</span>
                  </div>
                  <div className="space-y-2 flex-1">
                    <p className="text-muted-foreground">
                      Send the bot a command with the token or use the direct link:
                    </p>
                    <div className="flex gap-2">
                      <code className="flex-1 px-3 py-2 bg-muted rounded-md text-sm font-mono">
                        /start {linkToken}
                      </code>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={handleCopyLink}
                        title="Copy link"
                      >
                        {copied ? (
                          <Check className="h-4 w-4" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                    <a
                      href={`https://t.me/${BOT_USERNAME.replace("@", "")}?start=${linkToken}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-primary hover:underline text-sm"
                    >
                      <Send className="h-3 w-3" />
                      Open in Telegram
                    </a>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-primary/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-medium">4</span>
                </div>
                <p className="text-muted-foreground">
                  The bot will automatically link your Telegram account to the website
                </p>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-500/15 border border-blue-500/40 rounded-lg text-sm">
              <p className="text-blue-800 dark:text-blue-200">
                <strong>Token is valid for 24 hours.</strong> After linking, you'll be able
                to use the bot for video analysis and viewing statistics.
              </p>
            </div>
          </div>
        )}

        {/* Benefits */}
        <div className="card p-6 space-y-4">
          <h3 className="font-medium">Benefits of linking:</h3>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
              Quick access to analysis via Telegram
            </li>
            <li className="flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
              Notifications when analysis is ready
            </li>
            <li className="flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
              Unified analysis history on website and bot
            </li>
            <li className="flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
              Log in to website via Telegram Login Widget
            </li>
          </ul>
        </div>
      </section>
    </SiteShell>
  )
}
