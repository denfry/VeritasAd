"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { supabase, isMockAuth } from "@/lib/supabase"
import type { MockUser, MockSession } from "@/lib/mock-auth"

// Unified types that work with both Supabase and Mock
type User = MockUser
type Session = MockSession

type AuthContextType = {
  user: User | null
  session: Session | null
  loading: boolean
  /** false если не заданы NEXT_PUBLIC_SUPABASE_URL и NEXT_PUBLIC_SUPABASE_ANON_KEY (используется mock) */
  supabaseConfigured: boolean
  /** true если используется mock-аутентификация для локальной разработки */
  isMock: boolean
  /** true если авторизация отключена (DISABLE_AUTH=true на бэкенде) */
  authDisabled: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
}

// Mock user для режима без авторизации
const MOCK_ADMIN_USER: User = {
  id: '0',
  email: 'test@veritasad.ai',
  role: 'admin',
  plan: 'enterprise',
  created_at: new Date().toISOString(),
}

const MOCK_SESSION: Session = {
  user: MOCK_ADMIN_USER,
  access_token: 'mock-token',
  refresh_token: 'mock-refresh-token',
  expires_at: Date.now() + 86400000, // 24 hours
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  // Проверяем, отключена ли авторизация через переменную окружения
  const authDisabled = process.env.NEXT_PUBLIC_DISABLE_AUTH === 'true'

  useEffect(() => {
    if (authDisabled) {
      // Режим без авторизации - сразу устанавливаем mock-пользователя
      setSession(MOCK_SESSION)
      setUser(MOCK_ADMIN_USER)
      setLoading(false)
      return
    }

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const authStateChangeResult = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Поддержка обоих форматов: { data: { subscription } } (Supabase) и { subscription } (Mock)
    const subscription = 'data' in authStateChangeResult
      ? (authStateChangeResult as any).data.subscription
      : (authStateChangeResult as any).subscription

    return () => subscription.unsubscribe()
  }, [authDisabled])

  const signIn = async (email: string, password: string) => {
    if (authDisabled) {
      // В режиме без авторизации просто устанавливаем mock-пользователя
      setSession(MOCK_SESSION)
      setUser(MOCK_ADMIN_USER)
      return
    }
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
  }

  const signUp = async (email: string, password: string) => {
    if (authDisabled) {
      setSession(MOCK_SESSION)
      setUser(MOCK_ADMIN_USER)
      return
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/login`,
      },
    })

    if (error) throw error

    // Check if email confirmation is required (only for real Supabase)
    if (!isMockAuth && data.user && !data.session) {
      console.log("Email confirmation required for:", email)
    }
  }

  const signOut = async () => {
    if (authDisabled) {
      // В режиме без авторизации просто очищаем пользователя
      setSession(null)
      setUser(null)
      return
    }
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  const value = {
    user,
    session,
    loading,
    supabaseConfigured: !isMockAuth && !authDisabled,
    isMock: isMockAuth && !authDisabled,
    authDisabled,
    signIn,
    signUp,
    signOut,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
