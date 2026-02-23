'use client'

import React, { createContext, useContext, useCallback, useMemo } from 'react'
import { useCurrencyRates, ExchangeRates } from '@/hooks/useCurrencyRates'
import { ALL_CURRENCIES, getCurrencyByCode, Currency } from '@/lib/currency'

interface CurrencyContextValue {
  // State
  rates: ExchangeRates
  selectedCurrency: string
  loading: boolean
  error: string | null
  currentCurrency: Currency | undefined
  
  // Actions
  convert: (amountRub: number, targetCurrency?: string) => number
  convertToBase: (amount: number, fromCurrency: string) => number
  formatPrice: (amountRub: number, currency?: string) => string
  setSelectedCurrency: (currency: string) => void
  hasRate: (currency: string) => boolean
  
  // Constants
  baseCurrency: string
  allCurrencies: Currency[]
}

const CurrencyContext = createContext<CurrencyContextValue | undefined>(undefined)

interface CurrencyProviderProps {
  children: React.ReactNode
}

export function CurrencyProvider({ children }: CurrencyProviderProps) {
  const currencyHook = useCurrencyRates()
  
  const value = useMemo<CurrencyContextValue>(() => ({
    rates: currencyHook.rates,
    selectedCurrency: currencyHook.selectedCurrency,
    loading: currencyHook.loading,
    error: currencyHook.error,
    currentCurrency: currencyHook.currentCurrency,
    convert: currencyHook.convert,
    convertToBase: currencyHook.convertToBase,
    formatPrice: currencyHook.formatPrice,
    setSelectedCurrency: currencyHook.setSelectedCurrency,
    hasRate: currencyHook.hasRate,
    baseCurrency: currencyHook.baseCurrency,
    allCurrencies: currencyHook.allCurrencies,
  }), [currencyHook])
  
  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  )
}

/**
 * Hook для использования валюты в любом компоненте приложения
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { formatPrice, selectedCurrency } = useCurrency()
 *   return <div>Price: {formatPrice(10000)}</div>
 * }
 * ```
 */
export function useCurrency(): CurrencyContextValue {
  const context = useContext(CurrencyContext)
  if (context === undefined) {
    throw new Error(
      'useCurrency must be used within a CurrencyProvider. ' +
      'Wrap your app with <CurrencyProvider> in layout.tsx'
    )
  }
  return context
}

/**
 * Компонент для отображения цены в выбранной валюте
 * 
 * @example
 * ```tsx
 * <Price amount={7900} />  // Покажет цену в выбранной валюте
 * <Price amount={7900} showOriginal />  // Покажет цену и оригинал в RUB
 * ```
 */
interface PriceProps {
  amount: number
  className?: string
  showOriginal?: boolean
  currency?: string  // Переопределить валюту для конкретного случая
}

export function Price({ amount, className = '', showOriginal = false, currency }: PriceProps) {
  const { formatPrice, selectedCurrency } = useCurrency()
  
  const formattedPrice = formatPrice(amount, currency)
  const showOriginalPrice = showOriginal && selectedCurrency !== 'RUB'
  
  return (
    <span className={className}>
      {formattedPrice}
      {showOriginalPrice && (
        <span className="text-sm text-muted-foreground ml-2">
          ({formatPrice(amount, 'RUB')})
        </span>
      )}
    </span>
  )
}

/**
 * Компонент для отображения цены с периодом оплаты
 * 
 * @example
 * ```tsx
 * <PricePerMonth amount={7900} />  // "$87 / month"
 * ```
 */
interface PricePerMonthProps {
  amount: number
  className?: string
  period?: 'month' | 'year' | 'once'
}

export function PricePerMonth({ amount, className = '', period = 'month' }: PricePerMonthProps) {
  const { formatPrice } = useCurrency()
  
  const formattedPrice = formatPrice(amount)
  const periodText = period === 'month' ? '/ month' : period === 'year' ? '/ year' : ''
  
  return (
    <span className={className}>
      {formattedPrice}
      <span className="text-sm text-muted-foreground">{periodText}</span>
    </span>
  )
}

/**
 * Компонент для отображения экономии
 * 
 * @example
 * ```tsx
 * <SavingsBadge originalPrice={15000} salePrice={7900} />  // "Save 47%"
 * ```
 */
interface SavingsBadgeProps {
  originalPrice: number
  salePrice: number
  className?: string
}

export function SavingsBadge({ originalPrice, salePrice, className = '' }: SavingsBadgeProps) {
  const savings = Math.round(((originalPrice - salePrice) / originalPrice) * 100)
  
  return (
    <span className={`badge bg-green-500/10 text-green-600 dark:text-green-400 ${className}`}>
      Save {savings}%
    </span>
  )
}
