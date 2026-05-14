'use client'

import { useState, useMemo, useRef, useEffect } from 'react'
import { ChevronDown, Search, X } from 'lucide-react'
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
