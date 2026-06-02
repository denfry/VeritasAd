"use client"

import { useLanguage } from "@/contexts/language-context"

export function LanguageSwitcher() {
  const { locale, setLocale } = useLanguage()

  return (
    <div className="flex items-center gap-0.5 rounded-full border border-border/60 bg-background/70 p-0.5 backdrop-blur-sm">
      <button
        type="button"
        onClick={() => setLocale("ru")}
        className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider transition-all duration-150 ${
          locale === "ru"
            ? "bg-primary text-primary-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
        }`}
      >
        RU
      </button>
      <button
        type="button"
        onClick={() => setLocale("en")}
        className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider transition-all duration-150 ${
          locale === "en"
            ? "bg-primary text-primary-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
        }`}
      >
        EN
      </button>
    </div>
  )
}
