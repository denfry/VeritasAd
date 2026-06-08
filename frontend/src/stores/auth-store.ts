"use client"

import { create } from "zustand"
import type { MockUser, MockSession } from "@/lib/mock-auth"

type User = MockUser
type Session = MockSession

/**
 * Global auth state store (Zustand), per thesis sec. 3.3.
 *
 * The `AuthProvider` (React Context) remains the single source of auth side
 * effects (Supabase listeners, sign in/out), and pushes its resolved state
 * into this store via `setAuth`. Any component can then read user/session/token
 * directly from the store without prop-drilling or context nesting.
 */
type AuthState = {
  user: User | null
  session: Session | null
  loading: boolean
  setAuth: (next: { user: User | null; session: Session | null }) => void
  setLoading: (loading: boolean) => void
  reset: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  session: null,
  loading: true,
  setAuth: ({ user, session }) => set({ user, session, loading: false }),
  setLoading: (loading) => set({ loading }),
  reset: () => set({ user: null, session: null, loading: false }),
}))

/** Convenience selector for the current access token. */
export const useAccessToken = () =>
  useAuthStore((s) => s.session?.access_token ?? null)
