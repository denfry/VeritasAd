import type { ReactNode } from "react"
import { SiteHeader } from "./SiteHeader"
import { SiteFooter } from "./SiteFooter"
import { InteractiveSpiderweb } from "./InteractiveSpiderweb"

export function SiteShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col text-foreground relative">
      <InteractiveSpiderweb />
      <div className="relative z-10 flex flex-col min-h-screen">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </div>
    </div>
  )
}
