"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import en from "@/lib/i18n/en"
import ru from "@/lib/i18n/ru"
import type { Translations } from "@/lib/i18n/en"

type Locale = "en" | "ru"

interface LanguageContextValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: Translations
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

const translations: Record<Locale, Translations> = { en, ru }

const STORAGE_KEY = "veritasad-locale"

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("ru")

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as Locale | null
    if (saved === "en" || saved === "ru") {
      setLocaleState(saved)
    }
  }, [])

  const setLocale = (next: Locale) => {
    setLocaleState(next)
    localStorage.setItem(STORAGE_KEY, next)
  }

  return (
    <LanguageContext.Provider value={{ locale, setLocale, t: translations[locale] }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider")
  return ctx
}
