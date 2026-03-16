import { createClient } from "@supabase/supabase-js"
import { createMockClient, type MockSupabaseClient } from "./mock-auth"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

const isProduction = process.env.NODE_ENV === "production"

// В продакшене обязательно наличие конфигурации Supabase
if (isProduction && (!supabaseUrl || !supabaseAnonKey)) {
  console.error("Supabase configuration is missing in production environment!")
  // В рантайме бросаем ошибку, если это не серверный билд (где env может быть пустым при сборке, но не при запуске)
  if (typeof window !== "undefined") {
    throw new Error("Missing Supabase environment variables")
  }
}

// Используем mock-клиент если не заданы переменные Supabase (только для разработки/тестов)
export const supabase =
  supabaseUrl && supabaseAnonKey
    ? (createClient(supabaseUrl, supabaseAnonKey) as unknown as MockSupabaseClient)
    : createMockClient()

export const isMockAuth = !(supabaseUrl && supabaseAnonKey)
