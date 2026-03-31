"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, ShieldCheck, Sparkles, X, User } from "lucide-react"
import { cn } from "@/lib/utils"
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
  const pathname = usePathname()

  return (
    <motion.header
      className="sticky top-0 z-50 border-b border-border/50 bg-background/72 backdrop-blur-2xl supports-[backdrop-filter]:bg-background/65"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
    >
      <div className="container mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group shrink-0">
          <motion.span
            className="inline-flex h-8 w-8 items-center justify-center rounded-full gradient-premium text-primary-foreground shadow-[0_8px_20px_-8px_hsl(var(--primary)/0.55)]"
            whileHover={{ scale: 1.06, rotate: 5 }}
            transition={{ duration: 0.18 }}
          >
            <ShieldCheck className="h-4.5 w-4.5" />
          </motion.span>
          <span className="gradient-text hidden sm:inline-block text-base font-semibold">VeritasAd</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-0.5 text-sm">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href))
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "nav-link",
                  isActive && "nav-link-active"
                )}
              >
                {link.label}
              </Link>
            )
          })}
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
              <Link href="/analyze" className="hidden sm:inline-flex btn btn-primary btn-premium h-9 px-4 text-xs">
                <Sparkles className="h-3.5 w-3.5" />
                Analyze
              </Link>
              <Link
                href="/account"
                className="hidden md:inline-flex btn btn-ghost h-9 w-9 p-0 rounded-full"
                title="Account"
              >
                <User className="h-4 w-4" />
              </Link>
            </>
          ) : (
            <>
              <Link href="/auth/login" className="btn btn-ghost h-9 px-4 hidden sm:inline-flex text-xs">
                Sign in
              </Link>
              <Link href="/auth/register" className="btn btn-primary btn-premium h-9 px-4 hidden sm:inline-flex text-xs">
                Get started
              </Link>
            </>
          )}

          {/* Mobile menu button */}
          <motion.button
            type="button"
            onClick={() => setIsOpen((open) => !open)}
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-full border border-border/70 bg-background/80 text-muted-foreground hover:text-foreground hover:border-primary/40 hover:bg-primary/5 transition-all backdrop-blur-sm"
            aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
            whileTap={{ scale: 0.93 }}
          >
            <AnimatePresence mode="wait" initial={false}>
              {isOpen ? (
                <motion.div
                  key="x"
                  initial={{ opacity: 0, rotate: -90 }}
                  animate={{ opacity: 1, rotate: 0 }}
                  exit={{ opacity: 0, rotate: 90 }}
                  transition={{ duration: 0.18 }}
                >
                  <X className="h-4 w-4" />
                </motion.div>
              ) : (
                <motion.div
                  key="menu"
                  initial={{ opacity: 0, rotate: 90 }}
                  animate={{ opacity: 1, rotate: 0 }}
                  exit={{ opacity: 0, rotate: -90 }}
                  transition={{ duration: 0.18 }}
                >
                  <Menu className="h-4 w-4" />
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
            className="md:hidden border-t border-border/50 bg-background/92 backdrop-blur-2xl"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
          >
            <div className="container mx-auto max-w-6xl px-4 py-4 flex flex-col gap-1 text-sm">
              {navLinks.map((link, index) => {
                const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href))
                return (
                  <motion.div
                    key={link.href}
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.04 }}
                  >
                    <Link
                      href={link.href}
                      className={cn(
                        "block rounded-xl px-3 py-2.5 font-medium transition-colors",
                        isActive
                          ? "bg-accent/70 text-foreground"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                      )}
                      onClick={() => setIsOpen(false)}
                    >
                      {link.label}
                    </Link>
                  </motion.div>
                )
              })}

              <div className="pt-3 mt-2 border-t border-border/50">
                {user ? (
                  <div className="flex flex-col gap-2">
                    <Link
                      href="/account"
                      className="block rounded-xl px-3 py-2.5 font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                      onClick={() => setIsOpen(false)}
                    >
                      Account
                    </Link>
                    <Link
                      href="/analyze"
                      className="btn btn-primary btn-premium w-full"
                      onClick={() => setIsOpen(false)}
                    >
                      <Sparkles className="h-4 w-4" />
                      Start analysis
                    </Link>
                  </div>
                ) : (
                  <div className="flex flex-col gap-2">
                    <Link
                      href="/auth/login"
                      className="btn btn-outline"
                      onClick={() => setIsOpen(false)}
                    >
                      Sign in
                    </Link>
                    <Link
                      href="/auth/register"
                      className="btn btn-primary btn-premium"
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

export function CurrencySelectorCompact() {
  const { selectedCurrency, setSelectedCurrency } = useCurrency()

  return (
    <CurrencySelector
      selectedCurrency={selectedCurrency}
      onCurrencyChange={setSelectedCurrency}
    />
  )
}
