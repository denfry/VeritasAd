import { createClient } from "@supabase/supabase-js"
import { createMockClient, type MockSupabaseClient } from "./mock-auth"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
const authDisabled = process.env.NEXT_PUBLIC_DISABLE_AUTH === "true"

const isProduction = process.env.NODE_ENV === "production"
const shouldUseMockAuth = authDisabled || !(supabaseUrl && supabaseAnonKey)

// Missing Supabase is only acceptable in explicit self-hosted MVP mode.
if (isProduction && !authDisabled && (!supabaseUrl || !supabaseAnonKey)) {
  console.error("Supabase configuration is missing in production environment!")
  if (typeof window !== "undefined") {
    throw new Error(
      "Missing Supabase environment variables. Set NEXT_PUBLIC_DISABLE_AUTH=true for self-hosted MVP mode."
    )
  }
}

export const supabase = !shouldUseMockAuth
  ? (createClient(supabaseUrl, supabaseAnonKey) as unknown as MockSupabaseClient)
  : createMockClient()

export const isMockAuth = shouldUseMockAuth
