"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

export default function RegisterPage() {
  const router = useRouter()
  const { signUp, supabaseConfigured, isMock } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error("Passwords don't match")
      return
    }

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters")
      return
    }

    setLoading(true)

    try {
      await signUp(email, password)
      if (isMock) {
        toast.success("Mock-режим: аккаунт создан. Войдите с теми же данными.", { duration: 3000 })
        setTimeout(() => {
          router.push("/auth/login?registered=true")
        }, 1500)
      } else {
        toast.success(
          "Registration successful! Please check your email (" + email + ") to confirm your account.",
          { duration: 8000 }
        )
        setTimeout(() => {
          router.push("/auth/login?registered=true")
        }, 2000)
      }
    } catch (error: any) {
      const errorMessage = error.message || "Failed to create account"
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <SiteShell>
      <section className="container mx-auto max-w-md px-4 section">
        {isMock && (
          <div className="mb-4 p-4 rounded-lg bg-blue-500/15 border border-blue-500/40 text-blue-800 dark:text-blue-200 text-sm">
            <strong>Mock-режим:</strong> регистрация работает локально без Supabase.
            Аккаунт создаётся автоматически при первом входе.
          </div>
        )}
        <div className="card p-8 space-y-6">
          <div className="space-y-2 text-center">
            <h1 className="text-3xl font-semibold">Create account</h1>
            <p className="text-sm text-muted-foreground">
              Enter your email and password to get started
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <input
                type="email"
                className="input-field"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <input
                type="password"
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
              <p className="text-xs text-muted-foreground">At least 8 characters</p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Confirm password</label>
              <input
                type="password"
                className="input-field"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary w-full py-3">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create account"}
            </button>
          </form>

          <div className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </div>

          <div className="space-y-3">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">Coming soon</span>
              </div>
            </div>

            <div className="grid gap-2">
              <button disabled className="btn btn-outline py-2 opacity-50 cursor-not-allowed">
                Sign up with Phone
              </button>
              <button disabled className="btn btn-outline py-2 opacity-50 cursor-not-allowed">
                Sign up with Telegram
              </button>
              <button disabled className="btn btn-outline py-2 opacity-50 cursor-not-allowed">
                Sign up with Google
              </button>
            </div>
          </div>
        </div>
      </section>
    </SiteShell>
  )
}
