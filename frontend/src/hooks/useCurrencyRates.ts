'use client'

import { useState, useEffect, useCallback } from 'react'
import { BASE_CURRENCY, ALL_CURRENCIES, getCurrencyByCode } from '@/lib/currency'

const FRANKFURTER_API = 'https://api.frankfurter.dev/v1'
const CACHE_KEY = 'veritasad_currency_rates'
const CACHE_DURATION = 60 * 60 * 1000 // 1 hour in milliseconds
const SELECTED_CURRENCY_KEY = 'veritasad_selected_currency'

export interface ExchangeRates {
  [currency: string]: number
}

export interface RatesData {
  rates: ExchangeRates
  timestamp: number
  base: string
}

/**
 * Get cached rates from localStorage
 */
function getCachedRates(): RatesData | null {
  if (typeof window === 'undefined') return null
  
  try {
    const cached = localStorage.getItem(CACHE_KEY)
    if (!cached) return null
    
    const data: RatesData = JSON.parse(cached)
    const now = Date.now()
    
    // Check if cache is still valid
    if (now - data.timestamp < CACHE_DURATION) {
      return data
    }
    
    // Cache expired
    localStorage.removeItem(CACHE_KEY)
    return null
  } catch {
    return null
  }
}

/**
 * Save rates to localStorage cache
 */
function saveRatesCache(rates: ExchangeRates): void {
  if (typeof window === 'undefined') return
  
  try {
    const data: RatesData = {
      rates,
      timestamp: Date.now(),
      base: BASE_CURRENCY,
    }
    localStorage.setItem(CACHE_KEY, JSON.stringify(data))
  } catch (error) {
    console.error('Failed to cache currency rates:', error)
  }
}

/**
 * Get selected currency from localStorage
 */
function getSelectedCurrency(): string {
  if (typeof window === 'undefined') return BASE_CURRENCY
  
  try {
    const saved = localStorage.getItem(SELECTED_CURRENCY_KEY)
    if (saved && getCurrencyByCode(saved)) {
      return saved
    }
  } catch {
    // Ignore errors
  }
  
  return BASE_CURRENCY
}

/**
 * Save selected currency to localStorage
 */
function saveSelectedCurrency(currency: string): void {
  if (typeof window === 'undefined') return
  
  try {
    localStorage.setItem(SELECTED_CURRENCY_KEY, currency)
  } catch (error) {
    console.error('Failed to save selected currency:', error)
  }
}

/**
 * Fetch exchange rates with fallback mechanism
 */
async function fetchExchangeRates(): Promise<ExchangeRates> {
  // Try cache first
  const cached = getCachedRates()
  if (cached) {
    return cached.rates
  }

  // List of APIs to try in order
  const apis = [
    // 1. ExchangeRate-API (Free, no key needed for some endpoints, very reliable)
    async () => {
      const resp = await fetch('https://open.er-api.com/v6/latest/RUB')
      if (!resp.ok) throw new Error('ER-API failed')
      const data = await resp.json()
      if (data.result === 'success') return data.rates
      throw new Error('ER-API returned error')
    },
    // 2. Frankfurter (Backup)
    async () => {
      const resp = await fetch(`${FRANKFURTER_API}/latest?base=USD`)
      if (!resp.ok) throw new Error('Frankfurter failed')
      const data = await resp.json()
      const usdRates = data.rates
      const rubPerUsd = usdRates.RUB || 90
      
      const rates: ExchangeRates = { RUB: 1 }
      for (const [curr, val] of Object.entries(usdRates)) {
        rates[curr] = (val as number) / rubPerUsd
      }
      rates['USD'] = 1 / rubPerUsd
      return rates
    }
  ]

  for (const api of apis) {
    try {
      const rates = await api()
      saveRatesCache(rates)
      return rates
    } catch (e) {
      console.warn(`Currency API failed: ${e instanceof Error ? e.message : 'Unknown error'}`)
      continue
    }
  }

  // Last resort: Fallback rates
  return getFallbackRates()
}

/**
 * Fallback rates when API is unavailable
 * These are approximate and should only be used as last resort
 */
