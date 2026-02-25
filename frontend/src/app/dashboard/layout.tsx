"use client"

import { useState } from "react"
import { DashboardSidebar } from "@/components/DashboardSidebar"
import { InteractiveSpiderweb } from "@/components/InteractiveSpiderweb"
import { Menu, X, ShieldCheck } from "lucide-react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-background relative overflow-hidden">
      <InteractiveSpiderweb />
      
      {/* Desktop Sidebar */}
      <div className="hidden md:flex">
        <DashboardSidebar />
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between px-4 h-14 border-b bg-card/50 backdrop-blur-md z-30">
          <Link href="/" className="flex items-center gap-2 font-bold">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <span>VeritasAd</span>
          </Link>
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-md hover:bg-accent"
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </header>

        {/* Mobile Menu Overlay */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed inset-0 z-40 md:hidden bg-card"
            >
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between px-4 h-14 border-b">
                   <Link href="/" className="flex items-center gap-2 font-bold">
                    <ShieldCheck className="h-5 w-5 text-primary" />
                    <span>VeritasAd</span>
                  </Link>
                  <button 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="p-2 rounded-md hover:bg-accent"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto" onClick={() => setIsMobileMenuOpen(false)}>
                  <DashboardSidebar />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <main className="flex-1 overflow-y-auto bg-muted/10 backdrop-blur-[2px] relative z-10">
          <div className="container mx-auto max-w-7xl p-4 md:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
