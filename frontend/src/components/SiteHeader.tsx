"use client"

import { useState } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, ShieldCheck, Sparkles, X, User, Globe } from "lucide-react"
import { ThemeToggle } from "./ThemeToggle"
import { CurrencySelector } from "./CurrencySelector"
import { useAuth } from "@/contexts/auth-context"
import { useCurrency } from "@/contexts/currency-context"

const navLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/analyze", label: "Analyze" },
  { href: "/history", label: "History" },
  { href: "/pricing", label: "Pricing" },
  { href: "/docs", label: "Docs" },
]

export function SiteHeader() {
  const [isOpen, setIsOpen] = useState(false)
  const { user } = useAuth()

  return (
    <motion.header
      className="sticky top-0 z-50 border-b border-border/50 glass"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="container mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 font-semibold text-lg group">
          <motion.span
            className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-primary"
            whileHover={{ scale: 1.05, rotate: 5 }}
            transition={{ duration: 0.2 }}
          >
            <ShieldCheck className="h-5 w-5" />
          </motion.span>
          <span className="gradient-text hidden sm:inline-block">VeritasAd</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1 text-sm">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="relative px-3 py-2 text-muted-foreground hover:text-foreground transition-colors group"
            >
              {link.label}
              <span className="absolute inset-x-2 -bottom-px h-px bg-gradient-primary scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2 text-sm">
          {/* Currency Selector - Desktop */}
          <div className="hidden lg:block">
            <CurrencySelectorCompact />
          </div>

          <ThemeToggle />
          
          {user ? (
            <>
              <Link href="/analyze" className="hidden sm:inline-flex btn btn-primary">
                <Sparkles className="h-4 w-4" />
                Start
              </Link>
              <Link
                href="/account"
                className="hidden md:inline-flex btn btn-ghost"
                title="Account"
              >
                <User className="h-4 w-4" />
              </Link>
            </>
          ) : (
            <>
              <Link href="/auth/login" className="btn btn-ghost hidden sm:inline-flex">
                Sign in
              </Link>
              <Link href="/auth/register" className="btn btn-primary hidden sm:inline-flex">
                Get started
              </Link>
            </>
          )}
          
          {/* Mobile menu button */}
          <motion.button
            type="button"
            onClick={() => setIsOpen((open) => !open)}
            className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-background text-muted-foreground hover:text-foreground hover:border-primary/50 hover:bg-primary/5 transition-all"
            aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
            whileTap={{ scale: 0.95 }}
          >
            <AnimatePresence mode="wait" initial={false}>
              {isOpen ? (
                <motion.div
                  key="x"
                  initial={{ opacity: 0, rotate: -90 }}
                  animate={{ opacity: 1, rotate: 0 }}
                  exit={{ opacity: 0, rotate: 90 }}
                  transition={{ duration: 0.2 }}
                >
                  <X className="h-5 w-5" />
                </motion.div>
              ) : (
                <motion.div
                  key="menu"
                  initial={{ opacity: 0, rotate: 90 }}
                  animate={{ opacity: 1, rotate: 0 }}
                  exit={{ opacity: 0, rotate: -90 }}
                  transition={{ duration: 0.2 }}
                >
                  <Menu className="h-5 w-5" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="md:hidden border-t border-border/50 glass"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="container mx-auto max-w-6xl px-4 py-4 flex flex-col gap-2 text-sm">
              {navLinks.map((link, index) => (
                <motion.div
                  key={link.href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    href={link.href}
                    className="block rounded-lg px-3 py-2 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    {link.label}
                  </Link>
                </motion.div>
              ))}
              
              <div className="pt-2 mt-2 border-t border-border/50">
                {user ? (
                  <>
                    <Link
                      href="/account"
                      className="block rounded-lg px-3 py-2 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                      onClick={() => setIsOpen(false)}
                    >
                      Account
                    </Link>
                    <Link
                      href="/analyze"
                      className="btn btn-primary w-full mt-2"
                      onClick={() => setIsOpen(false)}
                    >
                      <Sparkles className="h-4 w-4" />
                      Start analysis
                    </Link>
                  </>
                ) : (
                  <div className="flex flex-col gap-2 pt-2">
                    <Link
                      href="/auth/login"
                      className="btn btn-outline"
                      onClick={() => setIsOpen(false)}
                    >
                      Sign in
                    </Link>
                    <Link
                      href="/auth/register"
                      className="btn btn-primary"
                      onClick={() => setIsOpen(false)}
                    >
                      Get started
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  )
}

/**
 * Compact currency selector for header
 */
function CurrencySelectorCompact() {
  const { selectedCurrency, setSelectedCurrency } = useCurrency()
  
  return (
    <CurrencySelector
      selectedCurrency={selectedCurrency}
      onCurrencyChange={setSelectedCurrency}
    />
  )
}
