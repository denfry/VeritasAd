'use client'

import { useState, useMemo, useRef, useEffect } from 'react'
import { ChevronDown, Search, X } from 'lucide-react'
import { ALL_CURRENCIES, POPULAR_CURRENCIES, Currency, getFlagUrl } from '@/lib/currency'

interface CurrencySelectorProps {
  selectedCurrency: string
  onCurrencyChange: (currency: string) => void
}

export function CurrencySelector({ selectedCurrency, onCurrencyChange }: CurrencySelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close on Escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  // Filter currencies based on search
  const filteredCurrencies = useMemo(() => {
    if (!searchQuery.trim()) {
      return ALL_CURRENCIES
    }

    const query = searchQuery.toLowerCase().trim()
    return ALL_CURRENCIES.filter(
      (currency) =>
        currency.code.toLowerCase().includes(query) ||
        currency.name.toLowerCase().includes(query) ||
        currency.symbol.toLowerCase().includes(query)
    )
  }, [searchQuery])

  // Get selected currency data
  const selectedCurrencyData = ALL_CURRENCIES.find((c) => c.code === selectedCurrency)

  // Handle currency selection
  const handleSelect = (currency: Currency) => {
    onCurrencyChange(currency.code)
    setIsOpen(false)
    setSearchQuery('')
  }

  return (
    <div ref={containerRef} className="relative inline-block">
      {/* Selector Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-3 px-3.5 py-2 rounded-xl border border-border bg-card/50 backdrop-blur-md hover:bg-accent hover:border-accent transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20 shadow-sm"
        aria-label="Select currency"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2">
           <img 
             src={getFlagUrl(selectedCurrency)} 
             alt="" 
             className="w-5 h-3.5 object-cover rounded-[2px] shadow-[0_0_0_1px_rgba(0,0,0,0.1)]"
             onError={(e) => {
               (e.target as HTMLImageElement).style.display = 'none';
               const sibling = (e.target as HTMLImageElement).nextElementSibling;
               if (sibling) (sibling as HTMLElement).style.display = 'block';
             }}
           />
           <span className="hidden text-base leading-none" style={{ display: 'none' }}>{selectedCurrencyData?.flag}</span>
           <span className="font-bold text-sm tracking-tight">{selectedCurrencyData?.code}</span>
        </div>
        <div className="w-[1px] h-3 bg-border mx-0.5" />
        <span className="text-muted-foreground font-mono text-xs">{selectedCurrencyData?.symbol}</span>
        <ChevronDown
          className={`h-3.5 w-3.5 text-muted-foreground transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 z-50 mt-3 w-72 max-h-[400px] rounded-2xl border border-border bg-popover/95 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200">
          {/* Search Input */}
          <div className="p-3 border-b border-border/50">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/50" />
              <input
                type="text"
                placeholder="Search currency..."
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

          {/* Currency List */}
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-border">
            {/* Popular Currencies Section */}
            {!searchQuery && (
              <div>
                <div className="px-4 py-2 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-[0.1em]">
                  Popular
                </div>
                <div className="grid grid-cols-2 gap-1 p-1 px-2 mb-2">
                  {POPULAR_CURRENCIES.slice(0, 6).map((currency) => (
                    <button
                      key={currency.code}
                      onClick={() => handleSelect(currency)}
                      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-accent transition-all ${
                        currency.code === selectedCurrency ? 'bg-primary/10 text-primary' : 'text-foreground/80'
                      }`}
                    >
                      <img src={getFlagUrl(currency.code)} alt="" className="w-5 h-3.5 rounded-[1px] object-cover" />
                      <span className="text-xs font-bold">{currency.code}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* All Currencies Section */}
            <div>
              {!searchQuery && (
                <div className="px-4 py-2 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-[0.1em] border-t border-border/50">
                  All Currencies
                </div>
              )}
              {filteredCurrencies.length > 0 ? (
                <div className="p-1 px-2">
                  {filteredCurrencies
                    .map((currency) => (
                      <CurrencyItem
                        key={currency.code}
                        currency={currency}
                        isSelected={currency.code === selectedCurrency}
                        onSelect={() => handleSelect(currency)}
                      />
                    ))
                  }
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

interface CurrencyItemProps {
  currency: Currency
  isSelected: boolean
  onSelect: () => void
}

function CurrencyItem({ currency, isSelected, onSelect }: CurrencyItemProps) {
  return (
    <button
      onClick={onSelect}
      className={`group w-full px-3 py-2.5 flex items-center gap-3 rounded-lg transition-all ${
        isSelected ? 'bg-primary/5' : 'hover:bg-accent/50'
      }`}
    >
      <div className="relative">
        <img 
          src={getFlagUrl(currency.code)} 
          alt="" 
          className="w-6 h-4 rounded-[2px] object-cover shadow-sm group-hover:scale-110 transition-transform" 
        />
      </div>
      <div className="flex-1 text-left min-w-0">
        <div className="flex items-center gap-2">
          <span className={`font-bold text-xs ${isSelected ? 'text-primary' : 'text-foreground'}`}>
            {currency.code}
          </span>
          <span className="text-[10px] text-muted-foreground/50 font-medium truncate">
            {currency.name}
          </span>
        </div>
      </div>
      <span className="text-xs font-mono font-medium text-muted-foreground/70 group-hover:text-foreground transition-colors">
        {currency.symbol}
      </span>
    </button>
  )
}
