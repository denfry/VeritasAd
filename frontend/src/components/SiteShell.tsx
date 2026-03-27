import type { ReactNode } from "react"
import { SiteHeader } from "./SiteHeader"
import { SiteFooter } from "./SiteFooter"

export function SiteShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden text-foreground">
      <div className="relative z-10 flex min-h-screen flex-col">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </div>
    </div>
  )
}
