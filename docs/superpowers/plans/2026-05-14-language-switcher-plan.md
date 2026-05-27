# Language Switcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add language switcher for all ~150 currencies/languages + integration with settings and SiteHeader

**Architecture:** New `Language` data model (mapped from currencies) → `LanguageContext` provider → `LanguageSelector` component → integration in `SiteHeader` and Settings page. No i18n/translation, only switcher infrastructure.

**Tech Stack:** Next.js, React Context, TypeScript, Tailwind CSS

---

### Task 1: Language data model

**Files:**
- Create: `frontend/src/lib/languages.ts`

- [ ] **Step 1: Create languages.ts with ALL_LANGUAGES, POPULAR_LANGUAGES, getLanguageByCode**

```ts
export interface Language {
  code: string
  name: string
  nativeName: string
  flag: string
}

export const POPULAR_LANGUAGES: Language[] = [
  { code: 'ru', name: 'Russian', nativeName: 'Русский', flag: '🇷🇺' },
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', nativeName: '한국어', flag: '🇰🇷' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳' },
  { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', flag: '🇹🇷' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇧🇷' },
]

export const ALL_LANGUAGES: Language[] = [
  ...POPULAR_LANGUAGES,
  { code: 'af', name: 'Afrikaans', nativeName: 'Afrikaans', flag: '🇿🇦' },
  { code: 'am', name: 'Amharic', nativeName: 'አማርኛ', flag: '🇪🇹' },
  { code: 'az', name: 'Azerbaijani', nativeName: 'Azərbaycan dili', flag: '🇦🇿' },
  { code: 'be', name: 'Belarusian', nativeName: 'Беларуская', flag: '🇧🇾' },
  { code: 'bg', name: 'Bulgarian', nativeName: 'Български', flag: '🇧🇬' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: '🇧🇩' },
  { code: 'bs', name: 'Bosnian', nativeName: 'Bosanski', flag: '🇧🇦' },
  { code: 'ca', name: 'Catalan', nativeName: 'Català', flag: '🇪🇸' },
  { code: 'cs', name: 'Czech', nativeName: 'Čeština', flag: '🇨🇿' },
  { code: 'da', name: 'Danish', nativeName: 'Dansk', flag: '🇩🇰' },
  { code: 'dv', name: 'Divehi', nativeName: 'ދިވެހި', flag: '🇲🇻' },
  { code: 'el', name: 'Greek', nativeName: 'Ελληνικά', flag: '🇬🇷' },
  { code: 'et', name: 'Estonian', nativeName: 'Eesti', flag: '🇪🇪' },
  { code: 'fa', name: 'Persian', nativeName: 'فارسی', flag: '🇮🇷' },
  { code: 'fi', name: 'Finnish', nativeName: 'Suomi', flag: '🇫🇮' },
  { code: 'fj', name: 'Fijian', nativeName: 'Na vosa vaka-Viti', flag: '🇫🇯' },
  { code: 'ga', name: 'Irish', nativeName: 'Gaeilge', flag: '🇮🇪' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'he', name: 'Hebrew', nativeName: 'עברית', flag: '🇮🇱' },
  { code: 'hr', name: 'Croatian', nativeName: 'Hrvatski', flag: '🇭🇷' },
  { code: 'ht', name: 'Haitian Creole', nativeName: 'Kreyòl ayisyen', flag: '🇭🇹' },
  { code: 'hu', name: 'Hungarian', nativeName: 'Magyar', flag: '🇭🇺' },
  { code: 'hy', name: 'Armenian', nativeName: 'Հայերեն', flag: '🇦🇲' },
  { code: 'id', name: 'Indonesian', nativeName: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'is', name: 'Icelandic', nativeName: 'Íslenska', flag: '🇮🇸' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹' },
  { code: 'ka', name: 'Georgian', nativeName: 'ქართული', flag: '🇬🇪' },
  { code: 'kk', name: 'Kazakh', nativeName: 'Қазақша', flag: '🇰🇿' },
  { code: 'km', name: 'Khmer', nativeName: 'ភាសាខ្មែរ', flag: '🇰🇭' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'ku', name: 'Kurdish', nativeName: 'Kurdî', flag: '🇹🇷' },
  { code: 'ky', name: 'Kyrgyz', nativeName: 'Кыргызча', flag: '🇰🇬' },
  { code: 'lb', name: 'Luxembourgish', nativeName: 'Lëtzebuergesch', flag: '🇱🇺' },
  { code: 'lo', name: 'Lao', nativeName: 'ລາວ', flag: '🇱🇦' },
  { code: 'lt', name: 'Lithuanian', nativeName: 'Lietuvių', flag: '🇱🇹' },
  { code: 'lv', name: 'Latvian', nativeName: 'Latviešu', flag: '🇱🇻' },
  { code: 'mg', name: 'Malagasy', nativeName: 'Malagasy', flag: '🇲🇬' },
  { code: 'mk', name: 'Macedonian', nativeName: 'Македонски', flag: '🇲🇰' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', flag: '🇮🇳' },
  { code: 'mn', name: 'Mongolian', nativeName: 'Монгол', flag: '🇲🇳' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳' },
  { code: 'ms', name: 'Malay', nativeName: 'Bahasa Melayu', flag: '🇲🇾' },
  { code: 'mt', name: 'Maltese', nativeName: 'Malti', flag: '🇲🇹' },
  { code: 'my', name: 'Burmese', nativeName: 'မြန်မာဘာသာ', flag: '🇲🇲' },
  { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', flag: '🇳🇵' },
  { code: 'nl', name: 'Dutch', nativeName: 'Nederlands', flag: '🇳🇱' },
  { code: 'no', name: 'Norwegian', nativeName: 'Norsk', flag: '🇳🇴' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  { code: 'pl', name: 'Polish', nativeName: 'Polski', flag: '🇵🇱' },
  { code: 'ps', name: 'Pashto', nativeName: 'پښتو', flag: '🇦🇫' },
  { code: 'ro', name: 'Romanian', nativeName: 'Română', flag: '🇷🇴' },
  { code: 'rw', name: 'Kinyarwanda', nativeName: 'Ikinyarwanda', flag: '🇷🇼' },
  { code: 'sd', name: 'Sindhi', nativeName: 'سنڌي', flag: '🇮🇳' },
  { code: 'si', name: 'Sinhala', nativeName: 'සිංහල', flag: '🇱🇰' },
  { code: 'sk', name: 'Slovak', nativeName: 'Slovenčina', flag: '🇸🇰' },
  { code: 'sl', name: 'Slovenian', nativeName: 'Slovenščina', flag: '🇸🇮' },
  { code: 'sm', name: 'Samoan', nativeName: 'Gagana Samoa', flag: '🇼🇸' },
  { code: 'sn', name: 'Shona', nativeName: 'chiShona', flag: '🇿🇼' },
  { code: 'so', name: 'Somali', nativeName: 'Soomaali', flag: '🇸🇴' },
  { code: 'sq', name: 'Albanian', nativeName: 'Shqip', flag: '🇦🇱' },
  { code: 'sr', name: 'Serbian', nativeName: 'Српски', flag: '🇷🇸' },
  { code: 'sv', name: 'Swedish', nativeName: 'Svenska', flag: '🇸🇪' },
  { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', flag: '🇹🇿' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', flag: '🇮🇳' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳' },
  { code: 'tg', name: 'Tajik', nativeName: 'Тоҷикӣ', flag: '🇹🇯' },
  { code: 'th', name: 'Thai', nativeName: 'ไทย', flag: '🇹🇭' },
  { code: 'ti', name: 'Tigrinya', nativeName: 'ትግርኛ', flag: '🇪🇷' },
  { code: 'tk', name: 'Turkmen', nativeName: 'Türkmen', flag: '🇹🇲' },
  { code: 'tn', name: 'Tswana', nativeName: 'Setswana', flag: '🇧🇼' },
  { code: 'to', name: 'Tongan', nativeName: 'Lea Faka-Tonga', flag: '🇹🇴' },
  { code: 'uk', name: 'Ukrainian', nativeName: 'Українська', flag: '🇺🇦' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', flag: '🇵🇰' },
  { code: 'uz', name: 'Uzbek', nativeName: "O'zbek", flag: '🇺🇿' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'xh', name: 'Xhosa', nativeName: 'isiXhosa', flag: '🇿🇦' },
  { code: 'yo', name: 'Yoruba', nativeName: 'Yorùbá', flag: '🇳🇬' },
  { code: 'zu', name: 'Zulu', nativeName: 'isiZulu', flag: '🇿🇦' },
]

export function getLanguageByCode(code: string): Language | undefined {
  return ALL_LANGUAGES.find(l => l.code === code)
}

export function getFlagUrl(languageCode: string): string {
  const mapping: Record<string, string> = {
    'en': 'us', 'zh': 'cn', 'ja': 'jp', 'ko': 'kr', 'ar': 'sa',
    'hi': 'in', 'pt': 'br', 'ms': 'my', 'bn': 'bd', 'ur': 'pk',
    'ta': 'in', 'te': 'in', 'mr': 'in', 'gu': 'in', 'kn': 'in',
    'ml': 'in', 'pa': 'in', 'sd': 'in', 'ne': 'np', 'si': 'lk',
    'km': 'kh', 'lo': 'la', 'my': 'mm', 'ka': 'ge', 'hy': 'am',
    'kk': 'kz', 'ky': 'kg', 'uz': 'uz', 'tk': 'tm', 'tg': 'tj',
    'az': 'az', 'be': 'by', 'uk': 'ua', 'ro': 'ro', 'bg': 'bg',
    'sr': 'rs', 'hr': 'hr', 'sl': 'si', 'sk': 'sk', 'cs': 'cz',
    'pl': 'pl', 'hu': 'hu', 'et': 'ee', 'lv': 'lv', 'lt': 'lt',
    'sq': 'al', 'mk': 'mk', 'bs': 'ba', 'mt': 'mt', 'is': 'is',
    'da': 'dk', 'no': 'no', 'sv': 'se', 'fi': 'fi', 'nl': 'nl',
    'af': 'za', 'xh': 'za', 'zu': 'za', 'sn': 'zw', 'rw': 'rw',
    'mg': 'mg', 'so': 'so', 'am': 'et', 'ti': 'er', 'dz': 'bt',
    'sm': 'ws', 'to': 'to', 'fj': 'fj', 'dv': 'mv', 'ps': 'af',
    'fa': 'ir', 'ku': 'tr', 'he': 'il', 'el': 'gr', 'ca': 'es',
    'eu': 'es', 'gl': 'es', 'sw': 'tz', 'yo': 'ng', 'ht': 'ht',
    'lb': 'lu', 'mt': 'mt', 'mn': 'mn',
  }
  const country = mapping[languageCode] || languageCode
  return `https://purecatamphetamine.github.io/country-flag-icons/3x2/${country.toUpperCase()}.svg`
}
```

- [ ] **Step 2: Verify file reads correctly**

Run: `cd frontend && npx tsc --noEmit src/lib/languages.ts`
Expected: No type errors (will warn about isolatedModules but no structural errors)

---

### Task 2: LanguageContext + Provider

**Files:**
- Create: `frontend/src/contexts/language-context.tsx`
- Modify: `frontend/src/app/providers.tsx`

- [ ] **Step 1: Create language-context.tsx**

```tsx
'use client'

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
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
```

- [ ] **Step 2: Add LanguageProvider to providers.tsx**

Read `frontend/src/app/providers.tsx` first:

```bash
cat frontend/src/app/providers.tsx
```

Add `LanguageProvider` import and wrap in the tree:

```tsx
import { LanguageProvider } from "@/contexts/language-context"

