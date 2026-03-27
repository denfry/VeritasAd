"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, Cookie, Settings } from "lucide-react"
import { Switch } from "@/components/ui/Switch"

interface CookieCategory {
  id: string
  name: string
  nameRu: string
  description: string
  descriptionRu: string
  required: boolean
}

const COOKIE_CATEGORIES: CookieCategory[] = [
  {
    id: "necessary",
    name: "Necessary",
    nameRu: "Необходимые",
    description: "Essential for the website to function properly",
    descriptionRu: "Необходимы для работы сайта",
    required: true,
  },
  {
    id: "analytics",
    name: "Analytics",
    nameRu: "Аналитика",
    description: "Help us understand how visitors interact with our website",
    descriptionRu: "Помогают понять, как посетители взаимодействуют с сайтом",
    required: false,
  },
  {
    id: "marketing",
    name: "Marketing",
    nameRu: "Маркетинг",
    description: "Used to deliver personalized advertisements",
    descriptionRu: "Используются для показа персонализированной рекламы",
    required: false,
  },
  {
    id: "functional",
    name: "Functional",
    nameRu: "Функциональные",
    description: "Enable enhanced functionality and personalization",
    descriptionRu: "Обеспечивают расширенный функционал и персонализацию",
    required: false,
  },
]

interface ConsentState {
  necessary: boolean
  analytics: boolean
  marketing: boolean
  functional: boolean
  timestamp: string
  version: string
}

const DEFAULT_CONSENT: ConsentState = {
  necessary: true,
  analytics: false,
  marketing: false,
  functional: false,
  timestamp: "",
  version: "1.0",
}

const STORAGE_KEY = "veritasad_cookie_consent"

export function CookieConsent() {
  const [showSettings, setShowSettings] = React.useState(false)
  const [consent, setConsent] = React.useState<ConsentState>(DEFAULT_CONSENT)
  const [isVisible, setIsVisible] = React.useState(false)
  const [isMounted, setIsMounted] = React.useState(false)

  React.useEffect(() => {
    setIsMounted(true)
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setConsent(parsed)
      } catch {
        setIsVisible(true)
      }
    } else {
      setIsVisible(true)
    }
  }, [])

  const saveConsent = (newConsent: ConsentState) => {
    const consentWithTimestamp = {
      ...newConsent,
      timestamp: new Date().toISOString(),
      version: "1.0",
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(consentWithTimestamp))
    setConsent(consentWithTimestamp)
    
    // Apply consent (enable/disable trackers)
    if (newConsent.analytics) {
      // Enable analytics
      console.log("Analytics cookies enabled")
    }
    if (newConsent.marketing) {
      // Enable marketing
      console.log("Marketing cookies enabled")
    }
    if (newConsent.functional) {
      // Enable functional
      console.log("Functional cookies enabled")
    }
  }

  const acceptAll = () => {
    const allConsent: ConsentState = {
      necessary: true,
      analytics: true,
      marketing: true,
      functional: true,
      timestamp: "",
      version: "1.0",
    }
    saveConsent(allConsent)
    setIsVisible(false)
  }

  const rejectAll = () => {
    const minimalConsent: ConsentState = {
      necessary: true,
      analytics: false,
      marketing: false,
      functional: false,
      timestamp: "",
      version: "1.0",
    }
    saveConsent(minimalConsent)
    setIsVisible(false)
  }

  const saveSettings = () => {
    saveConsent(consent)
    setIsVisible(false)
    setShowSettings(false)
  }

  const updateCategory = (id: string, value: boolean) => {
    setConsent(prev => ({ ...prev, [id]: value }))
  }

  if (!isMounted) return null

  return (
    <>
      {/* Floating button to reopen settings */}
      <AnimatePresence>
        {!isVisible && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={() => setIsVisible(true)}
            className="fixed bottom-20 right-4 z-40 flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm text-primary-foreground shadow-lg hover:bg-primary/90 md:bottom-4"
          >
            <Cookie className="h-4 w-4" />
            <span className="hidden sm:inline">Cookie Settings</span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Main banner */}
      <AnimatePresence>
        {isVisible && !showSettings && (
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background/95 backdrop-blur-md p-4 shadow-2xl md:bottom-4 md:left-auto md:right-4 md:max-w-md md:rounded-2xl md:border"
          >
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="rounded-full bg-primary/10 p-2">
                  <Cookie className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold">Cookie Consent</h3>
                  <p className="text-sm text-muted-foreground">
                    We use cookies to enhance your experience. You can customize your preferences or accept all cookies.
                  </p>
                </div>
                <button
                    onClick={() => setIsVisible(false)}
                    className="rounded-md p-1 hover:bg-muted"
                  >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={acceptAll}
                  className="btn btn-primary flex-1"
                >
                  Accept All
                </button>
                <button
                  onClick={rejectAll}
                  className="btn btn-outline flex-1"
                >
                  Reject All
                </button>
                <button
                  onClick={() => setShowSettings(true)}
                  className="btn btn-ghost flex-1 gap-2"
                >
                  <Settings className="h-4 w-4" />
                  Customize
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings modal */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-lg rounded-2xl border bg-background p-6 shadow-2xl"
            >
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-xl font-semibold">Cookie Settings</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="rounded-md p-1 hover:bg-muted"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-4 mb-6">
                {COOKIE_CATEGORIES.map((category) => (
                  <div
                    key={category.id}
                    className="flex items-start justify-between gap-4 rounded-lg border p-4"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{category.name}</h4>
                        {category.required && (
                          <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-xs text-amber-600">
                            Required
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {category.description}
                      </p>
                    </div>
                    <Switch
                      checked={consent[category.id as keyof ConsentState] as boolean}
                      onChange={(checked) => updateCategory(category.id, checked)}
                      disabled={category.required}
                    />
                  </div>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setConsent(DEFAULT_CONSENT)
                    saveSettings()
                  }}
                  className="btn btn-outline flex-1"
                >
                  Save Necessary Only
                </button>
                <button
                  onClick={saveSettings}
                  className="btn btn-primary flex-1"
                >
                  Save Preferences
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export function getCookieConsent(): ConsentState | null {
  if (typeof window === "undefined") return null
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch {
      return null
    }
  }
  return null
}
