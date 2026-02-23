import { DashboardSidebar } from "@/components/DashboardSidebar"
import { InteractiveSpiderweb } from "@/components/InteractiveSpiderweb"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen bg-background relative overflow-hidden">
      <InteractiveSpiderweb />
      <DashboardSidebar />
      <main className="flex-1 overflow-y-auto bg-muted/10 backdrop-blur-[2px] relative z-10">
        <div className="container mx-auto max-w-7xl p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