// Inside the provider tree, wrap children
<LanguageProvider>
  <CurrencyProvider>
    {children}
  </CurrencyProvider>
</LanguageProvider>
```

- [ ] **Step 3: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No type errors

---

### Task 3: LanguageSelector Component

**Files:**
- Create: `frontend/src/components/LanguageSelector.tsx`

- [ ] **Step 1: Create LanguageSelector.tsx**

```tsx
'use client'

import { useState, useMemo, useRef, useEffect } from 'react'
import { ChevronDown, Search, X, Globe } from 'lucide-react'
import { ALL_LANGUAGES, POPULAR_LANGUAGES, getLanguageByCode, getFlagUrl, type Language } from '@/lib/languages'

interface LanguageSelectorProps {
  selectedLanguage: string
  onLanguageChange: (code: string) => void
}

export function LanguageSelector({ selectedLanguage, onLanguageChange }: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsOpen(false)
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  const filteredLanguages = useMemo(() => {
    if (!searchQuery.trim()) return ALL_LANGUAGES
    const query = searchQuery.toLowerCase().trim()
    return ALL_LANGUAGES.filter(
      (lang) =>
        lang.code.toLowerCase().includes(query) ||
        lang.name.toLowerCase().includes(query) ||
        lang.nativeName.toLowerCase().includes(query)
    )
  }, [searchQuery])

  const selectedLanguageData = getLanguageByCode(selectedLanguage)

  const handleSelect = (lang: Language) => {
    onLanguageChange(lang.code)
    setIsOpen(false)
    setSearchQuery('')
  }

  return (
    <div ref={containerRef} className="relative inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-3 px-3.5 py-2 rounded-xl border border-border bg-card/50 backdrop-blur-md hover:bg-accent hover:border-accent transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20 shadow-sm"
        aria-label="Select language"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2">
          <img
            src={getFlagUrl(selectedLanguage)}
            alt=""
            className="w-5 h-3.5 object-cover rounded-[2px] shadow-[0_0_0_1px_rgba(0,0,0,0.1)]"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none'
              const sibling = (e.target as HTMLImageElement).nextElementSibling
              if (sibling) (sibling as HTMLElement).style.display = 'block'
            }}
          />
          <span className="hidden text-base leading-none" style={{ display: 'none' }}>{selectedLanguageData?.flag}</span>
          <span className="font-bold text-sm tracking-tight">{selectedLanguageData?.code?.toUpperCase()}</span>
        </div>
        <ChevronDown
          className={`h-3.5 w-3.5 text-muted-foreground transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 z-50 mt-3 w-72 max-h-[400px] rounded-2xl border border-border bg-popover/95 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200">
          <div className="p-3 border-b border-border/50">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/50" />
              <input
                type="text"
                placeholder="Search language..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-8 py-2 text-sm rounded-lg border border-border bg-background/50 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                autoFocus
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  type="button"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-border">
            {!searchQuery && (
              <div>
                <div className="px-4 py-2 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-[0.1em]">
                  Popular
                </div>
                <div className="grid grid-cols-2 gap-1 p-1 px-2 mb-2">
                  {POPULAR_LANGUAGES.slice(0, 6).map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => handleSelect(lang)}
                      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-accent transition-all ${
                        lang.code === selectedLanguage ? 'bg-primary/10 text-primary' : 'text-foreground/80'
                      }`}
                    >
                      <img src={getFlagUrl(lang.code)} alt="" className="w-5 h-3.5 rounded-[1px] object-cover" />
                      <span className="text-xs font-bold">{lang.code.toUpperCase()}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div>
              {!searchQuery && (
                <div className="px-4 py-2 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-[0.1em] border-t border-border/50">
                  All Languages
                </div>
              )}
              {filteredLanguages.length > 0 ? (
                <div className="p-1 px-2">
                  {filteredLanguages.map((lang) => (
                    <LanguageItem
                      key={lang.code}
                      language={lang}
                      isSelected={lang.code === selectedLanguage}
                      onSelect={() => handleSelect(lang)}
                    />
                  ))}
                </div>
              ) : (
                <div className="px-4 py-12 text-center">
                  <p className="text-sm font-medium text-muted-foreground">No matches found</p>
                  <p className="text-xs text-muted-foreground/50 mt-1">Try searching for a code or name</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

interface LanguageItemProps {
  language: Language
  isSelected: boolean
  onSelect: () => void
}

function LanguageItem({ language, isSelected, onSelect }: LanguageItemProps) {
  return (
    <button
      onClick={onSelect}
      className={`group w-full px-3 py-2.5 flex items-center gap-3 rounded-lg transition-all ${
        isSelected ? 'bg-primary/5' : 'hover:bg-accent/50'
      }`}
    >
      <div className="relative">
        <img
          src={getFlagUrl(language.code)}
          alt=""
          className="w-6 h-4 rounded-[2px] object-cover shadow-sm group-hover:scale-110 transition-transform"
        />
      </div>
      <div className="flex-1 text-left min-w-0">
        <div className="flex items-center gap-2">
          <span className={`font-bold text-xs ${isSelected ? 'text-primary' : 'text-foreground'}`}>
            {language.code.toUpperCase()}
          </span>
          <span className="text-[10px] text-muted-foreground/50 font-medium truncate">
            {language.nativeName}
          </span>
        </div>
        <div className="text-[10px] text-muted-foreground/40">{language.name}</div>
      </div>
      <span className="text-[10px] font-medium text-muted-foreground/50 group-hover:text-foreground transition-colors">
        {language.flag}
      </span>
    </button>
  )
}
```

- [ ] **Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No type errors

---

### Task 4: Integrate LanguageSelector in SiteHeader

**Files:**
- Read: `frontend/src/components/SiteHeader.tsx`
- Modify: `frontend/src/components/SiteHeader.tsx`

- [ ] **Step 1: Read SiteHeader.tsx**

```bash
cat frontend/src/components/SiteHeader.tsx
```

- [ ] **Step 2: Add import and LanguageSelector next to CurrencySelector**

Add imports:
```tsx
import { LanguageSelector } from "@/components/LanguageSelector"
import { useLanguage } from "@/contexts/language-context"
```

Add inside the component:
```tsx
const { language, setLanguage } = useLanguage()
```

Find the CurrencySelector usage in the JSX and add LanguageSelector before or after it:
```tsx
<LanguageSelector selectedLanguage={language} onLanguageChange={setLanguage} />
```

- [ ] **Step 3: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No type errors

---

### Task 5: Update Settings Page languages

**Files:**
- Modify: `frontend/src/app/(app)/dashboard/settings/page.tsx`

- [ ] **Step 1: Read and update Settings page**

Read the settings page:
```bash
cat "frontend/src/app/(app)/dashboard/settings/page.tsx" | head -40
```

Add import:
```tsx
import { ALL_LANGUAGES } from "@/lib/languages"
```

Replace hardcoded languages array:
```tsx
// Old:
const languages = [
  { id: "en", label: "English" },
  { id: "zh", label: "中文" },
  { id: "es", label: "Español" },
  { id: "fr", label: "Français" },
]

// New:
const languages = ALL_LANGUAGES.map(l => ({ id: l.code, label: l.nativeName, name: l.name }))
```

Update the grid display to show name in English subtitle:
```tsx
{languages.map((l) => (
  <button
    key={l.id}
    onClick={() => handleLanguageChange(l.id)}
    className={cn(
      "flex flex-col items-center justify-center gap-1 rounded-xl border px-4 py-3 text-sm font-medium transition-all",
      language === l.id
        ? "border-primary bg-primary/10 text-primary"
        : "border-border bg-transparent text-muted-foreground hover:bg-muted/50"
    )}
  >
    <Globe className="h-4 w-4" />
    <span>{l.label}</span>
    <span className="text-[10px] text-muted-foreground/50">{l.name}</span>
  </button>
))}
```

- [ ] **Step 2: Verify compilation**

Run: `cd frontend && npx tsc --noEmit`
Expected: No type errors

---

### Task 6: Commit

- [ ] **Step 1: Stage and commit**

```bash
cd frontend
git add src/lib/languages.ts src/contexts/language-context.tsx src/components/LanguageSelector.tsx src/components/SiteHeader.tsx "src/app/(app)/dashboard/settings/page.tsx" src/app/providers.tsx
git commit -m "feat: add language switcher with ~150 languages mapped from currencies"
```
