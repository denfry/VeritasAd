import type { ReactNode } from "react"
import { SiteHeader } from "./SiteHeader"
import { SiteFooter } from "./SiteFooter"
import { InteractiveSpiderweb } from "./InteractiveSpiderweb"

export function SiteShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden text-foreground">
      <div className="pointer-events-none absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(14,165,233,0.13),transparent_40%),radial-gradient(circle_at_80%_85%,rgba(6,182,212,0.1),transparent_38%)]" />
      </div>
      <InteractiveSpiderweb />
      <div className="relative z-10 flex flex-col min-h-screen">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </div>
    </div>
  )
}
