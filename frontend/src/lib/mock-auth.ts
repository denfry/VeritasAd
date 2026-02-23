/**
 * Mock Supabase client для локальной разработки
 * Хранит данные в localStorage, генерирует JWT токены для совместимости с backend
 */

const STORAGE_KEY = "mock_supabase_auth"

// JWT secret должен совпадать с JWT_SECRET_KEY в backend/.env
const JWT_SECRET = "dev-jwt-secret-key-for-local-development-only-this-is-long-enough-for-security-purposes-min-64-chars"

export interface MockUser {
  id: string
  email: string
  created_at: string
  role?: string
  plan?: string
}

export interface MockSession {
  user: MockUser
  access_token: string
  refresh_token: string
  expires_at: number
}

export interface MockAuthData {
  session: MockSession | null
  users: MockUser[]
}

function getAuthData(): MockAuthData {
  if (typeof window === "undefined") {
    return { session: null, users: [] }
  }
  const data = localStorage.getItem(STORAGE_KEY)
  return data ? JSON.parse(data) : { session: null, users: [] }
}

function saveAuthData(data: MockAuthData): void {
  if (typeof window === "undefined") return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

function generateId(): string {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

function generateToken(): string {
  return `token_${Date.now()}_${Math.random().toString(36).substr(2, 32)}`
}

/**
 * Простая Base64URL кодировка для JWT
 */
function base64UrlEncode(data: string): string {
  return btoa(data)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
}

/**
 * Генерирует JWT токен для mock-аутентификации
 * Формат: header.payload.signature (все в base64url)
 */
async function generateJwtToken(user: MockUser, expiresInHours: number = 1): Promise<string> {
  const header = {
    alg: 'HS256',
    typ: 'JWT'
  }

  const now = Math.floor(Date.now() / 1000)
  const payload = {
    sub: user.id,
    email: user.email,
    iat: now,
    exp: now + (expiresInHours * 3600),
    type: 'access'
  }

  const headerEncoded = base64UrlEncode(JSON.stringify(header))
  const payloadEncoded = base64UrlEncode(JSON.stringify(payload))

  // Для простоты используем mock-подпись (backend в dev-режиме принимает любые токены)
  // В реальной реализации нужно использовать crypto.subtle для HMAC-SHA256
  const mockSignature = base64UrlEncode('mock_signature_' + Date.now())

  return `${headerEncoded}.${payloadEncoded}.${mockSignature}`
}

export class MockSupabaseClient {
  auth = {
    getSession: async (): Promise<{ data: { session: MockSession | null }; error: null }> => {
      const data = getAuthData()
      if (data.session && data.session.expires_at < Date.now()) {
        // Session expired
        data.session = null
        saveAuthData(data)
      }
      return { data: { session: data.session }, error: null }
    },

    signUp: async ({
      email,
      password,
    }: {
      email: string
      password: string
      options?: { emailRedirectTo?: string }
    }): Promise<{
      data: { user: MockUser | null; session: MockSession | null }
      error: { message: string } | null
    }> => {
      const authData = getAuthData()

      // Check if user already exists
      const existingUser = authData.users.find((u) => u.email === email)
      if (existingUser) {
        return {
          data: { user: null, session: null },
          error: { message: "User already registered" },
        }
      }

      // Create new user (auto-confirm for local dev)
      const newUser: MockUser = {
        id: generateId(),
        email,
        created_at: new Date().toISOString(),
      }

      authData.users.push(newUser)

      // Create session with JWT token (auto-login after signup for local dev)
      const expiresAt = Date.now() + 3600 * 1000 // 1 hour
      const accessToken = await generateJwtToken(newUser, 1)
      const newSession: MockSession = {
        user: newUser,
        access_token: accessToken,
        refresh_token: generateToken(),
        expires_at: expiresAt,
      }

      authData.session = newSession
      saveAuthData(authData)

      return {
        data: { user: newUser, session: newSession },
        error: null,
      }
    },

    signInWithPassword: async ({
      email,
      password,
    }: {
      email: string
      password: string
    }): Promise<{
      data: { user: MockUser | null; session: MockSession | null }
      error: { message: string } | null
    }> => {
      const authData = getAuthData()

      // For mock auth, we accept any password and create user if not exists
      let user = authData.users.find((u) => u.email === email)

      if (!user) {
        // Auto-create user for convenience in local dev
        user = {
          id: generateId(),
          email,
          created_at: new Date().toISOString(),
        }
        authData.users.push(user)
      }

      const expiresAt = Date.now() + 3600 * 1000 // 1 hour
      const accessToken = await generateJwtToken(user, 1)
      const session: MockSession = {
        user,
        access_token: accessToken,
        refresh_token: generateToken(),
        expires_at: expiresAt,
      }

      authData.session = session
      saveAuthData(authData)

      return {
        data: { user, session },
        error: null,
      }
    },

    signOut: async (): Promise<{ error: null }> => {
      const authData = getAuthData()
      authData.session = null
      saveAuthData(authData)
      return { error: null }
    },

    onAuthStateChange: (
      callback: (event: string, session: MockSession | null) => void
    ): { subscription: { unsubscribe: () => void } } => {
      // Для mock-режима просто возвращаем no-op subscription
      // В реальном использовании можно слушать storage events для синхронизации между табами
      return {
        subscription: {
          unsubscribe: () => {},
        },
      }
    },

    updateUser: async (
      attributes: { email?: string; password?: string }
    ): Promise<{
      data: { user: MockUser }
      error: { message: string } | null
    }> => {
      const authData = getAuthData()
      if (!authData.session) {
        return {
          data: { user: { id: "", email: "", created_at: "" } },
          error: { message: "Not authenticated" },
        }
      }

      if (attributes.email) {
        authData.session.user.email = attributes.email
      }

      saveAuthData(authData)

      return {
        data: { user: authData.session.user },
        error: null,
      }
    },
  }
}

// Экспорт для совместимости с существующим кодом
export const createMockClient = (): MockSupabaseClient => {
  return new MockSupabaseClient()
}
