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
  /** Только для DEV: обновить данные текущего мок-пользователя */
  updateMockUser: (updates: Partial<User>) => void
}

// Mock user для режима без авторизации
const DEFAULT_MOCK_USER: User = {
  id: '0',
  email: 'dev-mode@veritasad.ai',
  role: 'admin',
  plan: 'enterprise',
  created_at: new Date().toISOString(),
}

const DEFAULT_MOCK_SESSION: Session = {
  user: DEFAULT_MOCK_USER,
  access_token: 'mock-token',
  refresh_token: 'mock-refresh-token',
  expires_at: Date.now() + 86400000, // 24 hours
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  // Проверяем, отключена ли авторизация через переменную окружения или в режиме разработки без Supabase
  const authDisabled = 
    process.env.NEXT_PUBLIC_DISABLE_AUTH === 'true' || 
    (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_SUPABASE_URL)

  useEffect(() => {
    if (authDisabled) {
      // Режим без авторизации - сразу устанавливаем mock-пользователя
      setSession(DEFAULT_MOCK_SESSION)
      setUser(DEFAULT_MOCK_USER)
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
      setSession(DEFAULT_MOCK_SESSION)
      setUser(DEFAULT_MOCK_USER)
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
      setSession(DEFAULT_MOCK_SESSION)
      setUser(DEFAULT_MOCK_USER)
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

    if (data.user && !data.session) {
      console.log("Email confirmation required for:", email)
    }
  }

  const signOut = async () => {
    if (authDisabled) {
      setSession(null)
      setUser(null)
      return
    }
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  const updateMockUser = (updates: Partial<User>) => {
    if (authDisabled || process.env.NODE_ENV === 'development') {
      const newUser = user ? { ...user, ...updates } : { ...DEFAULT_MOCK_USER, ...updates }
      setUser(newUser as User)
      setSession(prev => prev ? { ...prev, user: newUser as User } : { ...DEFAULT_MOCK_SESSION, user: newUser as User })
    }
  }

  const value = {
    user,
    session,
    loading,
    supabaseConfigured: !authDisabled,
    isMock: authDisabled,
    authDisabled,
    signIn,
    signUp,
    signOut,
    updateMockUser,
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
