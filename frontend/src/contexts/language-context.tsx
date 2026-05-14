'use client'

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { ALL_LANGUAGES, getLanguageByCode, type Language } from '@/lib/languages'

const STORAGE_KEY = 'veritasad_selected_language'

interface LanguageContextValue {
  language: string
  currentLanguage: Language | undefined
  setLanguage: (code: string) => void
  allLanguages: Language[]
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined)

function loadSavedLanguage(): string {
  if (typeof window === 'undefined') return 'ru'
  try {
    return localStorage.getItem(STORAGE_KEY) || 'ru'
  } catch {
    return 'ru'
  }
}

function saveLanguage(code: string): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, code)
  } catch { /* ignore */ }
}

export function LanguageProvider({ children, initialLanguage }: { children: ReactNode; initialLanguage?: string }) {
  const [language, setLanguageState] = useState<string>(initialLanguage || loadSavedLanguage)

  const setLanguage = useCallback((code: string) => {
    if (!getLanguageByCode(code)) return
    setLanguageState(code)
    saveLanguage(code)
  }, [])

  const value: LanguageContextValue = {
    language,
    currentLanguage: getLanguageByCode(language),
    setLanguage,
    allLanguages: ALL_LANGUAGES,
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider')
  return ctx
}
