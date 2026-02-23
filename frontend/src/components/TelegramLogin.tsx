"use client"

import { useEffect, useRef, useCallback } from "react"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

interface TelegramLoginProps {
  botUsername: string
  onAuthSuccess?: (authData: TelegramAuthData) => void
  onAuthError?: (error: Error) => void
  size?: "small" | "medium" | "large"
  cornerRadius?: number
  requestAccess?: boolean
}

interface TelegramAuthData {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

declare global {
  interface Window {
    onTelegramAuth?: (user: TelegramAuthData) => void
    Telegram?: {
      Login: {
        auth: (
          params: {
            "bot-id": string
            "request-access": string
            "userpic": boolean
            "lang": string
          },
          callback: (authData: TelegramAuthData | false) => void
        ) => void
      }
    }
  }
}

/**
 * Telegram Login Widget component
 * 
 * Integrates Telegram's official Login Widget for seamless authentication.
 * Requires a Telegram bot to be configured.
 * 
 * @see https://core.telegram.org/widgets/login
 */
export function TelegramLogin({
  botUsername,
  onAuthSuccess,
  onAuthError,
  size = "large",
  cornerRadius = 20,
  requestAccess = true,
}: TelegramLoginProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const scriptLoaded = useRef(false)
  const { supabaseConfigured } = useAuth()

  // Load Telegram widget script
  useEffect(() => {
    if (scriptLoaded.current) return

    const script = document.createElement("script")
    script.src = "https://telegram.org/js/telegram-widget.js?22"
    script.async = true
    script.onload = () => {
      scriptLoaded.current = true
    }
    document.body.appendChild(script)

    return () => {
      // Cleanup on unmount
      if (document.body.contains(script)) {
        document.body.removeChild(script)
      }
    }
  }, [])

  // Handle Telegram authentication callback
  const handleTelegramAuth = useCallback(
    async (authData: TelegramAuthData) => {
      try {
        // Send auth data to backend for validation and token exchange
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/telegram/auth`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(authData),
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Authentication failed")
        }

        const data = await response.json()

        // Store tokens in localStorage (for API access)
        localStorage.setItem("access_token", data.access_token)
        localStorage.setItem("refresh_token", data.refresh_token)

        toast.success("Logged in via Telegram successfully!")

        onAuthSuccess?.(authData)
      } catch (error) {
        const err = error instanceof Error ? error : new Error("Authentication failed")
        toast.error(`Login error: ${err.message}`)
        onAuthError?.(err)
      }
    },
    [onAuthSuccess, onAuthError]
  )

  // Initialize widget after script loads
  useEffect(() => {
    if (!scriptLoaded.current || !containerRef.current) return
    if (!window.Telegram || !window.Telegram.Login) return

    const container = containerRef.current

    // Clear previous widget
    container.innerHTML = ""

    // Initialize Telegram widget
    window.Telegram.Login.auth(
      {
        "bot-id": botUsername.replace("@", ""),
        "request-access": requestAccess ? "write" : "read",
        "userpic": true,
        "lang": "ru",
      },
      (authData: TelegramAuthData | false) => {
        if (!authData) {
          toast.error("Authorization cancelled")
          return
        }
        handleTelegramAuth(authData)
      }
    )
  }, [botUsername, requestAccess, handleTelegramAuth])

  if (!supabaseConfigured) {
    return (
      <div className="text-sm text-muted-foreground p-4 text-center">
        Telegram Login requires Supabase configuration
      </div>
    )
  }

  return (
    <div className="flex justify-center">
      <div ref={containerRef} className="telegram-login-container" />
      {!scriptLoaded.current && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading Telegram widget...
        </div>
      )}
    </div>
  )
}

/**
 * Telegram Login Button - simpler alternative using button element
 */
export function TelegramLoginButton({
  botUsername,
  onAuthSuccess,
  onAuthError,
  size = "large",
}: TelegramLoginProps) {
  const { supabaseConfigured } = useAuth()

  const sizeMap = {
    small: "small",
    medium: "medium",
    large: "large",
  }

  if (!supabaseConfigured) {
    return null
  }

  return (
    <div
      data-telegram-login={botUsername.replace("@", "")}
      data-size={sizeMap[size]}
      data-onauth="onTelegramAuth(user)"
      data-request-access="write"
      style={{ borderRadius: "20px" }}
    />
  )
}
