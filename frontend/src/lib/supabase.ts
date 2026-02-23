import { createClient } from "@supabase/supabase-js"
import { createMockClient, type MockSupabaseClient } from "./mock-auth"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Используем mock-клиент если не заданы переменные Supabase (для локальной разработки)
export const supabase =
  supabaseUrl && supabaseAnonKey
    ? (createClient(supabaseUrl, supabaseAnonKey) as unknown as MockSupabaseClient)
    : createMockClient()

export const isMockAuth = !(supabaseUrl && supabaseAnonKey)