function getFallbackRates(): ExchangeRates {
  return {
    USD: 0.011,
    EUR: 0.010,
    GBP: 0.0087,
    CNY: 0.079,
    JPY: 1.62,
    KRW: 15.2,
    KZT: 5.1,
    BYN: 0.036,
    UAH: 0.45,
    TRY: 0.38,
    INR: 0.92,
    BRL: 0.063,
    CAD: 0.015,
    AUD: 0.017,
    CHF: 0.0097,
    PLN: 0.044,
    SEK: 0.11,
    NOK: 0.12,
    DKK: 0.075,
    RUB: 1, // Base currency
  }
}

/**
 * Hook for managing currency rates and conversion
 */
export function useCurrencyRates() {
  const [rates, setRates] = useState<ExchangeRates>({})
  const [selectedCurrency, setSelectedCurrencyState] = useState<string>(BASE_CURRENCY)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize selected currency from localStorage
  useEffect(() => {
    setSelectedCurrencyState(getSelectedCurrency())
  }, [])

  // Fetch exchange rates on mount
  useEffect(() => {
    let mounted = true

    const loadRates = async () => {
      try {
        setLoading(true)
        const fetchedRates = await fetchExchangeRates()
        
        if (mounted) {
          setRates(fetchedRates)
          setError(null)
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load rates')
          // Use fallback rates
          setRates(getFallbackRates())
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadRates()

    return () => {
      mounted = false
    }
  }, [])

  /**
   * Convert amount from base currency (RUB) to selected currency
   */
  const convert = useCallback((amountRub: number, targetCurrency?: string): number => {
    const currency = targetCurrency || selectedCurrency
    const rate = rates[currency]
    
    if (!rate) {
      // If rate not found, return original amount
      return amountRub
    }
    
    return amountRub * rate
  }, [rates, selectedCurrency])

  /**
   * Convert amount from any currency to base currency (RUB)
   */
  const convertToBase = useCallback((amount: number, fromCurrency: string): number => {
    const rate = rates[fromCurrency]
    
    if (!rate) {
      return amount
    }
    
    return amount / rate
  }, [rates])

  /**
   * Format price in selected currency
   */
  const formatPrice = useCallback((amountRub: number, currency?: string): string => {
    const targetCurrency = currency || selectedCurrency
    const converted = convert(amountRub, targetCurrency)
    const currencyData = getCurrencyByCode(targetCurrency)
    
    if (!currencyData) {
      return `${converted.toFixed(2)} ${targetCurrency}`
    }

    const symbol = currencyData.symbol || targetCurrency
    const formatted = converted.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    })

    // Symbols that go before the amount
    const symbolsBefore = ['$', '€', '£', '¥', '₹', '₽', '₺', '₴', '₸', 'Br', '₩', '₪', '₱', '₫', '₮', '₡', '₲', '₾', '₼']
    
    if (symbolsBefore.includes(symbol)) {
      return `${symbol}${formatted}`
    }
    
    return `${formatted} ${symbol}`
  }, [convert, selectedCurrency])

  /**
   * Update selected currency
   */
  const setSelectedCurrency = useCallback((currency: string) => {
    if (getCurrencyByCode(currency)) {
      setSelectedCurrencyState(currency)
      saveSelectedCurrency(currency)
    }
  }, [])

  /**
   * Get current currency data
   */
  const currentCurrency = getCurrencyByCode(selectedCurrency)

  /**
   * Check if a currency rate is available
   */
  const hasRate = useCallback((currency: string): boolean => {
    return currency in rates
  }, [rates])

  return {
    // State
    rates,
    selectedCurrency,
    loading,
    error,
    currentCurrency,
    
    // Actions
    convert,
    convertToBase,
    formatPrice,
    setSelectedCurrency,
    hasRate,
    
    // Constants
    baseCurrency: BASE_CURRENCY,
    allCurrencies: ALL_CURRENCIES,
  }
}

/**
 * Utility function to get rates synchronously (uses cache)
 */
export function getSyncRates(): ExchangeRates {
  const cached = getCachedRates()
  if (cached) {
    return cached.rates
  }
  return getFallbackRates()
}
